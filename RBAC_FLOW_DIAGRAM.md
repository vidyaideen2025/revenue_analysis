# RBAC Flow Diagram - Revenue Guardian

## System Architecture Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER LOGIN                               │
│                                                                  │
│  Email + Password → Authentication → JWT Token + User Role      │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ROLE IDENTIFICATION                           │
│                                                                  │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐               │
│  │  ADMIN   │     │   CXO    │     │OPERATIONS│               │
│  │ (role=1) │     │ (role=3) │     │ (role=2) │               │
│  └──────────┘     └──────────┘     └──────────┘               │
└─────────────────────────────────────────────────────────────────┘
       │                   │                   │
       │                   │                   │
       ▼                   ▼                   ▼
```

## OPERATIONS User Flow (Reconciliation Focus)

```
┌──────────────────────────────────────────────────────────────────┐
│                    OPERATIONS USER DASHBOARD                      │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Data Upload  │     │  Data Grid   │     │Reconciliation│
│     Tab      │     │     Tab      │     │     Tab      │
└──────────────┘     └──────────────┘     └──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DATA UPLOAD TAB                                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Upload File                                                  │
│     ├─ Permission: reconciliation.file.upload                   │
│     ├─ Action: POST /api/v1/reconciliation/files                │
│     ├─ Formats: Excel, CSV, JSON                                │
│     └─ Result: File uploaded, AI error detection triggered      │
│                                                                  │
│  2. View Uploaded Files                                          │
│     ├─ Permission: reconciliation.data.read                     │
│     ├─ Action: GET /api/v1/reconciliation/files                 │
│     └─ Result: List of uploaded files with metadata             │
│                                                                  │
│  3. Delete File                                                  │
│     ├─ Permission: reconciliation.file.delete                   │
│     ├─ Action: DELETE /api/v1/reconciliation/files/{id}         │
│     └─ Result: File removed from system                         │
│                                                                  │
│  4. AI Error Detection                                           │
│     ├─ Permission: reconciliation.ai.error_detection            │
│     ├─ Shows: Duplicates, Missing Data, Amount Anomalies        │
│     └─ Actions: View, Auto-fix suggestions, AI Suggestion       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ DATA GRID TAB                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. View Fine Data Grid                                          │
│     ├─ Permission: reconciliation.data.read                     │
│     ├─ Action: GET /api/v1/reconciliation/fine-data             │
│     ├─ Shows: FINE_ID, AMOUNT, STATUS, ISSUE_DATE, etc.         │
│     └─ Features: Filters, Search, Pagination                    │
│                                                                  │
│  2. Edit Data Records                                            │
│     ├─ Permission: reconciliation.data.update                   │
│     ├─ Action: PATCH /api/v1/reconciliation/fine-data/{id}      │
│     ├─ Editable: AMOUNT, COLLECTION_DATE, STATUS, ZONE          │
│     └─ Validation: Data type checks, business rules             │
│                                                                  │
│  3. Validate Data                                                │
│     ├─ Permission: reconciliation.data.validate                 │
│     ├─ Action: POST /api/v1/reconciliation/validate             │
│     ├─ Checks: Required fields, data integrity, duplicates      │
│     └─ Result: Validation report with errors/warnings           │
│                                                                  │
│  4. Submit for Approval                                          │
│     ├─ Permission: reconciliation.data.submit                   │
│     ├─ Action: POST /api/v1/reconciliation/submit               │
│     ├─ Prerequisite: Data must pass validation                  │
│     └─ Result: Data locked, sent to CXO/Admin for review        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ RECONCILIATION TAB                                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. View Reconciliation Summary                                  │
│     ├─ Permission: reconciliation.summary.read                  │
│     ├─ Action: GET /api/v1/reconciliation/summary               │
│     ├─ Shows:                                                    │
│     │   ├─ Fine Issue Report: 206,972 records                   │
│     │   ├─ Fine Collection Report: 170,475 records              │
│     │   ├─ Matched records: 48,153                              │
│     │   ├─ Unmatched from Issue: 158,819                        │
│     │   ├─ Unmatched from Collection: 122,322                   │
│     │   └─ Conflicts: 247                                       │
│     └─ Actions: Match Selected, Unmatch Selected                │
│                                                                  │
│  2. View Reports                                                 │
│     ├─ Permission: reports.fine_issue.read                      │
│     ├─ Permission: reports.fine_collection.read                 │
│     └─ Action: GET /api/v1/reports/{type}                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## CXO User Flow (Executive Dashboard Focus)

```
┌──────────────────────────────────────────────────────────────────┐
│                      CXO USER DASHBOARD                           │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Executive   │     │  AI Insights │     │   Reports    │
│  Dashboard   │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ EXECUTIVE DASHBOARD                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. View KPI Cards                                               │
│     ├─ Permission: dashboard.executive.read                     │
│     ├─ Action: GET /api/v1/dashboard/executive                  │
│     ├─ Shows:                                                    │
│     │   ├─ Total Revenue at Risk: AED 22.7M (↑12.4%)            │
│     │   ├─ Collection Efficiency: 22.7% (↓3.2%)                 │
│     │   ├─ Monthly Collections: AED 24.6M (↑4.3%)               │
│     │   └─ AI-Predicted Recovery: AED 8.4M (87% confidence)     │
│     └─ Features: Auto-refresh, Last 7 months view               │
│                                                                  │
│  2. Revenue Trend Analysis                                       │
│     ├─ Permission: dashboard.revenue_trends.read                │
│     ├─ Action: GET /api/v1/dashboard/revenue-trends             │
│     ├─ Shows: Line chart with forecast period                   │
│     └─ Views: Amount View, Percentage View                      │
│                                                                  │
│  3. Collection Performance Matrix                                │
│     ├─ Permission: dashboard.collection_performance.read        │
│     ├─ Action: GET /api/v1/dashboard/collection-performance     │
│     ├─ Shows: Collection rate by Emirate and Week               │
│     │   ├─ Dubai: 85%, 82%, 78%, 88% (Avg: 83%)                │
│     │   └─ Abu Dhabi: 72%, 75%, 71%, 76% (Avg: 74%)            │
│     └─ Features: Heatmap colors, drill-down capability          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ AI INSIGHTS (Phase 2)                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. View AI Recommendations                                      │
│     ├─ Permission: dashboard.ai_insights.read                   │
│     ├─ Action: GET /api/v1/ai/insights                          │
│     ├─ Shows:                                                    │
│     │   ├─ Collection Efficiency Below Target (Critical)        │
│     │   ├─ Optimal Collection Window Identified (Opportunity)   │
│     │   ├─ Aging Receivables Accumulating (Warning)             │
│     │   └─ Data Integrity Alert (Info)                          │
│     └─ Actions: Deploy AI Agent, View Details, Dismiss          │
│                                                                  │
│  2. AI Assistant Chat                                            │
│     ├─ Permission: dashboard.ai_insights.read                   │
│     ├─ Try asking about:                                         │
│     │   ├─ "Show me collection trends for last quarter"         │
│     │   ├─ "What are high-risk accounts?"                       │
│     │   ├─ "Generate summary report of pending fines"           │
│     │   └─ "Suggest optimal collection strategies"              │
│     └─ Features: Natural language queries, contextual responses │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ REPORTS & EXPORT                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Export Reports                                               │
│     ├─ Permission: reports.export                               │
│     ├─ Action: POST /api/v1/reports/export                      │
│     ├─ Formats: PDF, Excel, CSV                                 │
│     └─ Types: All report types available                        │
│                                                                  │
│  2. View Reconciliation Summary (Read-Only)                      │
│     ├─ Permission: reconciliation.summary.read                  │
│     ├─ Action: GET /api/v1/reconciliation/summary               │
│     └─ Note: Cannot edit or upload data                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## ADMIN User Flow (Full System Access)

```
┌──────────────────────────────────────────────────────────────────┐
│                      ADMIN USER DASHBOARD                         │
└──────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┬──────────────┐
        │                     │                     │              │
        ▼                     ▼                     ▼              ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐  ┌─────────┐
│All OPERATIONS│     │  All CXO     │     │    User      │  │ System  │
│  Features    │     │  Features    │     │  Management  │  │Settings │
└──────────────┘     └──────────────┘     └──────────────┘  └─────────┘

┌─────────────────────────────────────────────────────────────────┐
│ ADMIN EXCLUSIVE FEATURES                                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User Management                                              │
│     ├─ Permission: users.create, users.read, users.update,      │
│     │              users.delete                                  │
│     ├─ Actions:                                                  │
│     │   ├─ POST /api/v1/users (Create user)                     │
│     │   ├─ GET /api/v1/users (List users)                       │
│     │   ├─ PATCH /api/v1/users/{id} (Update user)               │
│     │   ├─ DELETE /api/v1/users/{id} (Delete user)              │
│     │   └─ PUT /api/v1/users/{id}/status (Activate/Deactivate)  │
│     └─ Features: Role assignment, department assignment          │
│                                                                  │
│  2. Department Management                                        │
│     ├─ Permission: departments.create, departments.read,        │
│     │              departments.update, departments.delete        │
│     ├─ Actions:                                                  │
│     │   ├─ POST /api/v1/departments (Create department)         │
│     │   ├─ GET /api/v1/departments (List departments)           │
│     │   ├─ PATCH /api/v1/departments/{id} (Update)              │
│     │   └─ DELETE /api/v1/departments/{id} (Delete)             │
│     └─ Features: Active/inactive status, user assignment        │
│                                                                  │
│  3. Audit Logs                                                   │
│     ├─ Permission: system.audit_logs.read                       │
│     ├─ Action: GET /api/v1/audit_logs                           │
│     ├─ Shows: All user actions, login attempts, data changes    │
│     └─ Features: Filter by user, date, action type              │
│                                                                  │
│  4. System Settings                                              │
│     ├─ Permission: system.settings.update                       │
│     ├─ Action: PATCH /api/v1/system/settings                    │
│     └─ Configure: Email, notifications, thresholds, etc.        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Permission Check Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER MAKES REQUEST                            │
│                                                                  │
│  POST /api/v1/reconciliation/files/upload                        │
│  Headers: Authorization: Bearer <JWT_TOKEN>                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  AUTHENTICATION CHECK                            │
│                                                                  │
│  1. Verify JWT token                                             │
│  2. Extract user_id from token                                   │
│  3. Load user from database                                      │
│  4. Check if user is active                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PERMISSION CHECK                                │
│                                                                  │
│  @require_permission("reconciliation.file.upload")               │
│                                                                  │
│  1. Get user's role (ADMIN=1, OPERATIONS=2, CXO=3)              │
│  2. If ADMIN → Grant access (admins have all permissions)       │
│  3. Else → Query database:                                       │
│     SELECT permissions.*                                         │
│     FROM permissions                                             │
│     JOIN role_permissions ON permissions.id = permission_id      │
│     JOIN roles ON roles.id = role_id                             │
│     WHERE roles.code = 'OPERATIONS'                              │
│       AND permissions.code = 'reconciliation.file.upload'        │
│       AND permissions.is_active = true                           │
│       AND roles.is_active = true                                 │
│  4. If permission found → Grant access                           │
│  5. Else → Return 403 Forbidden                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌──────────────┐    ┌──────────────┐
          │   GRANTED    │    │   DENIED     │
          │              │    │              │
          │ Execute      │    │ Return 403   │
          │ endpoint     │    │ Forbidden    │
          │ logic        │    │              │
          └──────────────┘    └──────────────┘
                    │                   │
                    ▼                   ▼
          ┌──────────────┐    ┌──────────────┐
          │ Log success  │    │ Log denial   │
          │ to audit log │    │ to audit log │
          └──────────────┘    └──────────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────┐
│                         TABLES                                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│     users        │         │   departments    │
├──────────────────┤         ├──────────────────┤
│ id (UUID) PK     │────────▶│ id (UUID) PK     │
│ email            │         │ name             │
│ username         │         │ code (unique)    │
│ password_hash    │         │ description      │
│ full_name        │         │ is_active        │
│ role (int)       │         │ is_deleted       │
│ department_id FK │         │ created_at       │
│ is_active        │         │ updated_at       │
│ is_deleted       │         └──────────────────┘
│ created_at       │
│ updated_at       │
└──────────────────┘

┌──────────────────┐         ┌──────────────────┐
│      roles       │         │   permissions    │
├──────────────────┤         ├──────────────────┤
│ id (UUID) PK     │         │ id (UUID) PK     │
│ name             │         │ name             │
│ code (unique)    │         │ code (unique)    │
│ description      │         │ description      │
│ is_system_role   │         │ category         │
│ is_active        │         │ action           │
│ created_at       │         │ resource         │
│ updated_at       │         │ is_active        │
└──────────────────┘         │ created_at       │
        │                    │ updated_at       │
        │                    └──────────────────┘
        │                            │
        │    ┌──────────────────────┐│
        └───▶│ role_permissions     ││
             ├──────────────────────┤│
             │ role_id (FK) PK      ││
             │ permission_id (FK) PK││
             └──────────────────────┘│
                      └──────────────┘
```

## Quick Reference

### OPERATIONS Permissions
```
✅ reconciliation.file.upload
✅ reconciliation.data.read
✅ reconciliation.data.update
✅ reconciliation.file.delete
✅ reconciliation.summary.read
✅ reconciliation.data.validate
✅ reconciliation.data.submit
✅ reconciliation.ai.error_detection
✅ reports.fine_issue.read
✅ reports.fine_collection.read
```

### CXO Permissions
```
✅ dashboard.executive.read
✅ dashboard.revenue_trends.read
✅ dashboard.ai_insights.read
✅ dashboard.collection_performance.read
✅ reports.export
✅ reports.fine_issue.read
✅ reports.fine_collection.read
✅ reconciliation.summary.read (read-only)
```

### ADMIN Permissions
```
✅ ALL OPERATIONS permissions
✅ ALL CXO permissions
✅ users.* (create, read, update, delete)
✅ departments.* (create, read, update, delete)
✅ system.audit_logs.read
✅ system.settings.update
```
