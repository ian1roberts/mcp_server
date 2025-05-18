"""OpenAI client utilities for MCP Server."""

import logging
from typing import Dict, List, Any
from openai import OpenAI

from mcp_server.config import get_api_key

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=get_api_key())

def generate_blog_post(topic: str, content: str) -> str:
    """
    Generate a blog post using OpenAI.
    
    Args:
        topic: Blog post topic
        content: Content to use as inspiration
        
    Returns:
        Generated blog post text
        
    Raises:
        Exception: If API request fails
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes blog posts in R Markdown format."},
                {"role": "user", "content": f"Write a short blog post in R Markdown format about the topic '{topic}'. Use the following data as inspiration: {content}"}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e}")
        raise Exception(f"OpenAI API request failed: {str(e)}")
    