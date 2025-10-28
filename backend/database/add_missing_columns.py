"""
Add missing columns to movies table for enhanced recommendations
"""
from sqlalchemy import text
from database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_missing_columns():
    """Add missing columns to movies table if they don't exist"""
    
    columns_to_add = [
        ("director", "VARCHAR(255)"),
        ("cast", "TEXT"),
        ("keywords", "TEXT"),
        ("budget", "FLOAT"),
        ("revenue", "FLOAT"),
        ("director_score", "FLOAT DEFAULT 0.0"),
        ("actor_score", "FLOAT DEFAULT 0.0"),
        ("budget_revenue_ratio", "FLOAT DEFAULT 0.0"),
    ]
    
    with engine.connect() as conn:
        for column_name, column_type in columns_to_add:
            try:
                # Check if column exists
                result = conn.execute(text(f"SHOW COLUMNS FROM movies LIKE '{column_name}'"))
                if result.fetchone() is None:
                    # Column doesn't exist, add it
                    logger.info(f"Adding column: {column_name}")
                    conn.execute(text(f"ALTER TABLE movies ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    logger.info(f"✅ Added column: {column_name}")
                else:
                    logger.info(f"Column {column_name} already exists, skipping")
            except Exception as e:
                logger.error(f"Error adding column {column_name}: {str(e)}")
                conn.rollback()

if __name__ == "__main__":
    logger.info("Starting database migration...")
    add_missing_columns()
    logger.info("Migration completed!")
