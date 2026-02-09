"""Pydantic response models for web fetch operations."""

from pydantic import BaseModel


class FetchMetadata(BaseModel):
    title: str | None = None
    author: str | None = None
    date: str | None = None
    sitename: str | None = None
    url: str


class FetchResult(BaseModel):
    content: str
    metadata: FetchMetadata
    output_format: str  # "markdown" | "txt" | "html"


class RawFetchResult(BaseModel):
    html: str
    status_code: int
    url: str
    content_length: int
