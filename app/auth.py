from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.get_json()
    
    # Validate input data
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    # Create new user
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()
    
    # Validate input data
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Check if user exists
    user = User.query.filter_by(username=data['username']).first()
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create access token - convert user ID to string
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({'access_token': access_token}), 200


def auth_middleware():
    """Custom decorator for route protection"""
    def wrapper(fn):
        @wraps(fn)  # Use wraps instead of manually preserving __name__
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            # Convert the string ID back to an integer
            try:
                user_id = int(current_user_id)
                return fn(user_id, *args, **kwargs)
            except (ValueError, TypeError):
                return jsonify({"error": "Invalid user identity"}), 401
        return decorator
    return wrapper