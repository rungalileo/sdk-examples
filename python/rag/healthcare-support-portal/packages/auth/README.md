# Authentication Service

The Authentication Service handles user authentication, registration, and token management for the Healthcare Support Portal. It provides JWT-based authentication with role-based access control using Oso.

## Features

- **User Registration:** Create new healthcare professional accounts
- **Authentication:** JWT token-based login system
- **Authorization:** Role-based access control (doctor, nurse, admin)
- **User Management:** CRUD operations with Oso policy enforcement
- **Token Refresh:** Extend authentication sessions
- **Password Security:** Bcrypt hashing for secure password storage

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL with the Healthcare Support Portal database
- uv package manager

### Installation

```bash
# From project root
uv sync

# Or from package directory
cd packages/auth
uv sync
```

### Environment Variables

Create a `.env` file or set these environment variables:

```env
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Running the Service

```bash
# Set PYTHONPATH and run
export PYTHONPATH="../common/src:$PYTHONPATH"
uv run uvicorn src.auth_service.main:app --reload --port 8001

# Or use the run script from package directory
cd packages/auth
./run.sh
```

The service will be available at http://localhost:8001

### API Documentation

Interactive API docs are available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/login` | User login | No |
| POST | `/api/v1/auth/register` | User registration | No |
| GET | `/api/v1/auth/me` | Get current user info | Yes |
| POST | `/api/v1/auth/refresh` | Refresh access token | Yes |

### User Management

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/v1/users/` | List users (authorized) | Yes |
| GET | `/api/v1/users/{user_id}` | Get specific user | Yes |
| PUT | `/api/v1/users/{user_id}` | Update user | Yes |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Service health check | No |
| GET | `/` | Service info | No |

## Example Usage

### Register a New User

```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dr_smith",
    "email": "smith@hospital.com",
    "password": "secure_password",
    "role": "doctor",
    "department": "cardiology"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr_smith&password=secure_password"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Get Current User Info

```bash
curl -X GET "http://localhost:8001/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## User Roles

The service supports three user roles with different permissions:

- **Doctor:** Can read their own info, manage assigned patients
- **Nurse:** Can read their own info, view patients in their department
- **Admin:** Can read/write all users and resources

## Authorization Policies

Authorization is handled by Oso policies defined in `common/policies/authorization.polar`. Key rules:

- Users can read their own information
- Admins can read any user
- Role-based access to other resources

## Development

### Project Structure

```
src/auth_service/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
└── routers/
    ├── __init__.py
    ├── auth.py          # Authentication endpoints
    └── users.py         # User management endpoints
```

### Dependencies

Key dependencies include:
- FastAPI: Web framework
- SQLAlchemy: ORM for database operations
- Oso: Authorization framework
- python-jose: JWT handling
- passlib: Password hashing
- common: Shared models and utilities

### Testing

```bash
# Run tests (if implemented)
uv run pytest

# Test imports
uv run python -c "from common.models import User; print('Import successful!')"
```

## Troubleshooting

### Common Issues

1. **Import errors:** Ensure PYTHONPATH includes `../common/src`
2. **Database connection:** Verify PostgreSQL is running and DATABASE_URL is correct
3. **JWT errors:** Check SECRET_KEY is set and consistent across services

### Logs

The service logs to stdout. For debugging, set `DEBUG=true` in your environment.

## Security Considerations

- Use strong SECRET_KEY in production
- Set appropriate CORS origins
- Use HTTPS in production
- Regularly rotate JWT secrets
- Monitor for failed authentication attempts

## Integration

This service integrates with:
- **Patient Service:** Provides authentication for patient management
- **RAG Service:** Provides authentication for document operations
- **Common Package:** Shared models, database, and utilities

## Contributing

1. Follow the existing code structure
2. Add appropriate error handling
3. Update this README for new features
4. Ensure Oso policies are updated for new endpoints
