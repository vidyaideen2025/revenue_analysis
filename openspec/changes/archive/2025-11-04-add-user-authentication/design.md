# Design Document: User Authentication System

## Overview

Implement a secure JWT-based authentication system with role-based access control (RBAC) for the Revenue Guardian application.

## Architecture

### Authentication Flow

```
1. User Login
   ↓
2. Verify Credentials (email + password)
   ↓
3. Generate JWT Token
   ↓
4. Return Token to Client
   ↓
5. Client Stores Token
   ↓
6. Client Sends Token in Authorization Header
   ↓
7. Server Verifies Token
   ↓
8. Extract User Info from Token
   ↓
9. Check User Permissions
   ↓
10. Allow/Deny Access
```

### Components

#### 1. User Model
```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    
    id: int (primary key)
    email: str (unique, indexed)
    username: str (unique, indexed)
    password_hash: str
    full_name: str
    role: UserRole (enum: ADMIN, OPERATIONS, CXO)
    is_active: bool (default: True)
    
    # From TimestampMixin:
    # created_at, updated_at, created_by, updated_by, is_deleted
```

#### 2. UserRole Enum
```python
class UserRole(str, Enum):
    ADMIN = "admin"          # Full system access
    OPERATIONS = "operations" # Data upload, reconciliation
    CXO = "cxo"              # Analytics, insights
```

#### 3. JWT Token Structure
```json
{
  "sub": "123",           // User ID
  "email": "user@example.com",
  "role": "admin",
  "exp": 1699999999       // Expiration timestamp
}
```

#### 4. API Endpoints

**Authentication Endpoints** (`/api/v1/auth/`)
- `POST /login` - User login (returns JWT token)
- `POST /refresh` - Refresh access token
- `GET /me` - Get current user info

**User Management Endpoints** (`/api/v1/users/`)
- `GET /` - List all users (Admin only)
- `GET /{user_id}` - Get user by ID (Admin only)
- `POST /` - Create new user (Admin only)
- `PATCH /{user_id}` - Update user (Admin only)
- `DELETE /{user_id}` - Delete user (Admin only)

## Technical Decisions

### 1. JWT vs Session-Based Authentication

**Decision**: Use JWT (JSON Web Tokens)

**Rationale**:
- Stateless authentication (no server-side session storage)
- Scalable across multiple servers
- Works well with microservices architecture
- Client can verify token expiration
- Suitable for API-first applications

**Trade-offs**:
- Cannot revoke tokens before expiration (mitigated by short expiration times)
- Token size larger than session IDs
- Need secure storage on client side

### 2. Password Hashing Algorithm

**Decision**: Use bcrypt via passlib

**Rationale**:
- Industry standard for password hashing
- Built-in salt generation
- Adaptive (can increase rounds as hardware improves)
- Resistant to rainbow table attacks

**Configuration**:
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
```

### 3. Token Expiration

**Decision**: 30 minutes for access tokens

**Rationale**:
- Balance between security and user experience
- Short enough to limit exposure if token is compromised
- Long enough to avoid frequent re-authentication
- Can be refreshed without re-entering credentials

### 4. Role-Based Access Control

**Decision**: Enum-based roles with dependency injection

**Rationale**:
- Simple and maintainable
- Type-safe with Python enums
- Easy to extend with new roles
- FastAPI dependency injection for route protection

**Implementation**:
```python
@router.get("/admin-only")
async def admin_endpoint(
    current_user: User = Depends(require_admin)
):
    # Only admins can access
    pass
```

### 5. Password Requirements

**Decision**: Minimum 8 characters, validated by Pydantic

**Rationale**:
- Balance between security and usability
- Can be extended with complexity requirements later
- Validated at schema level

### 6. Soft Delete for Users

**Decision**: Use `is_deleted` flag instead of hard delete

**Rationale**:
- Preserve audit trail
- Can restore users if needed
- Maintain referential integrity
- Required for compliance

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    created_by INTEGER,
    updated_by INTEGER,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active);
```

## Security Considerations

### 1. Password Storage
- ✅ Never store plain text passwords
- ✅ Use bcrypt with automatic salt generation
- ✅ Hash on server side only
- ✅ Validate password strength

### 2. JWT Security
- ✅ Use strong SECRET_KEY (min 32 characters)
- ✅ Store SECRET_KEY in environment variables
- ✅ Set appropriate expiration times
- ✅ Use HTTPS in production
- ✅ Include token type in response

### 3. API Security
- ✅ Rate limiting on login endpoint (future)
- ✅ CORS configuration
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (FastAPI automatic escaping)

### 4. User Management
- ✅ Only admins can create/modify users
- ✅ Users cannot escalate their own privileges
- ✅ Soft delete preserves audit trail
- ✅ Email and username uniqueness enforced

## Admin User Seeding

### Default Admin Users

Three admin users will be created during initial setup:

1. **Primary Admin**
   - Email: `admin@revenueguardian.com`
   - Username: `admin`
   - Password: `Admin@123`
   - Role: ADMIN

2. **Super Admin**
   - Email: `superadmin@revenueguardian.com`
   - Username: `superadmin`
   - Password: `Super@123`
   - Role: ADMIN

3. **System Admin**
   - Email: `sysadmin@revenueguardian.com`
   - Username: `sysadmin`
   - Password: `Sys@123`
   - Role: ADMIN

### Seeding Script

```python
# scripts/seed_admin_users.py
async def seed_admin_users():
    """Create initial admin users if they don't exist."""
    admin_users = [
        {
            "email": "admin@revenueguardian.com",
            "username": "admin",
            "password": "Admin@123",
            "full_name": "Primary Administrator",
            "role": UserRole.ADMIN
        },
        # ... other admins
    ]
    
    for user_data in admin_users:
        existing = await user_repo.get_by_email(db, user_data["email"])
        if not existing:
            await user_repo.create(db, UserCreate(**user_data))
```

**Usage**:
```bash
python scripts/seed_admin_users.py
```

## API Examples

### Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@revenueguardian.com&password=Admin@123"

# Response:
{
  "status": 200,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Response:
{
  "status": 200,
  "message": "Users retrieved successfully",
  "data": [
    {
      "id": 1,
      "email": "admin@revenueguardian.com",
      "username": "admin",
      "full_name": "Primary Administrator",
      "role": "admin",
      "is_active": true
    }
  ]
}
```

### Unauthorized Access
```bash
curl -X GET "http://localhost:8000/api/v1/users/"

# Response:
{
  "status": 401,
  "message": "Not authenticated",
  "data": {
    "detail": "Not authenticated"
  }
}
```

## Migration Plan

### Phase 1: Setup (No Breaking Changes)
1. Add dependencies (python-jose, passlib)
2. Update configuration with JWT settings
3. Create User model and migration
4. Apply migration

### Phase 2: Implementation (No Breaking Changes)
1. Implement security utilities
2. Create schemas and CRUD
3. Implement authentication service
4. Create authentication dependencies

### Phase 3: Endpoints (No Breaking Changes)
1. Add auth endpoints (/login, /me)
2. Add user management endpoints
3. Keep existing endpoints public

### Phase 4: Protection (Breaking Change)
1. Add authentication to specific endpoints
2. Update documentation
3. Notify API consumers

### Phase 5: Seeding
1. Run seed script to create admin users
2. Test login with admin credentials
3. Verify role-based access control

## Testing Strategy

### Unit Tests
- Password hashing and verification
- JWT token creation and validation
- User CRUD operations
- Role validation

### Integration Tests
- Login flow
- Token-based authentication
- Protected endpoint access
- Role-based authorization
- User management operations

### Security Tests
- Invalid credentials
- Expired tokens
- Insufficient permissions
- SQL injection attempts
- XSS attempts

## Alternatives Considered

### 1. OAuth2 with External Provider
**Rejected**: Adds complexity, requires external dependency, not needed for internal system

### 2. Session-Based Authentication
**Rejected**: Not stateless, harder to scale, not suitable for API-first architecture

### 3. API Keys
**Rejected**: Less secure, no user context, harder to manage

### 4. Basic Authentication
**Rejected**: Credentials sent with every request, not secure without HTTPS

## Open Questions

1. **Token Refresh Strategy**: Should we implement refresh tokens or just re-login?
   - **Decision**: Start with re-login, add refresh tokens if needed

2. **Password Reset**: Should we implement password reset flow?
   - **Decision**: Defer to future iteration, admins can reset via user management

3. **Multi-Factor Authentication**: Should we add MFA?
   - **Decision**: Defer to future iteration based on security requirements

4. **Login Attempt Limiting**: Should we limit failed login attempts?
   - **Decision**: Defer to future iteration, can add rate limiting later

## Success Criteria

- ✅ Users can log in with email and password
- ✅ JWT tokens are generated and validated correctly
- ✅ Protected endpoints require valid tokens
- ✅ Role-based access control works as expected
- ✅ Three admin users are seeded successfully
- ✅ Passwords are securely hashed
- ✅ All tests pass
- ✅ Documentation is complete
