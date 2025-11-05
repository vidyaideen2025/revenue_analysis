# user-management Specification

## Purpose
TBD - created by archiving change add-user-management-apis. Update Purpose after archive.
## Requirements
### Requirement: List Users API
The system SHALL provide an API endpoint to list all users with pagination, search, and filtering capabilities.

#### Scenario: List all users with pagination
- **WHEN** an admin requests GET /api/v1/users/ with skip=0 and limit=20
- **THEN** the system SHALL return up to 20 users
- **AND** the response SHALL include total count
- **AND** the response SHALL exclude soft-deleted users
- **AND** the response SHALL exclude password hashes
- **AND** the response SHALL follow standardized format

#### Scenario: Search users by text
- **WHEN** an admin provides a search parameter
- **THEN** the system SHALL search across email, username, and full_name fields
- **AND** the search SHALL be case-insensitive
- **AND** the system SHALL return matching users only

#### Scenario: Filter users by role
- **WHEN** an admin provides a role filter (1, 2, or 3)
- **THEN** the system SHALL return only users with that role
- **AND** the system SHALL combine with other filters using AND logic

#### Scenario: Filter users by active status
- **WHEN** an admin provides is_active filter
- **THEN** the system SHALL return only users matching that status
- **AND** the system SHALL combine with other filters using AND logic

#### Scenario: Unauthorized access to list users
- **WHEN** a non-admin user attempts to list users
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate ADMIN role is required

### Requirement: Get User by ID API
The system SHALL provide an API endpoint to retrieve a specific user's details by UUID with role-based access control.

#### Scenario: Admin gets any user
- **WHEN** an admin requests GET /api/v1/users/{id} with valid UUID
- **THEN** the system SHALL return the user's details
- **AND** the response SHALL exclude password hash
- **AND** the response SHALL include all user fields
- **AND** the response SHALL follow standardized format

#### Scenario: User gets their own profile
- **WHEN** a non-admin user requests GET /api/v1/users/{id} where id matches their own user ID
- **THEN** the system SHALL return their own user details
- **AND** the response SHALL exclude password hash
- **AND** the response SHALL include all user fields

#### Scenario: User attempts to get another user's profile
- **WHEN** a non-admin user requests GET /api/v1/users/{id} where id does NOT match their own user ID
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate they can only view their own profile

#### Scenario: Get non-existent user
- **WHEN** a user requests a user that doesn't exist
- **THEN** the system SHALL return 404 Not Found
- **AND** the response SHALL include helpful error message

#### Scenario: Get soft-deleted user
- **WHEN** a user requests a soft-deleted user
- **THEN** the system SHALL return 404 Not Found
- **AND** the response SHALL indicate user not found

### Requirement: Create User API
The system SHALL provide an API endpoint to create new user accounts.

#### Scenario: Create user with valid data
- **WHEN** an admin submits POST /api/v1/users/ with valid user data
- **THEN** the system SHALL create a new user
- **AND** the system SHALL hash the password with bcrypt
- **AND** the system SHALL set created_by to current admin's UUID
- **AND** the system SHALL return 201 Created
- **AND** the response SHALL include the created user without password

#### Scenario: Create user with duplicate email
- **WHEN** an admin attempts to create a user with existing email
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate email already exists
- **AND** the system SHALL NOT create the user

#### Scenario: Create user with duplicate username
- **WHEN** an admin attempts to create a user with existing username
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate username already exists
- **AND** the system SHALL NOT create the user

#### Scenario: Create user with invalid password
- **WHEN** an admin submits a password shorter than 8 characters
- **THEN** the system SHALL return 422 Unprocessable Entity
- **AND** the response SHALL indicate password requirements
- **AND** the system SHALL NOT create the user

#### Scenario: Create user with invalid role
- **WHEN** an admin submits an invalid role value
- **THEN** the system SHALL return 422 Unprocessable Entity
- **AND** the response SHALL indicate valid role values (1, 2, 3)

### Requirement: Update User API
The system SHALL provide an API endpoint to update existing user information.

#### Scenario: Update user with valid data
- **WHEN** an admin submits PATCH /api/v1/users/{id} with valid update data
- **THEN** the system SHALL update only the provided fields
- **AND** the system SHALL set updated_by to current admin's UUID
- **AND** the system SHALL update updated_at timestamp
- **AND** the response SHALL include the updated user

#### Scenario: Update user password
- **WHEN** an admin includes password in update data
- **THEN** the system SHALL hash the new password with bcrypt
- **AND** the system SHALL replace the old password hash
- **AND** the response SHALL NOT include the password

#### Scenario: Update user email to duplicate
- **WHEN** an admin attempts to change email to one that exists
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate email already exists
- **AND** the system SHALL NOT update the user

#### Scenario: Update user username to duplicate
- **WHEN** an admin attempts to change username to one that exists
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate username already exists
- **AND** the system SHALL NOT update the user

#### Scenario: Update non-existent user
- **WHEN** an admin attempts to update a user that doesn't exist
- **THEN** the system SHALL return 404 Not Found
- **AND** the response SHALL include helpful error message

#### Scenario: Partial update
- **WHEN** an admin provides only some fields to update
- **THEN** the system SHALL update only those fields
- **AND** the system SHALL preserve other fields unchanged

### Requirement: Update User Status API
The system SHALL provide an API endpoint to update user account status (activate or deactivate).

#### Scenario: Activate inactive user
- **WHEN** an admin requests PUT /api/v1/users/{id}/status with is_active=true
- **THEN** the system SHALL set is_active to true
- **AND** the system SHALL set updated_by to current admin's UUID
- **AND** the system SHALL update updated_at timestamp
- **AND** the response SHALL confirm activation

#### Scenario: Deactivate active user
- **WHEN** an admin requests PUT /api/v1/users/{id}/status with is_active=false
- **THEN** the system SHALL set is_active to false
- **AND** the system SHALL set updated_by to current admin's UUID
- **AND** the system SHALL update updated_at timestamp
- **AND** the response SHALL confirm deactivation

#### Scenario: Self-deactivation prevention
- **WHEN** an admin attempts to set their own is_active to false
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate self-deactivation is not allowed
- **AND** the system SHALL NOT deactivate the account

#### Scenario: Update status of non-existent user
- **WHEN** an admin attempts to update status of a user that doesn't exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Update status of soft-deleted user
- **WHEN** an admin attempts to update status of a soft-deleted user
- **THEN** the system SHALL return 404 Not Found or 400 Bad Request
- **AND** the response SHALL indicate user cannot be updated

#### Scenario: Deactivated user cannot login
- **WHEN** a deactivated user attempts to log in
- **THEN** the authentication SHALL fail
- **AND** the system SHALL return 401 Unauthorized

### Requirement: Soft Delete User API
The system SHALL provide an API endpoint to soft-delete user accounts.

#### Scenario: Soft delete active user
- **WHEN** an admin requests DELETE /api/v1/users/{id}
- **THEN** the system SHALL set is_deleted to true
- **AND** the system SHALL set is_active to false
- **AND** the system SHALL set updated_by to current admin's UUID
- **AND** the system SHALL preserve all user data
- **AND** the response SHALL confirm deletion

#### Scenario: Self-deletion prevention
- **WHEN** an admin attempts to delete their own account
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate self-deletion is not allowed
- **AND** the system SHALL NOT delete the account

#### Scenario: Delete already deleted user
- **WHEN** an admin attempts to delete an already deleted user
- **THEN** the system SHALL return 400 Bad Request
- **AND** the response SHALL indicate user is already deleted

#### Scenario: Delete non-existent user
- **WHEN** an admin attempts to delete a user that doesn't exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Deleted user excluded from queries
- **WHEN** listing users or searching
- **THEN** soft-deleted users SHALL NOT appear in results
- **AND** the system SHALL filter by is_deleted=false

#### Scenario: Deleted user cannot login
- **WHEN** a deleted user attempts to log in
- **THEN** the authentication SHALL fail
- **AND** the system SHALL return 401 Unauthorized

#### Scenario: Audit trail preservation
- **WHEN** a user is soft-deleted
- **THEN** all user data SHALL remain in the database
- **AND** created_at, updated_at, created_by, updated_by SHALL be preserved
- **AND** the deletion SHALL be auditable

### Requirement: Authorization for User Management
All user management endpoints SHALL require ADMIN role.

#### Scenario: Admin access granted
- **WHEN** a user with ADMIN role accesses any user management endpoint
- **THEN** the system SHALL allow the request
- **AND** the system SHALL process the operation

#### Scenario: Operations role denied
- **WHEN** a user with OPERATIONS role attempts to access user management
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate ADMIN role is required

#### Scenario: CXO role denied
- **WHEN** a user with CXO role attempts to access user management
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate ADMIN role is required

#### Scenario: Unauthenticated access denied
- **WHEN** a request has no valid JWT token
- **THEN** the system SHALL return 401 Unauthorized
- **AND** the response SHALL indicate authentication is required

### Requirement: Response Format Consistency
All user management endpoints SHALL use standardized response format.

#### Scenario: Success response format
- **WHEN** any user management operation succeeds
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate HTTP code (200, 201, etc.)
- **AND** message SHALL be descriptive
- **AND** data SHALL contain relevant information

#### Scenario: Error response format
- **WHEN** any user management operation fails
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate error code (400, 403, 404, etc.)
- **AND** message SHALL be descriptive
- **AND** data SHALL include error details

#### Scenario: Password exclusion
- **WHEN** any endpoint returns user data
- **THEN** the response SHALL NOT include password_hash
- **AND** the response SHALL include all other user fields

### Requirement: Audit Trail
All user management operations SHALL maintain audit trail.

#### Scenario: Track creator on user creation
- **WHEN** an admin creates a new user
- **THEN** the system SHALL set created_by to the admin's UUID
- **AND** the system SHALL set created_at to current timestamp

#### Scenario: Track updater on modifications
- **WHEN** an admin updates, activates, deactivates, or deletes a user
- **THEN** the system SHALL set updated_by to the admin's UUID
- **AND** the system SHALL update updated_at to current timestamp

#### Scenario: Preserve audit history
- **WHEN** a user is soft-deleted
- **THEN** all audit fields SHALL be preserved
- **AND** the complete history SHALL remain accessible for compliance

