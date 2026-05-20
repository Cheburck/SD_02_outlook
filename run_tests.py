#!/usr/bin/env python3
"""
Test runner script for Email System API tests.
Sets up environment and runs pytest with proper configuration.
"""
import os
import subprocess
import sys

# Set environment variables for testing
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_PORT'] = '5432'
os.environ['DB_NAME'] = 'outlook_db'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'postgres'

# Disable rate limiting for tests by using very high limits
os.environ['RATE_LIMIT_DEFAULT'] = '10000/minute'
os.environ['RATE_LIMIT_AUTH'] = '10000/minute'
os.environ['RATE_LIMIT_REGISTER'] = '10000/minute'
os.environ['RATE_LIMIT_SEARCH'] = '10000/minute'
os.environ['RATE_LIMIT_STRATEGY'] = 'fixed-window'

# Disable Redis for tests (use in-memory)
os.environ['REDIS_URL'] = 'redis://localhost:6379/0'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    # Run pytest
    exit_code = subprocess.run([
        sys.executable, '-m', 'pytest',
        'tests/test_api.py',
        '-v',
        '--tb=short'
    ], cwd=os.path.dirname(__file__))
    
    sys.exit(exit_code.returncode)
