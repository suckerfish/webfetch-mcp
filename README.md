# webfetch-mcp

A lightweight MCP server that fetches web pages with Chrome TLS fingerprint spoofing and extracts article content.

Anti-bot services like PerimeterX block based on **TLS fingerprint** (JA3/JA4), not just HTTP headers. Standard Python HTTP clients get blocked even with perfect Chrome headers. This server uses `curl_cffi` (which wraps `curl-impersonate`) to replicate Chrome's exact TLS handshake, then extracts clean article content via `trafilatura`.

## Tools

### `fetch_url`
Fetch a URL and extract article content as markdown, plain text, or HTML.

- Chrome TLS fingerprint + spoofed browser headers
- Article extraction via trafilatura (strips ads, navigation, boilerplate)
- Returns content + metadata (title, author, date, sitename)
- Parameters: `url`, `output_format` (markdown|txt|html), `favor_precision`, `favor_recall`, `include_links`, `include_images`, `include_tables`, `timeout`

**Note:** `favor_precision=True` produces tighter extraction with less boilerplate bleed (newsletter blocks, author bios). Default extraction favors recall.

### `fetch_raw`
Fetch a URL and return raw HTML without extraction. Truncates at 500KB. Useful when you need the full page structure.

## Quick Start

```bash
# Install dependencies
uv venv && uv pip install -e ".[dev]"

# Run locally (stdio)
uv run python -m src.server

# Run as HTTP server
uv run python -m src.server --transport streamable-http --host 0.0.0.0 --port 8080
```

## Docker

Pre-built multi-arch images (amd64/arm64) are published to GHCR on every push to main:

```bash
docker pull ghcr.io/suckerfish/webfetch-mcp:latest
```

Or use Docker Compose:

```bash
docker compose up
```

Default port mapping is 8082:8080. Health check at `GET /health`.

## CI/CD

GitHub Actions builds and pushes to `ghcr.io/suckerfish/webfetch-mcp` on pushes to `main` that touch `src/`, `Dockerfile`, `pyproject.toml`, or `uv.lock`. Manual trigger via `workflow_dispatch` is also available.

## Tech Stack

| Component | Choice |
|-----------|--------|
| MCP framework | [FastMCP](https://gofastmcp.com) 2.0+ |
| HTTP client | [curl_cffi](https://github.com/lexiforest/curl_cffi) (Chrome TLS impersonation) |
| Content extraction | [trafilatura](https://github.com/adbar/trafilatura) |
| Models | Pydantic 2.0+ |
| Build | hatchling + uv |

## Tests

```bash
uv run pytest tests/ -v
```
