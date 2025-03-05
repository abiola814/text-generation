from sqlalchemy import func
from ..models import db, User
import logging

class UserRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def normalize_username(self, username):
        """Normalize username to lowercase for consistent comparisons"""
        return username.lower() if username else None
    
    def get_by_id(self, user_id):
        """Get a user by ID"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            self.logger.error(f"Error retrieving user by ID {user_id}: {str(e)}")
            return None
    
    def get_by_username(self, username):
        """Get a user by username (case-insensitive)"""
        try:
            normalized_username = self.normalize_username(username)
            return User.query.filter(func.lower(User.username) == normalized_username).first()
        except Exception as e:
            self.logger.error(f"Error retrieving user by username '{username}': {str(e)}")
            return None
    
    def create(self, username, password):
        """Create a new user"""
        try:
            # Normalize the username before checking for duplicates
            normalized_username = self.normalize_username(username)
            
            # Check if user already exists (case-insensitive)
            existing_user = self.get_by_username(normalized_username)
            if existing_user:
                self.logger.warning(f"Attempted to create duplicate user: {username}")
                return None
            
            # Create new user with the original case but we'll query with normalized case
            new_user = User(username=username)
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            self.logger.info(f"Created new user: {username}")
            return new_user
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating user '{username}': {str(e)}")
            raise
    
    def update_password(self, user_id, new_password):
        """Update a user's password"""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
                
            user.set_password(new_password)
            db.session.commit()
            
            self.logger.info(f"Updated password for user ID {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating password for user ID {user_id}: {str(e)}")
            return False
    
    def delete(self, user_id):
        """Delete a user"""
        try:
            user = self.get_by_id(user_id)
            if not user:
                return False
                
            db.session.delete(user)
            db.session.commit()
            
            self.logger.info(f"Deleted user ID {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting user ID {user_id}: {str(e)}")
            return False