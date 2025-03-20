# backend/main.py

from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import logging
<<<<<<< HEAD
from app import collect_and_scrape  # Adjust the import path if needed
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from database import engine, SessionLocal  # Ensure your database is set up correctly
from models import Base, User  # Ensure your models are defined correctly
from sqlalchemy.orm import Session
=======
from app import collect_and_scrape
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
# Database imports
from database import get_user_by_email, create_user, save_query, save_feedback, get_query_by_id
from models import User, Query, Feedback  # Updated User import
>>>>>>> 09b176411f8743d33b9f52bd741f2b1102b56f30
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uuid
from dotenv import load_dotenv
import os

load_dotenv()



# Try to import auth_utils, but handle if it doesn't exist
try:
    from auth_utils import get_supabase_client
    has_auth_utils = True
except ImportError:
    has_auth_utils = False
    logging.warning("auth_utils module not found. Some functionality may be limited.")

app = FastAPI(
    title="InfoMorph API",
    description="An API for collecting and analyzing information",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Welcome to InfoMorph API"}

# Configure CORS
origins = [
    "http://localhost:3000",  # Next.js development server
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
error_handler = logging.FileHandler('errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
logging.getLogger().addHandler(error_handler)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
SECRET_KEY = "your-secret-key"  # Replace with a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Only try to connect to Supabase at startup if auth_utils is available
if has_auth_utils:
    try:
        supabase_client = get_supabase_client()
        if supabase_client:
            logging.info("Successfully connected to Supabase at startup")
        else:
            logging.warning("Could not authenticate with Supabase at startup")
    except Exception as e:
        logging.error(f"Error connecting to Supabase at startup: {e}")

# Pydantic models
class ScrapeRequest(BaseModel):
    query: str
    num_urls: int = 5
    input_language: str = "en"
    output_language: str = "en"

class Article(BaseModel):
    url: str
    title: str
    authors: List[str]
    publish_date: str
    content: str

class ScrapeResponse(BaseModel):
    articles: List[Article]
    final_summary: Optional[str] = None
    errors: List[str] = []

class FeedbackRequest(BaseModel):
    query: str
    feedback: str

class UserCreate(BaseModel):
    name: str  # Add name field
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserInDB(UserCreate):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Placeholder functions for database operations (to be implemented later)
def get_user(email: str) -> Optional[User]:
    """Placeholder - Get user by email"""
    logging.info(f"Database operation: get_user({email}) - Not implemented yet")
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Placeholder - Authenticate a user with email and password"""
    logging.info(f"Database operation: authenticate_user({email}) - Not implemented yet")
    return None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Placeholder - Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    logging.info(f"Attempting to authenticate with token: {token[:10]}...")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        logging.info(f"Token decoded successfully, email: {email}")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        logging.error(f"JWT Error: {str(e)}")
        raise credentials_exception
        
    # This will always raise an exception until database is implemented
    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

<<<<<<< HEAD
@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": new_user.email}, expires_delta=access_token_expires)
    logging.info(f"New user registered: {new_user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    logging.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/feedback")
async def receive_feedback(feedback_request: FeedbackRequest, current_user: User = Depends(get_current_user)):
    try:
        logging.info(f"Feedback received from {current_user.email} for query '{feedback_request.query}': {feedback_request.feedback}")
        return {"message": "Feedback received. Thank you!"}
=======
# Authentication Endpoints
@app.post("/signup", response_model=Token)
async def signup(user: UserCreate):
    """
    Endpoint to register a new user.
    """
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user.email)
        if (existing_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create the new user
        new_user = await create_user(user.name, user.email)
        
        if not new_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logging.error(f"Signup error: {e}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint to authenticate a user and provide a JWT token.
    NOTE: This is a placeholder until the database is implemented.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Database functionality not implemented yet"
    )

# Feedback Endpoint
@app.post("/feedback", response_model=dict)
async def receive_feedback(feedback_request: FeedbackRequest):
    """
    Endpoint to receive user feedback.
    """
    try:
        # Look up the query ID based on the query text
        query_response = await save_query(
            feedback_request.query, 
            "", 
            "feedback_only"
        )
        
        if query_response:
            query_id = query_response.get('id')
            # Save the feedback
            await save_feedback(query_id, feedback_request.feedback)
            return {"message": "Feedback submitted successfully", "success": True}
        else:
            raise HTTPException(status_code=404, detail="Query not found")
>>>>>>> 09b176411f8743d33b9f52bd741f2b1102b56f30
    except Exception as e:
        logging.error(f"Error processing feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process feedback: {str(e)}")

<<<<<<< HEAD
@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_articles(request: ScrapeRequest, current_user: User = Depends(get_current_user)):
    try:
        logging.info(f"Authentication successful for user: {current_user.email}")
        logging.info(f"Scrape request received from {current_user.email}: Query='{request.query}', Num URLs={request.num_urls}")
        result = await collect_and_scrape(
            query=request.query,
            desired_num_articles=request.num_urls,
            input_language=request.input_language,
=======
# Scrape Endpoint
@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_articles(request: ScrapeRequest):
    """
    Endpoint to scrape articles based on a query and generate a unified summary.
    Authentication removed temporarily.
    """
    try:
        logging.info(f"Scrape request received: Query='{request.query}', Num URLs={request.num_urls}")
        result = await collect_and_scrape(
            query=request.query,
            desired_num_articles=request.num_urls,
            input_language=request.input_language, 
>>>>>>> 09b176411f8743d33b9f52bd741f2b1102b56f30
            output_language=request.output_language
        )
        articles = result.get('articles', [])
        final_summary = result.get('final_summary', "")
<<<<<<< HEAD
=======
    
        # Convert articles to Pydantic models
>>>>>>> 09b176411f8743d33b9f52bd741f2b1102b56f30
        response_articles = [
            Article(
                url=article['url'],
                title=article['title'],
                authors=article['authors'],
                publish_date=article['publish_date'],
                content=article['content']
            )
            for article in articles
        ]
<<<<<<< HEAD
        return ScrapeResponse(articles=response_articles, final_summary=final_summary)
=======

        # Save the query and summary to database
        try:
            await save_query(request.query, final_summary)
        except Exception as db_error:
            logging.error(f"Failed to save query to database: {db_error}")
            # Continue with response even if database save fails
    
        return ScrapeResponse(
            articles=response_articles,
            final_summary=final_summary
        )
>>>>>>> 09b176411f8743d33b9f52bd741f2b1102b56f30
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    static_dir = "static"
    full_path = os.path.join(static_dir, file_path)
    if os.path.exists(full_path):
        return FileResponse(full_path)
    else:
        raise HTTPException(status_code=404, detail="File not found.")
