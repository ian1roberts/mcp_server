# MCP Server

An MCP server providing blog post generation capabilities using web scraping and OpenAI.

## Features

- Generate blog posts in R Markdown format
- Uses web scraping to gather context
- Powered by OpenAI's language models

## Installation

```bash
# Install with Poetry
poetry install

# Or with pip
pip install mcp-server

## Running it

```bash
# If installed with poetry
poetry run mcp_server

# Otherwise
python -m mcp_server.server

