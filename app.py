import requests
from bs4 import BeautifulSoup

def google_search(api_key, cse_id, query, num_results=5):
    """Search Google using the Custom Search API and return the top URLs."""
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}&num={num_results}"
    response = requests.get(url)
    response.raise_for_status()  # Ensure that the request was successful

    results = response.json()
    urls = [item['link'] for item in results.get('items', [])]
    return urls

def scrape_content(url):
    """Scrape the content from a URL."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Attempt to find the main article text; you might need to adjust this selector based on the site's layout
        content = soup.find('article')
        if not content:
            content = soup.find('main')
        if content:
            return content.get_text(strip=True)
        return "No main content found."
    except requests.exceptions.RequestException as e:
        return f"Failed to scrape {url}: {e}"

if __name__ == "__main__":
    API_KEY = 'AIzaSyCYmndDIOnGCipni1lnhURr6Hm95BvHwi4'
    CSE_ID = '72e62b8642f194f09'
    query = input("Enter the topic or keywords to search: ")

    # Get top 5 URLs from Google Search
    urls = google_search(API_KEY, CSE_ID, query)
    print("Top URLs:")
    for url in urls:
        print(url)

    # Scrape the content of each URL
    print("\nScraped Content:")
    for url in urls:
        content = scrape_content(url)
        print(f"Content from {url}:\n{content[:500]}")  # Print the first 500 characters of the content
