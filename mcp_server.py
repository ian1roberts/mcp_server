from fastmcp import FastMCP
import logging
import os
from openai import OpenAI
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")

client = OpenAI(api_key=api_key)

mcp = FastMCP(name="raspian")

@mcp.tool(
    name="blogpost",
    description="Generate a short blog post in R Markdown format about a given topic.",
    annotations={
        "topic": {
            "type": "string",
            "description": "The topic to write the blog post about."
        },
        "output": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "The generated blog post."},
                "description": {"type": "string", "description": "Operation status."}
            },
        "required": ["message", "description"]
        }
    }        
)
def blogpost(topic: str) -> dict:
    logger.info(f"Scraping web for topic: {topic}")
    google_url = f'https://www.google.com/search?q={topic}&num=5'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(google_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all('p')
        if not paragraphs:
            raise Exception("No content found on the page.")
        text_content = " ".join(p.get_text() for p in paragraphs)
    except Exception as e:
        logger.error(f"Web scraping failed: {e}")
        return {
            "message": "",
            "description": f"Web scraping failed: {str(e)}"
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes blog posts in R Markdown format."},
                {"role": "user", "content": f"Write a short blog post in R Markdown format about the topic '{topic}'. Use the following data as inspiration: {text_content}"}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        blog_post = response.choices[0].message.content.strip()
        return {
            "message": blog_post,
            "description": "Blog post generated successfully."
        }
    except Exception as e:
        logger.error(f"OpenAI API request failed: {e}")
        return {
            "message": "",
            "description": f"OpenAI API request failed: {str(e)}"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http",
        host="0.0.0.0",
        port=8844,
        path="/mcp",
        log_level="debug")
