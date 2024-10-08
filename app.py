import requests

def google_search(api_key, cse_id, query, num_results=5):
    """Search Google using the Custom Search API."""
    # Construct the API request URL
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}&num={num_results}"

    try:
        # Send the GET request to the API
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the JSON response
        results = response.json()

        # Extract and return URLs from the search results
        urls = []
        for item in results.get("items", []):
            urls.append(item["link"])  # Append each URL to the list

        return urls

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == "__main__":
    # Replace with your API key and Custom Search Engine ID
    API_KEY = 'AIzaSyCYmndDIOnGCipni1lnhURr6Hm95BvHwi4'
    CSE_ID = '72e62b8642f194f09'

    # Get user input for search query
    query = input("Enter the topic or keywords to search: ")

    # Retrieve and display URLs
    urls = google_search(API_KEY, CSE_ID, query)
    if urls:
        print("\nTop URLs related to your search:")
        for url in urls:
            print(url)
    else:
        print("No results found.")
