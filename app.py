import requests
from newspaper import Article
import time

def google_search(api_key, cse_id, query, num_results=5):
    """Search Google using the Custom Search API and return the top URLs."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': cse_id,
        'q': query,
        'num': num_results
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()
    urls = [item['link'] for item in results.get('items', [])]
    return urls

def scrape_content(url):
    """Scrape the content from a URL using newspaper3k."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        return f"Failed to scrape {url}: {e}"

if __name__ == "__main__":
    API_KEY = 'AIzaSyCYmndDIOnGCipni1lnhURr6Hm95BvHwi4'
    CSE_ID = '72e62b8642f194f09'
    query = input("Enter the topic or keywords to search: ")

    # Get top URLs from Google Search
    urls = google_search(API_KEY, CSE_ID, query)
    print("Top URLs:")
    for url in urls:
        print(url)

    # Scrape the content of each URL
    print("\nScraped Content:")
    for url in urls:
        print(f"Content from {url}:")
        content = scrape_content(url)
        print(content[:500])  # Print the first 500 characters of the content
        print("\n")
        time.sleep(2)  # Wait for 2 seconds before the next request
