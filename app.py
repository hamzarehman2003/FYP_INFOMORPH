# backend/app.py

import asyncio
import logging
import requests
import yaml
import json
import os
import time
import re
import html  # For unescaping HTML entities
from newspaper import Article, ArticleException
from urllib.parse import urlparse
from aiohttp import ClientSession, TCPConnector, ClientTimeout, ClientError
from tqdm.asyncio import tqdm_asyncio
from urllib.robotparser import RobotFileParser
from langdetect import detect, LangDetectException
from translate import Translator
from itertools import cycle
from bs4 import BeautifulSoup

# --------------------------------------------------------
# 1) ADD OUR NAIVE TRANSLITERATION MAP AT THE TOP
# --------------------------------------------------------
TRANSLIT_MAP = {
    'a': 'ا', 'b': 'ب', 'c': 'ک', 'd': 'د', 'e': 'ے',
    'f': 'ف', 'g': 'گ', 'h': 'ہ', 'i': 'ی', 'j': 'ج',
    'k': 'ک', 'l': 'ل', 'm': 'م', 'n': 'ن', 'o': 'و',
    'p': 'پ', 'q': 'ق', 'r': 'ر', 's': 'س', 't': 'ت',
    'u': 'ُ', 'v': 'و', 'w': 'و', 'x': 'کس', 'y': 'ے',
    'z': 'ز',
    # You could add uppercase letters or special combos, e.g. 'sh': 'ش'
}

def naive_transliterate_to_urdu(token: str, translit_map: dict) -> str:
    """
    Convert an English token into approximate Urdu script
    by replacing each English letter with an Urdu character.
    """
    result_chars = []
    for ch in token:
        lower_ch = ch.lower()
        if lower_ch in translit_map:
            result_chars.append(translit_map[lower_ch])
        else:
            # Keep digits, punctuation, or unknown characters as-is
            result_chars.append(ch)
    return "".join(result_chars)

def force_urdu_tokens(text: str) -> str:
    """
    If a token is 'mostly English' but the translator didn't convert it,
    forcibly transliterate it using our naive map.
    """
    tokens = text.split()
    new_tokens = []
    for token in tokens:
        # Count how many characters are ASCII letters
        ascii_count = sum(1 for ch in token if ch.isascii() and ch.isalpha())
        # If more than half the chars in a token are ASCII letters => "English"
        if len(token) > 0 and (ascii_count > 0.5 * len(token)):
            # Transliterate brand names, leftover words, etc.
            forced = naive_transliterate_to_urdu(token, TRANSLIT_MAP)
            new_tokens.append(forced)
        else:
            new_tokens.append(token)
    return " ".join(new_tokens)

# --------------------------------------------------------
# Configure logging
# --------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
error_handler = logging.FileHandler('errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(error_handler)

# --------------------------------------------------------
# Load configuration from config.yaml
# --------------------------------------------------------
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    API_KEY = config.get('api_key')
    CSE_ID = config.get('cse_id')
    if not API_KEY or not CSE_ID:
        logging.error("API_KEY or CSE_ID not found in config.yaml")
        raise ValueError("API_KEY and CSE_ID are required in config.yaml")
    blocked_domains = config.get('blocked_domains', [])
    proxies_list = config.get('proxies', [])
    logging.info("Configuration loaded successfully")
except Exception as e:
    logging.error(f"Error loading config.yaml: {e}")
    API_KEY = ""
    CSE_ID = ""
    blocked_domains = []
    proxies_list = []

# --------------------------------------------------------
# Google Search
# --------------------------------------------------------
def google_search(api_key, cse_id, query, num_results=10, start_index=1):
    """Search Google using the Custom Search API and return URLs."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num_results,
        'start': start_index
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        results = response.json()
        urls = [item['link'] for item in results.get('items', [])]
        logging.info(f"Google Search API returned {len(urls)} URLs")
        return urls
    except requests.exceptions.RequestException as e:
        logging.error(f"Google Search API request failed: {e}")
        return []

def is_blocked(url, blocked_domains):
    """Check if the URL's domain is in the list of blocked domains."""
    domain = urlparse(url).netloc.lower()
    for blocked_domain in blocked_domains:
        if blocked_domain in domain:
            logging.info(f"Blocked domain detected: {domain}")
            return True
    return False

def clean_url(url):
    """Clean URL by removing tracking parameters and fragments."""
    parsed = urlparse(url)
    clean_params = "&".join(
        [p for p in parsed.query.split("&") if not p.startswith(('utm_', 'fbclid', 'gclid'))]
    )
    cleaned = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean_params:
        cleaned += f"?{clean_params}"
    return cleaned

# --------------------------------------------------------
# Robots.txt checks
# --------------------------------------------------------
async def fetch_robots_txt(robots_url, timeout):
    """Asynchronously fetch robots.txt with a timeout."""
    async with ClientSession(timeout=ClientTimeout(total=timeout)) as session:
        try:
            async with session.get(robots_url) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                else:
                    logging.info(f"Non-200 response from {robots_url}: {response.status}")
                    return None
        except asyncio.TimeoutError:
            logging.info(f"Timeout occurred while fetching {robots_url}")
        except Exception as e:
            logging.error(f"Error fetching robots.txt from {robots_url}: {e}")
        return None

async def parse_robots_txt(robots_txt, url, user_agent='*'):
    """Parse the fetched robots.txt and check permissions."""
    rp = RobotFileParser()
    rp.parse(robots_txt.splitlines())
    return rp.can_fetch(user_agent, url)

async def is_allowed_async(url, user_agent='*', timeout=5):
    """Check if scraping is allowed asynchronously with timeout."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    logging.info(f"Fetching robots.txt from {robots_url}")
    robots_txt = await fetch_robots_txt(robots_url, timeout)
    if robots_txt is None:
        logging.info(f"Skipping {url} as robots.txt could not be fetched.")
        return True  # Optimistic if not fetchable
    allowed = await parse_robots_txt(robots_txt, url, user_agent)
    if not allowed:
        logging.info(f"Scraping not allowed for {url} as per robots.txt.")
    return allowed

async def is_allowed(url, user_agent='*', timeout=5):
    """Check if scraping is allowed asynchronously with timeout."""
    return await is_allowed_async(url, user_agent, timeout)

# --------------------------------------------------------
# Proxy Handling
# --------------------------------------------------------
def get_proxy():
    """Get a proxy from the list, if available."""
    if proxies_list:
        return next(get_proxy.proxy_cycle)
    return None

get_proxy.proxy_cycle = cycle(proxies_list) if proxies_list else None

# --------------------------------------------------------
# Text Cleaning / Checks
# --------------------------------------------------------
def clean_text(text):
    """Clean and normalize text by removing extra whitespace and control characters."""
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(
        r'(accept all cookies|accept cookies|use cookies|privacy policy|terms of service|terms and conditions|all rights reserved)',
        '',
        text, 
        flags=re.IGNORECASE
    )
    return text

def is_meaningful_content(text, min_length=200, max_ad_ratio=0.3):
    """Check if the text contains meaningful content rather than ads or boilerplate."""
    if not text or len(text.split()) < min_length:
        return False
    ad_patterns = r'(subscribe|subscription|advert|cookie|privacy|sign up|free trial|newsletter|click here)'
    ad_matches = len(re.findall(ad_patterns, text, re.IGNORECASE))
    word_count = len(text.split())
    ad_ratio = ad_matches / word_count if word_count > 0 else 1
    if ad_ratio > max_ad_ratio:
        logging.info(f"Text appears promotional (ad ratio: {ad_ratio:.2f})")
        return False
    return True

# --------------------------------------------------------
# Asynchronous article fetching / parsing
# --------------------------------------------------------
async def fetch_article(session, url, headers, semaphore, proxy=None, retries=3, backoff_factor=1.5):
    """Asynchronously fetch and parse an article with improved error handling and content extraction."""
    url = clean_url(url)
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, headers=headers, timeout=15, proxy=proxy) as response:
                    if response.status == 403:
                        logging.error(f"Access denied to {url}: HTTP 403 Forbidden.")
                        return None
                    elif response.status != 200:
                        logging.error(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
                    html_content = await response.text()
                    if not html_content or len(html_content.strip()) < 100:
                        logging.error(f"Empty or very short HTML from {url}")
                        return None
                    try:
                        article = Article(url)
                        article.set_html(html_content)
                        article.parse()
                        content = article.text
                        if not is_meaningful_content(content):
                            logging.info(f"newspaper3k extracted low-quality content from {url}, trying BeautifulSoup")
                            soup = BeautifulSoup(html_content, 'html.parser')
                            for unwanted in soup.select('script, style, nav, footer, header, [class*="cookie"], [class*="banner"], [class*="ad-"], [class*="advertisement"]'):
                                unwanted.decompose()
                            paragraphs = soup.find_all('p')
                            content = ' '.join([p.get_text() for p in paragraphs if len(p.get_text()) > 30])
                            if not is_meaningful_content(content):
                                logging.info(f"Failed to extract meaningful content from {url}")
                                return None
                        content = clean_text(content)

                        try:
                            lang = detect(content)
                            if lang != 'en':
                                logging.info(f"Translating article at {url} from {lang} to English.")
                                translator = Translator(to_lang='en')
                                # Break content into chunks because some translators have length limits
                                chunks = [content[i:i+500] for i in range(0, len(content), 500)]
                                translated_chunks = [translator.translate(chunk) for chunk in chunks]
                                content = ' '.join(translated_chunks)
                        except Exception as e:
                            logging.error(f"Language detection/translation failed for {url}: {e}")

                        content = clean_text(content)
                        if len(content.split()) < 300:
                            logging.info(f"Article at {url} has insufficient content after processing.")
                            return None
                        return {
                            'url': url,
                            'title': clean_text(article.title) or 'No Title',
                            'authors': article.authors or [],
                            'publish_date': (article.publish_date.strftime('%Y-%m-%d') if article.publish_date else 'No Publish Date'),
                            'content': content
                        }
                    except ArticleException as e:
                        logging.error(f"newspaper3k parsing failed for {url}: {e}")
                        return None
        except (asyncio.TimeoutError, ClientError) as e:
            if attempt < retries - 1:
                wait_time = backoff_factor * (2 ** attempt)
                logging.warning(f"Error fetching article at {url}: {e}. Retrying in {wait_time:.1f}s ({attempt + 1}/{retries})...")
                await asyncio.sleep(wait_time)
                continue
            else:
                logging.error(f"Max retries reached for {url}: {e}")
                return None
        except Exception as e:
            logging.error(f"Unexpected error fetching article at {url}: {e}")
            return None

async def scrape_contents(urls):
    """Scrape contents from a list of URLs asynchronously with improved resilience."""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/94.0.4606.81 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/'
    }
    semaphore = asyncio.Semaphore(3)
    connector = TCPConnector(limit_per_host=2, ssl=False)
    async with ClientSession(connector=connector, headers=headers) as session:
        tasks = []
        for url in urls:
            proxy = get_proxy() if proxies_list else None
            tasks.append(fetch_article(session, url, headers, semaphore, proxy))
        contents = []
        for task in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            try:
                content = await task
                if content:
                    contents.append(content)
            except Exception as e:
                logging.error(f"Error processing task: {e}")
        return [c for c in contents if c is not None]

# --------------------------------------------------------
# Initialize Gemini Summarization (using Google Generative AI)
# --------------------------------------------------------
try:
    import google.generativeai as genai
    GEMINI_API_KEY = config.get('gemini_api_key')
    if not GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY not found in config.yaml")
        raise ValueError("GEMINI_API_KEY is required in config.yaml")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    logging.info("Gemini model initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Gemini model: {e}")
    model = None

# --------------------------------------------------------
# Summary Helpers
# --------------------------------------------------------
def remove_duplicate_sentences(text):
    """Remove duplicate sentences from text with an improved algorithm."""
    if not text:
        return ""
    sentences = re.split(r'(?<=[.!?]) +', text)
    seen = set()
    unique_sentences = []
    for sentence in sentences:
        sentence_clean = re.sub(r'\W+', ' ', sentence.strip().lower())
        sentence_clean = re.sub(r'\s+', ' ', sentence_clean).strip()
        if not sentence_clean or len(sentence_clean) < 10:
            continue
        is_duplicate = False
        for existing in seen:
            if (len(sentence_clean) > 0.9 * len(existing)
                and len(existing) > 0.9 * len(sentence_clean)):
                if sentence_clean in existing or existing in sentence_clean:
                    is_duplicate = True
                    break
        if not is_duplicate:
            seen.add(sentence_clean)
            unique_sentences.append(sentence.strip())
    return ' '.join(unique_sentences)

def clean_summary(summary):
    """Post-process the summary to enhance readability."""
    if not summary:
        return ""
    summary = remove_duplicate_sentences(summary)
    summary = re.sub(r'ARTICLE\s*\d*\s*:', '', summary)
    summary = re.sub(r'([A-Z][a-z]+\s*)+(-|–|:|\|)\s*([A-Z][a-z]+\s*)+', '', summary)
    summary = re.sub(r'[A-Z][A-Z\s]+:', '', summary)
    summary = re.sub(r'\[EMAIL REDACTED\]|\[PHONE REDACTED\]|\[URL REDACTED\]', '', summary)
    summary = re.sub(r'https?://\S+', '', summary)
    summary = re.sub(r'contact.*?information|email|call|phone', '', summary, flags=re.IGNORECASE)
    sentences = re.split(r'(?<=[.!?]) +', summary)
    filtered_sentences = [
        s for s in sentences
        if not re.search(
            r'(located at|address|event details|call|email|contact|pm|am|\d{1,2}:\d{2}'
            r'|January|February|March|April|May|June|July|August'
            r'|September|October|November|December)',
            s, re.IGNORECASE
        )
    ]
    summary = ' '.join(filtered_sentences)
    summary = re.sub(r'\s+', ' ', summary)
    if summary:
        summary = summary[0].upper() + summary[1:]
    if summary and summary[-1] not in '.!?':
        summary += '.'
    return re.sub(r'\s+', ' ', summary).strip()

def format_article_content(articles):
    """Format article content for summarization by concatenating cleaned content without labels."""
    formatted_text = []
    for article in articles:
        content = article['content']
        content = re.sub(r'\s+', ' ', content).strip()
        formatted_text.append(content)
    return ' '.join(formatted_text)

def extractive_summarization_fallback(text, num_sentences=15):
    """Simple extractive summarization as a fallback."""
    logging.info("Using extractive summarization fallback")
    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) <= num_sentences:
        return ' '.join(sentences)
    summary_sentences = sentences[:5]
    middle_start = max(5, len(sentences) // 3)
    middle_end = min(len(sentences) - 5, 2 * len(sentences) // 3)
    middle_step = max(1, (middle_end - middle_start) // 5)
    for i in range(middle_start, middle_end, middle_step):
        if len(summary_sentences) < num_sentences - 5:
            summary_sentences.append(sentences[i])
    summary_sentences.extend(sentences[-5:])
    return ' '.join(summary_sentences[:num_sentences])

def summarize_with_gemini(text, max_length=300, min_length=150, article_count=None):
    """Summarize text using Gemini with fallback to extractive summarization."""
    if not model:
        logging.error("Gemini model not loaded properly. Using fallback summarizer.")
        return extractive_summarization_fallback(text)
    if not text or len(text.strip()) < 100:
        logging.error("Text too short for summarization")
        return "The collected content was insufficient for summarization."
    try:
        article_context = f"from {article_count} sources" if article_count else "from multiple sources"
        prompt = (
            f"Create a cohesive, concise summary focusing on relevant academic or event-related content.\n"
            f"Exclude any technical installation details, browser extension instructions, or non-academic content.\n"
            f"Your summary should be clear, factual, and between {min_length} and {max_length} words.\n\n"
            f"Text (ignore any formatting labels): \n{text[:30000]}"
        )
        generation_config = {
            "temperature": 0.1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        ]
        response = model.generate_content(
            contents=prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        if not hasattr(response, 'text'):
            logging.error("Gemini response has no text attribute")
            return extractive_summarization_fallback(text)
        summary = response.text
        summary = clean_summary(summary)
        word_count = len(summary.split())
        if word_count < min_length:
            logging.warning(f"Gemini generated a short summary ({word_count} words), using fallback")
            return extractive_summarization_fallback(text)
        return summary
    except Exception as e:
        logging.error(f"Error in Gemini summarization: {e}")
        logging.info("Falling back to extractive summarization")
        return extractive_summarization_fallback(text)

def summarize_in_chunks(text, max_length=300, min_length=150):
    """Summarize very long text by splitting it into chunks and combining summaries."""
    chunks = []
    current_chunk = ""
    sentences = re.split(r'(?<=[.!?]) +', text)
    for sentence in sentences:
        if len(current_chunk) + len(sentence) < 4000:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 100:
            continue
        logging.info(f"Summarizing chunk {i+1}/{len(chunks)}")
        try:
            chunk_summary = summarize_with_gemini(
                chunk,
                max_length=max(150, max_length // len(chunks)),
                min_length=min(100, min_length // len(chunks))
            )
            chunk_summaries.append(chunk_summary)
        except Exception as e:
            logging.error(f"Error summarizing chunk {i+1}: {e}")
            continue
    if not chunk_summaries:
        return "Failed to generate summary from chunks."
    combined_summary = " ".join(chunk_summaries)
    if len(combined_summary.split()) > 300:
        try:
            final_summary = summarize_with_gemini(
                combined_summary,
                max_length=max_length,
                min_length=min_length
            )
            return final_summary
        except Exception as e:
            logging.error(f"Error in final summarization: {e}")
            return combined_summary
    else:
        return combined_summary

# --------------------------------------------------------
# collect_and_scrape function with final translation + transliteration
# --------------------------------------------------------
async def collect_and_scrape(
    query,
    desired_num_articles,
    input_language="en",
    output_language="en",
    max_api_calls=10,
    max_urls_to_attempt=20
):
    """Collect URLs based on query and scrape articles. Then summarize and optionally translate to Urdu with forced transliteration."""
    if not API_KEY or not CSE_ID:
        raise ValueError("API_KEY and CSE_ID are required but not properly configured")
    collected_urls = []
    valid_articles = []
    start_index = 1
    api_calls_made = 0
    seen_titles = set()
    
    logging.info(f"Starting collection process for query: '{query}'")
    logging.info(f"Desired article count: {desired_num_articles}")

    while len(valid_articles) < desired_num_articles and api_calls_made < max_api_calls:
        num_results = 10
        urls = google_search(API_KEY, CSE_ID, query, num_results=num_results, start_index=start_index)
        api_calls_made += 1
        if not urls:
            logging.info("No more results from Google.")
            break
        filtered_urls = [url for url in urls if not is_blocked(url, blocked_domains)]
        logging.info(f"Filtered {len(urls) - len(filtered_urls)} blocked domains")
        allowed_urls = []
        for url in filtered_urls:
            allowed = await is_allowed(url)
            if allowed:
                allowed_urls.append(url)
        collected_urls.extend(allowed_urls)
        collected_urls = list(dict.fromkeys(collected_urls))
        logging.info(f"Collected {len(collected_urls)} unique URLs so far")
        start_index += num_results
        if len(collected_urls) >= max_urls_to_attempt:
            collected_urls = collected_urls[:max_urls_to_attempt]
            logging.info(f"Limited URL collection to {max_urls_to_attempt}")
            break
        await asyncio.sleep(1)
    
    if not collected_urls:
        logging.error("No URLs collected after filtering.")
        raise Exception("No valid URLs found for the query.")

    logging.info(f"Scraping content from {len(collected_urls)} collected URLs...")
    contents = await scrape_contents(collected_urls)
    valid_articles = []
    for content in contents:
        if content and content['title'] not in seen_titles:
            valid_articles.append(content)
            seen_titles.add(content['title'])
            logging.info(f"Article '{content['title']}' added to valid articles.")
            if len(valid_articles) >= desired_num_articles:
                break
        else:
            logging.info("No content retrieved, article skipped, or duplicate title found.")

    if not valid_articles:
        logging.error("No valid articles were collected.")
        raise Exception("No valid articles found after scraping.")
        
    valid_articles = valid_articles[:desired_num_articles]
    formatted_text = format_article_content(valid_articles)
    cleaned_text = remove_duplicate_sentences(formatted_text)
    logging.info(f"Formatted content for summarization with {len(cleaned_text.split())} words")
    
    if not is_meaningful_content(cleaned_text):
        logging.error("Combined text is not meaningful enough for summarization.")
        raise Exception("Insufficient unique content for summarization.")

    # ---------------------
    # 1) Generate summary in English
    # ---------------------
    try:
        start_time = time.time()
        try:
            final_summary = summarize_with_gemini(
                cleaned_text, 
                max_length=300,
                min_length=150,
                article_count=len(valid_articles)
            )
        except Exception as e:
            logging.error(f"Gemini summarization failed: {e}")
            final_summary = extractive_summarization_fallback(cleaned_text)
        final_summary = clean_summary(final_summary)
        logging.info(f"Summarization completed in {time.time() - start_time:.2f} seconds")
    except Exception as e:
        logging.error(f"All summarization methods failed: {e}")
        final_summary = "Summary could not be generated. Excerpts: \n\n"
        for article in valid_articles[:3]:
            sentences = re.split(r'(?<=[.!?]) +', article['content'])
            final_summary += f"{article['title']}: {' '.join(sentences[:3])}\n\n"

    word_count = len(final_summary.split())
    logging.info(f"Generated summary with {word_count} words.")

    # ---------------------
    # 2) If English is requested, enforce min/max word logic
    # ---------------------
    if output_language.lower() == "en":
        # If summary is too short, attempt to regenerate
        if word_count < 300:
            logging.warning(f"Generated summary is too short ({word_count} words). Attempting to regenerate.")
            try:
                new_summary = summarize_with_gemini(
                    cleaned_text, 
                    max_length=350,
                    min_length=200,
                    article_count=len(valid_articles)
                )
                new_summary = clean_summary(new_summary)
                new_word_count = len(new_summary.split())
                logging.info(f"Regenerated summary with {new_word_count} words.")
                if new_word_count > word_count:
                    final_summary = new_summary
                    word_count = new_word_count
                if word_count < 300:
                    logging.warning(f"Summary remains short ({word_count} words), returning as is.")
            except Exception as e:
                logging.error(f"Regeneration of summary failed: {e}")

        # If summary is too long, truncate
        elif word_count > 550:
            logging.warning(f"Generated summary is too long ({word_count} words). Truncating.")
            sentences = re.split(r'(?<=[.!?]) +', final_summary)
            truncated_sentences = []
            current_word_count = 0
            for sentence in sentences:
                sentence_word_count = len(sentence.split())
                if current_word_count + sentence_word_count <= 550:
                    truncated_sentences.append(sentence)
                    current_word_count += sentence_word_count
                else:
                    break
            final_summary = ' '.join(truncated_sentences)
            word_count = len(final_summary.split())
            logging.info(f"Truncated summary to {word_count} words at sentence boundaries.")

    # ---------------------
    # 3) If not English, do chunk translation + second pass transliteration
    # ---------------------
    if output_language.lower() != "en":
        try:
            translator = Translator(to_lang=output_language)
            # Break final summary into chunks to avoid "QUERY LENGTH LIMIT EXCEEDED"
            chunk_size = 500
            summary_chunks = [
                final_summary[i:i+chunk_size]
                for i in range(0, len(final_summary), chunk_size)
            ]
            translated_chunks = []
            for chunk in summary_chunks:
                translated_chunk = translator.translate(chunk)
                translated_chunks.append(translated_chunk)
            # Combine all translated chunks
            final_summary = ' '.join(translated_chunks)

            # Second pass: forcibly transliterate leftover English tokens
            final_summary = force_urdu_tokens(final_summary)

            logging.info(f"Final summary forcibly translated to {output_language}")
        except Exception as e:
            logging.error(f"Error translating final summary to {output_language}: {e}")

    # ---------------------
    # Prepare the final result
    # ---------------------
    result = {
        'articles': valid_articles,
        'final_summary': final_summary,
        'meta': {
            'query': query,
            'article_count': len(valid_articles),
            'summary_word_count': len(final_summary.split()),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }

    # Write to output.json if desired
    output_file = config.get('output_file', 'output.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        logging.info(f"Data written to {output_file}.")
    except Exception as e:
        logging.error(f"Failed to write output to file: {e}")

    return result
