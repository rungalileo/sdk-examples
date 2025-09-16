# Patient Service

The Patient Service manages patient records and information for the Healthcare Support Portal. It provides CRUD operations with comprehensive role-based authorization using Oso policies.

## Features

- **Patient CRUD:** Create, read, update, and delete patient records
- **Authorization:** Role-based access control with Oso policies
- **Department Filtering:** Search patients by department
- **Doctor Assignment:** Assign and manage doctor-patient relationships
- **Soft Delete:** Deactivate patients instead of hard deletion
- **Pagination:** Efficient handling of large patient lists
- **Medical Record Validation:** Ensure unique medical record numbers

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL with the Healthcare Support Portal database
- uv package manager
- Authentication Service running (for JWT validation)

### Installation

```bash
# From project root
uv sync

# Or from package directory
cd packages/patient
uv sync
```

### Environment Variables

Create a `.env` file or set these environment variables:

```env
DEBUG=true
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/healthcare
```

### Running the Service

```bash
# Set PYTHONPATH and run
export PYTHONPATH="../common/src:$PYTHONPATH"
uv run uvicorn src.patient_service.main:app --reload --port 8002

# Or use the run script from package directory
cd packages/patient
./run.sh
```

The service will be available at http://localhost:8002

### API Documentation

Interactive API docs are available at:
- Swagger UI: http://localhost:8002/docs
- ReDoc: http://localhost:8002/redoc

## API Endpoints

### Patient Management

| Method | Endpoint | Description | Auth Required | Roles |
|--------|----------|-------------|---------------|-------|
| GET | `/api/v1/patients/` | List patients (authorized) | Yes | doctor, nurse, admin |
| GET | `/api/v1/patients/{patient_id}` | Get specific patient | Yes | assigned doctor, dept nurse, admin |
| POST | `/api/v1/patients/` | Create new patient | Yes | doctor, admin |
| PUT | `/api/v1/patients/{patient_id}` | Update patient | Yes | assigned doctor, admin |
| DELETE | `/api/v1/patients/{patient_id}` | Soft delete patient | Yes | assigned doctor, admin |
| GET | `/api/v1/patients/search/by-department/{dept}` | Search by department | Yes | dept nurse, admin |

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Service health check | No |
| GET | `/` | Service info | No |

## Example Usage

### Get Your JWT Token First

```bash
# Login via auth service
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dr_smith&password=secure_password"
```

### Create a New Patient

```bash
curl -X POST "http://localhost:8002/api/v1/patients/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "medical_record_number": "MRN-2024-001",
    "department": "cardiology",
    "assigned_doctor_id": 1
  }'
```

### List Patients (with pagination)

```bash
curl -X GET "http://localhost:8002/api/v1/patients/?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Get Specific Patient

```bash
curl -X GET "http://localhost:8002/api/v1/patients/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Update Patient

```bash
curl -X PUT "http://localhost:8002/api/v1/patients/1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "medical_record_number": "MRN-2024-001",
    "department": "cardiology",
    "assigned_doctor_id": 2
  }'
```

### Search Patients by Department

```bash
curl -X GET "http://localhost:8002/api/v1/patients/search/by-department/cardiology?skip=0&limit=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Authorization Rules

The service implements comprehensive authorization using Oso policies:

### Doctor Access
- **Read:** Only assigned patients
- **Write:** Only assigned patients
- **Create:** Can create new patients

### Nurse Access
- **Read:** Patients in their department (non-sensitive)
- **Write:** No write access
- **Create:** No create access

### Admin Access
- **Read:** All patients
- **Write:** All patients
- **Create:** Can create new patients

## Data Models

### Patient Schema

```json
{
  "id": 1,
  "name": "John Doe",
  "medical_record_number": "MRN-2024-001",
  "department": "cardiology",
  "assigned_doctor_id": 1,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### Required Fields
- `name`: Patient's full name
- `medical_record_number`: Unique identifier (must be unique)

### Optional Fields
- `department`: Medical department
- `assigned_doctor_id`: ID of assigned doctor
- `date_of_birth`: Patient's birth date

## Query Parameters

### Pagination
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

### Filtering
- `department`: Filter by department name

## Development

### Project Structure

```
src/patient_service/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
└── routers/
    ├── __init__.py
    └── patients.py      # Patient management endpoints
```

### Dependencies

Key dependencies include:
- FastAPI: Web framework
- SQLAlchemy: ORM for database operations
- Oso: Authorization framework
- sqlalchemy-oso: SQLAlchemy integration for Oso
- common: Shared models and utilities

### Testing

```bash
# Test imports
uv run python -c "from common.models import Patient; print('Import successful!')"

# Test database connection
uv run python -c "from common.db import create_tables; create_tables(); print('DB connection successful!')"
```

## Error Handling

The service returns standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found (patient doesn't exist)
- `422`: Unprocessable Entity (invalid data)
- `500`: Internal Server Error

### Common Error Responses

```json
{
  "detail": "Not authorized to access this patient"
}
```

```json
{
  "detail": "Patient with this medical record number already exists"
}
```

## Performance Considerations

- Pagination is enforced to prevent large result sets
- Database indexes on frequently queried fields
- Oso authorization queries are optimized at the database level
- Soft delete preserves data integrity

## Security Features

- JWT token validation on all protected endpoints
- Role-based authorization with Oso policies
- Input validation and sanitization
- Medical record number uniqueness enforcement
- Audit trail through created_at timestamps

## Integration

This service integrates with:
- **Auth Service:** JWT token validation and user information
- **RAG Service:** Patient-specific document access
- **Common Package:** Shared models, database, and utilities

## Troubleshooting

### Common Issues

1. **Authorization errors:** Ensure user has correct role and department
2. **Database errors:** Check PostgreSQL connection and table creation
3. **Import errors:** Verify PYTHONPATH includes `../common/src`
4. **Token errors:** Ensure auth service is running and SECRET_KEY matches

### Debug Mode

Set `DEBUG=true` for detailed error messages and SQL query logging.

## Contributing

1. Follow existing code patterns and structure
2. Add appropriate authorization checks for new endpoints
3. Update Oso policies for new access patterns
4. Include comprehensive error handling
5. Update this README for new features
