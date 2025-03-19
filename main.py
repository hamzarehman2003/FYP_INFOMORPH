# backend/main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import logging
from app import collect_and_scrape  # Updated import
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
from database import engine, SessionLocal  # Updated import
from models import Base, User  # Updated import
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Create all tables
Base.metadata.create_all(bind=engine)

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
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],              # Allows all methods
    allow_headers=["*"],              # Allows all headers
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
SECRET_KEY = "your-secret-key"  # Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Pydantic model for feedback
class FeedbackRequest(BaseModel):
    query: str
    feedback: str

# Pydantic models for authentication
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserInDB(UserCreate):
    hashed_password: str

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Default expiry
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
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
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Authentication Endpoints

@app.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    """
    existing_user = get_user(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    )
    
    logging.info(f"New user registered: {new_user.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and provide a JWT token.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    logging.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

# Feedback Endpoint
@app.post("/feedback")
async def receive_feedback(feedback_request: FeedbackRequest, current_user: User = Depends(get_current_user)):
    """
    Endpoint to receive user feedback.
    """
    try:
        # Here, you can process the feedback, e.g., save it to a database or a file
        logging.info(f"Feedback received from {current_user.email} for query '{feedback_request.query}': {feedback_request.feedback}")
        return {"message": "Feedback received. Thank you!"}
    except Exception as e:
        logging.error(f"Failed to receive feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to receive feedback.")

# Existing Scrape and Static File Endpoints
@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_articles(request: ScrapeRequest, current_user: User = Depends(get_current_user)):
    """
    Endpoint to scrape articles based on a query and generate a unified summary.
    Requires authentication.
    """
    try:
        logging.info(f"Authentication successful for user: {current_user.email}")
        logging.info(f"Scrape request received from {current_user.email}: Query='{request.query}', Num URLs={request.num_urls}")
        result = await collect_and_scrape(
            query=request.query,
            desired_num_articles=request.num_urls
        )
        articles = result.get('articles', [])
        final_summary = result.get('final_summary', "")
    
        # Convert articles to Pydantic models without 'summary'
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
    
        return ScrapeResponse(
            articles=response_articles,
            final_summary=final_summary
        )
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """
    Endpoint to serve static files.
    """
    static_dir = "static"
    full_path = os.path.join(static_dir, file_path)
    if os.path.exists(full_path):
        return FileResponse(full_path)
    else:
        raise HTTPException(status_code=404, detail="File not found.")
