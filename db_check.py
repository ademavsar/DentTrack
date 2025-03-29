"""
Database connection check utility

This script attempts to connect to the database and run a simple query
to verify that the database connection is working correctly.

Usage: python db_check.py
"""

import os
import sys
from dotenv import load_dotenv
import logging
import traceback
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("db_check")

def check_database_connection():
    """Attempt to connect to the database and run a simple query."""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Get database URL from environment or use default
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/dent_track.db')
        logger.info(f"Using database URL: {db_url}")
        
        # Create engine and connect
        engine = create_engine(db_url)
        logger.info("Database engine created")
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Successfully connected to the database and executed a test query")
            
            # Check if key tables exist (optional)
            try:
                user_count = connection.execute(text("SELECT COUNT(*) FROM user")).scalar()
                logger.info(f"Found {user_count} users in the database")
            except SQLAlchemyError as e:
                logger.warning(f"Could not query user table: {e}")
        
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False

def suggest_solutions(db_url):
    """Suggest potential solutions based on the database URL."""
    if db_url.startswith('sqlite:///'):
        print("\nPossible solutions for SQLite:")
        print("1. Ensure the sqlite database file exists")
        print("2. Check file permissions on the database file")
        print("3. Make sure the instance directory exists")
        print("4. Run 'flask db upgrade' to create the database schema")
        print("5. Check if the database file is locked by another process")
    elif db_url.startswith(('postgresql://', 'mysql://')):
        print("\nPossible solutions for PostgreSQL/MySQL:")
        print("1. Verify database server is running")
        print("2. Check database credentials in .env file")
        print("3. Ensure database and user exist with proper permissions")
        print("4. Check network connectivity to database server")
        print("5. Run 'flask db upgrade' to create the database schema")

if __name__ == "__main__":
    print("DentTrack Database Connection Check")
    print("===================================")
    
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/dent_track.db')
    success = check_database_connection()
    
    if success:
        print("\n✅ Database connection is working correctly!")
    else:
        print("\n❌ Database connection failed!")
        suggest_solutions(db_url)
        sys.exit(1) 