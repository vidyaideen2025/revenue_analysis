# Design Document: User Management APIs

## Overview

This document outlines the design for comprehensive user management APIs that allow administrators to perform CRUD operations on user accounts. The system will provide a complete set of RESTful endpoints for managing users, including creation, updates, activation/deactivation, and soft deletion.

## Architecture

### Component Diagram

```
┌─────────────────┐
│   Frontend UI   │
│ (User Mgmt)     │
└────────┬────────┘
         │ HTTP/JSON
         ▼
┌─────────────────────────────────────┐
│      FastAPI Application            │
│  ┌───────────────────────────────┐  │
│  │  app/routers/users.py         │  │
│  │  - List Users (GET /)         │  │
│  │  - Get User (GET /{id})       │  │
│  │  - Create User (POST /)       │  │
│  │  - Update User (PATCH /{id})  │  │
│  │  - Update Status (PUT /{id}/status) │
│  │  - Delete (DELETE /{id})      │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  app/dependencies/auth.py     │  │
│  │  - require_admin              │  │
│  │  - get_current_user           │  │
│  └───────────┬───────────────────┘  │
│              │                       │
│  ┌───────────▼───────────────────┐  │
│  │  app/crud/user.py             │  │
│  │  - get_all() with filters     │  │
│  │  - get_by_id()                │  │
│  │  - create()                   │  │
│  │  - update()                   │  │
│  │  - delete() (soft)            │  │
│  └───────────┬───────────────────┘  │
└──────────────┼─────────────────────┘
               │
               ▼
      ┌────────────────┐
      │   PostgreSQL   │
      │  users table   │
      └────────────────┘
```

## API Endpoints

### 1. List Users
**Endpoint**: `GET /api/v1/users/`  
**Auth**: Admin only  
**Purpose**: Retrieve paginated list of users with search and filtering

**Query Parameters**:
```typescript
{
  skip?: number = 0,          // Pagination offset
  limit?: number = 100,       // Max results (max: 100)
  search?: string,            // Search in email, username, full_name
  role?: UserRole,            // Filter by role (1=ADMIN, 2=OPERATIONS, 3=CXO)
  is_active?: boolean         // Filter by active status
}
```

**Response**:
```json
{
  "status": 200,
  "message": "Users retrieved successfully",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "sarah.j@kpmg.com",
        "username": "sarah.johnson",
        "full_name": "Sarah Johnson",
        "role": 1,
        "is_active": true,
        "created_at": "2025-11-01T10:00:00Z",
        "updated_at": "2025-11-04T14:30:00Z"
      }
    ],
    "total": 48,
    "skip": 0,
    "limit": 100
  }
}
```

### 2. Get User by ID
**Endpoint**: `GET /api/v1/users/{id}`  
**Auth**: Authenticated users (with access control)  
**Purpose**: Retrieve a specific user's details

**Access Control**:
- **Admin users**: Can view any user's profile
- **Non-admin users**: Can only view their own profile (id must match current user's id)
- **Use cases**: User profile page, admin user management

**Response**:
```json
{
  "status": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "sarah.j@kpmg.com",
    "username": "sarah.johnson",
    "full_name": "Sarah Johnson",
    "role": 1,
    "is_active": true,
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-04T14:30:00Z"
  }
}
```

**Error Response (Non-admin accessing other user)**:
```json
{
  "status": 403,
  "message": "Forbidden",
  "data": {
    "detail": "You can only view your own profile"
  }
}
```

### 3. Create User
**Endpoint**: `POST /api/v1/users/`  
**Auth**: Admin only  
**Purpose**: Create a new user account

**Request Body**:
```json
{
  "email": "lisa.c@kpmg.com",
  "username": "lisa.chen",
  "full_name": "Lisa Chen",
  "password": "SecurePass@123",
  "role": 2
}
```

**Response**:
```json
{
  "status": 201,
  "message": "User created successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "lisa.c@kpmg.com",
    "username": "lisa.chen",
    "full_name": "Lisa Chen",
    "role": 2,
    "is_active": true,
    "created_at": "2025-11-04T16:00:00Z",
    "updated_at": "2025-11-04T16:00:00Z"
  }
}
```

**Validation Rules**:
- Email must be valid and unique
- Username must be unique (3-100 chars)
- Password must be at least 8 characters
- Full name is required (1-255 chars)
- Role must be 1 (ADMIN), 2 (OPERATIONS), or 3 (CXO)

### 4. Update User
**Endpoint**: `PATCH /api/v1/users/{id}`  
**Auth**: Admin only  
**Purpose**: Update user information (partial update)

**Request Body** (all fields optional):
```json
{
  "email": "lisa.chen@kpmg.com",
  "username": "lisa.chen",
  "full_name": "Lisa Chen",
  "password": "NewSecurePass@123",
  "role": 3,
  "is_active": false
}
```

**Response**:
```json
{
  "status": 200,
  "message": "User updated successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "lisa.chen@kpmg.com",
    "username": "lisa.chen",
    "full_name": "Lisa Chen",
    "role": 3,
    "is_active": false,
    "created_at": "2025-11-04T16:00:00Z",
    "updated_at": "2025-11-04T16:30:00Z"
  }
}
```

### 5. Update User Status
**Endpoint**: `PUT /api/v1/users/{id}/status`  
**Auth**: Admin only  
**Purpose**: Update user account status (activate or deactivate)

**Request Body**:
```json
{
  "is_active": true
}
```

**Business Rules**:
- Admin cannot deactivate themselves (when is_active=false)
- Deactivated users cannot log in
- Accepts boolean value: true (activate) or false (deactivate)

**Response (Activate)**:
```json
{
  "status": 200,
  "message": "User status updated successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "lisa.chen@kpmg.com",
    "is_active": true
  }
}
```

**Response (Deactivate)**:
```json
{
  "status": 200,
  "message": "User status updated successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "lisa.chen@kpmg.com",
    "is_active": false
  }
}
```

### 6. Soft Delete User
**Endpoint**: `DELETE /api/v1/users/{id}`  
**Auth**: Admin only  
**Purpose**: Soft delete a user (set is_deleted=true, is_active=false)

**Business Rules**:
- Admin cannot delete themselves
- Soft delete preserves user record for audit trail
- Deleted users are excluded from normal queries
- Deleted users cannot log in

**Response**:
```json
{
  "status": 200,
  "message": "User deleted successfully",
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "email": "lisa.chen@kpmg.com",
    "is_deleted": true,
    "deleted_at": "2025-11-04T17:00:00Z"
  }
}
```

## Data Models

### User Model (Existing)
```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(Integer, nullable=False, default=UserRole.OPERATIONS.value)
    
    # From TimestampMixin:
    # created_at, updated_at, created_by, updated_by, is_active, is_deleted
```

### UserRole Enum (Existing)
```python
class UserRole(int, Enum):
    ADMIN = 1
    OPERATIONS = 2
    CXO = 3
```

## Repository Enhancements

### Enhanced get_all Method
```python
async def get_all(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    role: int | None = None,
    is_active: bool | None = None
) -> list[User]:
    """Get all users with filtering and pagination."""
    query = select(User).where(User.is_deleted == False)
    
    # Search filter
    if search:
        search_filter = or_(
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
            User.full_name.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Role filter
    if role is not None:
        query = query.where(User.role == role)
    
    # Active status filter
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    # Pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())
```

### Count Method
```python
async def count(
    db: AsyncSession,
    search: str | None = None,
    role: int | None = None,
    is_active: bool | None = None
) -> int:
    """Count users with same filters as get_all."""
    query = select(func.count(User.id)).where(User.is_deleted == False)
    
    # Apply same filters as get_all
    # ... (same filter logic)
    
    result = await db.execute(query)
    return result.scalar_one()
```

## Security Considerations

### Authorization
- **All endpoints require ADMIN role**
- Use `require_admin` dependency on router or individual endpoints
- Return 403 Forbidden for non-admin users
- JWT token must be valid and not expired

### Self-Modification Prevention
- **Deactivate**: Admin cannot deactivate their own account
- **Delete**: Admin cannot delete their own account
- Return 400 Bad Request with helpful message

### Password Security
- Passwords are hashed with bcrypt before storage
- Password hashes are never returned in API responses
- Password validation (min 8 chars) at schema level

### Audit Trail
- All operations record `created_by` or `updated_by` with admin's UUID
- Timestamps are automatically updated
- Soft delete preserves complete user history

## Error Handling

### Standard Error Responses

**404 Not Found**:
```json
{
  "status": 404,
  "message": "User not found",
  "data": {
    "detail": "User with ID 550e8400-e29b-41d4-a716-446655440000 does not exist"
  }
}
```

**400 Bad Request** (Duplicate Email):
```json
{
  "status": 400,
  "message": "Email already exists",
  "data": {
    "detail": "A user with email lisa.c@kpmg.com already exists",
    "field": "email"
  }
}
```

**400 Bad Request** (Self-Deactivation):
```json
{
  "status": 400,
  "message": "Cannot deactivate your own account",
  "data": {
    "detail": "Administrators cannot deactivate themselves. Please ask another admin."
  }
}
```

**403 Forbidden** (Insufficient Permissions):
```json
{
  "status": 403,
  "message": "Insufficient permissions",
  "data": {
    "detail": "Required role: ADMIN"
  }
}
```

**422 Unprocessable Entity** (Validation Error):
```json
{
  "status": 422,
  "message": "Validation error",
  "data": {
    "detail": [
      {
        "loc": ["body", "password"],
        "msg": "String should have at least 8 characters",
        "type": "string_too_short"
      }
    ]
  }
}
```

## Frontend Integration

Based on the provided UI screenshot, the APIs support:

### User List Table
- **Columns**: Name, Email, Role, Department, Last Active, Status
- **Search**: Real-time search across name/email
- **Filters**: Role badges (Admin, CXO, Operations), Status (Active/Inactive)
- **Pagination**: "Showing 4 of 4 records"
- **Actions**: Add New User, Import Users, Export List

### Mapping
```typescript
// Frontend to API mapping
{
  Name: user.full_name,
  Email: user.email,
  Role: getRoleName(user.role),  // 1→Admin, 2→Operations, 3→CXO
  Department: user.department,    // Not in current model (future enhancement)
  "Last Active": user.updated_at,
  Status: user.is_active ? "Active" : "Inactive"
}
```

## Performance Considerations

### Indexing
- Email and username already have unique indexes
- Consider adding composite index on (is_deleted, is_active) for filtering
- Consider adding GIN index on full_name for full-text search

### Pagination
- Default limit: 100 users per page
- Maximum limit: 100 (prevent excessive data transfer)
- Use offset-based pagination (simple, works well for admin interfaces)

### Query Optimization
- Use select() for efficient queries
- Avoid N+1 problems (no relationships yet, but consider for future)
- Exclude password_hash at query level if possible

## Testing Strategy

### Unit Tests
- Test each repository method with various filters
- Test validation logic (email/username uniqueness)
- Test password hashing
- Test soft delete behavior

### Integration Tests
- Test complete request/response cycle for each endpoint
- Test authorization (admin vs non-admin)
- Test self-modification prevention
- Test error responses

### Test Data
```python
# Test users
admin_user = User(email="admin@test.com", role=UserRole.ADMIN)
ops_user = User(email="ops@test.com", role=UserRole.OPERATIONS)
cxo_user = User(email="cxo@test.com", role=UserRole.CXO)
inactive_user = User(email="inactive@test.com", is_active=False)
deleted_user = User(email="deleted@test.com", is_deleted=True)
```

## Future Enhancements

### Phase 2 Features
- **Department field**: Add department to User model
- **Bulk operations**: Import/export users via CSV
- **User roles management**: Separate role management UI
- **Activity logging**: Track user actions (login history, etc.)
- **Password reset**: Self-service password reset flow
- **Email notifications**: Notify users when account is created/modified

### Advanced Features
- **Advanced search**: Full-text search with PostgreSQL
- **Cursor-based pagination**: For better performance with large datasets
- **Audit log**: Dedicated table for tracking all user changes
- **Role permissions**: Granular permissions beyond basic roles
- **Multi-tenancy**: Support for multiple organizations

## Migration Plan

### Step 1: Implementation
1. Create `app/routers/users.py` with all endpoints
2. Enhance `app/crud/user.py` with filtering methods
3. Register router in `app/api.py`
4. Add comprehensive tests

### Step 2: Testing
1. Run unit tests for all CRUD operations
2. Run integration tests for authorization
3. Test with Swagger UI
4. Manual testing with curl/Postman

### Step 3: Documentation
1. Update README with API examples
2. Ensure Swagger docs are complete
3. Add user management guide
4. Create troubleshooting section

### Step 4: Deployment
1. No database migrations needed (uses existing schema)
2. Deploy to staging environment
3. Perform smoke tests
4. Deploy to production
5. Monitor for errors

## Conclusion

This design provides a complete, secure, and scalable user management system for administrators. The APIs follow RESTful conventions, use standardized responses, implement proper authorization, and maintain a complete audit trail through soft deletes and audit fields.
