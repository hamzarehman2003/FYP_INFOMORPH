# app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import logging
from app import collect_and_scrape
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # React development server
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],              # Allows all methods
    allow_headers=["*"],              # Allows all headers
)

# Configure logging (redundant if already configured in scraper.py, but kept for completeness)
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
    # Removed 'summary' field as individual summaries are no longer generated

class ScrapeResponse(BaseModel):
    articles: List[Article]
    final_summary: Optional[str] = None
    errors: List[str] = []

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_articles(request: ScrapeRequest):
    """
    Endpoint to scrape articles based on a query and generate a unified summary.

    Args:
        request (ScrapeRequest): The scraping request containing the query and parameters.

    Returns:
        ScrapeResponse: The response containing the list of articles and the final summary.
    """
    try:
        logging.info(f"Scrape request received: Query='{request.query}', Num URLs={request.num_urls}")
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

# Endpoint to serve static files (optional)
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """
    Endpoint to serve static files.

    Args:
        file_path (str): The path to the static file.

    Returns:
        FileResponse: The requested static file.
    """
    static_dir = "static"
    full_path = os.path.join(static_dir, file_path)
    if os.path.exists(full_path):
        return FileResponse(full_path)
    else:
        raise HTTPException(status_code=404, detail="File not found.")
