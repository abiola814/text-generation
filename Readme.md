# AI Text Generation API

## Running the Application

Follow these simple steps to run the API using Docker Compose:

1. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key
   JWT_SECRET_KEY=your-jwt-secret
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-4o-mini
   ```

2. **Start the Application**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access the API**:
   - API available at http://localhost:5000
   - Health check at http://localhost:5000/health

4. **API Documentation**:
   - [Postman Documentation](https://documenter.getpostman.com/view/26542987/2sAYdhLWJK)

## Running Tests

1. **Set Up Test Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install pytest pytest-cov
   ```

2. **Run All Tests**:
   ```bash
   python -m pytest
   ```

3. **Run Specific Test Categories**:
   ```bash
   python -m pytest tests/unit/       # Unit tests only
   python -m pytest tests/integration/ # Integration tests only
   python -m pytest -v                 # Verbose output
   python -m pytest --cov=app          # With coverage
   ```

## Troubleshooting

- **Database Connection**: Verify port 5432 is available for container communication
- **Test Database Issues**: Delete test.db and restart tests if database errors occur
- **API Key Issues**: Ensure your OpenAI API key has sufficient quota