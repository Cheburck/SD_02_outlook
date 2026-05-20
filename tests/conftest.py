"""
Pytest configuration and fixtures for Email System API tests.
"""
import pytest
import os
import psycopg2
from unittest.mock import patch

# Set environment variables before importing app
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'outlook_db'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'postgres'
os.environ['RATE_LIMIT_DEFAULT'] = '10000/minute'
os.environ['RATE_LIMIT_AUTH'] = '10000/minute'
os.environ['RATE_LIMIT_REGISTER'] = '10000/minute'
os.environ['RATE_LIMIT_SEARCH'] = '10000/minute'


def pytest_configure():
    """Configure pytest before any tests run."""
    # Mock the limiter to disable rate limiting
    import slowapi
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    
    # Create a new limiter with high limits
    test_limiter = Limiter(
        key_func=get_remote_address,
        default_limits=['10000/minute'],
        storage_uri='memory://'
    )
    
    # Patch the limiter in rate_limiter module
    import rate_limiter
    rate_limiter.limiter = test_limiter


@pytest.fixture(scope="function")
def clean_db():
    """Clean database before each test."""
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    cursor = conn.cursor()
    
    # Truncate all tables
    cursor.execute("TRUNCATE TABLE messages, folders, users RESTART IDENTITY CASCADE;")
    conn.commit()
    
    cursor.close()
    conn.close()
    
    yield
    
    # Cleanup after test
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE messages, folders, users RESTART IDENTITY CASCADE;")
    conn.commit()
    cursor.close()
    conn.close()
