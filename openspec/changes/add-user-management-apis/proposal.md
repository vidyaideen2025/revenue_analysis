# Add User Management APIs

## Why

Currently, the system has user authentication (login) but lacks comprehensive user management capabilities. Administrators need the ability to manage users through a web interface, including creating new users, updating user information, activating/deactivating accounts, and soft-deleting users. This is essential for:

- **User Administration**: Admins need to create and manage user accounts without direct database access
- **Access Control**: Ability to activate/deactivate users to control system access
- **Audit Trail**: Soft delete ensures user records are preserved for compliance and audit purposes
- **Self-Service**: Reduce dependency on developers/DBAs for basic user management tasks
- **Security**: Centralized user management with proper authorization checks

## What Changes

This change will implement a complete set of user management APIs accessible only to administrators:

### API Endpoints

#### Admin-Only Endpoints
1. **GET /api/v1/users/** - List all users with pagination, search, and filtering (Admin only)
2. **POST /api/v1/users/** - Create a new user (Admin only)
3. **PATCH /api/v1/users/{id}** - Update user information (Admin only)
4. **PUT /api/v1/users/{id}/status** - Update user status (Admin only)
5. **DELETE /api/v1/users/{id}** - Soft delete a user (Admin only)

#### Authenticated User Endpoints
6. **GET /api/v1/users/{id}** - Get a specific user by ID
   - **Admin**: Can view any user's profile
   - **Any authenticated user**: Can view their own profile (self-access)
   - Use case: User profile page, admin user management

### Features
- **Role-Based Access**: Admin-only for management operations, self-access for profile viewing
- **User Profile Support**: GET user by ID works for both admin management and user profile pages
- **Self-Access Control**: Users can view their own profile, admins can view any profile
- **Search & Filter**: Search by name/email, filter by role/status (admin only)
- **Pagination**: Support for skip/limit parameters
- **Validation**: Email/username uniqueness checks
- **Audit Trail**: Track created_by, updated_by for all operations
- **Soft Delete**: Preserve user records for compliance
- **Standardized Responses**: All endpoints use APIResponse format

### UI Integration
Based on the provided screenshot, the APIs will support:
- User listing with Name, Email, Role, Department, Last Active, Status columns
- Search functionality
- Add New User button
- Import/Export capabilities
- Active user count display
- Status indicators (Active/Inactive)

## Impact

### Benefits
- ✅ **Complete User Management**: Full CRUD operations for user administration
- ✅ **Security**: Admin-only access with proper authorization
- ✅ **Audit Compliance**: Soft delete and audit fields preserve history
- ✅ **User Experience**: Clean API for frontend integration
- ✅ **Scalability**: Pagination support for large user bases

### Technical Impact
- **New Files**: `app/routers/users.py` (user management endpoints)
- **Updated Files**: `app/api.py` (register new router)
- **Database**: No schema changes (uses existing users table)
- **Dependencies**: Uses existing auth dependencies for RBAC

### Breaking Changes
- None - This is purely additive functionality

### Migration Required
- None - No database schema changes

### Testing Requirements
- Unit tests for all CRUD operations
- Integration tests for authorization checks
- Test cases for validation (duplicate email/username)
- Test soft delete functionality
- Test pagination and filtering

### Documentation Updates
- API documentation in Swagger/ReDoc
- Update README with user management endpoints
- Add examples for each endpoint
