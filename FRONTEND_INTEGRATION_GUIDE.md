# Frontend Integration Guide - RBAC System

## Overview

This guide shows how to integrate the RBAC system in your frontend application. The system provides APIs for both **permission checking (UX)** and **backend enforcement (security)**.

## 🔑 Key Concept

```
Frontend Permission Check = Better User Experience (hide/show buttons)
Backend Permission Check = Security (prevent unauthorized access)

BOTH are required!
```

## API Endpoints

### 1. Get Current User's Permissions

**Endpoint**: `GET /api/v1/rbac/me/permissions`

**Purpose**: Get all permissions for the logged-in user. Use this to show/hide UI elements.

**Response**:
```json
{
  "success": true,
  "message": "User permissions retrieved successfully",
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "username": "john_doe",
      "full_name": "John Doe",
      "role": 2
    },
    "role": {
      "code": "OPERATIONS",
      "value": 2
    },
    "permissions": [
      "reconciliation.file.upload",
      "reconciliation.data.read",
      "reconciliation.data.update",
      "reconciliation.file.delete",
      "reconciliation.summary.read",
      "reconciliation.data.validate",
      "reconciliation.data.submit",
      "reconciliation.ai.error_detection",
      "reports.fine_issue.read",
      "reports.fine_collection.read"
    ],
    "permission_details": [
      {
        "id": "uuid",
        "code": "reconciliation.file.upload",
        "name": "Upload Files",
        "category": "reconciliation",
        "action": "execute",
        "resource": "fine_data_file",
        "description": "Upload fine data files (Excel, CSV, JSON)"
      }
      // ... more permissions
    ]
  }
}
```

### 2. List All Permissions (Admin Only)

**Endpoint**: `GET /api/v1/rbac/permissions`

**Purpose**: Get all available permissions for creating/editing roles.

**Query Parameters**:
- `skip`: Pagination offset (default: 0)
- `limit`: Max results (default: 100)
- `category`: Filter by category
- `is_active`: Filter by active status

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [...],
    "grouped": {
      "reconciliation": [
        {
          "id": "uuid",
          "code": "reconciliation.file.upload",
          "name": "Upload Files",
          "description": "Upload fine data files",
          "action": "execute",
          "resource": "fine_data_file",
          "is_active": true
        }
      ],
      "dashboard": [...],
      "reports": [...]
    },
    "total": 25,
    "skip": 0,
    "limit": 100
  }
}
```

### 3. List All Roles (Admin Only)

**Endpoint**: `GET /api/v1/rbac/roles`

**Response**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "uuid",
        "name": "Operations User",
        "code": "OPERATIONS",
        "description": "Reconciliation and data management access",
        "is_system_role": true,
        "is_active": true,
        "permissions": [...],
        "permission_count": 10
      }
    ],
    "total": 3
  }
}
```

### 4. Create Role (Admin Only)

**Endpoint**: `POST /api/v1/rbac/roles`

**Request Body**:
```json
{
  "name": "Manager",
  "code": "MANAGER",
  "description": "Team manager with limited admin access",
  "permission_ids": [
    "uuid-1",
    "uuid-2",
    "uuid-3"
  ]
}
```

### 5. Update Role (Admin Only)

**Endpoint**: `PATCH /api/v1/rbac/roles/{role_id}`

**Request Body**:
```json
{
  "name": "Senior Manager",
  "description": "Updated description",
  "is_active": true,
  "permission_ids": ["uuid-1", "uuid-2"]
}
```

### 6. Delete Role (Admin Only)

**Endpoint**: `DELETE /api/v1/rbac/roles/{role_id}`

Note: System roles (ADMIN, CXO, OPERATIONS) cannot be deleted.

## Frontend Implementation

### Step 1: Store Permissions on Login

```typescript
// auth.service.ts
import { api } from './api';

interface UserPermissions {
  user: {
    id: string;
    email: string;
    username: string;
    full_name: string;
    role: number;
  };
  role: {
    code: string;
    value: number;
  };
  permissions: string[];
  permission_details: Permission[];
}

export class AuthService {
  async login(email: string, password: string) {
    // 1. Login
    const loginResponse = await api.post('/public/login', { email, password });
    const { access_token } = loginResponse.data;
    
    // Store token
    localStorage.setItem('access_token', access_token);
    
    // 2. Get user permissions
    const permissionsResponse = await api.get('/rbac/me/permissions', {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    
    const userPermissions: UserPermissions = permissionsResponse.data.data;
    
    // Store permissions in state/context
    localStorage.setItem('user_permissions', JSON.stringify(userPermissions.permissions));
    localStorage.setItem('user_role', userPermissions.role.code);
    
    return userPermissions;
  }
  
  getPermissions(): string[] {
    const perms = localStorage.getItem('user_permissions');
    return perms ? JSON.parse(perms) : [];
  }
  
  hasPermission(permissionCode: string): boolean {
    const permissions = this.getPermissions();
    return permissions.includes(permissionCode);
  }
  
  hasAnyPermission(permissionCodes: string[]): boolean {
    const permissions = this.getPermissions();
    return permissionCodes.some(code => permissions.includes(code));
  }
  
  hasAllPermissions(permissionCodes: string[]): boolean {
    const permissions = this.getPermissions();
    return permissionCodes.every(code => permissions.includes(code));
  }
}
```

### Step 2: Create Permission Context (React)

```typescript
// PermissionContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthService } from './auth.service';

interface PermissionContextType {
  permissions: string[];
  hasPermission: (code: string) => boolean;
  hasAnyPermission: (codes: string[]) => boolean;
  hasAllPermissions: (codes: string[]) => boolean;
  userRole: string;
}

const PermissionContext = createContext<PermissionContextType | undefined>(undefined);

export const PermissionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [permissions, setPermissions] = useState<string[]>([]);
  const [userRole, setUserRole] = useState<string>('');
  const authService = new AuthService();
  
  useEffect(() => {
    // Load permissions from storage
    const perms = authService.getPermissions();
    const role = localStorage.getItem('user_role') || '';
    setPermissions(perms);
    setUserRole(role);
  }, []);
  
  const hasPermission = (code: string) => permissions.includes(code);
  
  const hasAnyPermission = (codes: string[]) => 
    codes.some(code => permissions.includes(code));
  
  const hasAllPermissions = (codes: string[]) => 
    codes.every(code => permissions.includes(code));
  
  return (
    <PermissionContext.Provider value={{
      permissions,
      hasPermission,
      hasAnyPermission,
      hasAllPermissions,
      userRole
    }}>
      {children}
    </PermissionContext.Provider>
  );
};

export const usePermissions = () => {
  const context = useContext(PermissionContext);
  if (!context) {
    throw new Error('usePermissions must be used within PermissionProvider');
  }
  return context;
};
```

### Step 3: Use Permissions in Components

```typescript
// DataUploadPage.tsx
import React from 'react';
import { usePermissions } from './PermissionContext';

export const DataUploadPage: React.FC = () => {
  const { hasPermission } = usePermissions();
  
  const canUpload = hasPermission('reconciliation.file.upload');
  const canDelete = hasPermission('reconciliation.file.delete');
  const canViewData = hasPermission('reconciliation.data.read');
  
  const handleUpload = async (file: File) => {
    // Frontend already checked permission (for UX)
    // Backend will also check (for security)
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/reconciliation/files/upload', formData);
      console.log('Upload successful:', response.data);
    } catch (error) {
      if (error.response?.status === 403) {
        alert('Permission denied: You do not have permission to upload files');
      }
    }
  };
  
  return (
    <div>
      <h1>Data Upload</h1>
      
      {/* Show upload button only if user has permission */}
      {canUpload && (
        <button onClick={() => handleUpload(selectedFile)}>
          Upload File
        </button>
      )}
      
      {/* Show delete button only if user has permission */}
      {canDelete && (
        <button onClick={handleDelete}>
          Delete File
        </button>
      )}
      
      {/* Show data grid only if user has permission */}
      {canViewData ? (
        <DataGrid data={files} />
      ) : (
        <p>You don't have permission to view data</p>
      )}
    </div>
  );
};
```

### Step 4: Conditional Routing

```typescript
// ProtectedRoute.tsx
import React from 'react';
import { Navigate } from 'react-router-dom';
import { usePermissions } from './PermissionContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  requiredAnyPermissions?: string[];
  requiredRole?: string;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredPermission,
  requiredAnyPermissions,
  requiredRole
}) => {
  const { hasPermission, hasAnyPermission, userRole } = usePermissions();
  
  // Check role
  if (requiredRole && userRole !== requiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  // Check single permission
  if (requiredPermission && !hasPermission(requiredPermission)) {
    return <Navigate to="/unauthorized" />;
  }
  
  // Check any of multiple permissions
  if (requiredAnyPermissions && !hasAnyPermission(requiredAnyPermissions)) {
    return <Navigate to="/unauthorized" />;
  }
  
  return <>{children}</>;
};

// Usage in routes
<Routes>
  <Route path="/upload" element={
    <ProtectedRoute requiredPermission="reconciliation.file.upload">
      <DataUploadPage />
    </ProtectedRoute>
  } />
  
  <Route path="/dashboard" element={
    <ProtectedRoute requiredAnyPermissions={[
      "dashboard.executive.read",
      "dashboard.operations.read"
    ]}>
      <DashboardPage />
    </ProtectedRoute>
  } />
  
  <Route path="/admin" element={
    <ProtectedRoute requiredRole="ADMIN">
      <AdminPage />
    </ProtectedRoute>
  } />
</Routes>
```

### Step 5: Admin UI - Role Management

```typescript
// RoleManagementPage.tsx
import React, { useState, useEffect } from 'react';
import { api } from './api';

export const RoleManagementPage: React.FC = () => {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState({});
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);
  
  useEffect(() => {
    loadRoles();
    loadPermissions();
  }, []);
  
  const loadRoles = async () => {
    const response = await api.get('/rbac/roles');
    setRoles(response.data.data.items);
  };
  
  const loadPermissions = async () => {
    const response = await api.get('/rbac/permissions');
    setPermissions(response.data.data.grouped);
  };
  
  const handleCreateRole = async (roleData) => {
    try {
      await api.post('/rbac/roles', {
        name: roleData.name,
        code: roleData.code,
        description: roleData.description,
        permission_ids: selectedPermissions
      });
      
      alert('Role created successfully!');
      loadRoles();
    } catch (error) {
      alert('Error creating role: ' + error.response?.data?.message);
    }
  };
  
  return (
    <div>
      <h1>Role Management</h1>
      
      {/* Create Role Form */}
      <div className="create-role-form">
        <h2>Create New Role</h2>
        <input type="text" placeholder="Role Name" />
        <input type="text" placeholder="Role Code" />
        <textarea placeholder="Description" />
        
        {/* Permission Checkboxes */}
        <h3>Permissions</h3>
        {Object.entries(permissions).map(([category, perms]) => (
          <div key={category}>
            <h4>{category}</h4>
            {perms.map(perm => (
              <label key={perm.id}>
                <input
                  type="checkbox"
                  checked={selectedPermissions.includes(perm.id)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedPermissions([...selectedPermissions, perm.id]);
                    } else {
                      setSelectedPermissions(
                        selectedPermissions.filter(id => id !== perm.id)
                      );
                    }
                  }}
                />
                {perm.name} - {perm.description}
              </label>
            ))}
          </div>
        ))}
        
        <button onClick={handleCreateRole}>Create Role</button>
      </div>
      
      {/* Roles List */}
      <div className="roles-list">
        <h2>Existing Roles</h2>
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Code</th>
              <th>Permissions</th>
              <th>System Role</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {roles.map(role => (
              <tr key={role.id}>
                <td>{role.name}</td>
                <td>{role.code}</td>
                <td>{role.permission_count}</td>
                <td>{role.is_system_role ? 'Yes' : 'No'}</td>
                <td>
                  <button onClick={() => handleEditRole(role)}>Edit</button>
                  {!role.is_system_role && (
                    <button onClick={() => handleDeleteRole(role.id)}>Delete</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

## Permission Codes Reference

### Operations User Permissions
```typescript
const OPERATIONS_PERMISSIONS = [
  'reconciliation.file.upload',
  'reconciliation.data.read',
  'reconciliation.data.update',
  'reconciliation.file.delete',
  'reconciliation.summary.read',
  'reconciliation.data.validate',
  'reconciliation.data.submit',
  'reconciliation.ai.error_detection',
  'reports.fine_issue.read',
  'reports.fine_collection.read'
];
```

### CXO User Permissions
```typescript
const CXO_PERMISSIONS = [
  'dashboard.executive.read',
  'dashboard.revenue_trends.read',
  'dashboard.ai_insights.read',
  'dashboard.collection_performance.read',
  'reports.export',
  'reports.fine_issue.read',
  'reports.fine_collection.read',
  'reconciliation.summary.read'
];
```

### Admin User Permissions
```typescript
// Admin has ALL permissions
```

## Best Practices

1. **Always check permissions in backend** - Frontend checks are for UX only
2. **Handle 403 errors gracefully** - Show user-friendly messages
3. **Refresh permissions on role change** - Call `/rbac/me/permissions` again
4. **Cache permissions** - Store in context/state, don't fetch on every render
5. **Clear permissions on logout** - Remove from localStorage/state
6. **Test with different roles** - Ensure UI adapts correctly

## Testing

```typescript
// Test with different roles
describe('Permission System', () => {
  it('should hide upload button for CXO user', () => {
    // Mock CXO permissions
    mockPermissions(['dashboard.executive.read']);
    
    render(<DataUploadPage />);
    
    expect(screen.queryByText('Upload File')).not.toBeInTheDocument();
  });
  
  it('should show upload button for Operations user', () => {
    // Mock Operations permissions
    mockPermissions(['reconciliation.file.upload']);
    
    render(<DataUploadPage />);
    
    expect(screen.getByText('Upload File')).toBeInTheDocument();
  });
});
```

## Summary

✅ **Frontend**: Use permissions to show/hide UI elements (better UX)
✅ **Backend**: Always verify permissions on API calls (security)
✅ **Admin UI**: Allow creating custom roles with permission checkboxes
✅ **Both layers working together** = Secure + User-friendly application
