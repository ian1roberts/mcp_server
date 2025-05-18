"""MCP Server main application."""

import logging
from fastmcp import FastMCP

from mcp_server.config import get_server_config
from mcp_server.tools.blogpost import blogpost_tool

logger = logging.getLogger(__name__)

def create_server() -> FastMCP:
    """Create and configure the MCP server."""
    mcp = FastMCP(name="raspian")
    
    # Register tools
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
        return blogpost_tool(topic)
    
    return mcp

def main():
    """Run the MCP server."""
    server = create_server()
    config = get_server_config()
    
    server.run(
        transport="streamable-http",
        host=config["host"],
        port=config["port"],
        path=config["path"],
        log_level=config["log_level"]
    )

if __name__ == "__main__":
    main()
