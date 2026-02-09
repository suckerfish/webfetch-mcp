"""WebFetch MCP Server — Lightweight web fetch with Chrome TLS fingerprint spoofing."""

import argparse
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from .tools.fetch_client import WebFetchClient

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

mcp = FastMCP(
    name="WebFetch MCP Server",
    version="0.1.0",
)

_client: Optional[WebFetchClient] = None


def get_client() -> WebFetchClient:
    """Get or create the WebFetch client."""
    global _client
    if _client is None:
        _client = WebFetchClient()
    return _client


@mcp.tool()
async def fetch_url(
    url: str,
    output_format: str = "markdown",
    favor_precision: bool = False,
    favor_recall: bool = False,
    include_links: bool = False,
    include_images: bool = False,
    include_tables: bool = True,
    timeout: int = 30,
) -> dict:
    """Fetch a URL with Chrome TLS fingerprint and extract article content.

    Uses curl_cffi to replicate Chrome's TLS handshake (JA3/JA4 fingerprint),
    bypassing anti-bot services like PerimeterX. Extracts article content
    via trafilatura.

    Args:
        url: The URL to fetch.
        output_format: Output format — "markdown", "txt", or "html". Default: "markdown".
        favor_precision: Favor precision over recall in extraction.
        favor_recall: Favor recall over precision in extraction.
        include_links: Include hyperlinks in extracted content.
        include_images: Include image references in extracted content.
        include_tables: Include tables in extracted content. Default: True.
        timeout: Request timeout in seconds. Default: 30.

    Returns:
        Extracted article content with metadata (title, author, date, sitename).
    """
    try:
        client = get_client()
        result = await client.fetch_and_extract(
            url,
            output_format=output_format,
            favor_precision=favor_precision,
            favor_recall=favor_recall,
            include_links=include_links,
            include_images=include_images,
            include_tables=include_tables,
            timeout=timeout,
        )
        return result.model_dump()
    except Exception as e:
        raise ToolError(f"Fetch failed: {e}")


@mcp.tool()
async def fetch_raw(url: str, timeout: int = 30) -> dict:
    """Fetch a URL with Chrome TLS fingerprint and return raw HTML.

    Returns the full page HTML without content extraction, truncated at 500KB.
    Useful when you need the complete page structure.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds. Default: 30.

    Returns:
        Raw HTML, HTTP status code, final URL (after redirects), and content length.
    """
    try:
        client = get_client()
        result = await client.fetch_raw(url, timeout=timeout)
        return result.model_dump()
    except Exception as e:
        raise ToolError(f"Fetch failed: {e}")


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for Docker/Komodo monitoring."""
    from starlette.responses import JSONResponse

    return JSONResponse({
        "status": "healthy",
        "version": "0.1.0",
        "service": "WebFetch MCP Server",
    })


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="WebFetch MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport mode (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", "8080")),
        help="Port for HTTP transport (default: 8080)",
    )

    args = parser.parse_args()

    logger.info("Starting WebFetch MCP server with %s transport", args.transport)

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=args.transport, host=args.host, port=args.port, stateless_http=True)


if __name__ == "__main__":
    main()
