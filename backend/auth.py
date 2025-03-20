from fastapi import APIRouter, HTTPException, status
from supabase import create_client
import os

router = APIRouter()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

# Check if keys are available
if not supabase_url or not supabase_key:
    print("WARNING: Supabase URL or Service Key not found in environment variables")
    print(f"SUPABASE_URL: {'Found' if supabase_url else 'Missing'}")
    print(f"SUPABASE_SERVICE_KEY: {'Found' if supabase_key else 'Missing'}")

supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

@router.post("/signup")
async def signup(user_data: dict):
    try:
        if not supabase:
            return {"success": False, "message": "Supabase client not initialized. Check your environment variables."}
            
        # Check if user exists
        email = user_data.get("email")
        existing_users = supabase.table("Users").select("*").eq("email", email).execute()
        
        if existing_users.data:
            return {"success": False, "message": "User already exists"}
        
        # User signup should be done client-side using Supabase Auth
        # Here we just insert additional data to the Users table if needed
        new_user = supabase.table("Users").insert({
            "email": email,
            "name": user_data.get("name"),
            # Add other fields as needed
        }).execute()
        
        return {"success": True, "user": new_user.data[0]}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

# No need for a custom /token endpoint - Supabase handles this
