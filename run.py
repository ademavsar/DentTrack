from dotenv import load_dotenv
import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from app import create_app, db
from sqlalchemy import inspect

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("denttrack")

# Ensure logs directory exists
if not os.path.exists('logs'):
    os.mkdir('logs')

# Add file handler
file_handler = RotatingFileHandler('logs/startup.log', maxBytes=10240, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(file_handler)

def verify_database_tables(app):
    """Verify that all required database tables exist."""
    required_tables = ['user', 'patient', 'treatment', 'treatment_type', 'payment']
    
    with app.app_context():
        try:
            # Check if database exists and has required tables
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            logger.info(f"Required tables: {', '.join(required_tables)}")
            logger.info(f"Existing tables: {', '.join(existing_tables)}")
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            
            if missing_tables:
                logger.error(f"Missing required tables: {', '.join(missing_tables)}")
                return False, missing_tables
            
            return True, []
        except Exception as e:
            logger.error(f"Error checking database: {str(e)}")
            return False, [str(e)]

try:
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded")
    
    # Force the DATABASE_URL to use the correct database file
    os.environ['DATABASE_URL'] = 'sqlite:///instance/dent_track.db'
    
    # Import app and db after environment variables are loaded
    app = create_app()
    logger.info("Application created successfully")

    if __name__ == '__main__':
        # Only auto-create database in development mode
        env = os.environ.get('FLASK_ENV', 'development')
        auto_create_db = app.config.get('AUTO_CREATE_DB', True)
        
        if env == 'development' and auto_create_db:
            with app.app_context():
                logger.info("Auto-creating database tables")
                db.create_all()
                
                # Only seed data if explicitly enabled
                if app.config.get('SEED_DB', False):
                    logger.info("Seeding database with initial data")
                    from app.core.seed import seed_data
                    seed_data(db)
        
        # In production, verify the database before starting the application
        elif env == 'production':
            tables_ok, missing_tables = verify_database_tables(app)
            
            if not tables_ok:
                logger.error("DATABASE ERROR: Missing required tables!")
                logger.error(f"Tables missing: {', '.join(missing_tables)}")
                logger.error("\nPlease run one of the following commands to set up the database:")
                logger.error("   flask db upgrade")
                logger.error("   python setup_db.py")
                logger.error("\nThen restart the application.")
                
                if os.environ.get('STRICT_DB_CHECK', 'True').lower() in ('true', '1', 't'):
                    logger.critical("Exiting due to database validation failure")
                    sys.exit(1)
                else:
                    logger.warning("Starting application despite database issues (STRICT_DB_CHECK is disabled)")
        
        # Log the application startup
        host = '0.0.0.0'
        debug = True if os.environ.get('FLASK_ENV', 'development') == 'development' else app.config.get('DEBUG', False)
        logger.info(f"Starting application on {host} with debug={debug}")
        
        app.run(
            host=host, 
            debug=debug
        )
except Exception as e:
    logger.critical(f"Application failed to start: {str(e)}")
    logger.critical(traceback.format_exc())
    # Re-raise the exception to ensure the application doesn't start in a broken state
    raise 