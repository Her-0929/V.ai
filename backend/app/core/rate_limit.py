"""HER AI — Rate Limiting Infrastructure

Uses slowapi to protect computational endpoints (Chat, Search) from resource exhaustion.
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)

