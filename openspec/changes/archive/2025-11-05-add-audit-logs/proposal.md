# Add Audit Logs System

## Why

The system needs comprehensive audit logging to track all user actions, system events, and administrative operations for:

- **Compliance**: Meet regulatory requirements for financial data tracking and user activity monitoring
- **Security**: Detect and investigate suspicious activities, unauthorized access attempts, and security breaches
- **Accountability**: Maintain a complete record of who did what, when, and from where
- **Troubleshooting**: Debug issues by reviewing historical actions and system events
- **Audit Trail**: Provide immutable records for internal and external audits
- **User Activity Monitoring**: Track user behavior patterns and system usage

## What Changes

This change will implement a comprehensive audit logging system that captures all significant user actions and system events:

### Core Features

1. **Audit Log Model**
   - Unique ID (UUID)
   - Timestamp (when the action occurred)
   - User ID (who performed the action)
   - Action type (login, create, update, delete, etc.)
   - Resource type (user, role, data upload, etc.)
   - Resource ID (which specific resource was affected)
   - Description (human-readable action description)
   - IP address (where the action came from)
   - User agent (browser/client information)
   - Status (success, failure, error)
   - Metadata (JSON field for additional context)

2. **Audit Log Categories**
   - **Authentication Events**: Login, logout, failed login attempts, password changes
   - **User Management**: User creation, updates, activation, deactivation, deletion
   - **Role & Permissions**: Role assignments, permission changes
   - **Data Operations**: File uploads, data imports, reconciliation runs
   - **System Settings**: Configuration changes, system updates
   - **Administrative Actions**: Any admin-level operations
   - **Error Events**: Application errors, exceptions, system failures

3. **API Endpoints**
   - `GET /api/v1/audit-logs/` - List audit logs with filtering and pagination (default: 50 per page)
   - `GET /api/v1/audit-logs/{id}` - Get specific audit log details
   - `GET /api/v1/audit-logs/errors` - List error logs only (default: 50 per page, max: 200)
   - `GET /api/v1/audit-logs/export` - Export audit logs to CSV/JSON

4. **Filtering Capabilities**
   - Filter by date range (from/to)
   - Filter by user
   - Filter by action type
   - Filter by resource type
   - Filter by status (success/failure)
   - Search by description or IP address

5. **Automatic Logging**
   - Middleware to automatically capture HTTP requests
   - Decorator for marking functions that should be audited
   - Integration with existing endpoints (user management, auth, etc.)
   - Global exception handler to automatically log all errors
   - Stack trace capture for debugging

6. **Error Logging Features**
   - Automatic capture of all unhandled exceptions
   - Stack trace and error details in metadata
   - Error severity levels (WARNING, ERROR, CRITICAL)
   - Efficient pagination (default: 50, max: 200 per page)
   - Quick filtering by error type and severity
   - Separate endpoint for error-only logs

7. **UI Integration** (Based on screenshot)
   - Audit Logs page showing:
     - Action description with color-coded status indicators
     - User who performed the action
     - Timestamp
     - IP address
     - Export functionality

## Impact

### Benefits
- ✅ **Complete Audit Trail**: Every action is logged and traceable
- ✅ **Security Monitoring**: Detect unauthorized access and suspicious activities
- ✅ **Compliance Ready**: Meet regulatory requirements for audit logging
- ✅ **Troubleshooting**: Quickly identify what happened and when
- ✅ **User Accountability**: Clear record of who did what
- ✅ **Forensic Analysis**: Investigate incidents with detailed logs

### Technical Impact
- **New Files**: 
  - `app/models/audit_log.py` - Audit log model
  - `app/schemas/audit_log.py` - Audit log schemas
  - `app/crud/audit_log.py` - Audit log repository
  - `app/routers/audit_logs.py` - Audit log endpoints
  - `app/middleware/audit.py` - Audit logging middleware
  - `app/utils/audit.py` - Audit logging utilities
- **Updated Files**: 
  - `app/api.py` - Register audit log router
  - `main.py` - Add audit middleware
  - Existing routers - Add audit logging calls
- **Database**: New `audit_logs` table with indexes on timestamp, user_id, action_type

### Performance Considerations
- Async logging to avoid blocking requests
- Indexed columns for fast querying
- Optional log rotation/archival for old logs
- Pagination for large result sets

### Breaking Changes
- None - This is purely additive functionality

### Migration Required
- Database migration to create `audit_logs` table
- Indexes on frequently queried columns

### Testing Requirements
- Unit tests for audit log creation
- Integration tests for automatic logging
- Test filtering and pagination
- Test export functionality
- Test middleware integration

### Documentation Updates
- API documentation for audit log endpoints
- Guide on how to add audit logging to new endpoints
- Examples of querying audit logs
- Compliance documentation
