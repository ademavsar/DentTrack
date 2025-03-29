from dotenv import load_dotenv
import os
from app import create_app, db

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == '__main__':
    # Only auto-create database in development mode
    if os.environ.get('FLASK_ENV', 'development') == 'development':
        with app.app_context():
            if app.config.get('AUTO_CREATE_DB', False):
                db.create_all()
                
            # Only seed data if explicitly enabled
            if app.config.get('SEED_DB', False):
                from app.core.seed import seed_data
                seed_data(db)
                
    app.run(host='0.0.0.0', debug=True if os.environ.get('FLASK_ENV', 'development') == 'development' else app.config.get('DEBUG', False)) 