# Role-Based Access Control (RBAC) Implementation Guide

## Overview

This system implements fine-grained RBAC for the Revenue Guardian application with three main roles:
- **ADMIN**: Full system access
- **CXO**: Executive dashboard and reporting
- **OPERATIONS**: Reconciliation and data management

## Architecture

### 1. Database Models

**Permission Model** (`app/models/permission.py`)
- Granular permissions with category, action, and resource
- Example: `reconciliation.file.upload`

**Role Model** (`app/models/permission.py`)
- Groups permissions together
- System roles: ADMIN, CXO, OPERATIONS

**Many-to-Many Relationship**
- Roles ↔ Permissions via `role_permissions` table

### 2. Permission Categories

```
RECONCILIATION
├── file.upload          (Operations)
├── data.read            (Operations, CXO read-only)
├── data.update          (Operations)
├── file.delete          (Operations)
├── summary.read         (Operations, CXO)
├── data.validate        (Operations)
├── data.submit          (Operations)
└── ai.error_detection   (Operations)

DASHBOARD
├── executive.read       (CXO, Admin)
├── revenue_trends.read  (CXO, Admin)
├── ai_insights.read     (CXO, Admin)
└── collection_performance.read (CXO, Admin)

REPORTS
├── export               (CXO, Admin)
├── fine_issue.read      (Operations, CXO, Admin)
└── fine_collection.read (Operations, CXO, Admin)

USER_MANAGEMENT
├── users.create         (Admin only)
├── users.read           (Admin only)
├── users.update         (Admin only)
└── users.delete         (Admin only)

DEPARTMENT_MANAGEMENT
├── departments.create   (Admin only)
├── departments.read     (Admin only)
├── departments.update   (Admin only)
└── departments.delete   (Admin only)

SYSTEM
├── audit_logs.read      (Admin only)
└── settings.update      (Admin only)
```

## Implementation Flow

### Step 1: Database Migration

Create migration for permissions and roles tables:

```bash
alembic revision --autogenerate -m "add_permissions_and_roles"
alembic upgrade head
```

### Step 2: Seed Permissions and Roles

Create a seeding script (`app/utils/seed_permissions.py`):

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.permission import Permission, Role, SYSTEM_PERMISSIONS, SYSTEM_ROLES

async def seed_permissions_and_roles(db: AsyncSession):
    """Seed system permissions and roles."""
    
    # Create permissions
    permission_map = {}
    for code, perm_data in SYSTEM_PERMISSIONS.items():
        permission = Permission(
            code=code,
            name=perm_data["name"],
            description=perm_data["description"],
            category=perm_data["category"].value,
            action=perm_data["action"].value,
            resource=perm_data["resource"],
            is_active=True
        )
        db.add(permission)
        permission_map[code] = permission
    
    await db.commit()
    
    # Create roles with permissions
    for role_code, role_data in SYSTEM_ROLES.items():
        role = Role(
            code=role_code,
            name=role_data["name"],
            description=role_data["description"],
            is_system_role=True,
            is_active=True
        )
        
        # Add permissions to role
        for perm_code in role_data["permissions"]:
            if perm_code in permission_map:
                role.permissions.append(permission_map[perm_code])
        
        db.add(role)
    
    await db.commit()
```

Run seeding:
```bash
python -m app.scripts.seed_permissions
```

### Step 3: Protect Endpoints with Permissions

#### Method 1: Using Decorators (Recommended)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.utils.permissions import require_permission

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

@router.post("/upload")
@require_permission("reconciliation.file.upload")
async def upload_file(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload fine data file - OPERATIONS only."""
    # Your upload logic here
    return {"message": "File uploaded successfully"}

@router.get("/data")
@require_permission("reconciliation.data.read")
async def get_fine_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View fine data grid - OPERATIONS only."""
    # Your data retrieval logic
    return {"data": []}

@router.delete("/files/{file_id}")
@require_permission("reconciliation.file.delete")
async def delete_file(
    file_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete uploaded file - OPERATIONS only."""
    # Your delete logic
    return {"message": "File deleted"}
```

#### Method 2: Manual Permission Check

```python
from app.utils.permissions import PermissionChecker

@router.patch("/data/{record_id}")
async def update_fine_data(
    record_id: str,
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update fine data record - OPERATIONS only."""
    
    # Manual permission check
    has_permission = await PermissionChecker.user_has_permission(
        db, current_user, "reconciliation.data.update"
    )
    
    if not has_permission:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update data"
        )
    
    # Your update logic
    return {"message": "Data updated"}
```

#### Method 3: Multiple Permissions

```python
from app.utils.permissions import require_any_permission, require_all_permissions

# User needs ANY of these permissions
@router.get("/dashboard")
@require_any_permission(
    "dashboard.executive.read",
    "dashboard.operations.read"
)
async def view_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """View dashboard - CXO or OPERATIONS."""
    return {"dashboard": "data"}

# User needs ALL of these permissions
@router.post("/reconcile")
@require_all_permissions(
    "reconciliation.data.read",
    "reconciliation.data.update"
)
async def reconcile_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Reconcile data - needs both read and update."""
    return {"status": "reconciled"}
```

### Step 4: Frontend Integration

#### Get User Permissions

```python
@router.get("/me/permissions")
async def get_my_permissions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's permissions for frontend."""
    from app.utils.permissions import PermissionChecker
    
    permissions = await PermissionChecker.get_user_permissions(db, current_user)
    
    return {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role
        },
        "permissions": [
            {
                "code": p.code,
                "name": p.name,
                "category": p.category,
                "action": p.action,
                "resource": p.resource
            }
            for p in permissions
        ]
    }
```

#### Frontend Permission Check

```typescript
// Store user permissions in state
const userPermissions = ['reconciliation.file.upload', 'reconciliation.data.read', ...];

// Check permission before showing UI elements
const canUploadFiles = userPermissions.includes('reconciliation.file.upload');
const canViewDashboard = userPermissions.includes('dashboard.executive.read');

// Conditional rendering
{canUploadFiles && (
  <Button onClick={handleUpload}>Upload File</Button>
)}

{canViewDashboard && (
  <DashboardWidget />
)}
```

## Role-Specific Flows

### OPERATIONS User Flow

1. **Login** → Authenticated as OPERATIONS role
2. **Data Upload Tab**
   - ✅ Can upload files (`reconciliation.file.upload`)
   - ✅ Can view uploaded files
   - ✅ Can delete files (`reconciliation.file.delete`)
3. **Data Grid Tab**
   - ✅ Can view data grid (`reconciliation.data.read`)
   - ✅ Can edit records (`reconciliation.data.update`)
   - ✅ Can validate data (`reconciliation.data.validate`)
   - ✅ Can submit for approval (`reconciliation.data.submit`)
4. **Reconciliation Tab**
   - ✅ Can view reconciliation summary (`reconciliation.summary.read`)
   - ✅ Can access AI error detection (`reconciliation.ai.error_detection`)
5. **Reports**
   - ✅ Can view fine issue/collection reports
   - ❌ Cannot access executive dashboard
   - ❌ Cannot manage users/departments

### CXO User Flow

1. **Login** → Authenticated as CXO role
2. **Executive Dashboard**
   - ✅ Can view executive dashboard (`dashboard.executive.read`)
   - ✅ Can view revenue trends (`dashboard.revenue_trends.read`)
   - ✅ Can view AI insights (`dashboard.ai_insights.read`)
   - ✅ Can view collection performance (`dashboard.collection_performance.read`)
3. **Reports**
   - ✅ Can export reports (`reports.export`)
   - ✅ Can view all report types
4. **Reconciliation**
   - ✅ Can view reconciliation summary (read-only)
   - ❌ Cannot upload/edit/delete data
5. **Management**
   - ❌ Cannot manage users/departments

### ADMIN User Flow

1. **Login** → Authenticated as ADMIN role
2. **Full Access**
   - ✅ All OPERATIONS permissions
   - ✅ All CXO permissions
   - ✅ User management
   - ✅ Department management
   - ✅ System settings
   - ✅ Audit logs

## Best Practices

### 1. Always Check Permissions at API Level
```python
# ✅ Good - Permission check in backend
@router.post("/upload")
@require_permission("reconciliation.file.upload")
async def upload_file(...):
    pass

# ❌ Bad - Only frontend check
# Frontend can be bypassed!
```

### 2. Use Specific Permissions
```python
# ✅ Good - Specific permission
@require_permission("reconciliation.file.upload")

# ❌ Bad - Too broad
@require_permission("reconciliation.*")
```

### 3. Combine with Role Checks for Critical Operations
```python
from app.models.user import UserRole

@router.delete("/system/reset")
async def reset_system(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Critical operation - double check
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Additional permission check
    has_permission = await PermissionChecker.user_has_permission(
        db, current_user, "system.reset"
    )
    if not has_permission:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Proceed with reset
    pass
```

### 4. Log Permission Denials
```python
from app.utils.audit import log_audit

@router.post("/sensitive-action")
async def sensitive_action(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    has_permission = await PermissionChecker.user_has_permission(
        db, current_user, "sensitive.action"
    )
    
    if not has_permission:
        # Log the denial
        await log_audit(
            db=db,
            user_id=current_user.id,
            action_type="PERMISSION_DENIED",
            description=f"User attempted sensitive action without permission",
            status="FAILURE"
        )
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Proceed
    pass
```

## Testing Permissions

```python
import pytest
from app.utils.permissions import PermissionChecker

@pytest.mark.asyncio
async def test_operations_can_upload_files(db_session, operations_user):
    """Test that operations user can upload files."""
    has_permission = await PermissionChecker.user_has_permission(
        db_session,
        operations_user,
        "reconciliation.file.upload"
    )
    assert has_permission is True

@pytest.mark.asyncio
async def test_cxo_cannot_upload_files(db_session, cxo_user):
    """Test that CXO user cannot upload files."""
    has_permission = await PermissionChecker.user_has_permission(
        db_session,
        cxo_user,
        "reconciliation.file.upload"
    )
    assert has_permission is False

@pytest.mark.asyncio
async def test_admin_has_all_permissions(db_session, admin_user):
    """Test that admin has all permissions."""
    has_permission = await PermissionChecker.user_has_permission(
        db_session,
        admin_user,
        "reconciliation.file.upload"
    )
    assert has_permission is True
```

## Summary

This RBAC system provides:
- ✅ **Granular control** - 25+ specific permissions
- ✅ **Role-based grouping** - ADMIN, CXO, OPERATIONS
- ✅ **Easy to use** - Decorators for endpoints
- ✅ **Flexible** - Can check single or multiple permissions
- ✅ **Secure** - Backend enforcement
- ✅ **Auditable** - Can log all permission checks
- ✅ **Scalable** - Easy to add new permissions/roles

The system ensures that:
- **OPERATIONS** users can only access reconciliation features
- **CXO** users can only view dashboards and reports
- **ADMIN** users have full system access
