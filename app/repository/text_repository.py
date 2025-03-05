from ..models import db, GeneratedText
import logging

class TextRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_by_id(self, text_id):
        """Get a generated text by ID"""
        try:
            return GeneratedText.query.get(text_id)
        except Exception as e:
            self.logger.error(f"Error retrieving text by ID {text_id}: {str(e)}")
            return None
    
    def get_by_id_and_user(self, text_id, user_id):
        """Get a text by ID and ensure it belongs to the specified user"""
        try:
            return GeneratedText.query.filter_by(id=text_id, user_id=user_id).first()
        except Exception as e:
            self.logger.error(f"Error retrieving text ID {text_id} for user {user_id}: {str(e)}")
            return None
    
    def get_all_by_user_id(self, user_id):
        """Get all texts for a user"""
        try:
            return GeneratedText.query.filter_by(user_id=user_id).order_by(GeneratedText.timestamp.desc()).all()
        except Exception as e:
            self.logger.error(f"Error retrieving texts for user {user_id}: {str(e)}")
            return []
    
    def create(self, user_id, prompt, response, provider=None):
        """Create a new generated text"""
        try:
            new_text = GeneratedText(
                user_id=user_id,
                prompt=prompt,
                response=response,
                provider=provider
            )
            
            db.session.add(new_text)
            db.session.commit()
            
            self.logger.info(f"Created new text for user {user_id}, text ID: {new_text.id}")
            return new_text
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating text for user {user_id}: {str(e)}")
            raise
    
    def update(self, id, user_id, prompt=None, response=None):
        """Update a generated text"""
        try:
            text = self.get_by_id_and_user(id, user_id)
            if not text:
                return False
                
            if prompt is not None:
                text.prompt = prompt
                
            if response is not None:
                text.response = response
                
            db.session.commit()
            
            self.logger.info(f"Updated text ID {id} for user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error updating text ID {id} for user {user_id}: {str(e)}")
            return False
    
    def delete(self, text_id, user_id):
        """Delete a generated text"""
        try:
            text = self.get_by_id_and_user(text_id, user_id)
            if not text:
                return False
                
            db.session.delete(text)
            db.session.commit()
            
            self.logger.info(f"Deleted text ID {text_id} for user {user_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error deleting text ID {text_id} for user {user_id}: {str(e)}")
            return False