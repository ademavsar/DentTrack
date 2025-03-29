from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create extension instances
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

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
    
    return app 