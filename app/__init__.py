# __init__.py
import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS

from .config import config
from .models import db
from .cli import register_commands

migrate = Migrate()
jwt = JWTManager()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')  
    
    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        app.config['WTF_CSRF_ENABLED'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize JWT with enhanced configuration
    jwt.init_app(app)
    CORS(app)
    
    # Import blueprints here to avoid circular imports
    from .auth import auth_bp
    from .routes import api_bp
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
    
    # Enhanced JWT error handlers with more descriptive messages
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return jsonify({
            "status": "error",
            "message": "Missing Authorization Header",
            "error": "authorization_header_missing"
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            "status": "error",
            "message": "Signature verification failed",
            "error": "invalid_token"
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "status": "error",
            "message": "Token has expired",
            "error": "token_expired"
        }), 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "status": "error",
            "message": "Token has been revoked",
            "error": "token_revoked"
        }), 401
    
    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'GeneratedText': GeneratedText
        }
    
    # Register CLI commands
    register_commands(app)
    
    return app

# Import models for shell context
from .models import User, GeneratedText