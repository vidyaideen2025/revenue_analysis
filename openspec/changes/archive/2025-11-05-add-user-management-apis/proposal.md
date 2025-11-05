# Add User Management APIs

## Why

Currently, the system has user authentication (login) but lacks comprehensive user management capabilities. Administrators need the ability to manage users and departments through a web interface, including creating new users, updating user information, activating/deactivating accounts, and managing organizational departments. This is essential for:

- **User Administration**: Admins need to create and manage user accounts without direct database access
- **Department Management**: Dynamic department creation and management instead of hardcoded enums
- **Organizational Structure**: Support growing organizations with flexible department hierarchy
- **Access Control**: Ability to activate/deactivate users to control system access
- **Audit Trail**: Soft delete ensures user records are preserved for compliance and audit purposes
- **Self-Service**: Reduce dependency on developers/DBAs for basic user management tasks
- **Security**: Centralized user and department management with proper authorization checks

## What Changes

This change will implement a complete set of user management APIs accessible only to administrators:

### API Endpoints

#### User Management Endpoints (Admin-Only)
1. **GET /api/v1/users/** - List all users with pagination, search, and filtering
2. **POST /api/v1/users/** - Create a new user
3. **PATCH /api/v1/users/{id}** - Update user information
4. **PUT /api/v1/users/{id}/status** - Update user status
5. **DELETE /api/v1/users/{id}** - Soft delete a user

#### User Profile Endpoints (Authenticated)
6. **GET /api/v1/users/{id}** - Get a specific user by ID
   - **Admin**: Can view any user's profile
   - **Any authenticated user**: Can view their own profile (self-access)
   - Use case: User profile page, admin user management

#### Department Management Endpoints (Admin-Only)
7. **GET /api/v1/departments/** - List all departments with pagination and search
8. **GET /api/v1/departments/{id}** - Get specific department details
9. **POST /api/v1/departments/** - Create a new department
10. **PATCH /api/v1/departments/{id}** - Update department information
11. **DELETE /api/v1/departments/{id}** - Soft delete a department

### User Management Features
- **Role-Based Access**: Admin-only for management operations, self-access for profile viewing
- **User Profile Support**: GET user by ID works for both admin management and user profile pages
- **Self-Access Control**: Users can view their own profile, admins can view any profile
- **Search & Filter**: Search by name/email, filter by role/status/department (admin only)
- **Pagination**: Support for skip/limit parameters
- **Validation**: Email/username uniqueness checks
- **Audit Trail**: Track created_by, updated_by for all operations
- **Soft Delete**: Preserve user records for compliance
- **Standardized Responses**: All endpoints use APIResponse format

### Department Management Features
- **Dynamic Departments**: Create and manage departments without code changes
- **Department Model**: 
  - Department Name (e.g., "Information Technology")
  - Department Code (e.g., "IT") - unique identifier
  - Description (purpose and responsibilities)
  - Status (Active/Inactive)
  - Timestamps (created_at, updated_at)
- **Department-User Relationship**: Users can be assigned to departments via dropdown
- **Validation**: Department code uniqueness, name validation
- **Soft Delete**: Preserve department records for audit trail
- **Active Departments Only**: User creation dropdown shows only active departments
- **Search & Filter**: Search departments by name/code, filter by status

### UI Integration
Based on the provided screenshots, the APIs will support:

**User Management UI:**
- User listing with Name, Email, Role, Department, Last Active, Status columns
- Search functionality
- Add New User button with department dropdown
- Import/Export capabilities
- Active user count display
- Status indicators (Active/Inactive)
- Department selection dropdown showing "4 departments available"

**Department Management UI:**
- Create New Department form with:
  - Department Name field (e.g., "Information Technology")
  - Department Code field (e.g., "IT")
  - Description textarea (purpose and responsibilities)
  - Status dropdown (Active/Inactive)
  - Cancel and Create Department buttons

## Impact

### Benefits
- ✅ **Complete User Management**: Full CRUD operations for user administration
- ✅ **Dynamic Departments**: No code changes needed to add new departments
- ✅ **Organizational Flexibility**: Support growing organizations with custom departments
- ✅ **Security**: Admin-only access with proper authorization
- ✅ **Audit Compliance**: Soft delete and audit fields preserve history
- ✅ **User Experience**: Clean API for frontend integration
- ✅ **Scalability**: Pagination support for large user and department bases

### Technical Impact
- **New Files**: 
  - `app/models/department.py` - Department model
  - `app/schemas/department.py` - Department schemas
  - `app/crud/department.py` - Department repository
  - `app/routers/users.py` - User management endpoints
  - `app/routers/departments.py` - Department management endpoints
- **Updated Files**: 
  - `app/api.py` - Register new routers
  - `app/models/user.py` - Change department from Enum to ForeignKey
  - `app/schemas/user.py` - Update department field to UUID
- **Database**: 
  - New `departments` table
  - Migration to convert existing department enum values to department records
  - Add foreign key relationship from users to departments
- **Dependencies**: Uses existing auth dependencies for RBAC

### Breaking Changes
- **Department Field Change**: User.department changes from Integer (enum) to UUID (foreign key)
- **Migration Strategy**: 
  1. Create departments table
  2. Seed with existing enum values (IT, FINANCE, OPERATIONS, AUDIT, HR, SALES)
  3. Migrate user.department integer values to department UUIDs
  4. Update foreign key constraint

### Migration Required
- **Database Migration**: Create departments table and migrate existing data
- **Data Seeding**: Populate departments with existing enum values
- **Foreign Key Migration**: Convert user.department from integer to UUID foreign key

### Testing Requirements
**User Management:**
- Unit tests for all user CRUD operations
- Integration tests for authorization checks
- Test cases for validation (duplicate email/username)
- Test soft delete functionality
- Test pagination and filtering
- Test self-access control for user profiles

**Department Management:**
- Unit tests for all department CRUD operations
- Test department code uniqueness validation
- Test department-user relationship
- Test soft delete with existing user references
- Test active/inactive department filtering
- Test migration from enum to foreign key

### Documentation Updates
- API documentation in Swagger/ReDoc for both user and department endpoints
- Update README with user and department management endpoints
- Add examples for each endpoint
- Document migration process from enum to department table
- Add guide for department management workflow
