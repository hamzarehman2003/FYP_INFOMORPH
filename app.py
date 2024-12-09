# scraper.py

import asyncio

import logging
import requests
import argparse
import yaml
import time
import json
from newspaper import Article
from urllib.parse import urlparse
from aiohttp import ClientSession, TCPConnector, ClientTimeout
from tqdm.asyncio import tqdm_asyncio
from urllib.robotparser import RobotFileParser
from langdetect import detect
from translate import Translator
from itertools import cycle
import threading
from queue import Queue


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

# Command-line arguments
parser = argparse.ArgumentParser(description='Web Article Scraper')
parser.add_argument('--query', type=str, help='Search query', required=True)
parser.add_argument('--num_urls', type=int, default=5, help='Number of articles to collect')
parser.add_argument('--output', type=str, default='output.json', help='Output file name')
args = parser.parse_args()

query = args.query
desired_num_articles = args.num_urls
output_file = args.output

# Initialize variables
collected_urls = []
start_index = 1
max_api_calls = 10  # To prevent infinite loops
api_calls_made = 0

error_log = []

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
        print(f"Google Search API request failed: {e}")
        error_log.append(f"Google Search API request failed: {e}")
        return []


def is_blocked(url, blocked_domains):
    """Check if the URL's domain is in the list of blocked domains."""
    domain = urlparse(url).netloc.lower()
    for blocked_domain in blocked_domains:
        if blocked_domain in domain:
            return True
    return False

async def fetch_robots_txt(robots_url, timeout):
    """Asynchronously fetch robots.txt with a timeout."""
    async with ClientSession(timeout=ClientTimeout(total=timeout)) as session:
        try:
            async with session.get(robots_url) as response:
                if response.status == 200:
                    text = await response.text()
                    return text
                else:
                    print(f"Non-200 response from {robots_url}: {response.status}")
                    return None
        except asyncio.TimeoutError:
            print(f"Timeout occurred while fetching {robots_url}")
        except Exception as e:
            print(f"Error fetching robots.txt from {robots_url}: {e}")
        return None

async def parse_robots_txt(robots_txt, url, user_agent='*'):
    """Parse the fetched robots.txt and check permissions."""
    from urllib.robotparser import RobotFileParser
    rp = RobotFileParser()
    rp.parse(robots_txt.splitlines())
    return rp.can_fetch(user_agent, url)

async def is_allowed_async(url, user_agent='*', timeout=5):
    """Check if scraping is allowed asynchronously with timeout."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    print(f"Fetching robots.txt from {robots_url}")
    
    robots_txt = await fetch_robots_txt(robots_url, timeout)
    if robots_txt is None:
        print(f"Skipping {url} as robots.txt could not be fetched.")
        return False

    allowed = await parse_robots_txt(robots_txt, url, user_agent)
    if not allowed:
        print(f"Scraping not allowed for {url} as per robots.txt.")
    return allowed

async def is_allowed(url, user_agent='*', timeout=5):
    """Check if scraping is allowed asynchronously with timeout."""
    return await is_allowed_async(url, user_agent, timeout)
def get_proxy():
    """Get a proxy from the list, if available."""
    if proxies_list:
        return next(get_proxy.proxy_cycle)
    return None

get_proxy.proxy_cycle = cycle(proxies_list)

async def fetch_article(session, url, headers, semaphore, proxy=None, retries=3):
    """Asynchronously fetch and parse an article."""
    for attempt in range(retries):
        try:
            async with semaphore:
                async with session.get(url, headers=headers, timeout=10, proxy=proxy) as response:
                    if response.status == 403:
                        logging.error(f"Access denied to {url}: HTTP 403 Forbidden.")
                        print(f"Access denied to {url}: HTTP 403 Forbidden.")
                        error_log.append(f"Access denied to {url}: HTTP 403 Forbidden.")
                        return None
                    elif response.status != 200:
                        logging.error(f"Failed to fetch {url}: HTTP {response.status}")
                        print(f"Failed to fetch {url}: HTTP {response.status}")
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
                await asyncio.sleep(2)  # Wait before retrying
                continue
            else:
                logging.error(f"Error fetching article at {url}: {e}") 
                print(f"Error fetching article at {url}: {e}")
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
            proxy = get_proxy()
            tasks.append(fetch_article(session, url, headers, semaphore, proxy))
        # Progress Indicator
        contents = []
        for task in tqdm_asyncio.as_completed(tasks, total=len(tasks)):
            content = await task
            contents.append(content)
    return contents

async def main():
    logging.info("Collecting URLs...")
    collected_urls = []
    valid_articles = []
    start_index = 1
    api_calls_made = 0
    max_urls_to_attempt = 10  # Maximum number of URLs to attempt

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

        # Check robots.txt compliance asynchronously
        allowed_urls = []
        for url in filtered_urls:
            if await is_allowed(url):
                allowed_urls.append(url)

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
    else:
        # Write data to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(valid_articles[:desired_num_articles], f, ensure_ascii=False, indent=4)
        logging.info(f"Data written to {output_file}.")

    # Exception Handling and Reporting
    if error_log:
        logging.info("Errors encountered during scraping:")
        for error in error_log:
            logging.info(error)

if __name__ == "__main__":
    asyncio.run(main())
