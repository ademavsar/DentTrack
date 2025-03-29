from dotenv import load_dotenv
import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from app import create_app, db

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

try:
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded")
    
    # Import app and db after environment variables are loaded
    app = create_app()
    logger.info("Application created successfully")

    if __name__ == '__main__':
        # Only auto-create database in development mode
        if os.environ.get('FLASK_ENV', 'development') == 'development':
            with app.app_context():
                if app.config.get('AUTO_CREATE_DB', False):
                    logger.info("Auto-creating database tables")
                    db.create_all()
                    
                # Only seed data if explicitly enabled
                if app.config.get('SEED_DB', False):
                    logger.info("Seeding database with initial data")
                    from app.core.seed import seed_data
                    seed_data(db)
        
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