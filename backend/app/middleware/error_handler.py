import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Convert uncaught exceptions into structured JSON responses."""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled request error")
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An unexpected error occurred.",
                    "path": request.url.path,
                },
            )

