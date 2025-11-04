# Implementation Tasks

## 1. User Model and Database

- [ ] 1.1 Create User model with fields (id, email, username, password_hash, full_name, role, is_active)
- [ ] 1.2 Add UserRole enum (ADMIN, OPERATIONS, CXO)
- [ ] 1.3 Register User model in `app/models/registry.py`
- [ ] 1.4 Generate Alembic migration for users table
- [ ] 1.5 Apply migration to create users table

## 2. Authentication Configuration

- [ ] 2.1 Add JWT settings to `app/core/config.py` (SECRET_KEY, ALGORITHM, TOKEN_EXPIRE_MINUTES)
- [ ] 2.2 Update `.env.example` with JWT configuration
- [ ] 2.3 Add python-jose and passlib to dependencies in `pyproject.toml`
- [ ] 2.4 Install new dependencies with `uv pip install`

## 3. Security Utilities

- [ ] 3.1 Implement password hashing functions in `app/core/security.py`
- [ ] 3.2 Implement JWT token creation function
- [ ] 3.3 Implement JWT token verification function
- [ ] 3.4 Add token expiration handling

## 4. User Schemas

- [ ] 4.1 Create UserBase schema with common fields
- [ ] 4.2 Create UserCreate schema for registration
- [ ] 4.3 Create UserUpdate schema for updates
- [ ] 4.4 Create UserInDB schema with password_hash
- [ ] 4.5 Create User response schema (without password)
- [ ] 4.6 Create Token schema for JWT response
- [ ] 4.7 Create TokenData schema for decoded token
- [ ] 4.8 Create LoginRequest schema

## 5. User CRUD Operations

- [ ] 5.1 Create UserRepository in `app/crud/user.py`
- [ ] 5.2 Implement get_by_id method
- [ ] 5.3 Implement get_by_email method
- [ ] 5.4 Implement get_by_username method
- [ ] 5.5 Implement get_all method with pagination
- [ ] 5.6 Implement create method with password hashing
- [ ] 5.7 Implement update method
- [ ] 5.8 Implement delete method (soft delete)
- [ ] 5.9 Implement email_exists and username_exists checks

## 6. Authentication Service

- [ ] 6.1 Create AuthService in `app/services/auth.py`
- [ ] 6.2 Implement authenticate_user method (verify email + password)
- [ ] 6.3 Implement create_access_token method
- [ ] 6.4 Implement verify_token method
- [ ] 6.5 Implement refresh_token method
- [ ] 6.6 Add login attempt tracking (optional)

## 7. Authentication Dependencies

- [ ] 7.1 Create `app/dependencies/auth.py`
- [ ] 7.2 Implement OAuth2PasswordBearer scheme
- [ ] 7.3 Implement get_current_user dependency
- [ ] 7.4 Implement get_current_active_user dependency
- [ ] 7.5 Implement require_role dependency factory
- [ ] 7.6 Create convenience dependencies (require_admin, require_operations, require_cxo)

## 8. Authentication Endpoints

- [ ] 8.1 Create `app/routers/auth.py`
- [ ] 8.2 Implement POST /login endpoint (OAuth2 password flow)
- [ ] 8.3 Implement POST /refresh endpoint for token refresh
- [ ] 8.4 Implement GET /me endpoint for current user info
- [ ] 8.5 Add proper error handling for invalid credentials
- [ ] 8.6 Return standardized responses

## 9. User Management Endpoints

- [ ] 9.1 Create `app/routers/users.py`
- [ ] 9.2 Implement GET /users/ (list users - Admin only)
- [ ] 9.3 Implement GET /users/{user_id} (get user - Admin only)
- [ ] 9.4 Implement POST /users/ (create user - Admin only)
- [ ] 9.5 Implement PATCH /users/{user_id} (update user - Admin only)
- [ ] 9.6 Implement DELETE /users/{user_id} (delete user - Admin only)
- [ ] 9.7 Add validation for duplicate email/username
- [ ] 9.8 Use standardized APIResponse

## 10. Register Routes

- [ ] 10.1 Import auth and users routers in `app/api.py`
- [ ] 10.2 Register auth router with /auth prefix
- [ ] 10.3 Register users router with /users prefix

## 11. Admin User Seeding

- [ ] 11.1 Create `scripts/` directory
- [ ] 11.2 Create `scripts/seed_admin_users.py`
- [ ] 11.3 Implement function to create 3 admin users:
  - [ ] Admin 1: admin@revenueguardian.com / Admin@123
  - [ ] Admin 2: superadmin@revenueguardian.com / Super@123
  - [ ] Admin 3: sysadmin@revenueguardian.com / Sys@123
- [ ] 11.4 Add check to prevent duplicate seeding
- [ ] 11.5 Add script execution instructions to README

## 12. Update Health Endpoints

- [ ] 12.1 Keep health endpoints public (no authentication required)
- [ ] 12.2 Document which endpoints require authentication

## 13. Testing

- [ ] 13.1 Create test fixtures for authenticated users
- [ ] 13.2 Write tests for login endpoint
- [ ] 13.3 Write tests for token verification
- [ ] 13.4 Write tests for protected endpoints
- [ ] 13.5 Write tests for role-based access control
- [ ] 13.6 Write tests for user CRUD operations
- [ ] 13.7 Test password hashing and verification
- [ ] 13.8 Test token expiration

## 14. Documentation

- [ ] 14.1 Update README with authentication setup
- [ ] 14.2 Document how to seed admin users
- [ ] 14.3 Document authentication flow
- [ ] 14.4 Add examples of protected endpoints
- [ ] 14.5 Document role-based access control
- [ ] 14.6 Update API documentation with authentication
