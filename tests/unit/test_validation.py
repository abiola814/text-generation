import pytest
from app.validation.base import Validator, ValidationError
from app.validation.user_validator import UserValidator
from app.validation.text_validator import TextValidator


class TestBaseValidator:
    """Test the Base Validator class"""
    
    def test_validate_required(self):
        """Test validating required fields"""
        # Valid data
        data = {'field1': 'value1', 'field2': 'value2'}
        assert Validator.validate_required(data, ['field1', 'field2']) is True
        
        # Missing field
        data = {'field1': 'value1'}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_required(data, ['field1', 'field2'])
        
        assert 'field2' in excinfo.value.errors
        
        # Empty field
        data = {'field1': 'value1', 'field2': ''}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_required(data, ['field1', 'field2'])
        
        assert 'field2' in excinfo.value.errors
    
    def test_validate_length(self):
        """Test validating field length"""
        # Valid data
        data = {'field': 'test'}
        assert Validator.validate_length(data, 'field', min_length=1, max_length=10) is True
        
        # Too short
        data = {'field': 'a'}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_length(data, 'field', min_length=2)
        
        assert 'field' in excinfo.value.errors
        
        # Too long
        data = {'field': 'test_too_long'}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_length(data, 'field', max_length=10)
        
        assert 'field' in excinfo.value.errors
        
        # Field missing - should not raise error
        data = {}
        assert Validator.validate_length(data, 'field', min_length=5) is None
    
    def test_validate_type(self):
        """Test validating field type"""
        # Valid data
        data = {'int_field': 42, 'str_field': 'text'}
        assert Validator.validate_type(data, 'int_field', int) is True
        assert Validator.validate_type(data, 'str_field', str) is True
        
        # Wrong type
        data = {'field': 'not_an_int'}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_type(data, 'field', int)
        
        assert 'field' in excinfo.value.errors
        
        # Field missing - should not raise error
        data = {}
        assert Validator.validate_type(data, 'field', int) is None
    
    def test_validate_custom(self):
        """Test custom validation function"""
        # Valid data
        data = {'email': 'user@example.com'}
        validator_func = lambda x: '@' in x
        assert Validator.validate_custom(
            data, 'email', validator_func, '{field_name} must be valid'
        ) is True
        
        # Invalid data
        data = {'email': 'invalid_email'}
        with pytest.raises(ValidationError) as excinfo:
            Validator.validate_custom(
                data, 'email', validator_func, '{field_name} must be valid'
            )
        
        assert 'email' in excinfo.value.errors


class TestUserValidator:
    """Test the User Validator"""
    
    def test_validate_registration_valid(self):
        """Test validating registration with valid data"""
        data = {
            'username': 'validuser',
            'password': 'Password123'
        }
        assert UserValidator.validate_registration(data) is True
    
    def test_registration_missing_fields(self):
        """Test registration with missing fields"""
        # Missing username
        data = {'password': 'Password123'}
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'username' in excinfo.value.errors
        
        # Missing password
        data = {'username': 'validuser'}
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'password' in excinfo.value.errors
    
    def test_registration_invalid_username(self):
        """Test registration with invalid username"""
        # Username too short
        data = {
            'username': 'ab',  # Too short
            'password': 'Password123'
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'username' in excinfo.value.errors
        
        # Username with invalid characters
        data = {
            'username': 'user@name',  # Contains @
            'password': 'Password123'
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'username' in excinfo.value.errors
    
    def test_registration_weak_password(self):
        """Test registration with weak password"""
        # Password too short
        data = {
            'username': 'validuser',
            'password': 'short'  # Too short
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'password' in excinfo.value.errors
        
        # Password missing uppercase
        data = {
            'username': 'validuser',
            'password': 'password123'  # No uppercase
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'password' in excinfo.value.errors
        
        # Password missing lowercase
        data = {
            'username': 'validuser',
            'password': 'PASSWORD123'  # No lowercase
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'password' in excinfo.value.errors
        
        # Password missing digit
        data = {
            'username': 'validuser',
            'password': 'PasswordOnly'  # No digit
        }
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_registration(data)
        
        assert 'password' in excinfo.value.errors
    
    def test_validate_login(self):
        """Test login validation"""
        # Valid login
        data = {
            'username': 'loginuser',
            'password': 'loginpass'
        }
        assert UserValidator.validate_login(data) is True
        
        # Missing fields
        data = {'username': 'loginuser'}  # Missing password
        with pytest.raises(ValidationError) as excinfo:
            UserValidator.validate_login(data)
        
        assert 'password' in excinfo.value.errors


class TestTextValidator:
    """Test the Text Validator"""
    
    def test_validate_generate_text_valid(self):
        """Test validating text generation with valid data"""
        data = {'prompt': 'Valid prompt text'}
        assert TextValidator.validate_generate_text(data) is True
    
    def test_validate_generate_text_missing_prompt(self):
        """Test validation with missing prompt"""
        data = {}
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_generate_text(data)
        
        assert 'prompt' in excinfo.value.errors
    
    def test_validate_generate_text_with_options(self):
        """Test validation with options"""
        # Valid options
        data = {
            'prompt': 'Test prompt',
            'options': {
                'temperature': 0.7,
                'max_tokens': 500
            }
        }
        assert TextValidator.validate_generate_text(data) is True
        
        # Invalid temperature
        data = {
            'prompt': 'Test prompt',
            'options': {
                'temperature': 1.5  # Should be between 0 and 1
            }
        }
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_generate_text(data)
        
        assert 'options.temperature' in excinfo.value.errors
        
        # Invalid max_tokens
        data = {
            'prompt': 'Test prompt',
            'options': {
                'max_tokens': -10  # Should be positive
            }
        }
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_generate_text(data)
        
        assert 'options.max_tokens' in excinfo.value.errors
        
        # Invalid options type
        data = {
            'prompt': 'Test prompt',
            'options': 'not a dict'  # Should be a dict
        }
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_generate_text(data)
        
        assert 'options' in excinfo.value.errors
    
    def test_validate_update_text_valid(self):
        """Test validating text update with valid data"""
        # Valid with both fields
        data = {
            'prompt': 'Updated prompt',
            'response': 'Updated response'
        }
        assert TextValidator.validate_update_text(data) is True
        
        # Valid with only prompt
        data = {'prompt': 'Only prompt updated'}
        assert TextValidator.validate_update_text(data) is True
        
        # Valid with only response
        data = {'response': 'Only response updated'}
        assert TextValidator.validate_update_text(data) is True
    
    def test_validate_update_text_invalid(self):
        """Test validation with invalid update data"""
        # Empty data
        data = {}
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_update_text(data)
        
        assert 'data' in excinfo.value.errors
        
        # Neither prompt nor response
        data = {'other_field': 'value'}
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_update_text(data)
        
        assert 'prompt/response' in excinfo.value.errors
        
        # Empty prompt
        data = {'prompt': ''}
        with pytest.raises(ValidationError) as excinfo:
            TextValidator.validate_update_text(data)
        
        assert 'prompt' in excinfo.value.errors
