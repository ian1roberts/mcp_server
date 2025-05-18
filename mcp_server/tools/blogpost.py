"""Blog post generation tool for MCP Server."""

import logging
from typing import Dict, Any

from mcp_server.utils.scraper import scrape_google
from mcp_server.utils.openai_client import generate_blog_post

logger = logging.getLogger(__name__)

def blogpost_tool(topic: str) -> Dict[str, str]:
    """
    Generate a short blog post in R Markdown format about a given topic.
    
    Args:
        topic: The topic to write the blog post about
        
    Returns:
        Dictionary with message and description
    """
    logger.info(f"Scraping web for topic: {topic}")
    
    try:
        # Scrape web content
        text_content = scrape_google(topic)
        
        # Generate blog post
        blog_post = generate_blog_post(topic, text_content)
        
        return {
            "message": blog_post,
            "description": "Blog post generated successfully."
        }
    except Exception as e:
        logger.error(f"Blog post generation failed: {e}")
        return {
            "message": "",
            "description": f"Error: {str(e)}"
        }
    