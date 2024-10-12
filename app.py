# import asyncio
# import aiohttp
# import logging
# import requests
# from newspaper import Article
# from urllib.parse import urlparse
# import time
# from aiohttp import ClientSession

# # Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler('app.log'),
#         logging.StreamHandler()
#     ]
# )

# def google_search(api_key, cse_id, query, num_results=5, start_index=1):
#     """Search Google using the Custom Search API and return URLs."""
#     url = "https://www.googleapis.com/customsearch/v1"
#     params = {
#         'key': api_key,
#         'cx': cse_id,
#         'q': query,
#         'num': num_results,
#         'start': start_index
#     }
#     try:
#         response = requests.get(url, params=params)
#         response.raise_for_status()
#         results = response.json()
#         urls = [item['link'] for item in results.get('items', [])]
#         return urls
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Google Search API request failed: {e}")
#         return []

# def is_blocked(url, blocked_domains):
#     """Check if the URL's domain is in the list of blocked domains."""
#     domain = urlparse(url).netloc.lower()
#     for blocked_domain in blocked_domains:
#         if blocked_domain in domain:
#             return True
#     return False

# async def fetch_article(session, url, headers):
#     """Asynchronously fetch and parse an article."""
#     try:
#         async with session.get(url, headers=headers, timeout=10) as response:
#             if response.status != 200:
#                 logging.error(f"Failed to fetch {url}: HTTP {response.status}")
#                 return None
#             html = await response.text()
#             article = Article(url)
#             article.set_html(html)
#             article.parse()
#             # Content Filtering: Check article length and language
#             if len(article.text) < 200:
#                 logging.info(f"Article at {url} is too short; skipping.")
#                 return None
#             if article.meta_lang and article.meta_lang != 'en':
#                 logging.info(f"Article at {url} is not in English; skipping.")
#                 return None
#             return article.text
#     except Exception as e:
#         logging.error(f"Error fetching article at {url}: {e}")
#         return None

# async def scrape_contents(urls):
#     """Scrape contents from a list of URLs asynchronously."""
#     headers = {
#         'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                        'AppleWebKit/537.36 (KHTML, like Gecko) '
#                        'Chrome/58.0.3029.110 Safari/537.3')
#     }
#     async with ClientSession() as session:
#         tasks = [fetch_article(session, url, headers) for url in urls]
#         contents = await asyncio.gather(*tasks)
#     return contents

# if __name__ == "__main__":
#     API_KEY = 'AIzaSyCYmndDIOnGCipni1lnhURr6Hm95BvHwi4'
#     CSE_ID = '72e62b8642f194f09'
#     query = input("Enter the topic or keywords to search: ")

#     # List of domains to block
#     blocked_domains = ['reddit.com', 'instagram.com', 'wikipedia.org', 'pk.linkedin.com']

#     # Initialize variables
#     desired_num_urls = 5
#     collected_urls = []
#     start_index = 1
#     max_api_calls = 10  # To prevent infinite loops
#     api_calls_made = 0

#     logging.info("Collecting URLs...")

#     while len(collected_urls) < desired_num_urls and api_calls_made < max_api_calls:
#         # Fetch more URLs as needed
#         num_results = 10  # Fetch 10 results at a time to increase chances
#         urls = google_search(API_KEY, CSE_ID, query, num_results=num_results, start_index=start_index)
#         api_calls_made += 1

#         if not urls:
#             logging.info("No more results from Google.")
#             break

#         # Filter out blocked domains
#         filtered_urls = [url for url in urls if not is_blocked(url, blocked_domains)]

#         # Add filtered URLs to the collected list
#         collected_urls.extend(filtered_urls)

#         # Update the start index for the next API call
#         start_index += num_results

#         # Remove duplicates
#         collected_urls = list(dict.fromkeys(collected_urls))

#         # Limit the collected URLs to the desired number
#         if len(collected_urls) >= desired_num_urls:
#             collected_urls = collected_urls[:desired_num_urls]
#             break

#         time.sleep(1)  # Respectful delay between API calls

#     logging.info(f"Collected {len(collected_urls)} URLs after filtering.")

#     # Scrape the content of each URL asynchronously
#     logging.info("Scraping content from collected URLs...")
#     contents = asyncio.run(scrape_contents(collected_urls))

#     # Display the content
#     for url, content in zip(collected_urls, contents):
#         if content:
#             logging.info(f"Content from {url}:\n{content[:1500]}\n")
#         else:
#             logging.info(f"No content retrieved from {url}.\n")

import asyncio
import aiohttp
import logging
import requests
from newspaper import Article
from urllib.parse import urlparse
import time
from aiohttp import ClientSession

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

def google_search(api_key, cse_id, query, num_results=5, start_index=1):
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
        return []

def is_blocked(url, blocked_domains):
    """Check if the URL's domain is in the list of blocked domains."""
    domain = urlparse(url).netloc.lower()
    for blocked_domain in blocked_domains:
        if blocked_domain in domain:
            return True
    return False

def get_first_n_words(text, n):
    """Return the first n words of the given text."""
    words = text.split()
    return ' '.join(words[:n])

async def fetch_article(session, url, headers):
    """Asynchronously fetch and parse an article."""
    try:
        async with session.get(url, headers=headers, timeout=10) as response:
            if response.status != 200:
                logging.error(f"Failed to fetch {url}: HTTP {response.status}")
                return None
            html = await response.text()
            article = Article(url)
            article.set_html(html)
            article.parse()
            # Content Filtering: Check article length and language
            if len(article.text.split()) < 200:
                logging.info(f"Article at {url} is too short; skipping.")
                return None
            if article.meta_lang and article.meta_lang != 'en':
                logging.info(f"Article at {url} is not in English; skipping.")
                return None
            return article.text
    except Exception as e:
        logging.error(f"Error fetching article at {url}: {e}")
        return None

async def scrape_contents(urls):
    """Scrape contents from a list of URLs asynchronously."""
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/58.0.3029.110 Safari/537.3')
    }
    async with ClientSession() as session:
        tasks = [fetch_article(session, url, headers) for url in urls]
        contents = await asyncio.gather(*tasks)
    return contents

if __name__ == "__main__":
    API_KEY = 'AIzaSyCYmndDIOnGCipni1lnhURr6Hm95BvHwi4'
    CSE_ID = '72e62b8642f194f09'
    query = input("Enter the topic or keywords to search: ")

    # List of domains to block
    blocked_domains = ['reddit.com', 'instagram.com', 'wikipedia.org', 'linkedin.com', 'youtube.com', 'vexforum.com']

    # Initialize variables
    desired_num_urls = 5
    collected_urls = []
    start_index = 1
    max_api_calls = 10  # To prevent infinite loops
    api_calls_made = 0

    logging.info("Collecting URLs...")

    while len(collected_urls) < desired_num_urls and api_calls_made < max_api_calls:
        # Fetch more URLs as needed
        num_results = 10  # Fetch 10 results at a time to increase chances
        urls = google_search(API_KEY, CSE_ID, query, num_results=num_results, start_index=start_index)
        api_calls_made += 1

        if not urls:
            logging.info("No more results from Google.")
            break

        # Filter out blocked domains
        filtered_urls = [url for url in urls if not is_blocked(url, blocked_domains)]

        # Add filtered URLs to the collected list
        collected_urls.extend(filtered_urls)

        # Update the start index for the next API call
        start_index += num_results

        # Remove duplicates
        collected_urls = list(dict.fromkeys(collected_urls))

        # Limit the collected URLs to the desired number
        if len(collected_urls) >= desired_num_urls:
            collected_urls = collected_urls[:desired_num_urls]
            break

        time.sleep(1)  # Respectful delay between API calls

    logging.info(f"Collected {len(collected_urls)} URLs after filtering.")

    # Scrape the content of each URL asynchronously
    logging.info("Scraping content from collected URLs...")
    contents = asyncio.run(scrape_contents(collected_urls))

    # Write the URLs and content to a text file
    with open('output.txt', 'w', encoding='utf-8') as f:
        for url, content in zip(collected_urls, contents):
            if content:
                f.write(f"URL: {url}\n")
                f.write("Content:\n")
                f.write(content)
                f.write("\n" + "-"*80 + "\n\n")
                logging.info(f"Content from {url} written to file.")
            else:
                logging.info(f"No content retrieved from {url}.")
