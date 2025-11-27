# RBAC Implementation - Complete

## Overview
Basic Role-Based Access Control (RBAC) system with 3 roles and department-level access control.

## Roles

### 1. Registrar
- **Permissions**: Full access to all departments and timetables
- **Can**:
  - Generate timetables for entire university
  - Approve/reject timetables
  - View all department timetables
  - Manage all resources (faculty, courses, rooms)
  - Resolve conflicts across departments

### 2. Department Head
- **Permissions**: Full access to own department only
- **Can**:
  - View own department timetables
  - Edit own department timetables
  - Manage faculty in own department
  - Manage courses in own department
  - View and resolve conflicts in own department
- **Cannot**:
  - Approve timetables (Registrar only)
  - Access other departments
  - Manage university-wide resources

### 3. Coordinator
- **Permissions**: Read-only access to own department
- **Can**:
  - View own department timetables
  - View conflicts in own department
- **Cannot**:
  - Edit timetables
  - Manage faculty or courses
  - Approve timetables
  - Access other departments

## Implementation Files

### 1. Core RBAC Module
**File**: `backend/django/core/rbac.py`
- Role constants (REGISTRAR, DEPT_HEAD, COORDINATOR)
- Permission classes (IsRegistrar, IsDepartmentHead, IsCoordinator, etc.)
- Department access control (DepartmentAccessPermission)
- Helper functions (has_department_access, check_role, has_permission)
- Decorators (@require_role, @require_department_access)
- Permission matrix (PERMISSION_MATRIX)

### 2. Database Migration
**File**: `backend/django/academics/migrations/0008_add_rbac_roles.py`
- Adds `department` field to User model (UUID, nullable)
- Updates role choices to include: registrar, dept_head, coordinator
- Maintains backward compatibility with existing roles

### 3. Management Command
**File**: `backend/django/core/management/commands/create_rbac_users.py`
- Creates test users for all 3 roles
- Credentials:
  - Registrar: `registrar / registrar123`
  - Dept Head: `dept_head / depthead123`
  - Coordinator: `coordinator / coordinator123`

### 4. Updated Views
**File**: `backend/django/academics/workflow_views.py`
- TimetableWorkflowViewSet: Added CanViewTimetable permission
- approve(): Restricted to CanApproveTimetable (Registrar only)
- reject(): Restricted to CanApproveTimetable (Registrar only)
- TimetableVariantViewSet: Added CanViewTimetable permission
- department_view(): Added DepartmentAccessPermission with access check

## Permission Matrix

| Action | Registrar | Dept Head | Coordinator |
|--------|-----------|-----------|-------------|
| Generate Timetable | ✅ | ❌ | ❌ |
| Approve Timetable | ✅ | ❌ | ❌ |
| View Timetable | ✅ | ✅ (own dept) | ✅ (own dept) |
| Edit Timetable | ✅ | ✅ (own dept) | ❌ |
| View Dept Timetable | ✅ (all) | ✅ (own) | ✅ (own) |
| Manage Faculty | ✅ | ✅ (own dept) | ❌ |
| Manage Courses | ✅ | ✅ (own dept) | ❌ |
| Manage Rooms | ✅ | ❌ | ❌ |
| View Conflicts | ✅ | ✅ (own dept) | ✅ (own dept) |
| Resolve Conflicts | ✅ | ✅ (own dept) | ❌ |

## Setup Instructions

### 1. Run Migration
```bash
cd backend/django
python manage.py migrate
```

### 2. Create Test Users
```bash
python manage.py create_rbac_users
```

### 3. Test Login
```bash
# Registrar
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "registrar", "password": "registrar123"}'

# Department Head
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "dept_head", "password": "depthead123"}'

# Coordinator
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "coordinator", "password": "coordinator123"}'
```

## Usage Examples

### 1. Check User Role
```python
from core.rbac import check_role, Role

if check_role(request.user, [Role.REGISTRAR]):
    # Registrar-only logic
    pass
```

### 2. Check Department Access
```python
from core.rbac import has_department_access

if has_department_access(request.user, department_id):
    # User has access to this department
    pass
```

### 3. Use Decorators
```python
from core.rbac import require_role, require_department_access, Role

@require_role(Role.REGISTRAR, Role.DEPT_HEAD)
def manage_timetable(request):
    # Only Registrar and Dept Head can access
    pass

@require_department_access
def view_department_data(request):
    # Checks department access automatically
    pass
```

### 4. Use Permission Classes
```python
from core.rbac import CanApproveTimetable, DepartmentAccessPermission

class TimetableViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, CanApproveTimetable]
    
    @action(detail=True, methods=['get'], permission_classes=[DepartmentAccessPermission])
    def department_view(self, request, pk=None):
        # Department-level access control
        pass
```

## API Endpoints with RBAC

### Approve Timetable (Registrar Only)
```bash
POST /api/timetable/workflow/{id}/approve/
Authorization: Bearer <registrar_token>
```

### View Department Timetable (Department-Level Access)
```bash
GET /api/timetable/variants/{id}/department_view/?department_id=<dept_id>
Authorization: Bearer <token>
```

## Security Features

1. **Role-Based Access**: Users can only perform actions allowed by their role
2. **Department Isolation**: Dept Heads and Coordinators can only access their own department
3. **Hierarchical Permissions**: Registrar > Dept Head > Coordinator
4. **Automatic Enforcement**: Permissions checked at view level via decorators/classes
5. **Audit Trail**: All actions logged with user ID and role

## Testing

### Test Registrar Access
```python
# Should succeed
client.login(username='registrar', password='registrar123')
response = client.post('/api/timetable/workflow/123/approve/')
assert response.status_code == 200
```

### Test Dept Head Access
```python
# Should succeed for own department
client.login(username='dept_head', password='depthead123')
response = client.get('/api/timetable/variants/123/department_view/?department_id=own_dept')
assert response.status_code == 200

# Should fail for other department
response = client.get('/api/timetable/variants/123/department_view/?department_id=other_dept')
assert response.status_code == 403
```

### Test Coordinator Access
```python
# Should succeed for viewing
client.login(username='coordinator', password='coordinator123')
response = client.get('/api/timetable/variants/123/department_view/?department_id=own_dept')
assert response.status_code == 200

# Should fail for approving
response = client.post('/api/timetable/workflow/123/approve/')
assert response.status_code == 403
```

## Future Enhancements

1. **Fine-Grained Permissions**: Add more granular permissions (e.g., can_edit_faculty, can_view_analytics)
2. **Role Hierarchy**: Implement role inheritance (Registrar inherits all Dept Head permissions)
3. **Dynamic Permissions**: Allow runtime permission assignment via admin panel
4. **Multi-Department Access**: Allow users to have access to multiple departments
5. **Temporary Permissions**: Time-limited access grants for special cases
6. **Audit Logging**: Detailed audit trail of all permission checks and actions

## Status
✅ **IMPLEMENTED** - Basic RBAC with 3 roles and department-level access control
