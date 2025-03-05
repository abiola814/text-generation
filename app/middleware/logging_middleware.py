import time
import logging
from flask import request, g


class LoggingMiddleware:
    # Middleware for logging requests and responses

    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    def __call__(self, environ, start_response):
        # Start timer
        start_time = time.time()

        # Process the request
        def custom_start_response(status, headers, exc_info=None):
            # Log after request is processed
            duration = time.time() - start_time
            status_code = int(status.split(" ")[0])

            # Get the path and method
            path = environ.get("PATH_INFO", "")
            method = environ.get("REQUEST_METHOD", "")

            # Get user ID if it's in g
            user_id = getattr(g, "user_id", None)

            # Log basic info for all requests
            log_data = {
                "method": method,
                "path": path,
                "status": status_code,
                "duration_ms": round(duration * 1000, 2),
            }

            # Add user ID if available
            if user_id:
                log_data["user_id"] = user_id

            # Determine log level based on status code
            if status_code >= 500:
                self.logger.error(f"Request processed: {log_data}")
            elif status_code >= 400:
                self.logger.warning(f"Request processed: {log_data}")
            else:
                self.logger.info(f"Request processed: {log_data}")

            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
