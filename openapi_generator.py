import yaml
from fastapi import FastAPI
from typing import Dict, Any

def create_openapi_spec(server_url: str, tools: Dict[str, Dict[str, Any]]) -> Dict:
    """Creates a basic OpenAPI 3.0 spec for FastAPI tool endpoints."""
    paths = {
        "/tools": {
            "get": {
                "summary": "List available tools.",
                "responses": {
                    "200": {
                        "description": "A list of available tools.",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object"}
                            }
                        }
                    }
                }
            }
        },
        "/invoke": {
            "post": {
                "summary": "Invoke a specific tool with provided parameters.",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "tool": {"type": "string"},
                                    "parameters": {"type": "object"}
                                },
                                "required": ["tool", "parameters"]
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Result from the tool.",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "tool": {"type": "string"},
                                        "result": {"type": "string"},
                                        "message": {"type": "string"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "MCP Server Tools",
            "version": "1.0.0",
            "description": "Auto-generated OpenAPI spec for MCP Server tools"
        },
        "servers": [
            {"url": server_url}
        ],
        "paths": paths,
        "components": {},
    }
    return openapi_spec

def write_openapi_yaml(spec: Dict, filename: str = "openapi.yaml"):
    with open(filename, "w") as f:
        yaml.dump(spec, f, sort_keys=False)
    print(f"OpenAPI spec written to {filename}")

if __name__ == "__main__":
    # Example tool metadata (expand as you add tools)
    TOOLS = {
        "blogpost": {
            "description": "Create a short blog post in R markdown about a given topic.",
            "parameters": {
                "topic": {
                    "type": "string",
                    "description": "The blog topic"
                }
            }
        }
    }
    SERVER_URL = "http://127.0.0.1:8000"
    spec = create_openapi_spec(SERVER_URL, TOOLS)
    write_openapi_yaml(spec)
