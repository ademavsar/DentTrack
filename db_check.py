"""
Database connection check utility

This script attempts to connect to the database and run a simple query
to verify that the database connection is working correctly.
It also checks that all required tables exist in the database.

Usage: python db_check.py [--verbose]
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import logging
import traceback
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from tabulate import tabulate

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("db_check")

# Required tables for the application to function
REQUIRED_TABLES = [
    'user',
    'patient',
    'treatment',
    'treatment_type', 
    'payment',
    'payment_detail',
    'treatment_history',
    'payment_history'
]

def check_database_connection(verbose=False):
    """Attempt to connect to the database and run a simple query."""
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Get database URL from environment or use default
        db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/denttrack.db')
        logger.info(f"Using database URL: {db_url}")
        
        # Create engine and connect
        engine = create_engine(db_url)
        logger.info("Database engine created")
        
        # Test connection with a simple query
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            logger.info("Successfully connected to the database and executed a test query")
            
            # Get inspector and check tables
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            logger.info(f"Found {len(existing_tables)} tables in the database")
            
            if verbose:
                print("\nExisting tables:")
                for table in existing_tables:
                    print(f"  - {table}")
            
            # Check for required tables
            missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
            if missing_tables:
                logger.warning(f"Missing required tables: {', '.join(missing_tables)}")
                print("\n⚠️ MISSING REQUIRED TABLES:")
                for table in missing_tables:
                    print(f"  - {table}")
            else:
                logger.info("All required tables are present")
                if verbose:
                    print("\n✅ All required tables are present")
            
            # Check table contents if verbose
            if verbose:
                try:
                    # Get table stats
                    table_stats = []
                    for table in existing_tables:
                        try:
                            count = connection.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                            table_stats.append([table, count])
                        except SQLAlchemyError as e:
                            table_stats.append([table, f"Error: {str(e)[:30]}..."])
                    
                    print("\nTable Statistics:")
                    print(tabulate(table_stats, headers=["Table Name", "Record Count"], tablefmt="grid"))
                except Exception as e:
                    logger.error(f"Error getting table statistics: {e}")
        
        return True, missing_tables
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        logger.error(traceback.format_exc())
        return False, []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        return False, []

def suggest_solutions(db_url, missing_tables):
    """Suggest potential solutions based on the database URL and missing tables."""
    print("\n🔧 POSSIBLE SOLUTIONS:")
    
    if missing_tables:
        print("\nMissing tables can be created using one of these methods:")
        print("1. Run migrations: `flask db upgrade`")
        print("2. Use the setup script: `python setup_db.py`")
        print("3. To create and seed with test data: `python setup_db.py --seed`")
    
    if db_url.startswith('sqlite:///'):
        print("\nAdditional SQLite specific checks:")
        print("• Ensure the sqlite database file exists")
        print("• Check file permissions on the database file")
        print("• Make sure the instance directory exists")
        print("• Check if the database file is locked by another process")
    elif db_url.startswith(('postgresql://', 'mysql://')):
        print("\nAdditional PostgreSQL/MySQL specific checks:")
        print("• Verify database server is running")
        print("• Check database credentials in .env file")
        print("• Ensure database and user exist with proper permissions")
        print("• Check network connectivity to database server")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Check DentTrack database connection and tables")
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed information about the database')
    args = parser.parse_args()
    
    print("\n" + "="*50)
    print(" DentTrack Database Connection Check")
    print("="*50)
    
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/denttrack.db')
    connection_success, missing_tables = check_database_connection(args.verbose)
    
    if connection_success:
        if not missing_tables:
            print("\n✅ Database connection and structure are valid!")
        else:
            print(f"\n⚠️ Database connection works but {len(missing_tables)} required tables are missing!")
            suggest_solutions(db_url, missing_tables)
            sys.exit(1)
    else:
        print("\n❌ Database connection failed!")
        suggest_solutions(db_url, missing_tables)
        sys.exit(1) 