import pytest
import json
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from app.models import db, User
from app.auth import auth_bp

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = Flask(__name__)
    app.config.from_object('app.config.TestingConfig')
    
    # Add explicit JWT configuration
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    # Initialize JWT extension
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Set up database
    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client for the app."""
    return app.test_client()

# Tests for /register endpoint
def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        '/auth/register',
        data=json.dumps({'username': 'newuser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    assert json.loads(response.data)['message'] == 'User registered successfully'

def test_register_missing_data(client):
    """Test registration with missing data."""
    # Missing password
    response = client.post(
        '/auth/register',
        data=json.dumps({'username': 'newuser'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing username or password'
    
    # Missing username
    response = client.post(
        '/auth/register',
        data=json.dumps({'password': 'password123'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing username or password'
    
    # Missing both
    response = client.post(
        '/auth/register',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing username or password'

def test_register_duplicate_username(client):
    """Test registration with an existing username."""
    # Register first user
    client.post(
        '/auth/register',
        data=json.dumps({'username': 'existinguser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    # Try to register same username again
    response = client.post(
        '/auth/register',
        data=json.dumps({'username': 'existinguser', 'password': 'differentpassword'}),
        content_type='application/json'
    )
    
    assert response.status_code == 409
    assert json.loads(response.data)['error'] == 'Username already exists'

# Tests for /login endpoint
def test_login_success(client):
    """Test successful login."""
    # Register a user first
    client.post(
        '/auth/register',
        data=json.dumps({'username': 'loginuser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    # Login with that user
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'loginuser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['access_token'] is not None

def test_login_missing_data(client):
    """Test login with missing data."""
    # Missing password
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'user'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing username or password'
    
    # Missing username
    response = client.post(
        '/auth/login',
        data=json.dumps({'password': 'password123'}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Missing username or password'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    # Register a user first
    client.post(
        '/auth/register',
        data=json.dumps({'username': 'validuser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    # Wrong password
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'validuser', 'password': 'wrongpassword'}),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Invalid username or password'
    
    # Wrong username
    response = client.post(
        '/auth/login',
        data=json.dumps({'username': 'nonexistentuser', 'password': 'password123'}),
        content_type='application/json'
    )
    
    assert response.status_code == 401
    assert json.loads(response.data)['error'] == 'Invalid username or password'

