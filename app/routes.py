from flask import Blueprint, request, jsonify, current_app
from .models import db, GeneratedText
from .auth import jwt_required,auth_middleware
from .openai_service import OpenAIService
from flask_jwt_extended import create_access_token, get_jwt_identity


api_bp = Blueprint('api', __name__)

@api_bp.route('/generate-text', methods=['POST'])
@auth_middleware()
def generate_text(current_user_id):
   
    data = request.get_json()
    try:
        user_id = int(current_user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user identity"}), 401
    
    # Validate input data
    if not data or not data.get('prompt'):
        return jsonify({'error': 'Missing prompt'}), 400
    
    try:
        # Initialize OpenAI service with just the API key
        api_key = current_app.config.get('OPENAI_API_KEY')
        model = current_app.config.get('OPENAI_MODEL')
        
        # Debug logging
        current_app.logger.info(f"Initializing OpenAI service with model: {model}")
        print(api_key,'dkkdkkkdk')
        # openai_service = OpenAIService(
        #     api_key=api_key,
        #     model=model
        # )
        # print(openai_service,'kkkkk')
        
        # Generate text from OpenAI
        response_text = OpenAIService().generate_text(prompt=data['prompt'])
        print(response_text,'dkkdkjd')
        
        # Store the generated text in the database
        new_generated_text = GeneratedText(
            user_id=current_user_id,
            prompt=data['prompt'],
            response=response_text
        )
        
        db.session.add(new_generated_text)
        db.session.commit()
        
        return jsonify(new_generated_text.to_dict()), 201
    
    except Exception as e:
        current_app.logger.error(f"Error in generate-text: {str(e)}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/generated-text/<int:id>', methods=['GET'])
@auth_middleware()
def get_generated_text(current_user_id, id):
    try:
        user_id = int(current_user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user identity"}), 401

    # Retrieve the generated text by ID
    generated_text = GeneratedText.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not generated_text:
        return jsonify({'error': 'Generated text not found or not authorized'}), 404
    
    return jsonify(generated_text.to_dict()), 200


@api_bp.route('/generated-text/<int:id>', methods=['PUT'])
@auth_middleware()
def update_generated_text(current_user_id, id):
 
    data = request.get_json()
    
    # Validate input data
    try:
        user_id = int(current_user_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid user identity"}), 401
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Retrieve the generated text by ID
    generated_text = GeneratedText.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not generated_text:
        return jsonify({'error': 'Generated text not found or not authorized'}), 404
    
    # Update fields if provided
    if 'prompt' in data:
        generated_text.prompt = data['prompt']
    
    if 'response' in data:
        generated_text.response = data['response']
    
    db.session.commit()
    
    return jsonify(generated_text.to_dict()), 200


@api_bp.route('/generated-text/<int:id>', methods=['DELETE'])
@auth_middleware()
def delete_generated_text(current_user_id, id):
  
    # Retrieve the generated text by ID
    generated_text = GeneratedText.query.filter_by(id=id, user_id=current_user_id).first()
    
    if not generated_text:
        return jsonify({'error': 'Generated text not found or not authorized'}), 404
    
    db.session.delete(generated_text)
    db.session.commit()
    
    return jsonify({'message': 'Generated text deleted successfully'}), 200


@api_bp.route('/generated-texts', methods=['GET'])
@auth_middleware()
def get_all_generated_texts(current_user_id):

    # Retrieve all generated texts for the current user
    generated_texts = GeneratedText.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([text.to_dict() for text in generated_texts]), 200