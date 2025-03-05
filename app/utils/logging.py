import os
import logging
from logging.handlers import RotatingFileHandler
import sys
from flask import has_request_context, request
import json

class RequestFormatter(logging.Formatter):
    """Custom formatter that adds request information to log records"""
    
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.remote_addr = request.remote_addr
            # Add user ID if available and authenticated
            if hasattr(request, 'user_id'):
                record.user_id = request.user_id
            else:
                record.user_id = None
        else:
            record.url = None
            record.method = None
            record.remote_addr = None
            record.user_id = None
            
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        # Add request context if available
        if hasattr(record, 'url') and record.url:
            log_record['request'] = {
                'url': record.url,
                'method': record.method,
                'remote_addr': record.remote_addr
            }
            
            if hasattr(record, 'user_id') and record.user_id:
                log_record['request']['user_id'] = record.user_id
                
        return json.dumps(log_record)


def configure_logging(app):
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set log level based on configuration
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Clear any existing handlers
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
        
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)
    
    # Configure console handler for development
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = RequestFormatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Configure file handler for structured logging
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, 'app.log'),
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setLevel(log_level)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure SQLAlchemy logging separately if needed
    if app.config.get('SQLALCHEMY_ECHO', False):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    app.logger.info(f"Logging configured at level: {log_level}")
