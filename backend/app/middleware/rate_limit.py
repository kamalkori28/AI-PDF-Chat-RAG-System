import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory sliding-window rate limiter.

    This is enough for local and single-instance deployments. In distributed
    production, replace the storage with Redis while keeping the middleware API.
    """

    def __init__(self, app, requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self.requests = requests
        self.window_seconds = window_seconds
        self.clients: defaultdict[str, deque[float]] = defaultdict(deque)

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        if request.url.path.endswith("/health"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        timestamps = self.clients[client_ip]
        while timestamps and now - timestamps[0] > self.window_seconds:
            timestamps.popleft()

        if len(timestamps) >= self.requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again shortly."},
            )

        timestamps.append(now)
        return await call_next(request)
