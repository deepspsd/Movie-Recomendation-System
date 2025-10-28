"""
Centralized configuration loader
Loads environment variables from the global .env file in project root
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Find the project root (where .env file is located)
def get_project_root():
    """Get the project root directory"""
    current = Path(__file__).resolve()
    # Go up from backend/config.py to project root
    return current.parent.parent

# Load environment variables from project root
PROJECT_ROOT = get_project_root()
ENV_PATH = PROJECT_ROOT / '.env'

# Load the .env file
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    print(f"[CONFIG] Loaded environment from: {ENV_PATH}")
else:
    print(f"[WARNING] .env file not found at: {ENV_PATH}")

# Export commonly used variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SSL_CA = os.getenv("DB_SSL_CA", "")

SECRET_KEY = os.getenv("SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

OMDB_API_KEY = os.getenv("OMDB_API_KEY", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
CORS_ORIGINS = os.getenv("CORS_ORIGINS", '["http://localhost:3000","http://localhost:5173","http://127.0.0.1:5173","http://127.0.0.1:3000"]')

# Database URL
if all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = None
    print("[WARNING] Database credentials not fully configured")
