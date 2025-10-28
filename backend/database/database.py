from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import sys
import os
from pathlib import Path

# Add parent directory to path to import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import centralized config
from config import DATABASE_URL, DB_SSL_CA, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

if not DATABASE_URL:
    raise ValueError("Database credentials not found in .env file. Please check DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME")

# Handle SSL configuration
connect_args = {
    "charset": "utf8mb4",  # Support for emojis and special characters
    "autocommit": False,
    "sql_mode": "TRADITIONAL",
}

# If SSL CA file is specified and exists, use it
if DB_SSL_CA and os.path.exists(DB_SSL_CA):
    connect_args["ssl"] = {
        "ca": DB_SSL_CA
    }
else:
    # For Aiven MySQL with SSL required but no CA file
    connect_args["ssl"] = {"check_hostname": False, "verify_mode": False}

# Create SQLAlchemy engine for MySQL with enhanced performance
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Optimal pool size (5-10 for most apps)
    max_overflow=20,  # Additional connections for burst traffic
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
    echo=False,  # Set to True for SQL query logging
    connect_args=connect_args,
    # Performance optimizations
    future=True,  # Use SQLAlchemy 2.0 style
    query_cache_size=500,  # Cache compiled queries
    # Connection pool optimization
    pool_use_lifo=True,  # Use LIFO for better connection reuse
    echo_pool=False,  # Set to True for pool debugging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session.
    Use this for non-FastAPI contexts.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    Call this when starting the application.
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully!")
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        # Don't raise the exception to allow the app to start even without database
        pass


def close_db():
    """
    Close database connections.
    Call this when shutting down the application.
    """
    engine.dispose()
    print("[OK] Database connections closed!")