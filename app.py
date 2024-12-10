import asyncio
import aiohttp
import logging
import requests
import yaml
import json
import os
from newspaper import Article
from urllib.parse import urlparse
from aiohttp import ClientSession, TCPConnector, ClientTimeout
from tqdm.asyncio import tqdm_asyncio
from urllib.robotparser import RobotFileParser
from langdetect import detect
from translate import Translator
from itertools import cycle

# Configure logging
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

# Load configuration from config.yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

API_KEY = config['api_key']
CSE_ID = config['cse_id']
blocked_domains = config.get('blocked_domains', [])
proxies_list = config.get('proxies', [])

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
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json()
        urls = [item['link'] for item in results.get('items', [])]
        return urls
    except requests.exceptions.RequestException as e:
        logging.error(f"Google Search API request failed: {e}")
        error_log.append(f"Google Search API request failed: {e}")
        return []


def is_blocked(url, blocked_domains):
    """Check if the URL's domain is in the list of blocked domains."""
    domain = urlparse(url).netloc.lower()
    for blocked_domain in blocked_domains:
        if blocked_domain in domain:
            return True
    return False

def is_allowed(url, user_agent='*'):
    """Check if scraping is allowed by robots.txt."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        return rp.can_fetch(user_agent, url)
    except:
        return False  # Disallow if robots.txt cannot be read

def get_proxy():
    """Get a proxy from the list, if available."""
    if proxies_list:
        return next(get_proxy.proxy_cycle)
    return None

get_proxy.proxy_cycle = cycle(proxies_list) if proxies_list else None

async def fetch_article(session, url, headers, semaphore, proxy=None, retries=3):
    """Asynchronously fetch and parse an article."""
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, headers=headers, timeout=10, proxy=proxy) as response:
                    if response.status == 403:
                        logging.error(f"Access denied to {url}: HTTP 403 Forbidden.")
                        error_log.append(f"Access denied to {url}: HTTP 403 Forbidden.")
                        return None
                    elif response.status != 200:
                        logging.error(f"Failed to fetch {url}: HTTP {response.status}")
                        error_log.append(f"Failed to fetch {url}: HTTP {response.status}")
                        return None
                    html = await response.text()
                    article = Article(url)
                    article.set_html(html)
                    article.parse()
                    # Enhanced Content Filtering
                    if len(article.text.split()) < 200:
                        logging.info(f"Article at {url} is too short; skipping.")
                        print(f"Article at {url} is too short; skipping.")
                        return None
                    # Multi-language Support
                    lang = detect(article.text)
                    if lang != 'en':
                        logging.info(f"Translating article at {url} from {lang} to English.")
                        print(f"Translating article at {url} from {lang} to English.")
                        translator = Translator(to_lang='en')
                        article.text = translator.translate(article.text)
                    return {
                        'url': url,
                        'title': article.title or 'No Title',
                        'authors': article.authors or [],
                        'publish_date': (article.publish_date.strftime('%Y-%m-%d')
                                         if article.publish_date else 'No Publish Date'),
                        'content': article.text
                    }
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Error fetching article at {url}: {e}. Retrying ({attempt + 1}/{retries})...")
                await asyncio.sleep(2)  # Wait before retrying
                continue
            else:
                logging.error(f"Error fetching article at {url}: {e}")
                error_log.append(f"Error fetching article at {url}: {e}")
                return None

async def scrape_contents(urls):
    """Scrape contents from a list of URLs asynchronously."""
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/94.0.4606.81 Safari/537.36')
    }
    semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
    connector = TCPConnector(limit_per_host=2)
    async with ClientSession(connector=connector) as session:
        tasks = []
        for url in urls:
            proxy = get_proxy() if proxies_list else None
            tasks.append(fetch_article(session, url, headers, semaphore, proxy))
        # Progress Indicator
        contents = []
        for task in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            content = await task
            contents.append(content)
    return contents

def summarize_with_pegasus(text, max_length=150, min_length=40):
    """
    Summarize the input text using Pegasus.

    Args:
        text (str): The text to summarize.
        max_length (int): Maximum length of the summary.
        min_length (int): Minimum length of the summary.

    Returns:
        str: The summarized text.
    """
    tokens = tokenizer(text, truncation=True, padding='longest', return_tensors="pt").to(DEVICE)
    summary_ids = model.generate(
        tokens['input_ids'],
        num_beams=4,
        max_length=max_length,
        min_length=min_length,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

async def collect_and_scrape(query, desired_num_articles, max_api_calls=10, max_urls_to_attempt=10):
    """Collect URLs based on query and scrape articles."""
    collected_urls = []
    valid_articles = []
    start_index = 1
    api_calls_made = 0
    error_log = []

    while len(valid_articles) < desired_num_articles and api_calls_made < max_api_calls:
        # Fetch more URLs as needed
        num_results = 10  # Fetch 10 results at a time to increase chances
        urls = google_search(API_KEY, CSE_ID, query, num_results=num_results, start_index=start_index)
        api_calls_made += 1

        if not urls:
            logging.info("No more results from Google.")
            break

        # Filter out blocked domains
        filtered_urls = [url for url in urls if not is_blocked(url, blocked_domains)]

        # Check robots.txt compliance
        allowed_urls = [url for url in filtered_urls if is_allowed(url)]

        # Add allowed URLs to the collected list
        collected_urls.extend(allowed_urls)

        # Remove duplicates
        collected_urls = list(dict.fromkeys(collected_urls))

        # Update the start index for the next API call
        start_index += num_results

        # Limit the number of URLs to attempt
        if len(collected_urls) >= max_urls_to_attempt:
            collected_urls = collected_urls[:max_urls_to_attempt]
            break

        await asyncio.sleep(1)  # Respectful delay between API calls

    logging.info(f"Collected {len(collected_urls)} URLs after filtering.")

    # Scrape the content of each URL asynchronously
    logging.info("Scraping content from collected URLs...")
    contents = await scrape_contents(collected_urls)

    # Collect data in a list of dictionaries
    for content in contents:
        if content:
            valid_articles.append(content)
            logging.info(f"Article '{content['title']}' added to valid articles.")
            if len(valid_articles) >= desired_num_articles:
                break
        else:
            logging.info("No content retrieved or article skipped.")

    if not valid_articles:
        logging.error("No valid articles were collected.")
        raise Exception("No valid articles found.")

    # Summarize each article individually
    individual_summaries = []
    for article in valid_articles:
        try:
            summary = summarize_with_pegasus(article['content'])
            article['summary'] = summary
            individual_summaries.append(summary)
        except Exception as e:
            logging.error(f"Summarization failed for article '{article['title']}': {e}")
            # Fallback: Use first 500 characters
            article['summary'] = article['content'][:500] + "..."
            individual_summaries.append(article['summary'])

    # Combine all individual summaries into one text
    combined_summaries = " ".join(individual_summaries)

    try:
        # Generate a unified summary from the combined summaries
        final_summary = summarize_with_pegasus(combined_summaries, max_length=200, min_length=80)
    except Exception as e:
        logging.error(f"Final summarization failed: {e}")
        final_summary = combined_summaries  # Fallback to combined summaries

    # Prepare the result with articles and the final summary
    result = {
        'articles': valid_articles[:desired_num_articles],
        'final_summary': final_summary
    }

    # Save articles to JSON file
    output_file = config.get('output_file', 'output.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    logging.info(f"Data written to {output_file}.")

    # Exception Handling and Reporting
    if error_log:
        logging.info("Errors encountered during scraping:")
        for error in error_log:
            logging.info(error)

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
