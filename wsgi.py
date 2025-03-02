"""WSGI entry point for the application."""
import os
from app import create_app

# Create app instance
app = create_app(os.environ.get('FLASK_CONFIG', 'production'))

# Add health check endpoint
@app.route('/api/health')
def health_check():
    """Health check endpoint for container orchestration."""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0')