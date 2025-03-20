import logging
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for database operations
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
db_logger.addHandler(handler)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_USERNAME = os.getenv("SUPABASE_USERNAME")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

# Print partial API key for debugging (only first and last 4 chars for security)
if SUPABASE_KEY:
    key_length = len(SUPABASE_KEY)
    masked_key = SUPABASE_KEY[:4] + "*" * (key_length - 8) + SUPABASE_KEY[-4:] if key_length > 8 else "****"
    db_logger.info(f"Using Supabase URL: {SUPABASE_URL}")
    db_logger.info(f"API Key found (masked): {masked_key}")
else:
    db_logger.error("No Supabase API key found")

# Log that we have the username/password (without revealing them)
if SUPABASE_USERNAME and SUPABASE_PASSWORD:
    db_logger.info("Supabase username and password found in environment variables")
else:
    db_logger.warning("Supabase username and/or password not found in environment variables")

# Initialize a mock supabase client for fallback
class MockSupabase:
    def table(self, _):
        return self
    
    def select(self, _):
        return self
    
    def eq(self, _, __):
        return self
    
    def insert(self, _):
        return self
    
    def execute(self):
        return {"data": []}

# Initialize Supabase client
supabase = None
try:
    # Initialize Supabase client with the URL and anon key (public key)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    db_logger.info("Supabase client initialized successfully")
except Exception as e:
    db_logger.error(f"Failed to initialize Supabase client: {str(e)}")
    db_logger.warning("Using mock Supabase client - database operations will not work")
    supabase = MockSupabase()

# User related functions with error handling
async def get_user_by_id(user_id):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: get_user_by_id will return None")
            return None
            
        response = supabase.table("Users").select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error getting user by ID: {str(e)}")
        return None

async def get_user_by_email(email):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: get_user_by_email will return None")
            return None
            
        response = supabase.table("Users").select("*").eq("email", email).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error getting user by email: {str(e)}")
        return None

async def create_user(name, email):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: create_user will return None")
            return None
            
        user_data = {
            "name": name, 
            "email": email
        }
        
        # First check if the user already exists
        existing_user = await get_user_by_email(email)
        if existing_user:
            db_logger.warning(f"User with email {email} already exists")
            return existing_user
            
        response = supabase.table("Users").insert(user_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error creating user: {str(e)}")
        return None

# Query related functions
async def save_query(query_text, summary_text, status="completed"):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: save_query will return None")
            return None
            
        query_data = {
            "query_text": query_text,
            "summary_text": summary_text,
            "status": status
        }
        response = supabase.table("Queries").insert(query_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error saving query: {str(e)}")
        return None

async def get_query_by_id(query_id):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: get_query_by_id will return None")
            return None
            
        response = supabase.table("Queries").select("*").eq("id", query_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error getting query: {str(e)}")
        return None

# Feedback related functions
async def save_feedback(query_id, feedback_text):
    try:
        if isinstance(supabase, MockSupabase):
            db_logger.warning("Using mock client: save_feedback will return None")
            return None
            
        feedback_data = {
            "query_id": query_id,
            "feedback_text": feedback_text
        }
        response = supabase.table("feedback").insert(feedback_data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        db_logger.error(f"Error saving feedback: {str(e)}")
        return None
