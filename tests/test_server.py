"""Tests for MCP server tool registration and health endpoint."""

import pytest

from src.server import mcp


class TestServerSetup:
    """Test that the MCP server is configured correctly."""

    def test_server_name(self):
        assert mcp.name == "WebFetch MCP Server"

    @pytest.mark.asyncio
    async def test_tool_list(self):
        tools = await mcp.get_tools()
        tool_names = {t.name for t in tools.values()}
        assert "fetch_url" in tool_names
        assert "fetch_raw" in tool_names

    @pytest.mark.asyncio
    async def test_health_endpoint_registered(self):
        # The custom_route decorator registers a route on the ASGI app.
        # We verify it exists by checking the server has the health route.
        # A full integration test would use httpx against the running app.
        app = mcp.http_app()
        routes = app.routes
        health_paths = [r.path for r in routes if hasattr(r, "path")]
        assert "/health" in health_paths
