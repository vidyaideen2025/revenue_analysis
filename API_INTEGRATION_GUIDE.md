# Revenue Guardian API - Frontend Integration Guide

## 📦 Postman Collection

This package includes:
- **Revenue_Guardian_API.postman_collection.json** - Complete API collection with all endpoints
- **Revenue_Guardian.postman_environment.json** - Environment variables for local development

## 🚀 Quick Start

### 1. Import into Postman

1. Open Postman
2. Click **Import** button (top left)
3. Drag and drop both JSON files:
   - `Revenue_Guardian_API.postman_collection.json`
   - `Revenue_Guardian.postman_environment.json`
4. Select the **Revenue Guardian - Local** environment from the dropdown (top right)

### 2. Test the API

1. Go to **Authentication** folder
2. Run **Login** request
3. The access token will be automatically saved
4. All other requests will use this token automatically

### 3. Default Test Users

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@revenueguardian.com | Admin@123 |
| Operations | operations@revenueguardian.com | Operations@123 |
| CXO | cxo@revenueguardian.com | CXO@123 |

## 📚 API Overview

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All endpoints (except `/public/login` and `/health`) require JWT Bearer token:
```
Authorization: Bearer <access_token>
```

## 🔐 Authentication Flow

### 1. Login
```http
POST /api/v1/public/login
Content-Type: application/json

{
    "email": "admin@revenueguardian.com",
    "password": "Admin@123"
}
```

**Response:**
```json
{
    "status": 200,
    "message": "Login successful",
    "data": {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "id": "uuid",
            "email": "admin@revenueguardian.com",
            "username": "admin",
            "full_name": "System Administrator",
            "role": 1
        }
    }
}
```

### 2. Get User Permissions (Frontend)
```http
GET /api/v1/rbac/me/permissions
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "user": {
        "id": "uuid",
        "email": "admin@revenueguardian.com",
        "username": "admin",
        "full_name": "System Administrator",
        "role": 1
    },
    "role": {
        "code": "ADMIN",
        "value": 1
    },
    "permissions": [
        "reconciliation.file.upload",
        "dashboard.executive.read",
        "user.create",
        "user.update"
    ],
    "permission_details": [...]
}
```

## 📋 API Endpoints Summary

### Public Endpoints (No Auth Required)
- `POST /public/login` - User login
- `GET /health/` - Basic health check
- `GET /health/db` - Database health check

### User Management (Admin Only)
- `GET /users/` - List all users (with pagination & filters)
- `GET /users/{user_id}` - Get user by ID (self-access allowed)
- `POST /users/` - Create new user
- `PATCH /users/{user_id}` - Update user
- `PUT /users/{user_id}/status` - Activate/deactivate user
- `DELETE /users/{user_id}` - Soft delete user

### Department Management (Admin Only)
- `GET /departments/` - List all departments
- `GET /departments/{department_id}` - Get department by ID
- `POST /departments/` - Create department
- `PATCH /departments/{department_id}` - Update department
- `DELETE /departments/{department_id}` - Delete department

### RBAC - Permissions & Roles
- `GET /rbac/me/permissions` - Get current user's permissions (All users)
- `GET /rbac/permissions` - List all permissions (Admin only)
- `GET /rbac/roles` - List all roles (Admin only)
- `GET /rbac/roles/{role_id}` - Get role by ID (Admin only)
- `POST /rbac/roles` - Create custom role (Admin only)
- `PATCH /rbac/roles/{role_id}` - Update role (Admin only)
- `DELETE /rbac/roles/{role_id}` - Delete role (Admin only)

### Audit Logs (Admin Only)
- `GET /audit_logs/` - List audit logs (with filters)
- `GET /audit_logs/errors` - List error logs only
- `GET /audit_logs/{audit_log_id}` - Get audit log by ID

## 🎨 Frontend Implementation Examples

### React/TypeScript Example

#### 1. API Service
```typescript
// api.service.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to all requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle 401 errors (redirect to login)
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export default api;
```

#### 2. Auth Service
```typescript
// auth.service.ts
import api from './api.service';

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    user: {
        id: string;
        email: string;
        username: string;
        full_name: string;
        role: number;
    };
}

export const authService = {
    async login(credentials: LoginRequest): Promise<LoginResponse> {
        const response = await api.post('/public/login', credentials);
        const data = response.data.data;
        
        // Save token
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        return data;
    },

    async getMyPermissions() {
        const response = await api.get('/rbac/me/permissions');
        const permissions = response.data.permissions;
        
        // Save permissions for frontend use
        localStorage.setItem('permissions', JSON.stringify(permissions));
        
        return response.data;
    },

    logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        localStorage.removeItem('permissions');
        window.location.href = '/login';
    },

    hasPermission(permissionCode: string): boolean {
        const permissions = JSON.parse(localStorage.getItem('permissions') || '[]');
        return permissions.includes(permissionCode);
    },

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
};
```

#### 3. User Service
```typescript
// user.service.ts
import api from './api.service';

export interface User {
    id: string;
    email: string;
    username: string;
    full_name: string;
    department_id: string | null;
    role: number;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    department_name?: string;
    department_code?: string;
}

export interface CreateUserRequest {
    email: string;
    username: string;
    full_name: string;
    password: string;
    role: number;
    department_id?: string;
}

export const userService = {
    async listUsers(params?: {
        skip?: number;
        limit?: number;
        search?: string;
        role?: number;
        is_active?: boolean;
        department_id?: string;
    }) {
        const response = await api.get('/users/', { params });
        return response.data.data;
    },

    async getUserById(userId: string) {
        const response = await api.get(`/users/${userId}`);
        return response.data.data;
    },

    async createUser(userData: CreateUserRequest) {
        const response = await api.post('/users/', userData);
        return response.data.data;
    },

    async updateUser(userId: string, updates: Partial<User>) {
        const response = await api.patch(`/users/${userId}`, updates);
        return response.data.data;
    },

    async updateUserStatus(userId: string, isActive: boolean) {
        const response = await api.put(`/users/${userId}/status`, { is_active: isActive });
        return response.data.data;
    },

    async deleteUser(userId: string) {
        const response = await api.delete(`/users/${userId}`);
        return response.data;
    }
};
```

#### 4. Permission Hook (React)
```typescript
// usePermissions.ts
import { useState, useEffect } from 'react';
import { authService } from './auth.service';

export const usePermissions = () => {
    const [permissions, setPermissions] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadPermissions();
    }, []);

    const loadPermissions = async () => {
        try {
            const data = await authService.getMyPermissions();
            setPermissions(data.permissions);
        } catch (error) {
            console.error('Failed to load permissions:', error);
        } finally {
            setLoading(false);
        }
    };

    const hasPermission = (code: string) => permissions.includes(code);
    
    const hasAnyPermission = (codes: string[]) => 
        codes.some(code => permissions.includes(code));
    
    const hasAllPermissions = (codes: string[]) => 
        codes.every(code => permissions.includes(code));

    return {
        permissions,
        loading,
        hasPermission,
        hasAnyPermission,
        hasAllPermissions
    };
};
```

#### 5. Protected Component Example
```typescript
// UserManagement.tsx
import React, { useEffect, useState } from 'react';
import { userService } from './user.service';
import { usePermissions } from './usePermissions';

export const UserManagement: React.FC = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const { hasPermission } = usePermissions();

    const canCreateUser = hasPermission('user.create');
    const canUpdateUser = hasPermission('user.update');
    const canDeleteUser = hasPermission('user.delete');

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            const data = await userService.listUsers({ skip: 0, limit: 100 });
            setUsers(data.items);
        } catch (error) {
            console.error('Failed to load users:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateUser = async (userData: any) => {
        try {
            await userService.createUser(userData);
            loadUsers(); // Refresh list
        } catch (error) {
            console.error('Failed to create user:', error);
        }
    };

    const handleDeleteUser = async (userId: string) => {
        if (!confirm('Are you sure you want to delete this user?')) return;
        
        try {
            await userService.deleteUser(userId);
            loadUsers(); // Refresh list
        } catch (error) {
            console.error('Failed to delete user:', error);
        }
    };

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <h1>User Management</h1>
            
            {canCreateUser && (
                <button onClick={() => handleCreateUser(/* userData */)}>
                    Create New User
                </button>
            )}

            <table>
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Full Name</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {users.map((user: any) => (
                        <tr key={user.id}>
                            <td>{user.email}</td>
                            <td>{user.full_name}</td>
                            <td>{user.role === 1 ? 'Admin' : user.role === 2 ? 'Operations' : 'CXO'}</td>
                            <td>{user.is_active ? 'Active' : 'Inactive'}</td>
                            <td>
                                {canUpdateUser && (
                                    <button>Edit</button>
                                )}
                                {canDeleteUser && (
                                    <button onClick={() => handleDeleteUser(user.id)}>
                                        Delete
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};
```

## 🔑 Permission Codes Reference

### Reconciliation Permissions
- `reconciliation.file.upload` - Upload fine data files
- `reconciliation.data.read` - View reconciliation data
- `reconciliation.data.update` - Edit reconciliation data
- `reconciliation.file.delete` - Delete uploaded files
- `reconciliation.summary.read` - View reconciliation summary
- `reconciliation.data.validate` - Validate data
- `reconciliation.data.submit` - Submit for approval
- `reconciliation.ai.error_detection` - Use AI error detection

### Dashboard Permissions
- `dashboard.executive.read` - View executive dashboard
- `dashboard.operations.read` - View operations dashboard
- `dashboard.revenue_trends.read` - View revenue trends
- `dashboard.ai_insights.read` - View AI insights
- `dashboard.collection_performance.read` - View collection performance

### Reports Permissions
- `reports.export` - Export reports
- `reports.fine_issue.read` - View fine issue reports
- `reports.fine_collection.read` - View collection reports

### User Management Permissions
- `user.create` - Create users
- `user.read` - View users
- `user.update` - Update users
- `user.delete` - Delete users

## 📊 Response Format

All API responses follow this standardized format:

### Success Response
```json
{
    "status": 200,
    "message": "Operation successful",
    "data": {
        // Response data here
    }
}
```

### Error Response
```json
{
    "status": 400,
    "message": "Error message",
    "data": {
        "detail": "Detailed error information",
        "field": "field_name"  // Optional: which field caused the error
    }
}
```

### Paginated Response
```json
{
    "status": 200,
    "message": "Success",
    "data": {
        "items": [...],
        "total": 150,
        "skip": 0,
        "limit": 100
    }
}
```

## 🚨 Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (no permission)
- `404` - Not Found
- `422` - Unprocessable Entity
- `500` - Internal Server Error

### Example Error Handling
```typescript
try {
    const response = await api.post('/users/', userData);
    console.log('User created:', response.data);
} catch (error) {
    if (error.response) {
        switch (error.response.status) {
            case 400:
                alert(`Validation error: ${error.response.data.message}`);
                break;
            case 401:
                alert('Please login again');
                authService.logout();
                break;
            case 403:
                alert('You do not have permission to perform this action');
                break;
            case 404:
                alert('Resource not found');
                break;
            default:
                alert('An error occurred. Please try again.');
        }
    }
}
```

## 🔄 Pagination

All list endpoints support pagination:

```typescript
// Example: Get users page 2 (skip 100, limit 100)
const response = await api.get('/users/', {
    params: {
        skip: 100,
        limit: 100
    }
});

// Response includes pagination info
const { items, total, skip, limit } = response.data.data;
const currentPage = Math.floor(skip / limit) + 1;
const totalPages = Math.ceil(total / limit);
```

## 🔍 Filtering & Search

Most list endpoints support filtering:

```typescript
// Example: Search users by email/name, filter by role
const response = await api.get('/users/', {
    params: {
        search: 'john',
        role: 2,  // Operations
        is_active: true,
        skip: 0,
        limit: 50
    }
});
```

## 📝 Notes for Frontend Developers

### 1. Token Management
- Store JWT token in `localStorage` or secure cookie
- Include token in all API requests (except public endpoints)
- Handle token expiration (401 errors)
- Clear token on logout

### 2. Permission-Based UI
- Fetch user permissions on login: `GET /rbac/me/permissions`
- Store permissions in state/context
- Show/hide UI elements based on permissions
- Always validate on backend (frontend checks are for UX only)

### 3. Role Values
- `1` = ADMIN (full access)
- `2` = OPERATIONS (reconciliation & data management)
- `3` = CXO (dashboard & reports, read-only)

### 4. Date Formats
- All dates are in ISO 8601 format: `2025-03-15T10:30:00Z`
- Use `new Date(dateString)` in JavaScript

### 5. UUID Format
- All IDs are UUIDs: `550e8400-e29b-41d4-a716-446655440000`
- Use as strings in frontend

## 🛠️ Testing Tips

1. **Test with different roles**: Use the 3 default users to test different permission levels
2. **Test pagination**: Try different skip/limit values
3. **Test filters**: Combine multiple filters to ensure they work together
4. **Test error cases**: Try invalid data to see error responses
5. **Test token expiration**: Remove token to see 401 handling

## 📞 Support

For API issues or questions:
- Check the Postman collection for request examples
- Review the `FRONTEND_INTEGRATION_GUIDE.md` for detailed RBAC implementation
- Check the `RBAC_IMPLEMENTATION_GUIDE.md` for permission system details

## 🎯 Next Steps

1. Import Postman collection and environment
2. Test all endpoints with different user roles
3. Implement authentication flow in your frontend
4. Implement permission-based UI rendering
5. Add error handling for all API calls
6. Test with real data and edge cases

Happy coding! 🚀
