from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging


# Custom decorator for route protection
def auth_middleware():

    logger = logging.getLogger(__name__)

    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()

            # Convert the string ID back to an integer
            try:
                user_id = int(current_user_id)

                # Set user_id on request for logging middleware
                request.user_id = user_id

                logger.debug(f"Authenticated request for user ID: {user_id}")
                return fn(user_id, *args, **kwargs)

            except (ValueError, TypeError) as e:
                logger.warning(
                    f"Invalid user identity in token: {current_user_id}. Error: {str(e)}"
                )
                return jsonify({"error": "Invalid user identity"}), 401

        return decorator

    return wrapper
