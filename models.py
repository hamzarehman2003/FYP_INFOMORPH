from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import uuid
from datetime import datetime

class User(BaseModel):
    """User model based on Supabase Users table"""
    id: uuid.UUID
    name: str
    email: str  # Added email for authentication purposes
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Query(BaseModel):
    """Query model based on Supabase Queries table"""
    id: Optional[int] = None
    query_text: str
    summary_text: str
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class Feedback(BaseModel):
    """Feedback model based on Supabase feedback table"""
    id: Optional[int] = None
    query_id: int
    feedback_text: str
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True
