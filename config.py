import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Environment flags
    AUTO_CREATE_DB = os.environ.get('AUTO_CREATE_DB', 'True').lower() in ('true', '1', 't')
    ALLOW_EMPTY_DB = os.environ.get('ALLOW_EMPTY_DB', 'True').lower() in ('true', '1', 't')
    SEED_DB = os.environ.get('SEED_DB', 'False').lower() in ('true', '1', 't')

class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/dent_track_dev.db'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///instance/test.db'
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/dent_track.db'

# Environment configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    return config_by_name[env] 