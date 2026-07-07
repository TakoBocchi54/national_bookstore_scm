"""
Application factory for National Book Store SCM System
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Add datetime utilities to Jinja2 context
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow}
    
    # Register blueprints
    from app.routes import auth, dashboard, suppliers, products, inventory, purchase_orders, deliveries, sales, reports
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(suppliers.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(purchase_orders.bp)
    app.register_blueprint(deliveries.bp)
    app.register_blueprint(sales.bp)
    app.register_blueprint(reports.bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
