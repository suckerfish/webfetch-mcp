"""Tests for WebFetchClient extraction logic (no network calls)."""

import pytest

import trafilatura

from src.models.fetch import FetchMetadata, FetchResult, RawFetchResult


SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Article Title</title>
    <meta name="author" content="John Doe">
    <meta name="date" content="2025-01-15">
    <meta property="og:site_name" content="Test Site">
</head>
<body>
    <article>
        <h1>Test Article Title</h1>
        <p>This is the first paragraph of a test article that contains enough text
        for trafilatura to extract meaningful content. We need several sentences to
        ensure the extraction algorithm identifies this as article content worth
        preserving in the output.</p>
        <p>The second paragraph provides additional context and information about
        the topic being discussed. Trafilatura uses various heuristics to determine
        what constitutes the main content of a web page, filtering out navigation,
        ads, and other boilerplate elements.</p>
        <p>A third paragraph helps ensure we have enough content density for the
        extraction to succeed. Articles with very little text may be filtered out
        as they could be navigation pages or error pages rather than real content.</p>
    </article>
</body>
</html>
"""


class TestTrafilaturaExtraction:
    """Test that trafilatura extracts content from known HTML."""

    def test_extract_text(self):
        content = trafilatura.extract(SAMPLE_HTML, output_format="txt")
        assert content is not None
        assert "first paragraph" in content

    def test_extract_markdown(self):
        content = trafilatura.extract(SAMPLE_HTML, output_format="markdown")
        assert content is not None
        assert len(content) > 0

    def test_extract_metadata(self):
        meta = trafilatura.extract_metadata(SAMPLE_HTML)
        assert meta is not None
        assert meta.title == "Test Article Title"


class TestModels:
    """Test Pydantic model construction."""

    def test_fetch_metadata(self):
        m = FetchMetadata(
            title="Test",
            author="Author",
            date="2025-01-15",
            sitename="Site",
            url="https://example.com",
        )
        assert m.title == "Test"
        assert m.url == "https://example.com"

    def test_fetch_metadata_optional_fields(self):
        m = FetchMetadata(url="https://example.com")
        assert m.title is None
        assert m.author is None

    def test_fetch_result(self):
        r = FetchResult(
            content="Hello world",
            metadata=FetchMetadata(url="https://example.com"),
            output_format="markdown",
        )
        dump = r.model_dump()
        assert dump["content"] == "Hello world"
        assert dump["metadata"]["url"] == "https://example.com"

    def test_raw_fetch_result(self):
        r = RawFetchResult(
            html="<html></html>",
            status_code=200,
            url="https://example.com",
            content_length=13,
        )
        assert r.status_code == 200
        assert r.content_length == 13
