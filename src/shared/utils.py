"""Shared utility functions."""

import functools
import time

from src.shared.logging import get_logger

logger = get_logger(__name__)


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(
                        "Attempt %s/%s failed for %s: %s",
                        attempt,
                        max_attempts,
                        func.__name__,
                        e,
                    )
                    if attempt < max_attempts:
                        time.sleep(delay)
                    else:
                        raise

        return wrapper

    return decorator


def truncate_text(text: str, max_tokens: int = 3000) -> str:
    """Rough token-safe truncation (4 chars ~ 1 token)."""
    max_chars = max_tokens * 4
    if len(text) > max_chars:
        logger.warning("Truncating text from %s to %s chars", len(text), max_chars)
        return text[:max_chars] + "\n[TRUNCATED]"
    return text
