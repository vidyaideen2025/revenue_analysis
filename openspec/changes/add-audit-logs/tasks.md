# Implementation Tasks: Add Audit Logs System

## 1. Audit Log Model (4 tasks)

### Task 1.1: Create audit log model
- [ ] Create `app/models/audit_log.py`
- [ ] Define AuditLog model with all fields (id, timestamp, user_id, action_type, etc.)
- [ ] Add ActionType enum (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, ERROR_OCCURRED, EXCEPTION_RAISED, etc.)
- [ ] Add ResourceType enum (USER, ROLE, DATA_UPLOAD, SETTING, etc.)
- [ ] Add Status enum (SUCCESS, FAILURE, ERROR)
- [ ] Add ErrorSeverity enum (WARNING, ERROR, CRITICAL)
- [ ] Add error-specific fields (severity, error_type, stack_trace)

### Task 1.2: Register model for migrations
- [ ] Import AuditLog in `app/models/registry.py`
- [ ] Ensure model is discoverable by Alembic

### Task 1.3: Create database migration
- [ ] Run `alembic revision --autogenerate -m "Add audit_logs table"`
- [ ] Review generated migration
- [ ] Add indexes on timestamp, user_id, action_type, resource_type, status
- [ ] Add indexes on severity and error_type for efficient error log queries
- [ ] Run `alembic upgrade head`

### Task 1.4: Add model documentation
- [ ] Add docstrings to model and fields
- [ ] Document enum values
- [ ] Add usage examples in comments

## 2. Audit Log Schemas (3 tasks)

### Task 2.1: Create base schemas
- [ ] Create `app/schemas/audit_log.py`
- [ ] Define AuditLogBase schema
- [ ] Define AuditLogCreate schema
- [ ] Define AuditLogInDB schema
- [ ] Define AuditLog (response) schema

### Task 2.2: Create filter schemas
- [ ] Define AuditLogFilter schema with optional filters
- [ ] Add date_from and date_to fields
- [ ] Add user_id, action_type, resource_type filters
- [ ] Add status and search fields

### Task 2.3: Create list response schema
- [ ] Define AuditLogListResponse with pagination
- [ ] Include items, total, skip, limit fields
- [ ] Add proper field descriptions

## 3. Audit Log Repository (5 tasks)

### Task 3.1: Create repository class
- [ ] Create `app/crud/audit_log.py`
- [ ] Define AuditLogRepository class
- [ ] Add create method
- [ ] Add get_by_id method

### Task 3.2: Implement filtering
- [ ] Add get_all method with filters
- [ ] Support date range filtering (from/to)
- [ ] Support user_id filtering
- [ ] Support action_type filtering
- [ ] Support resource_type filtering
- [ ] Support status filtering
- [ ] Support search in description

### Task 3.3: Add pagination
- [ ] Add skip and limit parameters
- [ ] Implement offset-based pagination
- [ ] Add count method for total results

### Task 3.4: Add export functionality
- [ ] Create export method
- [ ] Support CSV format
- [ ] Support JSON format
- [ ] Apply same filters as get_all

### Task 3.5: Optimize queries
- [ ] Ensure indexes are used
- [ ] Order by timestamp DESC by default
- [ ] Test query performance with large datasets

## 4. Audit Logging Utility (4 tasks)

### Task 4.1: Create audit utility
- [ ] Create `app/utils/audit.py`
- [ ] Define log_audit function
- [ ] Accept user_id, action_type, resource_type, resource_id, description
- [ ] Accept optional metadata, ip_address, user_agent, status

### Task 4.2: Add async logging
- [ ] Make log_audit async
- [ ] Use background tasks if needed
- [ ] Handle logging errors gracefully (don't fail requests)

### Task 4.3: Add helper functions
- [ ] Create log_login function
- [ ] Create log_logout function
- [ ] Create log_user_action function
- [ ] Create log_admin_action function
- [ ] Create log_error function for exception logging
- [ ] Add automatic stack trace capture
- [ ] Add severity level determination

### Task 4.4: Add decorator for automatic logging
- [ ] Create @audit_log decorator
- [ ] Automatically capture function name and parameters
- [ ] Extract user from request context
- [ ] Log success/failure based on exception

## 5. Audit Log Endpoints (7 tasks)

### Task 5.1: Create router
- [ ] Create `app/routers/audit_logs.py`
- [ ] Create APIRouter with tags=["Audit Logs"]
- [ ] Add docstring explaining admin-only access

### Task 5.2: Implement list endpoint
- [ ] Create `GET /api/v1/audit-logs/` endpoint
- [ ] Require admin authentication
- [ ] Accept filter parameters (date_from, date_to, user_id, etc.)
- [ ] Accept pagination parameters (skip, limit)
- [ ] Return paginated results with total count

### Task 5.3: Implement get by ID endpoint
- [ ] Create `GET /api/v1/audit-logs/{id}` endpoint
- [ ] Require admin authentication
- [ ] Return 404 if not found
- [ ] Return full audit log details

### Task 5.4: Implement error logs endpoint
- [ ] Create `GET /api/v1/audit-logs/errors` endpoint
- [ ] Require admin authentication
- [ ] Filter to only show status='error' logs
- [ ] Default page size: 50 (efficient for quick loading)
- [ ] Maximum page size: 200 (prevent excessive memory usage)
- [ ] Accept severity filter (warning, error, critical)
- [ ] Accept error_type filter
- [ ] Include stack trace in response

### Task 5.5: Implement export endpoint
- [ ] Create `GET /api/v1/audit-logs/export` endpoint
- [ ] Require admin authentication
- [ ] Accept format parameter (csv, json)
- [ ] Accept same filters as list endpoint
- [ ] Return file download response

### Task 5.6: Add response formatting
- [ ] Convert models to schemas
- [ ] Use standardized APIResponse format
- [ ] Include helpful error messages

### Task 5.7: Add comprehensive documentation
- [ ] Add docstrings with examples
- [ ] Document all query parameters
- [ ] Add curl examples
- [ ] Document response formats

## 6. Global Exception Handler (3 tasks)

### Task 6.1: Create exception handler
- [ ] Add global exception handler in `main.py`
- [ ] Capture all unhandled exceptions
- [ ] Extract user from request state if available
- [ ] Call log_error utility function

### Task 6.2: Add severity determination
- [ ] Classify exceptions by severity
- [ ] CRITICAL for SystemError, MemoryError
- [ ] ERROR for general exceptions
- [ ] WARNING for validation errors

### Task 6.3: Test exception handling
- [ ] Test that exceptions are logged
- [ ] Test that stack traces are captured
- [ ] Test that requests don't fail if logging fails
- [ ] Test severity classification

## 7. Middleware Integration (3 tasks)

### Task 6.1: Create audit middleware
- [ ] Create `app/middleware/audit.py`
- [ ] Define AuditMiddleware class
- [ ] Capture request method, path, user, IP, user agent
- [ ] Log after response (include status code)

### Task 6.2: Add selective logging
- [ ] Skip health check endpoints
- [ ] Skip static files
- [ ] Log only significant actions
- [ ] Make configurable via settings

### Task 6.3: Register middleware
- [ ] Add middleware to `main.py`
- [ ] Configure middleware settings
- [ ] Test middleware integration

## 7. Integration with Existing Endpoints (8 tasks)

### Task 7.1: Add logging to auth endpoints
- [ ] Log successful logins
- [ ] Log failed login attempts
- [ ] Log logout events
- [ ] Include IP address and user agent

### Task 7.2: Add logging to user management
- [ ] Log user creation
- [ ] Log user updates
- [ ] Log user activation/deactivation
- [ ] Log user deletion

### Task 7.3: Add logging to status updates
- [ ] Log when user status changes
- [ ] Include old and new status in metadata

### Task 7.4: Add logging to password changes
- [ ] Log password updates
- [ ] Don't log actual passwords
- [ ] Mark as sensitive action

### Task 7.5: Extract request context
- [ ] Create helper to get IP address from request
- [ ] Create helper to get user agent from request
- [ ] Handle proxy headers (X-Forwarded-For)

### Task 7.6: Add metadata capture
- [ ] Capture old and new values for updates
- [ ] Capture relevant context for each action
- [ ] Store as JSON in metadata field

### Task 7.7: Handle errors gracefully
- [ ] Wrap audit logging in try/except
- [ ] Log audit failures separately
- [ ] Don't fail requests if audit logging fails

### Task 7.8: Test integration
- [ ] Test that actions are logged correctly
- [ ] Test that metadata is captured
- [ ] Test that IP and user agent are recorded

## 8. Export Functionality (4 tasks)

### Task 8.1: Implement CSV export
- [ ] Create CSV formatter
- [ ] Include all relevant fields
- [ ] Handle special characters
- [ ] Set proper headers for download

### Task 8.2: Implement JSON export
- [ ] Create JSON formatter
- [ ] Use proper JSON structure
- [ ] Set proper headers for download

### Task 8.3: Add streaming for large exports
- [ ] Use streaming response for large datasets
- [ ] Avoid loading all data into memory
- [ ] Test with large result sets

### Task 8.4: Add export limits
- [ ] Limit max export size
- [ ] Return error if too many results
- [ ] Suggest filtering for large exports

## 9. UI Support (3 tasks)

### Task 9.1: Add status indicators
- [ ] Return color codes for different statuses
- [ ] SUCCESS = green/blue
- [ ] FAILURE = red
- [ ] ERROR = orange/yellow

### Task 9.2: Add action categorization
- [ ] Group actions by category
- [ ] Return category in response
- [ ] Support filtering by category

### Task 9.3: Add user-friendly descriptions
- [ ] Format descriptions for display
- [ ] Include user names (not just IDs)
- [ ] Make descriptions human-readable

## 10. Testing (7 tasks)

### Task 10.1: Test audit log creation
- [ ] Test creating audit logs
- [ ] Test all field combinations
- [ ] Test with and without optional fields

### Task 10.2: Test filtering
- [ ] Test date range filtering
- [ ] Test user filtering
- [ ] Test action type filtering
- [ ] Test resource type filtering
- [ ] Test status filtering
- [ ] Test search functionality

### Task 10.3: Test pagination
- [ ] Test skip and limit
- [ ] Test total count accuracy
- [ ] Test with large datasets

### Task 10.4: Test export
- [ ] Test CSV export
- [ ] Test JSON export
- [ ] Test with filters
- [ ] Test large exports

### Task 10.5: Test middleware
- [ ] Test that requests are logged
- [ ] Test that health checks are skipped
- [ ] Test IP and user agent capture

### Task 10.6: Test integration
- [ ] Test login logging
- [ ] Test user management logging
- [ ] Test that metadata is captured correctly

### Task 10.7: Test authorization
- [ ] Test admin access (should succeed)
- [ ] Test non-admin access (should fail)
- [ ] Test unauthenticated access (should fail)

## 11. Documentation (4 tasks)

### Task 11.1: Update README
- [ ] Add audit logs section
- [ ] Document endpoints
- [ ] Add examples
- [ ] Explain filtering options

### Task 11.2: Create audit logging guide
- [ ] Document how to add audit logging to new endpoints
- [ ] Provide code examples
- [ ] Explain best practices
- [ ] Document metadata structure

### Task 11.3: Update API documentation
- [ ] Ensure all endpoints appear in Swagger
- [ ] Add proper descriptions
- [ ] Include example responses

### Task 11.4: Create compliance documentation
- [ ] Document what is logged
- [ ] Document retention policy
- [ ] Document access controls
- [ ] Document export capabilities

## Summary

**Total Tasks**: 58
- Audit Log Model: 4 tasks
- Schemas: 3 tasks
- Repository: 5 tasks
- Utility: 4 tasks
- Endpoints: 7 tasks (includes error logs endpoint)
- Global Exception Handler: 3 tasks (NEW)
- Middleware: 3 tasks
- Integration: 8 tasks
- Export: 4 tasks
- UI Support: 3 tasks
- Testing: 10 tasks (includes error logging tests)
- Documentation: 4 tasks
