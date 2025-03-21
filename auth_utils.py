# backend/auth_utils.py

import os
import logging
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
auth_logger = logging.getLogger('auth')
auth_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
auth_logger.addHandler(handler)

# Supabase configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

def get_supabase_client() -> Optional[Client]:
    """
    Get an authenticated Supabase client.
    Returns:
        Optional[Client]: An authenticated Supabase client or None if authentication fails.
    """
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            auth_logger.error("Missing Supabase URL or key")
            return None
            
        # Create a Supabase client with the anon key
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        auth_logger.info("Successfully created Supabase client")
        
        # Test the connection with a simple query
        try:
            # Just try to access a table to verify connection
            response = client.table("Users").select("count").limit(1).execute()
            auth_logger.info("Successfully connected to Supabase")
        except Exception as query_error:
            auth_logger.warning(f"Connection test failed: {query_error}")
            # Still return the client as it might work for other operations
        
        return client
    except Exception as e:
        auth_logger.error(f"Error getting Supabase client: {e}")
        return None
