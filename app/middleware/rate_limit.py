from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from app.settings.config import settings


# Create limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_requests}/{settings.rate_limit_window}"] if hasattr(settings, "rate_limit_requests") else ["100/minute"],
    storage_uri=settings.redis_url if hasattr(settings, "redis_url") and settings.redis_url else "memory://",
)


def setup_rate_limiting(app: FastAPI) -> None:
    """Configure rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def get_rate_limiter() -> Limiter:
    """Get the rate limiter instance."""
    return limiter