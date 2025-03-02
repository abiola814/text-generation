# Deployment Guide with Testing

With appropriate testing prior to deployment, this post walks you through using Docker and Docker Compose how to deploy your Flask Text Generator application.

## Postman documentation

link 
´´´
https://documenter.getpostman.com/view/26542987/2sAYdhLWJK


´´´

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Git (to clone the repository)




## Setup

1. Clone the repository:
   ```bash
   git clone <your-repository-url>
   cd text-generator
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Edit the `.env` file and update the environment variables:
   - Set strong secret keys for `SECRET_KEY` and `JWT_SECRET_KEY`
   - Add your OpenAI API key as `OPENAI_API_KEY`
   - Adjust other settings as needed

4. Make the run script executable:
   ```bash
   chmod +x run-with-tests.sh
   ```

## Deployment with Testing

### Option 1: Using the Run Script (Recommended)

The script will run tests first and only start the application if tests pass:

```bash
./run-with-tests.sh
```

### Option 2: Using Docker Compose Directly

1. Start the database first:
   ```bash
   docker-compose up -d db
   ```

2. Run the tests:
   ```bash
   docker-compose run --rm test
   ```

3. If tests pass, start the web application:
   ```bash
   docker-compose up -d web pgadmin
   ```

## Accessing the Application

- Flask application: http://localhost:5003
- pgAdmin: http://localhost:5050 (login with admin@example.com/admin)

## Continuous Integration Workflow

For CI/CD pipelines, you can use the testing approach in your automation:

```bash
# Example CI workflow
docker-compose up -d db
docker-compose run --rm test

# Check exit code
if [ $? -eq 0 ]; then
  echo "Tests passed, deploying..."
  # Deployment steps here
else
  echo "Tests failed, aborting deployment"
  exit 1
fi
```


## Scaling

To scale the application horizontally:

```bash
docker-compose up -d --scale web=3
```

This will create 3 instances of the web application.

For production-grade scaling, consider using:
- Kubernetes
- Docker Swarm
- AWS ECS/EKS

## Maintenance

### Viewing Logs

```bash
docker-compose logs -f web
```

### Database Migrations

Database migrations are applied automatically when the container starts.

To manually run migrations:

```bash
docker-compose exec web flask db upgrade
```

### Database Backup

```bash
docker-compose exec db pg_dump -U postgres text_generator > backup.sql
```

## Manually Running Tests

To run tests without starting the application:

```bash
docker-compose run --rm test
```

To run specific tests:

```bash
docker-compose run --rm test python -m pytest test/test_auth.py
```

## Troubleshooting

### Test Database Connection Issues

If tests can't connect to the database:

1. Check if the PostgreSQL container is running:
   ```bash
   docker-compose ps
   ```

2. Verify the database URL in the test environment variables.

3. Check the logs:
   ```bash
   docker-compose logs db
   ```

### Test Failures

If tests fail:

1. Check the test output for specific error messages

2. Run tests with more verbose output:
   ```bash
   docker-compose run --rm test python -m pytest -v
   ```

3. For debugging, you can access the test container:
   ```bash
   docker-compose run --rm test bash
   ```

## Maintenance

To stop all services:

```bash
docker-compose down
```

To restart with fresh tests:

```bash
docker-compose up -d --build


```