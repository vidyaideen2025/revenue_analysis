# Implementation Tasks: Add User Management APIs

## 1. User Router Setup (3 tasks)

### Task 1.1: Create user router file
- [ ] Create `app/routers/users.py`
- [ ] Import required dependencies (FastAPI, SQLAlchemy, auth dependencies)
- [ ] Create APIRouter with tags=["Users"]
- [ ] Add docstring explaining admin-only access

### Task 1.2: Register user router
- [ ] Open `app/api.py`
- [ ] Import users router
- [ ] Add router with prefix="/users" and ADMIN role requirement
- [ ] Add comment indicating admin-only endpoints

### Task 1.3: Add router dependencies
- [ ] Import `require_admin` from auth dependencies
- [ ] Apply to all user management endpoints
- [ ] Ensure standardized error responses for unauthorized access

## 2. List Users Endpoint (5 tasks)

### Task 2.1: Create list users endpoint
- [ ] Create `GET /api/v1/users/` endpoint
- [ ] Add pagination parameters (skip: int = 0, limit: int = 100)
- [ ] Add search parameter (search: str | None = None)
- [ ] Add role filter parameter (role: UserRole | None = None)
- [ ] Add status filter parameter (is_active: bool | None = None)

### Task 2.2: Implement search functionality
- [ ] Update `user_repo.get_all()` to support search
- [ ] Search across email, username, full_name fields
- [ ] Use case-insensitive LIKE/ILIKE queries
- [ ] Return filtered results

### Task 2.3: Implement filtering
- [ ] Add role filtering to repository method
- [ ] Add is_active filtering to repository method
- [ ] Combine filters with AND logic
- [ ] Exclude soft-deleted users (is_deleted=false)

### Task 2.4: Add response formatting
- [ ] Convert User models to User schemas
- [ ] Exclude password_hash from response
- [ ] Include total count in response metadata
- [ ] Return standardized APIResponse.success()

### Task 2.5: Add documentation
- [ ] Add comprehensive docstring with examples
- [ ] Document query parameters
- [ ] Add response schema examples
- [ ] Include curl example in docstring

## 3. Get User by ID Endpoint (4 tasks)

### Task 3.1: Create get user endpoint
- [ ] Create `GET /api/v1/users/{id}` endpoint
- [ ] Accept UUID path parameter
- [ ] Require authentication (any authenticated user)
- [ ] Get current user from auth dependency

### Task 3.2: Add access control logic
- [ ] Check if current user is ADMIN or requesting their own profile
- [ ] If admin: allow access to any user
- [ ] If non-admin: only allow if id matches current_user.id
- [ ] Return 403 Forbidden if non-admin accessing other user's profile

### Task 3.3: Fetch and validate user
- [ ] Call `user_repo.get_by_id()`
- [ ] Return 404 if user not found
- [ ] Return 404 if user is soft-deleted
- [ ] Use APIResponse.not_found()

### Task 3.4: Format response
- [ ] Convert to User schema
- [ ] Exclude password_hash
- [ ] Return APIResponse.success()
- [ ] Add documentation with both admin and self-access examples

## 4. Create User Endpoint (6 tasks)

### Task 4.1: Create endpoint structure
- [ ] Create `POST /api/v1/users/` endpoint
- [ ] Accept UserCreate schema in request body
- [ ] Require admin authentication
- [ ] Get current user from auth dependency

### Task 4.2: Add validation checks
- [ ] Check if email already exists
- [ ] Check if username already exists
- [ ] Return 400 Bad Request if duplicate found
- [ ] Use APIResponse.bad_request()

### Task 4.3: Implement user creation
- [ ] Call `user_repo.create()` with UserCreate data
- [ ] Pass current_user.id as created_by
- [ ] Hash password automatically in repository
- [ ] Handle database errors

### Task 4.4: Add role validation
- [ ] Validate role is one of: ADMIN, OPERATIONS, CXO
- [ ] Ensure role is provided (no default in create)
- [ ] Return validation error if invalid role
- [ ] Document allowed roles

### Task 4.5: Format response
- [ ] Convert created user to User schema
- [ ] Exclude password_hash
- [ ] Return APIResponse.created() with 201 status
- [ ] Include user ID in response

### Task 4.6: Add comprehensive documentation
- [ ] Add docstring with example request
- [ ] Document all validation rules
- [ ] Add example response
- [ ] Include curl example

## 5. Update User Endpoint (7 tasks)

### Task 5.1: Create endpoint structure
- [ ] Create `PATCH /api/v1/users/{id}` endpoint
- [ ] Accept UUID path parameter
- [ ] Accept UserUpdate schema in request body
- [ ] Require admin authentication

### Task 5.2: Get existing user
- [ ] Fetch user by ID
- [ ] Return 404 if not found
- [ ] Return 404 if soft-deleted
- [ ] Use APIResponse.not_found()

### Task 5.3: Validate unique constraints
- [ ] If email is being updated, check uniqueness
- [ ] If username is being updated, check uniqueness
- [ ] Exclude current user from uniqueness check
- [ ] Return 400 if duplicate found

### Task 5.4: Handle password update
- [ ] Check if password is in update data
- [ ] Validate password meets requirements (min 8 chars)
- [ ] Hash password before storage
- [ ] Clear password from response

### Task 5.5: Update user record
- [ ] Call `user_repo.update()` with UserUpdate data
- [ ] Pass current_user.id as updated_by
- [ ] Update only provided fields (partial update)
- [ ] Handle database errors

### Task 5.6: Format response
- [ ] Convert updated user to User schema
- [ ] Exclude password_hash
- [ ] Return APIResponse.success()
- [ ] Include updated fields in response

### Task 5.7: Add documentation
- [ ] Add docstring with example
- [ ] Document updatable fields
- [ ] Add validation rules
- [ ] Include curl example

## 6. Update User Status Endpoint (6 tasks)

### Task 6.1: Create status update endpoint
- [ ] Create `PUT /api/v1/users/{id}/status` endpoint
- [ ] Accept UUID path parameter
- [ ] Accept request body with is_active boolean
- [ ] Require admin authentication
- [ ] Get current user from auth

### Task 6.2: Add self-deactivation check
- [ ] Check if user is trying to deactivate themselves (is_active=false)
- [ ] Return 400 Bad Request if self-deactivation
- [ ] Use APIResponse.bad_request()
- [ ] Add helpful error message

### Task 6.3: Validate user exists
- [ ] Fetch user by ID
- [ ] Return 404 if not found or deleted
- [ ] Prevent updating deleted users
- [ ] Use APIResponse.not_found()

### Task 6.4: Update status
- [ ] Set is_active to provided boolean value
- [ ] Pass current_user.id as updated_by
- [ ] Update updated_at timestamp
- [ ] Handle database errors

### Task 6.5: Format response
- [ ] Return appropriate message (activated/deactivated)
- [ ] Include updated user data
- [ ] Use APIResponse.success()
- [ ] Exclude password_hash

### Task 6.6: Add documentation
- [ ] Add docstring with examples for both activate and deactivate
- [ ] Document self-deactivation prevention
- [ ] Add request/response examples
- [ ] Include curl examples for both cases

## 7. Soft Delete User Endpoint (6 tasks)

### Task 7.1: Create delete endpoint
- [ ] Create `DELETE /api/v1/users/{id}` endpoint
- [ ] Accept UUID path parameter
- [ ] Require admin authentication
- [ ] Get current user from auth

### Task 7.2: Add self-deletion check
- [ ] Check if user is trying to delete themselves
- [ ] Return 400 Bad Request if self-deletion
- [ ] Use APIResponse.bad_request()
- [ ] Add helpful error message

### Task 7.3: Validate user exists
- [ ] Fetch user by ID
- [ ] Return 404 if not found
- [ ] Return 400 if already deleted
- [ ] Use appropriate APIResponse methods

### Task 7.4: Perform soft delete
- [ ] Call `user_repo.delete()` (soft delete)
- [ ] Set is_deleted = true
- [ ] Set is_active = false
- [ ] Pass current_user.id as updated_by

### Task 7.5: Format response
- [ ] Return 204 No Content or 200 with message
- [ ] Use APIResponse.success()
- [ ] Include deletion confirmation message
- [ ] Document that it's a soft delete

### Task 7.6: Add documentation
- [ ] Add docstring explaining soft delete
- [ ] Document self-deletion prevention
- [ ] Explain audit trail preservation
- [ ] Include curl example

## 8. Repository Enhancements (4 tasks)

### Task 8.1: Add search to get_all
- [ ] Update `user_repo.get_all()` signature
- [ ] Add search parameter
- [ ] Implement ILIKE search on email, username, full_name
- [ ] Return filtered results

### Task 8.2: Add filtering to get_all
- [ ] Add role filter parameter
- [ ] Add is_active filter parameter
- [ ] Combine filters with WHERE clauses
- [ ] Maintain pagination support

### Task 8.3: Add count method
- [ ] Create `user_repo.count()` method
- [ ] Support same filters as get_all
- [ ] Return total count
- [ ] Use for pagination metadata

### Task 8.4: Optimize queries
- [ ] Add appropriate indexes if needed
- [ ] Use select() for efficient queries
- [ ] Avoid N+1 query problems
- [ ] Test query performance

## 9. Response Schemas (3 tasks)

### Task 9.1: Create list response schema
- [ ] Create UserListResponse schema
- [ ] Include items: list[User]
- [ ] Include total: int
- [ ] Include pagination metadata (skip, limit)

### Task 9.2: Create user detail response
- [ ] Ensure User schema excludes password_hash
- [ ] Include all relevant fields
- [ ] Add proper field descriptions
- [ ] Use ConfigDict(from_attributes=True)

### Task 9.3: Create operation response schemas
- [ ] Create UserStatusUpdateRequest schema (is_active: bool)
- [ ] Create UserStatusUpdateResponse
- [ ] Create UserDeleteResponse
- [ ] Include success message and user info

## 10. Error Handling (4 tasks)

### Task 10.1: Add duplicate email/username handling
- [ ] Catch unique constraint violations
- [ ] Return 400 Bad Request
- [ ] Include specific field in error message
- [ ] Use APIResponse.bad_request()

### Task 10.2: Add not found handling
- [ ] Return 404 for non-existent users
- [ ] Return 404 for soft-deleted users
- [ ] Include helpful error message
- [ ] Use APIResponse.not_found()

### Task 10.3: Add authorization error handling
- [ ] Return 403 for non-admin users
- [ ] Include required role in message
- [ ] Use existing auth dependency errors
- [ ] Test with different roles

### Task 10.4: Add validation error handling
- [ ] Catch Pydantic validation errors
- [ ] Return 422 Unprocessable Entity
- [ ] Include field-specific errors
- [ ] Use existing validation handlers

## 11. Testing (7 tasks)

### Task 11.1: Test list users
- [ ] Test pagination (skip, limit)
- [ ] Test search functionality
- [ ] Test role filtering
- [ ] Test status filtering

### Task 11.2: Test get user by ID
- [ ] Test successful retrieval
- [ ] Test user not found
- [ ] Test soft-deleted user
- [ ] Test response format

### Task 11.3: Test create user
- [ ] Test successful creation
- [ ] Test duplicate email
- [ ] Test duplicate username
- [ ] Test password hashing

### Task 11.4: Test update user
- [ ] Test partial update
- [ ] Test password update
- [ ] Test duplicate email/username
- [ ] Test non-existent user

### Task 11.5: Test update status
- [ ] Test activation (is_active=true)
- [ ] Test deactivation (is_active=false)
- [ ] Test self-deactivation prevention
- [ ] Test non-existent user

### Task 11.6: Test soft delete
- [ ] Test successful deletion
- [ ] Test self-deletion prevention
- [ ] Test already deleted user
- [ ] Test audit trail preservation

### Task 11.7: Test authorization
- [ ] Test admin access (should succeed)
- [ ] Test operations role (should fail)
- [ ] Test CXO role (should fail)
- [ ] Test unauthenticated access (should fail)

## 12. Documentation (4 tasks)

### Task 12.1: Update README
- [ ] Add user management section
- [ ] Document all endpoints
- [ ] Add curl examples
- [ ] Include authentication requirements

### Task 12.2: Add API examples
- [ ] Create examples for each endpoint
- [ ] Include request/response samples
- [ ] Add error response examples
- [ ] Document query parameters

### Task 12.3: Update Swagger/ReDoc
- [ ] Ensure all endpoints appear in docs
- [ ] Add proper tags and descriptions
- [ ] Include example values
- [ ] Test interactive documentation

### Task 12.4: Create user management guide
- [ ] Document user lifecycle
- [ ] Explain soft delete vs hard delete
- [ ] Add best practices
- [ ] Include troubleshooting tips

## Summary

**Total Tasks**: 64
- Router Setup: 3 tasks
- List Users: 5 tasks
- Get User: 4 tasks (includes self-access control)
- Create User: 6 tasks
- Update User: 7 tasks
- Update Status: 6 tasks (combined activate/deactivate)
- Delete User: 6 tasks
- Repository: 4 tasks
- Schemas: 3 tasks
- Error Handling: 4 tasks
- Testing: 7 tasks
- Documentation: 4 tasks
