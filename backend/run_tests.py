"""
Test runner script that loads environment variables and runs pytest
"""
import os
import sys
from dotenv import load_dotenv

# Set testing flag
os.environ['TESTING'] = 'true'

# Load environment variables from parent directory
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(env_path)

# Add backend to path
backend_path = os.path.dirname(__file__)
sys.path.insert(0, backend_path)

# Run pytest
import pytest
sys.exit(pytest.main(['-v', 'tests/', '--tb=short']))
