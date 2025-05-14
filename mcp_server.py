#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Dict, Any
import requests
from bs4 import BeautifulSoup

app = FastAPI(title="MCP Server", description="Hosts agentic tools for LibreChat", version="0.1")

# Load environment variables
load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")
client = OpenAI(api_key=api_key)

class ToolRequest(BaseModel):
    tool: str
    parameters: Dict[str, Any]

class ToolResponse(BaseModel):
    tool: str
    result: str
    message: str = "Success"

def scrape_web(topic: str) -> str:
    """Scrape web content for a given topic."""
    google_url = f'https://www.google.com/search?q={topic}&num=5'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(google_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all('p')
        if not paragraphs:
            raise ValueError("No content found on the page.")
        text_content = " ".join(p.get_text() for p in paragraphs)
        return text_content
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Web scraping failed: {str(e)}")

def generate_blog_post(topic: str, scraped_content: str) -> str:
    """Use OpenAI's API to generate a blog post in R Markdown format about the topic."""
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes blog posts in R Markdown format."},
                {"role": "user", "content": f"Write a short blog post in R Markdown format about the topic '{topic}'. Use the following data as inspiration: {scraped_content}"}
            ],
            max_tokens=300,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        blog_post = response.choices[0].message.content.strip()
        return blog_post
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API request failed: {str(e)}")

def handle_blogpost_tool(parameters: Dict[str, Any]) -> str:
    """Validate parameters, scrape content, and generate a blog post using OpenAI."""
    if "topic" not in parameters:
        raise HTTPException(status_code=400, detail="Missing 'topic' parameter for blogpost tool.")
    topic = parameters["topic"]
    # Scrape web content based on topic
    scraped = scrape_web(topic)
    # Generate blog post in R Markdown style using the scraped content
    blog_post = generate_blog_post(topic, scraped)
    return blog_post

@app.get("/tools")
def list_tools():
    """List available tools."""
    return {
        "available_tools": [
            {
                "name": "blogpost",
                "description": "Create a short blog post in R markdown about a given topic."
            }
        ]
    }

@app.post("/invoke", response_model=ToolResponse)
def invoke_tool(request: ToolRequest):
    """Invoke a specific tool with the provided parameters."""
    if request.tool == "blogpost":
        try:
            result = handle_blogpost_tool(request.parameters)
            return ToolResponse(tool="blogpost", result=result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool}' not found.")