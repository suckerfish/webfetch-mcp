"""Core web fetch client using curl_cffi for Chrome TLS fingerprinting and trafilatura for extraction."""

import logging

import trafilatura
from curl_cffi.requests import AsyncSession

from ..models.fetch import FetchMetadata, FetchResult, RawFetchResult

logger = logging.getLogger(__name__)

# Chrome headers from working n8n flow.
# curl_cffi handles TLS fingerprint (JA3/JA4) via impersonate="chrome",
# but we control HTTP headers explicitly with default_headers=False.
CHROME_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Google Chrome";v="123", "Not:A-Brand";v="8"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

RAW_HTML_MAX_BYTES = 500_000


class WebFetchClient:
    """Fetches web pages with Chrome TLS fingerprint and extracts article content."""

    async def fetch_and_extract(
        self,
        url: str,
        output_format: str = "markdown",
        favor_precision: bool = False,
        favor_recall: bool = False,
        include_links: bool = False,
        include_images: bool = False,
        include_tables: bool = True,
        timeout: int = 30,
    ) -> FetchResult:
        """Fetch a URL and extract article content using trafilatura.

        Args:
            url: The URL to fetch.
            output_format: Output format - "markdown", "txt", or "html".
            favor_precision: Favor precision over recall in extraction.
            favor_recall: Favor recall over precision in extraction.
            include_links: Include hyperlinks in extracted content.
            include_images: Include image references in extracted content.
            include_tables: Include tables in extracted content.
            timeout: Request timeout in seconds.

        Returns:
            FetchResult with extracted content and metadata.
        """
        html = await self._fetch(url, timeout=timeout)

        content = trafilatura.extract(
            html,
            output_format=output_format,
            favor_precision=favor_precision,
            favor_recall=favor_recall,
            include_links=include_links,
            include_images=include_images,
            include_tables=include_tables,
        )

        meta = trafilatura.extract_metadata(html)

        metadata = FetchMetadata(
            title=meta.title if meta else None,
            author=meta.author if meta else None,
            date=meta.date if meta else None,
            sitename=meta.sitename if meta else None,
            url=url,
        )

        return FetchResult(
            content=content or "",
            metadata=metadata,
            output_format=output_format,
        )

    async def fetch_raw(self, url: str, timeout: int = 30) -> RawFetchResult:
        """Fetch a URL and return raw HTML (truncated at 500KB).

        Args:
            url: The URL to fetch.
            timeout: Request timeout in seconds.

        Returns:
            RawFetchResult with raw HTML and status info.
        """
        async with AsyncSession(impersonate="chrome") as session:
            response = await session.get(
                url,
                headers=CHROME_HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )

        html = response.text[:RAW_HTML_MAX_BYTES]

        return RawFetchResult(
            html=html,
            status_code=response.status_code,
            url=str(response.url),
            content_length=len(response.text),
        )

    async def _fetch(self, url: str, timeout: int = 30) -> str:
        """Fetch URL HTML with Chrome TLS impersonation."""
        async with AsyncSession(impersonate="chrome") as session:
            response = await session.get(
                url,
                headers=CHROME_HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )
        logger.info("Fetched %s — status %d, %d bytes", url, response.status_code, len(response.text))
        return response.text
