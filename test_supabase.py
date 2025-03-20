"""
Test script to verify Supabase connection
Run this script with: python test_supabase.py
"""

import os
from dotenv import load_dotenv
from supabase import create_client
import sys

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def test_connection():
    """Test the connection to Supabase"""
    print("Testing Supabase connection...")
    
    # Check if environment variables are set
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("ERROR: Supabase credentials not found in .env file")
        print("Make sure you have set SUPABASE_URL and SUPABASE_KEY in your .env file")
        return False
    
    try:
        # Initialize the client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try a simple query to verify connection
        response = supabase.table("Users").select("*").limit(1).execute()
        
        # If we get here, the connection worked
        print("SUCCESS: Connected to Supabase successfully!")
        print(f"Response received: {response}")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to connect to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1)
