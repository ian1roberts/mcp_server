
"""Tests for the MCP server."""

import pytest
from unittest.mock import patch, MagicMock
from mcp_server.server import create_server

def test_create_server():
    """Test that the server is created successfully."""
    server = create_server()
    assert server is not None
    assert server.name == "raspian"
