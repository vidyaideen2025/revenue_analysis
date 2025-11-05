# department-management Specification

## Purpose
TBD - created by archiving change add-user-management-apis. Update Purpose after archive.
## Requirements
### Requirement: Department Data Model
The system SHALL maintain a department model to organize users by organizational units.

#### Scenario: Department record structure
- **WHEN** a department is created
- **THEN** it SHALL include a unique ID (UUID)
- **AND** it SHALL include department name (e.g., "Information Technology")
- **AND** it SHALL include unique department code (e.g., "IT")
- **AND** it SHALL include description of purpose and responsibilities
- **AND** it SHALL include is_active status (boolean)
- **AND** it SHALL include timestamps (created_at, updated_at)
- **AND** it SHALL support soft delete (is_deleted flag)

#### Scenario: Department code uniqueness
- **WHEN** creating or updating a department
- **THEN** the department code SHALL be unique across all departments
- **AND** the system SHALL return 400 Bad Request if duplicate code exists
- **AND** the code SHALL be case-insensitive for uniqueness check

#### Scenario: Department name validation
- **WHEN** creating or updating a department
- **THEN** the department name SHALL be required
- **AND** the name SHALL be between 1 and 255 characters
- **AND** the name SHALL allow alphanumeric and special characters

### Requirement: List Departments API
The system SHALL provide an API endpoint to list departments with filtering and pagination.

#### Scenario: List all departments
- **WHEN** an admin requests GET /api/v1/departments/
- **THEN** the system SHALL return paginated departments
- **AND** the response SHALL include total count
- **AND** the response SHALL exclude soft-deleted departments by default
- **AND** the response SHALL order by name ASC

#### Scenario: Filter by status
- **WHEN** an admin provides is_active parameter
- **THEN** the system SHALL return only departments matching that status
- **AND** is_active=true SHALL return only active departments
- **AND** is_active=false SHALL return only inactive departments

#### Scenario: Search departments
- **WHEN** an admin provides search parameter
- **THEN** the system SHALL search in department name and code fields
- **AND** the search SHALL be case-insensitive
- **AND** the search SHALL use partial matching (LIKE/ILIKE)

#### Scenario: Pagination
- **WHEN** an admin provides skip and limit parameters
- **THEN** the system SHALL return the specified page of results
- **AND** the default limit SHALL be 100
- **AND** the system SHALL order by name ASC

#### Scenario: Unauthorized access
- **WHEN** a non-admin user attempts to list departments
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate ADMIN role is required

### Requirement: Get Department by ID API
The system SHALL provide an API endpoint to retrieve specific department details.

#### Scenario: Get existing department
- **WHEN** an admin requests GET /api/v1/departments/{id}
- **THEN** the system SHALL return the department details
- **AND** the response SHALL include all fields
- **AND** the response SHALL include user count for that department

#### Scenario: Get non-existent department
- **WHEN** an admin requests a department that doesn't exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Get soft-deleted department
- **WHEN** an admin requests a soft-deleted department
- **THEN** the system SHALL return 404 Not Found

### Requirement: Create Department API
The system SHALL provide an API endpoint to create new departments.

#### Scenario: Create valid department
- **WHEN** an admin submits POST /api/v1/departments/ with valid data
- **THEN** the system SHALL create the department
- **AND** the system SHALL return 201 Created
- **AND** the response SHALL include the created department with ID
- **AND** the department SHALL be active by default

#### Scenario: Duplicate department code
- **WHEN** an admin creates a department with existing code
- **THEN** the system SHALL return 400 Bad Request
- **AND** the error message SHALL indicate code already exists

#### Scenario: Missing required fields
- **WHEN** an admin submits without name or code
- **THEN** the system SHALL return 422 Unprocessable Entity
- **AND** the error SHALL indicate which fields are required

#### Scenario: Invalid status value
- **WHEN** an admin provides invalid is_active value
- **THEN** the system SHALL return 422 Unprocessable Entity
- **AND** the error SHALL indicate valid values are true/false

### Requirement: Update Department API
The system SHALL provide an API endpoint to update department information.

#### Scenario: Update department fields
- **WHEN** an admin submits PATCH /api/v1/departments/{id} with valid data
- **THEN** the system SHALL update only provided fields
- **AND** the system SHALL return 200 OK
- **AND** the response SHALL include updated department
- **AND** the updated_at timestamp SHALL be updated

#### Scenario: Update to duplicate code
- **WHEN** an admin updates code to an existing code
- **THEN** the system SHALL return 400 Bad Request
- **AND** the error SHALL indicate code already exists
- **AND** the department SHALL NOT be updated

#### Scenario: Update non-existent department
- **WHEN** an admin updates a department that doesn't exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Update soft-deleted department
- **WHEN** an admin attempts to update a soft-deleted department
- **THEN** the system SHALL return 404 Not Found

### Requirement: Soft Delete Department API
The system SHALL provide an API endpoint to soft delete departments.

#### Scenario: Delete department without users
- **WHEN** an admin deletes a department with no assigned users
- **THEN** the system SHALL set is_deleted=true
- **AND** the system SHALL set is_active=false
- **AND** the system SHALL return 200 OK
- **AND** the department SHALL be excluded from list endpoints

#### Scenario: Delete department with users
- **WHEN** an admin deletes a department with assigned users
- **THEN** the system SHALL return 400 Bad Request
- **AND** the error SHALL indicate department has active users
- **AND** the error SHALL include user count
- **AND** the department SHALL NOT be deleted

#### Scenario: Delete non-existent department
- **WHEN** an admin deletes a department that doesn't exist
- **THEN** the system SHALL return 404 Not Found

#### Scenario: Delete already deleted department
- **WHEN** an admin deletes an already soft-deleted department
- **THEN** the system SHALL return 400 Bad Request
- **AND** the error SHALL indicate department is already deleted

### Requirement: Department-User Relationship
The system SHALL maintain a foreign key relationship between users and departments.

#### Scenario: Assign user to department
- **WHEN** creating or updating a user with department_id
- **THEN** the system SHALL validate department exists
- **AND** the system SHALL validate department is active
- **AND** the system SHALL return 400 if department doesn't exist
- **AND** the system SHALL return 400 if department is inactive

#### Scenario: Get users by department
- **WHEN** listing users with department filter
- **THEN** the system SHALL return only users in that department
- **AND** the response SHALL include department information

#### Scenario: Department in user response
- **WHEN** retrieving user information
- **THEN** the response SHALL include department name and code
- **AND** the response SHALL include department_id as UUID
- **AND** the response SHALL handle null department gracefully

### Requirement: Active Departments for User Creation
The system SHALL provide only active departments for user assignment.

#### Scenario: List active departments for dropdown
- **WHEN** frontend requests departments for user creation
- **THEN** the system SHALL return only active departments (is_active=true)
- **AND** the system SHALL exclude soft-deleted departments
- **AND** the system SHALL order by name ASC
- **AND** the response SHALL include id, name, and code

### Requirement: Department Migration
The system SHALL migrate existing department enum values to department records.

#### Scenario: Create departments table
- **WHEN** running database migration
- **THEN** the system SHALL create departments table with all fields
- **AND** the system SHALL add indexes on code and name
- **AND** the system SHALL add unique constraint on code

#### Scenario: Seed initial departments
- **WHEN** running migration
- **THEN** the system SHALL create records for existing enum values:
  - IT (Information Technology)
  - FINANCE (Finance)
  - OPERATIONS (Operations)
  - AUDIT (Audit)
  - HR (Human Resources)
  - SALES (Sales)
- **AND** all SHALL be marked as active
- **AND** all SHALL have appropriate descriptions

#### Scenario: Migrate user department references
- **WHEN** running migration
- **THEN** the system SHALL convert user.department integer to UUID
- **AND** the system SHALL map enum values to department UUIDs
- **AND** the system SHALL preserve all user-department associations
- **AND** the system SHALL add foreign key constraint

### Requirement: Authorization
All department management endpoints SHALL require admin authorization.

#### Scenario: Admin access
- **WHEN** a user with ADMIN role accesses department endpoints
- **THEN** the system SHALL allow the request

#### Scenario: Non-admin access denied
- **WHEN** a user without ADMIN role attempts to access department endpoints
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Unauthenticated access denied
- **WHEN** an unauthenticated request is made to department endpoints
- **THEN** the system SHALL return 401 Unauthorized

### Requirement: Response Format
All department endpoints SHALL use standardized response format.

#### Scenario: Success response
- **WHEN** a department operation succeeds
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate HTTP code
- **AND** message SHALL be descriptive

#### Scenario: Error response
- **WHEN** a department operation fails
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate error code
- **AND** data SHALL include error details

