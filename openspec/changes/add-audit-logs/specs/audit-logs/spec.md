# audit-logs Specification

## Purpose
Provide comprehensive audit logging to track all user actions, system events, and administrative operations for compliance, security monitoring, accountability, and troubleshooting.

## ADDED Requirements

### Requirement: Audit Log Data Model
The system SHALL maintain a comprehensive audit log model that captures all significant actions and events.

#### Scenario: Audit log record structure
- **WHEN** an audit log is created
- **THEN** it SHALL include a unique ID (UUID)
- **AND** it SHALL include timestamp of when the action occurred
- **AND** it SHALL include user ID of who performed the action
- **AND** it SHALL include action type (login, create, update, delete, etc.)
- **AND** it SHALL include resource type (user, role, data, etc.)
- **AND** it SHALL include resource ID of affected resource
- **AND** it SHALL include human-readable description
- **AND** it SHALL include IP address of the client
- **AND** it SHALL include user agent information
- **AND** it SHALL include status (success, failure, error)
- **AND** it SHALL support optional metadata as JSON

#### Scenario: Immutable audit logs
- **WHEN** an audit log is created
- **THEN** it SHALL NOT be modifiable
- **AND** it SHALL NOT be deletable via API
- **AND** it SHALL preserve complete historical record

### Requirement: Authentication Event Logging
The system SHALL log all authentication-related events.

#### Scenario: Successful login
- **WHEN** a user logs in successfully
- **THEN** the system SHALL create an audit log with action_type=LOGIN
- **AND** the log SHALL include user ID
- **AND** the log SHALL include IP address
- **AND** the log SHALL include user agent
- **AND** the log SHALL have status=SUCCESS

#### Scenario: Failed login attempt
- **WHEN** a user login fails
- **THEN** the system SHALL create an audit log with action_type=LOGIN_FAILED
- **AND** the log SHALL include attempted email/username
- **AND** the log SHALL include IP address
- **AND** the log SHALL have status=FAILURE

#### Scenario: Logout event
- **WHEN** a user logs out
- **THEN** the system SHALL create an audit log with action_type=LOGOUT
- **AND** the log SHALL include user ID
- **AND** the log SHALL include timestamp

#### Scenario: Password change
- **WHEN** a user changes their password
- **THEN** the system SHALL create an audit log with action_type=PASSWORD_CHANGE
- **AND** the log SHALL NOT include the actual password
- **AND** the log SHALL mark as sensitive action

### Requirement: User Management Event Logging
The system SHALL log all user management operations.

#### Scenario: User creation
- **WHEN** an admin creates a new user
- **THEN** the system SHALL create an audit log with action_type=USER_CREATE
- **AND** the log SHALL include admin user ID as performer
- **AND** the log SHALL include new user ID as resource_id
- **AND** the log SHALL include user details in metadata

#### Scenario: User update
- **WHEN** an admin updates a user
- **THEN** the system SHALL create an audit log with action_type=USER_UPDATE
- **AND** the log SHALL include old and new values in metadata
- **AND** the log SHALL include which fields were changed

#### Scenario: User activation
- **WHEN** an admin activates a user
- **THEN** the system SHALL create an audit log with action_type=USER_ACTIVATE
- **AND** the log SHALL include target user ID

#### Scenario: User deactivation
- **WHEN** an admin deactivates a user
- **THEN** the system SHALL create an audit log with action_type=USER_DEACTIVATE
- **AND** the log SHALL include target user ID

#### Scenario: User deletion
- **WHEN** an admin deletes a user
- **THEN** the system SHALL create an audit log with action_type=USER_DELETE
- **AND** the log SHALL include target user ID
- **AND** the log SHALL preserve user information in metadata

### Requirement: List Audit Logs API
The system SHALL provide an API endpoint to list audit logs with filtering and pagination.

#### Scenario: List all audit logs
- **WHEN** an admin requests GET /api/v1/audit-logs/
- **THEN** the system SHALL return paginated audit logs
- **AND** the response SHALL include total count
- **AND** the response SHALL exclude sensitive data
- **AND** the response SHALL follow standardized format

#### Scenario: Filter by date range
- **WHEN** an admin provides date_from and date_to parameters
- **THEN** the system SHALL return only logs within that range
- **AND** the system SHALL use timestamp field for filtering

#### Scenario: Filter by user
- **WHEN** an admin provides user_id parameter
- **THEN** the system SHALL return only logs for that user
- **AND** the system SHALL include user information in response

#### Scenario: Filter by action type
- **WHEN** an admin provides action_type parameter
- **THEN** the system SHALL return only logs of that action type

#### Scenario: Filter by resource type
- **WHEN** an admin provides resource_type parameter
- **THEN** the system SHALL return only logs affecting that resource type

#### Scenario: Filter by status
- **WHEN** an admin provides status parameter
- **THEN** the system SHALL return only logs with that status (success/failure/error)

#### Scenario: Search in description
- **WHEN** an admin provides search parameter
- **THEN** the system SHALL search in description field
- **AND** the search SHALL be case-insensitive

#### Scenario: Pagination
- **WHEN** an admin provides skip and limit parameters
- **THEN** the system SHALL return the specified page of results
- **AND** the system SHALL order by timestamp DESC by default

#### Scenario: Unauthorized access
- **WHEN** a non-admin user attempts to list audit logs
- **THEN** the system SHALL return 403 Forbidden
- **AND** the response SHALL indicate ADMIN role is required

### Requirement: Get Audit Log by ID API
The system SHALL provide an API endpoint to retrieve specific audit log details.

#### Scenario: Get existing audit log
- **WHEN** an admin requests GET /api/v1/audit-logs/{id}
- **THEN** the system SHALL return the audit log details
- **AND** the response SHALL include all fields including metadata
- **AND** the response SHALL include user information

#### Scenario: Get non-existent audit log
- **WHEN** an admin requests an audit log that doesn't exist
- **THEN** the system SHALL return 404 Not Found

### Requirement: Export Audit Logs API
The system SHALL provide an API endpoint to export audit logs.

#### Scenario: Export to CSV
- **WHEN** an admin requests export with format=csv
- **THEN** the system SHALL return a CSV file
- **AND** the file SHALL include all relevant fields
- **AND** the file SHALL apply the same filters as list endpoint
- **AND** the response SHALL have proper download headers

#### Scenario: Export to JSON
- **WHEN** an admin requests export with format=json
- **THEN** the system SHALL return a JSON file
- **AND** the file SHALL include all audit logs matching filters
- **AND** the response SHALL have proper download headers

#### Scenario: Export with filters
- **WHEN** an admin requests export with filters
- **THEN** the system SHALL apply the same filters as list endpoint
- **AND** the system SHALL export only matching records

#### Scenario: Large export limit
- **WHEN** an admin requests export of very large dataset
- **THEN** the system SHALL limit maximum export size
- **AND** the system SHALL return error if limit exceeded
- **AND** the system SHALL suggest applying filters

### Requirement: Automatic Logging
The system SHALL automatically log significant actions without explicit calls.

#### Scenario: Middleware logging
- **WHEN** a significant HTTP request is made (POST, PUT, PATCH, DELETE)
- **THEN** the middleware SHALL automatically create an audit log
- **AND** the log SHALL include request method and path
- **AND** the log SHALL include user from authentication
- **AND** the log SHALL include IP address and user agent

#### Scenario: Skip health checks
- **WHEN** a health check endpoint is called
- **THEN** the system SHALL NOT create an audit log
- **AND** the system SHALL NOT log static file requests

### Requirement: IP Address and User Agent Capture
The system SHALL capture client information for all audit logs.

#### Scenario: Capture IP address
- **WHEN** creating an audit log
- **THEN** the system SHALL extract IP address from request
- **AND** the system SHALL handle proxy headers (X-Forwarded-For)
- **AND** the system SHALL support both IPv4 and IPv6

#### Scenario: Capture user agent
- **WHEN** creating an audit log
- **THEN** the system SHALL extract user agent from request headers
- **AND** the system SHALL store complete user agent string

### Requirement: Metadata Capture
The system SHALL capture relevant context in metadata field.

#### Scenario: Capture old and new values
- **WHEN** an update action is logged
- **THEN** the metadata SHALL include old values
- **AND** the metadata SHALL include new values
- **AND** the metadata SHALL include list of changed fields

#### Scenario: Capture additional context
- **WHEN** creating an audit log
- **THEN** the metadata MAY include additional relevant context
- **AND** the metadata SHALL be stored as JSON
- **AND** the metadata SHALL NOT include sensitive data (passwords, tokens)

### Requirement: Error Handling
Audit logging SHALL NOT fail requests if logging fails.

#### Scenario: Logging failure
- **WHEN** audit log creation fails
- **THEN** the system SHALL log the error separately
- **AND** the system SHALL NOT fail the original request
- **AND** the system SHALL continue processing

### Requirement: Performance
Audit logging SHALL NOT significantly impact request performance.

#### Scenario: Async logging
- **WHEN** creating an audit log
- **THEN** the system SHALL use async operations
- **AND** the system SHALL NOT block the request

#### Scenario: Indexed queries
- **WHEN** querying audit logs
- **THEN** the system SHALL use database indexes
- **AND** queries SHALL perform efficiently with large datasets

### Requirement: Authorization
All audit log endpoints SHALL require admin authorization.

#### Scenario: Admin access
- **WHEN** a user with ADMIN role accesses audit log endpoints
- **THEN** the system SHALL allow the request

#### Scenario: Non-admin access denied
- **WHEN** a user without ADMIN role attempts to access audit logs
- **THEN** the system SHALL return 403 Forbidden

#### Scenario: Unauthenticated access denied
- **WHEN** an unauthenticated request is made to audit log endpoints
- **THEN** the system SHALL return 401 Unauthorized

### Requirement: Response Format
All audit log endpoints SHALL use standardized response format.

#### Scenario: Success response
- **WHEN** an audit log operation succeeds
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate HTTP code
- **AND** message SHALL be descriptive

#### Scenario: Error response
- **WHEN** an audit log operation fails
- **THEN** the response SHALL have structure {status, message, data}
- **AND** status SHALL be appropriate error code
- **AND** data SHALL include error details
