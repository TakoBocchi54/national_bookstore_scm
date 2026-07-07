import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:Areta12345@localhost/national_bookstore_scm'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Session configuration
    SESSION_COOKIE_NAME = 'nbs_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Application settings
    ITEMS_PER_PAGE = 20
    LOW_STOCK_THRESHOLD_MULTIPLIER = 1.0  # Alert when stock <= reorder_level * this value
    
    # National Book Store branding
    APP_NAME = 'National Book Store'
    APP_TAGLINE = 'Inventory & Supply Chain Management'
    BRAND_COLOR = '#DC143C'  # Crimson red
