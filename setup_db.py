"""
Database Initialization Script

This script creates all necessary database tables based on the SQLAlchemy models
and optionally seeds the database with initial data.

Usage: python setup_db.py [--seed]
"""

import os
import sys
import argparse
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from sqlalchemy import inspect

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("setup_db")

# Ensure logs directory exists
if not os.path.exists('logs'):
    os.mkdir('logs')

# Add file handler
file_handler = RotatingFileHandler('logs/db_setup.log', maxBytes=10240, backupCount=5)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
logger.addHandler(file_handler)

def setup_database(seed=False):
    """
    Create all database tables and optionally seed with initial data
    
    Args:
        seed (bool): Whether to seed the database with initial data
    """
    try:
        # Load environment variables
        load_dotenv()
        logger.info("Environment variables loaded")
        
        # Import after loading environment variables
        from app import create_app, db
        from app.core.models import User, Patient, TreatmentType, Treatment, Payment
        
        # Create app and push app context
        app = create_app()
        with app.app_context():
            # Check if database tables already exist
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'patient' in tables:
                logger.info("Patient table already exists")
                existing_tables = ", ".join(tables)
                logger.info(f"Existing tables: {existing_tables}")
                
                # Verify table structure
                patient_columns = {col['name'] for col in inspector.get_columns('patient')}
                expected_columns = {'id', 'first_name', 'last_name', 'phone', 'tc_no', 'address', 'registration_date'}
                missing_columns = expected_columns - patient_columns
                
                if missing_columns:
                    logger.warning(f"Patient table is missing columns: {', '.join(missing_columns)}")
                    logger.warning("Will attempt to recreate tables to fix structure")
                    db.drop_all()
                    logger.info("Dropped all tables")
                    db.create_all()
                    logger.info("Created all tables with correct structure")
                else:
                    logger.info("Patient table structure looks correct")
            else:
                logger.info("Creating all database tables")
                db.create_all()
                logger.info("All database tables created successfully")
            
            # Seed the database if requested
            if seed:
                from app.core.seed import seed_treatment_types, seed_test_patients, seed_test_treatments
                
                # Only seed if tables are empty
                if TreatmentType.query.count() == 0:
                    logger.info("Seeding treatment types")
                    seed_treatment_types(db)
                
                if Patient.query.count() == 0:
                    logger.info("Seeding test patients")
                    seed_test_patients(db)
                    
                    logger.info("Seeding test treatments")
                    seed_test_treatments(db)
                else:
                    logger.info("Database already contains data, skipping seeding")
                
                # Create admin user if it doesn't exist
                if User.query.filter_by(username='admin').first() is None:
                    logger.info("Creating admin user")
                    admin = User(username='admin', role='admin')
                    admin.set_password('admin')  # Default password, should be changed after first login
                    db.session.add(admin)
                    db.session.commit()
                    logger.info("Admin user created with username 'admin' and password 'admin'")
                else:
                    logger.info("Admin user already exists")
            
            # Count records in key tables
            patient_count = Patient.query.count()
            treatment_count = Treatment.query.count()
            payment_count = Payment.query.count()
            user_count = User.query.count()
            
            logger.info(f"Database summary - Users: {user_count}, Patients: {patient_count}, "
                        f"Treatments: {treatment_count}, Payments: {payment_count}")
            
            return True
    except Exception as e:
        logger.error(f"Error setting up database: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Set up the DentTrack database")
    parser.add_argument('--seed', action='store_true', help='Seed the database with initial data')
    args = parser.parse_args()
    
    print("DentTrack Database Setup")
    print("=======================")
    
    success = setup_database(seed=args.seed)
    
    if success:
        print("\n✅ Database setup completed successfully!")
        if args.seed:
            print("Database has been seeded with initial data")
    else:
        print("\n❌ Database setup failed!")
        print("Check logs/db_setup.log for details")
        sys.exit(1) 