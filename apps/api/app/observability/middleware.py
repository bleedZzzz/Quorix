"""Request middleware for observability."""

from __future__ import annotations

import time
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Inject a unique request_id into every request and log request metadata."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        logger = structlog.get_logger()
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            await logger.aerror("request_failed", duration_ms=_elapsed_ms(start_time))
            raise

        duration_ms = _elapsed_ms(start_time)
        response.headers["X-Request-Id"] = request_id

        await logger.ainfo(
            "request_completed",
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
