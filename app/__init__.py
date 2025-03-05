import os
from flask import Flask
from flask_jwt_extended import JWTManager
from .models import db
from .utils.logging import configure_logging
from .routes.auth import auth_bp
from .routes.api import api_bp
from .middleware.logging_middleware import LoggingMiddleware


def create_app(config_class=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    # Load configuration
    if config_class is None:
        env = os.environ.get("FLASK_ENV", "default")
        from .config import config

        app.config.from_object(config[env])
    else:
        app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)

    # Configure logging
    configure_logging(app)

    # Register middleware
    app.wsgi_app = LoggingMiddleware(app.wsgi_app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}, 200

    return app
