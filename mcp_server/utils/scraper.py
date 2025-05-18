"""Web scraping utilities for MCP Server."""

import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, List

logger = logging.getLogger(__name__)

def scrape_google(topic: str, num_results: int = 5) -> str:
    """
    Scrape Google search results for a given topic.
    
    Args:
        topic: The search query
        num_results: Number of results to return
        
    Returns:
        A string containing scraped text content
    
    Raises:
        Exception: If scraping fails
    """
    google_url = f'https://www.google.com/search?q={topic}&num={num_results}'
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(google_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all('p')
        
        if not paragraphs:
            raise Exception("No content found on the page.")
            
        text_content = " ".join(p.get_text() for p in paragraphs)
        return text_content
        
    except Exception as e:
        logger.error(f"Web scraping failed: {e}")
        raise Exception(f"Web scraping failed: {str(e)}")
