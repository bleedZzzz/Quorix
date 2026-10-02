"""Quorix API — Common Pydantic schemas."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    data: T
    meta: dict | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated API response."""
    data: list[T]
    total: int
    page: int
    page_size: int
    has_next: bool


class ErrorDetail(BaseModel):
    """Error response body."""
    error: str
    detail: str | None = None
    request_id: str | None = None


ErrorResponse = ErrorDetail


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "0.1.0"
    service: str = "quorix-api"
