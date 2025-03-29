from flask import Flask, session, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from sqlalchemy import inspect
import sys

# Load environment variables from .env file
load_dotenv()

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def verify_required_tables(app, inspector):
    """
    Verify that all required database tables exist.
    Returns (success, missing_tables) tuple.
    """
    required_tables = ['user', 'patient', 'treatment', 'treatment_type', 'payment']
    existing_tables = inspector.get_table_names()
    
    app.logger.info(f"Required tables: {', '.join(required_tables)}")
    app.logger.info(f"Existing tables: {', '.join(existing_tables)}")
    
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        app.logger.error(f"Missing required tables: {', '.join(missing_tables)}")
        return False, missing_tables
    
    return True, []

def create_app(config=None):
    """Application factory function that creates and configures the Flask app"""
    app = Flask(__name__, 
                template_folder='templates', 
                static_folder='static')
    
    # Load default configuration
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///dent_track.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        AUTO_CREATE_DB=True,
        ALLOW_EMPTY_DB=True,
        SEED_DB=False,
        SESSION_TYPE='filesystem',  # Ensure session is properly configured
        PERMANENT_SESSION_LIFETIME=86400,  # Session lifetime in seconds (24 hours)
        TEMPLATES_AUTO_RELOAD=False  # Added TEMPLATES_AUTO_RELOAD configuration
    )
    
    # Load configuration based on environment
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        app.config.from_pyfile('config/development.py', silent=True)
    elif env == 'testing':
        app.config.from_pyfile('config/testing.py', silent=True)
    elif env == 'production':
        app.config.from_pyfile('config/production.py', silent=True)
    
    # Override with instance config if it exists
    app.config.from_pyfile('config.py', silent=True)
    
    # Override with passed config object if provided
    if config:
        app.config.from_mapping(config)
    
    # Set up logging
    if not app.debug and not app.testing:
        # Ensure the logs directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Set up file handler for logs
        file_handler = RotatingFileHandler('logs/denttrack.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('DentTrack startup')
    
    # Register blueprints/routes
    from app.patients.routes import bp as patients_bp
    from app.treatments.routes import bp as treatments_bp
    from app.auth.routes import bp as auth_bp
    from app.admin.routes import bp as admin_bp
    
    app.register_blueprint(patients_bp)
    app.register_blueprint(treatments_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Enable template auto-reload in development
    if app.config.get('TEMPLATES_AUTO_RELOAD'):
        app.jinja_env.auto_reload = True
    
    # Initialize Flask-Login
    login_manager.init_app(app)
    print(f"[Flask-Login] Setting login_view to 'auth.login'")  # Debug print
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen bu sayfaya erişmek için giriş yapın.'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = 'strong'  # Add session protection
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.core.models import User
        print(f"[load_user] Called with user_id: {user_id}")
        user = User.query.get(int(user_id))
        print(f"[load_user] Returning: {user}")
        return user
    
    # Add a Flask-Login unauthorized handler for additional debugging
    @login_manager.unauthorized_handler
    def unauthorized():
        print("[unauthorized_handler] Called - user needs to log in")
        from flask import redirect, url_for, flash
        flash('Lütfen bu sayfaya erişmek için giriş yapın.', 'info')
        return redirect(url_for('auth.login'))
    
    # Verify database in production mode
    with app.app_context():
        env = os.environ.get('FLASK_ENV', 'development')
        auto_create_db = app.config.get('AUTO_CREATE_DB', True)
        
        if env == 'production' and not auto_create_db:
            try:
                # Check if database exists and has required tables
                inspector = inspect(db.engine)
                tables_ok, missing_tables = verify_required_tables(app, inspector)
                
                if not tables_ok:
                    app.logger.error(f"FATAL: Database is missing required tables: {', '.join(missing_tables)}")
                    app.logger.error("Please run 'flask db upgrade' to set up the database before starting the application.")
                    
                    # Register a special error handler for database issues
                    @app.route('/', defaults={'path': ''})
                    @app.route('/<path:path>')
                    def database_setup_required(path):
                        return render_template('errors/db_setup.html', missing_tables=missing_tables), 503
                    
                    # Don't register other routes if database is not ready
                    app.logger.warning("Application started in maintenance mode due to database issues")
            except Exception as e:
                app.logger.error(f"Error checking database: {str(e)}")
                
                # Register a catch-all error handler
                @app.route('/', defaults={'path': ''})
                @app.route('/<path:path>')
                def database_connection_error(path):
                    return render_template('errors/db_error.html', error=str(e)), 503
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 Error: {error}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Error: {error}", exc_info=True)
        db.session.rollback()  # Roll back any failed database transactions
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        app.logger.warning(f"403 Error: {error}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(400)
    def bad_request_error(error):
        app.logger.warning(f"400 Error: {error}")
        return render_template('errors/400.html'), 400
    
    @app.route('/health')
    def health_check():
        """Simple endpoint to check if the application is running"""
        try:
            # Check if required tables exist
            inspector = inspect(db.engine)
            tables_ok, missing_tables = verify_required_tables(app, inspector)
            
            if not tables_ok:
                db_status = "incomplete"
                details = f"Missing tables: {', '.join(missing_tables)}"
            else:
                # Simple database query check
                db.session.execute('SELECT 1').scalar()
                db_status = "ok"
                details = "All required tables present"
        except Exception as e:
            app.logger.error(f"Database health check failed: {e}")
            db_status = "error"
            details = str(e)
        
        status = {
            "status": "ok" if db_status == "ok" else "error",
            "db_connection": db_status,
            "db_details": details,
            "app": "DentTrack",
            "environment": os.environ.get("FLASK_ENV", "development")
        }
        
        if db_status != "ok":
            return jsonify(status), 500
        return jsonify(status)
    
    return app 