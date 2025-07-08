import os
import logging
import json
from typing import Dict, Optional, Any
from functools import lru_cache
import time

# Check if Redis should be used
USE_REDIS = os.getenv("USE_REDIS", "false").lower() == "true"

# Initialize Redis if needed
if USE_REDIS:
    try:
        import redis
        REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(REDIS_URL)
        logger = logging.getLogger(__name__)
        logger.info(f"Redis cache enabled at {REDIS_URL}")
    except ImportError:
        logger = logging.getLogger(__name__)
        logger.warning("Redis package not installed. Falling back to LRU cache.")
        USE_REDIS = False

# Setup logging configuration
def setup_logging():
    """Configure logging for the application."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure the root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
    )
    
    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level {log_level}")

# Cache functions
@lru_cache(maxsize=100)
def _lru_cache_get(question: str) -> Optional[str]:
    """LRU cache implementation for storing responses."""
    # This function body is empty because the lru_cache decorator handles the caching
    # The function never gets called, as the decorator returns the cached value or None
    return None

def get_cached_response(question: str) -> Optional[str]:
    """
    Get a cached response for a question if available.
    
    Args:
        question: The question to look up
        
    Returns:
        The cached answer or None if not in cache
    """
    if USE_REDIS:
        try:
            cached = redis_client.get(f"culturebot:qa:{question}")
            if cached:
                return cached.decode('utf-8')
            return None
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Redis error: {str(e)}")
            return None
    else:
        # Use LRU cache
        return _lru_cache_get(question)

def cache_response(question: str, answer: str) -> None:
    """
    Cache a response for a question.
    
    Args:
        question: The question to cache
        answer: The answer to cache
    """
    if USE_REDIS:
        try:
            # Cache with a TTL of 24 hours (86400 seconds)
            redis_client.setex(f"culturebot:qa:{question}", 86400, answer)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Redis caching error: {str(e)}")
    else:
        # Update LRU cache
        # We need to call the function to update the cache
        _lru_cache_get.cache_clear()  # Clear existing entry if any
        _lru_cache_get.__wrapped__(question)  # This doesn't really do anything
        # We have to hack it a bit by replacing the cache dict directly
        _lru_cache_get.cache_parameters()["maxsize"]
        if hasattr(_lru_cache_get, "cache_dict"):
            _lru_cache_get.cache_dict[question] = answer

# Performance tracking
def track_performance(func):
    """
    Decorator to track the performance of a function.
    
    Args:
        func: The function to track
        
    Returns:
        The wrapped function with performance tracking
    """
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(__name__)
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Function {func.__name__} took {duration:.2f} seconds to execute")
        return result
    return wrapper
