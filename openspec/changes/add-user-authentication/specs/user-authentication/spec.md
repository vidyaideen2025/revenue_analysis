# user-authentication Specification

## Purpose
Provide secure JWT-based authentication and role-based access control for the Revenue Guardian API.

## ADDED Requirements

### Requirement: JWT Authentication
The system SHALL implement JWT (JSON Web Token) based authentication for API access.

#### Scenario: User login with valid credentials
- **WHEN** a user submits valid email and password to the login endpoint
- **THEN** the system SHALL verify the credentials against the database
- **AND** the system SHALL generate a JWT access token
- **AND** the token SHALL include user ID, email, and role
- **AND** the token SHALL have a configurable expiration time
- **AND** the system SHALL return the token in standardized response format

#### Scenario: User login with invalid credentials
- **WHEN** a user submits invalid email or password
- **THEN** the system SHALL return a 401 Unauthorized response
- **AND** the system SHALL NOT reveal whether email or password was incorrect
- **AND** the response SHALL follow standardized error format

#### Scenario: Accessing protected endpoint with valid token
- **WHEN** a request includes a valid JWT token in Authorization header
- **THEN** the system SHALL verify the token signature
- **AND** the system SHALL check token expiration
- **AND** the system SHALL extract user information from token
- **AND** the system SHALL allow access to the endpoint

#### Scenario: Accessing protected endpoint without token
- **WHEN** a request to a protected endpoint has no Authorization header
- **THEN** the system SHALL return a 401 Unauthorized response
- **AND** the response SHALL indicate authentication is required

#### Scenario: Accessing protected endpoint with expired token
- **WHEN** a request includes an expired JWT token
- **THEN** the system SHALL return a 401 Unauthorized response
- **AND** the response SHALL indicate the token has expired

### Requirement: User Model
The system SHALL maintain a User model with authentication and profile information.

#### Scenario: User record structure
- **WHEN** a user record is created or retrieved
- **THEN** it SHALL include id, email, username, password_hash, full_name, and role
- **AND** it SHALL include is_active flag for account status
- **AND** it SHALL include audit fields (created_at, updated_at, created_by, updated_by, is_deleted)
- **AND** email SHALL be unique and indexed
- **AND** username SHALL be unique and indexed
- **AND** password SHALL be stored as bcrypt hash, never plain text

### Requirement: Role-Based Access Control
The system SHALL implement role-based access control with three user roles.

#### Scenario: Admin role permissions
- **WHEN** a user has ADMIN role
- **THEN** they SHALL have full system access
- **AND** they SHALL be able to create, read, update, and delete users
- **AND** they SHALL be able to access all API endpoints

#### Scenario: Operations role permissions
- **WHEN** a user has OPERATIONS role
- **THEN** they SHALL be able to upload data and trigger reconciliation
- **AND** they SHALL be able to view reports
- **AND** they SHALL NOT be able to manage users

#### Scenario: CXO role permissions
- **WHEN** a user has CXO role
- **THEN** they SHALL be able to view analytics and insights
- **AND** they SHALL be able to view high-level KPIs
- **AND** they SHALL NOT be able to manage users or upload data

#### Scenario: Insufficient permissions
- **WHEN** a user attempts to access an endpoint without required role
- **THEN** the system SHALL return a 403 Forbidden response
- **AND** the response SHALL indicate required role(s)

### Requirement: Password Security
The system SHALL implement secure password handling.

#### Scenario: Password hashing on user creation
- **WHEN** a new user is created with a password
- **THEN** the system SHALL hash the password using bcrypt
- **AND** the system SHALL generate a unique salt automatically
- **AND** the system SHALL store only the hash, never the plain text password

#### Scenario: Password verification on login
- **WHEN** a user attempts to log in
- **THEN** the system SHALL hash the provided password
- **AND** the system SHALL compare it with the stored hash
- **AND** the system SHALL use constant-time comparison to prevent timing attacks

#### Scenario: Password requirements
- **WHEN** a password is provided for user creation or update
- **THEN** it SHALL be at least 8 characters long
- **AND** validation SHALL occur at the schema level

### Requirement: User Management API
The system SHALL provide API endpoints for user management.

#### Scenario: List all users (Admin only)
- **WHEN** an admin requests the user list
- **THEN** the system SHALL return all users with pagination
- **AND** the response SHALL exclude password hashes
- **AND** the response SHALL follow standardized format

#### Scenario: Create new user (Admin only)
- **WHEN** an admin creates a new user
- **THEN** the system SHALL validate email and username uniqueness
- **AND** the system SHALL hash the provided password
- **AND** the system SHALL set audit fields (created_by)
- **AND** the system SHALL return the created user without password

#### Scenario: Update user (Admin only)
- **WHEN** an admin updates a user
- **THEN** the system SHALL allow updating email, username, full_name, role, and is_active
- **AND** if password is provided, it SHALL be hashed before storage
- **AND** the system SHALL update audit fields (updated_by, updated_at)

#### Scenario: Delete user (Admin only)
- **WHEN** an admin deletes a user
- **THEN** the system SHALL perform a soft delete (set is_deleted=true)
- **AND** the system SHALL preserve the user record for audit trail
- **AND** deleted users SHALL NOT be able to log in

### Requirement: Admin User Seeding
The system SHALL provide a mechanism to seed initial admin users.

#### Scenario: Seed admin users
- **WHEN** the seed script is executed
- **THEN** it SHALL create 3 admin users if they don't exist:
  - admin@revenueguardian.com (username: admin)
  - superadmin@revenueguardian.com (username: superadmin)
  - sysadmin@revenueguardian.com (username: sysadmin)
- **AND** each SHALL have a default password
- **AND** each SHALL have ADMIN role
- **AND** the script SHALL NOT create duplicates if users already exist

### Requirement: Authentication Endpoints
The system SHALL provide authentication-related API endpoints.

#### Scenario: Login endpoint
- **WHEN** POST /api/v1/auth/login is called with email and password
- **THEN** the system SHALL authenticate the user
- **AND** return a JWT token on success
- **AND** return standardized response format

#### Scenario: Current user endpoint
- **WHEN** GET /api/v1/auth/me is called with valid token
- **THEN** the system SHALL return current user information
- **AND** exclude password hash from response
- **AND** return standardized response format

### Requirement: Public Endpoints
The system SHALL maintain public endpoints that do not require authentication.

#### Scenario: Health check endpoints
- **WHEN** health check endpoints are accessed
- **THEN** they SHALL NOT require authentication
- **AND** they SHALL return health status in standardized format

### Requirement: Error Handling
All authentication errors SHALL follow the standardized response format.

#### Scenario: Authentication error response
- **WHEN** an authentication error occurs
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate HTTP code (401, 403, etc.)
- **AND** message SHALL be descriptive
- **AND** data SHALL include relevant error details
