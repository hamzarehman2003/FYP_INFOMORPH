"""
A simple script to check if your Supabase API key is valid
Run with: python check_api_key.py
"""

import os
from dotenv import load_dotenv
import sys
import requests

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def main():
    print("\n=== Supabase API Key Checker ===\n")
    
    if not SUPABASE_URL:
        print("ERROR: SUPABASE_URL not found in .env file")
        return False
        
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not found in .env file")
        return False
    
    # Display partial key for verification
    key_length = len(SUPABASE_KEY)
    masked_key = SUPABASE_KEY[:4] + "*" * (key_length - 8) + SUPABASE_KEY[-4:] if key_length > 8 else "****"
    print(f"URL: {SUPABASE_URL}")
    print(f"API Key (masked): {masked_key}")
    
    # Check if the URL is valid
    if not SUPABASE_URL.startswith("https://"):
        print("\nWARNING: SUPABASE_URL should start with 'https://'")
    
    print("\nTesting connection to Supabase...")
    
    # Make a simple request to the Supabase REST API
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    
    try:
        # Try to make a simple request to test authentication
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/Users?select=count", 
            headers=headers
        )
        
        if response.status_code == 200:
            print("\n✅ SUCCESS: API key is valid and connection works!")
            return True
        else:
            print(f"\n❌ ERROR: Got status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\nSuggestions:")
        print("1. Check that your SUPABASE_URL is correct (should be like: https://your-project-id.supabase.co)")
        print("2. Verify your API key in the Supabase dashboard (Project Settings > API)")
        print("3. Make sure you're using the 'anon' key or 'service_role' key")
        print("4. Check if your IP is allowed to access Supabase")
        sys.exit(1)
    else:
        print("\nYour Supabase configuration looks good!")
