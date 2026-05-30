import os
import redis
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def test_redis_connection():
    """
    Integration test to verify Redis connectivity.
    This test will fail if Redis is not reachable at the configured REDIS_URL.
    """
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    print(f"Connecting to Redis at: {redis_url}")
    
    try:
        client = redis.from_url(redis_url, socket_connect_timeout=5)
        # ping() returns True if successful, raises ConnectionError otherwise
        assert client.ping() is True
    except redis.exceptions.ConnectionError as e:
        pytest.fail(f"Redis is not reachable at {redis_url}. Error: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred while connecting to Redis: {e}")
