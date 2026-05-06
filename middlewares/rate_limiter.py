import time
from collections import defaultdict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Simple in-memory rate limiter (use Redis in production)
_request_counts: dict[str, list[float]] = defaultdict(list)

RATE_LIMIT = 100        # requests
WINDOW_SECONDS = 60     # per minute

# Stricter limits for auth endpoints
AUTH_RATE_LIMIT = 10
AUTH_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        now = time.time()

        is_auth = path.startswith("/auth/")
        limit = AUTH_RATE_LIMIT if is_auth else RATE_LIMIT
        window = AUTH_WINDOW if is_auth else WINDOW_SECONDS

        key = f"{client_ip}:{path if is_auth else 'global'}"
        timestamps = _request_counts[key]

        # Remove expired timestamps
        _request_counts[key] = [t for t in timestamps if now - t < window]
        timestamps = _request_counts[key]

        if len(timestamps) >= limit:
            retry_after = int(window - (now - timestamps[0]))
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Try again in {retry_after}s.",
                    "retry_after": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        _request_counts[key].append(now)
        return await call_next(request)