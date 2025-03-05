from flask import Blueprint, request, jsonify, current_app
import logging
from ..middleware.auth_middleware import auth_middleware
from ..repository.text_repository import TextRepository
from ..service.ai_service import AIService
from ..validation.text_validator import TextValidator
from ..validation.base import validate_request

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

@api_bp.route('/generate-text', methods=['POST'])
@auth_middleware()
@validate_request(TextValidator.validate_generate_text)
def generate_text(current_user_id):
    """Generate text using AI"""
    data = request.get_json()
    text_repo = TextRepository()
    
    try:
        # Get AI provider from query parameter or default
        provider_name = request.args.get('provider') or current_app.config.get('DEFAULT_AI_PROVIDER', 'openai')
        
        # Initialize AI service with provider
        ai_service = AIService(
            provider_name=provider_name,
            api_key=current_app.config.get(f'{provider_name.upper()}_API_KEY'),
            model=current_app.config.get(f'{provider_name.upper()}_MODEL')
        )
        
        # Generate text
        logger.info(f"Generating text with provider: {provider_name}")
        response_text = ai_service.generate_text(prompt=data['prompt'])
        
        # Store the generated text in the database
        new_generated_text = text_repo.create(
            user_id=current_user_id,
            prompt=data['prompt'],
            response=response_text,
            provider=ai_service.get_provider_name()
        )
        
        return jsonify(new_generated_text.to_dict()), 201
    
    except Exception as e:
        logger.error(f"Error in generate-text: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generated-text/<int:id>', methods=['GET'])
@auth_middleware()
def get_generated_text(current_user_id, id):
    """Get a generated text by ID"""
    text_repo = TextRepository()
    
    try:
        # Retrieve the generated text by ID
        generated_text = text_repo.get_by_id_and_user(id, current_user_id)
        
        if not generated_text:
            return jsonify({'error': 'Generated text not found or not authorized'}), 404
        
        return jsonify(generated_text.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error retrieving generated text ID {id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generated-text/<int:id>', methods=['PUT'])
@auth_middleware()
@validate_request(TextValidator.validate_update_text)
def update_generated_text(current_user_id, id):
    """Update a generated text"""
    data = request.get_json()
    text_repo = TextRepository()
    
    try:
        updated = text_repo.update(
            id=id,
            user_id=current_user_id,
            prompt=data.get('prompt'),
            response=data.get('response')
        )
        
        if not updated:
            return jsonify({'error': 'Generated text not found or not authorized'}), 404
        
        updated_text = text_repo.get_by_id(id)
        return jsonify(updated_text.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating generated text ID {id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generated-text/<int:id>', methods=['DELETE'])
@auth_middleware()
def delete_generated_text(current_user_id, id):
    """Delete a generated text"""
    text_repo = TextRepository()
    
    try:
        deleted = text_repo.delete(id, current_user_id)
        
        if not deleted:
            return jsonify({'error': 'Generated text not found or not authorized'}), 404
        
        return jsonify({'message': 'Generated text deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting generated text ID {id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generated-texts', methods=['GET'])
@auth_middleware()
def get_all_generated_texts(current_user_id):
    """Get all generated texts for a user"""
    text_repo = TextRepository()
    
    try:
        # Retrieve all generated texts for the current user
        generated_texts = text_repo.get_all_by_user_id(current_user_id)
        
        return jsonify([text.to_dict() for text in generated_texts]), 200
        
    except Exception as e:
        logger.error(f"Error retrieving all texts for user {current_user_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/providers', methods=['GET'])
@auth_middleware()
def get_available_providers(current_user_id):
    """Get list of available AI providers"""
    try:
        # This could be expanded to query the factory for all registered providers
        providers = {
            'openai': {
                'name': 'OpenAI',
                'models': ['gpt-3.5-turbo', 'gpt-4-turbo']
            }
            # Additional providers would be listed here
        }
        
        return jsonify(providers), 200
        
    except Exception as e:
        logger.error(f"Error retrieving providers: {str(e)}")
        return jsonify({'error': str(e)}), 500