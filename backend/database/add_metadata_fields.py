"""
Database Migration Script
Adds advanced metadata fields to Movie table for hybrid recommendation system
"""

from sqlalchemy import text
from database import engine, init_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_metadata_columns():
    """
    Add new metadata columns to movies table
    """
    try:
        with engine.connect() as conn:
            # Check if columns already exist
            result = conn.execute(text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'movies' 
                AND COLUMN_NAME IN ('director', 'cast', 'keywords', 'budget', 'revenue', 
                                   'director_score', 'actor_score', 'budget_revenue_ratio')
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Add missing columns
            columns_to_add = {
                'director': 'VARCHAR(255)',
                'cast': 'TEXT',
                'keywords': 'TEXT',
                'budget': 'FLOAT',
                'revenue': 'FLOAT',
                'director_score': 'FLOAT DEFAULT 0.0',
                'actor_score': 'FLOAT DEFAULT 0.0',
                'budget_revenue_ratio': 'FLOAT DEFAULT 0.0'
            }
            
            for column_name, column_type in columns_to_add.items():
                if column_name not in existing_columns:
                    logger.info(f"Adding column: {column_name}")
                    conn.execute(text(f"""
                        ALTER TABLE movies 
                        ADD COLUMN {column_name} {column_type}
                    """))
                    conn.commit()
                    logger.info(f"✅ Added column: {column_name}")
                else:
                    logger.info(f"⏭️  Column already exists: {column_name}")
            
            logger.info("✅ Database migration completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error during migration: {str(e)}")
        return False


def verify_migration():
    """
    Verify that all columns were added successfully
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COLUMN_NAME, DATA_TYPE 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'movies'
                ORDER BY ORDINAL_POSITION
            """))
            
            columns = list(result)
            
            logger.info("\n📊 Current Movie table schema:")
            logger.info("-" * 60)
            for column_name, data_type in columns:
                logger.info(f"  {column_name:<30} {data_type}")
            logger.info("-" * 60)
            
            # Check for required columns
            required_columns = [
                'director', 'cast', 'keywords', 'budget', 'revenue',
                'director_score', 'actor_score', 'budget_revenue_ratio'
            ]
            
            existing_column_names = [col[0] for col in columns]
            missing_columns = [col for col in required_columns if col not in existing_column_names]
            
            if missing_columns:
                logger.warning(f"⚠️  Missing columns: {', '.join(missing_columns)}")
                return False
            else:
                logger.info("✅ All required metadata columns are present!")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error verifying migration: {str(e)}")
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting database migration...")
    logger.info("=" * 60)
    
    # Initialize database connection
    init_db()
    
    # Add metadata columns
    success = add_metadata_columns()
    
    if success:
        # Verify migration
        verify_migration()
        logger.info("\n✅ Migration completed successfully!")
    else:
        logger.error("\n❌ Migration failed!")
        exit(1)
