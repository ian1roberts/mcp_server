#!/usr/bin/env python3
import os
import logging
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from openai import OpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MCP Server", description="Hosts agentic tools for LibreChat", version="0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
mcp = FastMCP(app,
                 name="Raspian API MCP",
                 port=8844)
mcp.mount()

# Load environment variables
load_dotenv(".env")
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")
client = OpenAI(api_key=api_key)

def scrape_web(topic: str) -> str:
    """Scrape web content for a given topic."""
    google_url = f'https://www.google.com/search?q={topic}&num=5'
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(google_url, headers=headers, timeout=10)
        response.raise_for_status()
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

@mcp.tool(
    name="blogpost",
    description="Generate a short blog post in R Markdown format about a given topic.",
    parameters={
        "topic": {
            "type": "string",
            "description": "The topic to write the blog post about."
        }
    },
    examples=[
        {
            "input": {"topic": "Artificial Intelligence"},
            "output": "## Blog Post\n\n### Title: The Future of Artificial Intelligence\n\n..."
        }
    ]
)
@app.post("/invoke",
          summary="Invoke a specific tool with provided parameters.",
          operation_id="create_blogpost",
          response_model=dict)
async def invoke_tool(request: Request):
    """
    Invoke a specific tool with provided parameters.
    Expects JSON: { "tool": "blogpost", "parameters": { "topic": "..." } }
    """
    try:
        data = await request.json()
        logger.info(f"Raw data received: {data}")

        tool = (
            data.get("tool") or
            data.get("name") or
            (data.get("tool", {}).get("name") if isinstance(data.get("tool"), dict) else None)
        )

        params = (
            data.get("parameters") or
            data.get("args") or
            (data.get("tool", {}).get("parameters") if isinstance(data.get("tool"), dict) else None) or
            {}
        )

        logger.info(f"Tool invocation: {tool}, params: {params}")

        if tool == "blogpost":
            topic = params.get("topic")
            if not topic:
                return JSONResponse(
                    status_code=404,
                    content={"message": "Missing required parameter: topic",
                            "description": "Please provide a topic for the blog post.",
                            "tool": tool}
                )
            try:
                logger.info(f"Scraping web for topic: {topic}")
                scraped = scrape_web(topic)

                logger.info(f"Generating blog post for topic: {topic}")
                blog_post = generate_blog_post(topic, scraped)
                
                return JSONResponse(
                    status_code=200,
                    content={
                        "message": blog_post,
                        "description": "Blog post generated successfully.",
                        "tool": tool
                    }
                )
            except Exception as e:
                logger.error(f"Error processing blogpost: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"message": "Error during tool invocation.",
                            "description": str(e),
                            "tool": tool}
                )
        else:
            return JSONResponse(
                status_code=404,
                content={"message": f"Tool '{tool}' not found.",
                        "description": "Available tools: blogpost",
                        "tool": tool}
            )
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e), str(request)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": f"Server error: {str(e)}",
                     "description": "An unexpected error occurred."}
        )
        

@app.get("/tools", summary="List available tools.")
def list_tools():
    """Return a list of available tools for LibreChat."""
    return {
        "tools": [
            {
                "name": "blogpost",
                "description": "Generate a short blog post in R Markdown format about a given topic.",
                "parameters": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to write the blog post about."
                    }
                }
            }
        ]
    }

@app.get("/.well-known/openapi.yaml", include_in_schema=True)
def openapi_yaml():
    return FileResponse("openapi.yaml", media_type="application/x-yaml")

mcp.setup_server()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8844)