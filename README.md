# Revenue Guardian

Revenue reconciliation and analytics system that helps organizations validate and align financial data across multiple sources.

## Features

- **FastAPI Backend**: High-performance async REST API
- **PostgreSQL Database**: Reliable data storage with async SQLAlchemy ORM
- **Alembic Migrations**: Version-controlled database schema management
- **UV Package Manager**: Fast, deterministic dependency management
- **Clean Architecture**: Modular, scalable project structure
- **Role-Based Access Control**: Admin, Operations, and CXO user roles
- **JWT Authentication**: Secure token-based authentication
- **Docker Support**: Containerized deployment with Docker Compose
- **Comprehensive Testing**: pytest with async support
- **OpenAPI Documentation**: Automatic API documentation with Swagger UI

## Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL 16 with asyncpg
- **ORM**: SQLAlchemy 2.0+ (async)
- **Migrations**: Alembic
- **Package Manager**: UV
- **Authentication**: JWT with python-jose
- **Testing**: pytest, pytest-asyncio
- **Deployment**: Docker, Docker Compose

## Project Structure

```
revenue_analysis/
├── app/
│   ├── core/              # Configuration, security, database
│   │   ├── config.py      # Pydantic settings
│   │   ├── database.py    # Database setup
│   │   └── security.py    # Password hashing, JWT
│   ├── models/            # SQLAlchemy models
│   │   ├── base.py        # Base model with timestamps
│   │   └── user.py        # User model
│   ├── schemas/           # Pydantic schemas
│   │   └── user.py        # User DTOs
│   ├── crud/              # Repository pattern
│   │   └── user.py        # User CRUD operations
│   ├── services/          # Business logic
│   │   └── auth.py        # Authentication service
│   ├── routers/           # API endpoints
│   │   ├── auth.py        # Login endpoints
│   │   ├── users.py       # User management
│   │   └── health.py      # Health checks
│   └── dependencies/      # Dependency injection
│       └── auth.py        # Auth dependencies
├── alembic/               # Database migrations
├── tests/                 # Test suite
├── main.py                # FastAPI application
├── pyproject.toml         # Project dependencies
├── docker-compose.yml     # Docker orchestration
└── Dockerfile             # Application container

```

## Getting Started

### Prerequisites

- Python 3.12+
- UV package manager
- PostgreSQL 16+ (or use Docker)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd revenue_analysis
   ```

2. **Create virtual environment with UV**
   ```bash
   uv venv
   ```

3. **Activate virtual environment**
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`

4. **Install dependencies**
   ```bash
   uv pip install -e ".[dev]"
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

7. **Start the application**
   ```bash
   # Development server with auto-reload
   python run.py
   
   # Or using uvicorn directly
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

### Using Docker

1. **Start all services**
   ```bash
   docker-compose up -d
   ```

2. **Run migrations**
   ```bash
   docker-compose exec app alembic upgrade head
   ```

3. **View logs**
   ```bash
   docker-compose logs -f app
   ```

4. **Stop services**
   ```bash
   docker-compose down
   ```

## API Documentation

Once the application is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Authentication

The API uses JWT tokens for authentication. To access protected endpoints:

1. **Login** to get an access token:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin@example.com&password=yourpassword"
   ```

2. **Use the token** in subsequent requests:
   ```bash
   curl -X GET "http://localhost:8000/api/v1/users/me" \
     -H "Authorization: Bearer <your-token>"
   ```

## User Roles

- **Admin**: Full system access, user management
- **Operations**: Upload data, trigger reconciliation, view reports
- **CXO**: View analytics, AI insights, high-level KPIs

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run with verbose output
pytest -v
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Development

### Adding a New Feature

1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Implement CRUD in `app/crud/`
4. Add business logic in `app/services/`
5. Create API endpoints in `app/routers/`
6. Write tests in `tests/`
7. Generate and apply migrations

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Keep functions small and focused
- Use async/await for I/O operations

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Required |
| `ENVIRONMENT` | Environment (development/staging/production) | development |
| `DEBUG` | Enable debug mode | false |
| `REDIS_URL` | Redis connection string | redis://localhost:6379/0 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | 30 |

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure all tests pass
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.