try:
    from .database import Base, engine, get_db, get_db_context, init_db, close_db, SessionLocal
except (ValueError, ImportError) as e:
    # Handle case where environment variables are not set or imports fail
    Base = None
    engine = None
    get_db = None
    get_db_context = None
    init_db = None
    close_db = None
    SessionLocal = None
    print(f"Warning: Database imports failed: {e}")

__all__ = ["Base", "engine", "get_db", "get_db_context", "init_db", "close_db", "SessionLocal"]