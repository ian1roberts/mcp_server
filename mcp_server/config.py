"""Configuration handling for MCP Server."""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")

def get_api_key() -> str:
    """Get OpenAI API key from environment variables."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in the environment variables.")
    return api_key

def get_server_config() -> dict:
    """Get server configuration from environment variables."""
    return {
        "host": os.getenv("MCP_HOST", "0.0.0.0"),
        "port": int(os.getenv("MCP_PORT", "8844")),
        "path": os.getenv("MCP_PATH", "/mcp"),
        "log_level": os.getenv("MCP_LOG_LEVEL", "debug"),
    }
