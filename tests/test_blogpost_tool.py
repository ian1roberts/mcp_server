"""Tests for the blog post generation tool."""

import pytest
from unittest.mock import patch, MagicMock
from mcp_server.tools.blogpost import blogpost_tool

@patch('mcp_server.tools.blogpost.scrape_google')
@patch('mcp_server.tools.blogpost.generate_blog_post')
def test_blogpost_tool_success(mock_generate, mock_scrape):
    """Test successful blog post generation."""
    # Setup mocks
    mock_scrape.return_value = "Scraped content"
    mock_generate.return_value = "Generated blog post"
    
    # Call the function
    result = blogpost_tool("Python programming")
    
    # Verify results
    assert result["message"] == "Generated blog post"
    assert result["description"] == "Blog post generated successfully."
    mock_scrape.assert_called_once_with("Python programming")
    mock_generate.assert_called_once_with("Python programming", "Scraped content")

@patch('mcp_server.tools.blogpost.scrape_google')
def test_blogpost_tool_scraping_error(mock_scrape):
    """Test blog post generation with scraping error."""
    # Setup mocks
    mock_scrape.side_effect = Exception("Scraping failed")
    
    # Call the function
    result = blogpost_tool("Python programming")
    
    # Verify results
    assert result["message"] == ""
    assert "Error: Scraping failed" in result["description"]
