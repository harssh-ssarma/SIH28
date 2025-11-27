"""
Basic RBAC System for Timetable Management
3 Roles: Registrar, Department Head, Coordinator
"""
from rest_framework import permissions
from functools import wraps
from django.http import JsonResponse


# ============================================
# ROLE DEFINITIONS
# ============================================

class Role:
    """Role constants"""
    REGISTRAR = "registrar"
    DEPT_HEAD = "dept_head"
    COORDINATOR = "coordinator"
    
    ALL_ROLES = [REGISTRAR, DEPT_HEAD, COORDINATOR]


# ============================================
# PERMISSIONS
# ============================================

class IsRegistrar(permissions.BasePermission):
    """Only Registrar can access"""
    message = "Only Registrar can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.REGISTRAR
        )


class IsDepartmentHead(permissions.BasePermission):
    """Only Department Head can access"""
    message = "Only Department Head can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.DEPT_HEAD
        )


class IsCoordinator(permissions.BasePermission):
    """Only Coordinator can access"""
    message = "Only Coordinator can perform this action."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.COORDINATOR
        )


class CanManageTimetable(permissions.BasePermission):
    """Registrar and Dept Head can manage timetables"""
    message = "Only Registrar and Department Head can manage timetables."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in [Role.REGISTRAR, Role.DEPT_HEAD]
        )


class CanViewTimetable(permissions.BasePermission):
    """All roles can view timetables"""
    message = "Authentication required to view timetables."
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanApproveTimetable(permissions.BasePermission):
    """Only Registrar can approve timetables"""
    message = "Only Registrar can approve timetables."
    
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.REGISTRAR
        )


class DepartmentAccessPermission(permissions.BasePermission):
    """Department-level access control"""
    message = "You do not have access to this department's resources."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Registrar has access to all departments
        if request.user.role == Role.REGISTRAR:
            return True
        
        # Dept Head and Coordinator need department_id
        department_id = request.query_params.get('department_id') or request.data.get('department_id')
        if not department_id:
            return False
        
        # Check if user has access to this department
        return has_department_access(request.user, department_id)
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Registrar has access to all
        if request.user.role == Role.REGISTRAR:
            return True
        
        # Check department access
        department_id = getattr(obj, 'department_id', None)
        if not department_id:
            return False
        
        return has_department_access(request.user, department_id)


# ============================================
# HELPER FUNCTIONS
# ============================================

def has_department_access(user, department_id: str) -> bool:
    """Check if user has access to department"""
    if not user or not user.is_authenticated:
        return False
    
    # Registrar has access to all departments
    if user.role == Role.REGISTRAR:
        return True
    
    # Dept Head and Coordinator can only access their department
    if user.role in [Role.DEPT_HEAD, Role.COORDINATOR]:
        return str(user.department) == str(department_id)
    
    return False


def check_role(user, required_roles: list) -> bool:
    """Check if user has required role"""
    if not user or not user.is_authenticated:
        return False
    
    return user.role in required_roles


# ============================================
# DECORATORS
# ============================================

def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user or not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if request.user.role not in roles:
                return JsonResponse({'error': 'Insufficient permissions'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_department_access(view_func):
    """Decorator to require department access"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Registrar has access to all
        if request.user.role == Role.REGISTRAR:
            return view_func(request, *args, **kwargs)
        
        # Get department_id from request
        department_id = (
            request.GET.get('department_id') or
            request.POST.get('department_id') or
            kwargs.get('department_id')
        )
        
        if not department_id:
            return JsonResponse({'error': 'Department ID required'}, status=400)
        
        if not has_department_access(request.user, department_id):
            return JsonResponse({'error': 'Access denied to this department'}, status=403)
        
        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================
# PERMISSION MATRIX
# ============================================

PERMISSION_MATRIX = {
    'generate_timetable': [Role.REGISTRAR],
    'approve_timetable': [Role.REGISTRAR],
    'view_timetable': [Role.REGISTRAR, Role.DEPT_HEAD, Role.COORDINATOR],
    'edit_timetable': [Role.REGISTRAR, Role.DEPT_HEAD],
    'view_department_timetable': [Role.REGISTRAR, Role.DEPT_HEAD, Role.COORDINATOR],
    'manage_faculty': [Role.REGISTRAR, Role.DEPT_HEAD],
    'manage_courses': [Role.REGISTRAR, Role.DEPT_HEAD],
    'manage_rooms': [Role.REGISTRAR],
    'view_conflicts': [Role.REGISTRAR, Role.DEPT_HEAD, Role.COORDINATOR],
    'resolve_conflicts': [Role.REGISTRAR, Role.DEPT_HEAD],
}


def has_permission(user, action: str) -> bool:
    """Check if user has permission for action"""
    if not user or not user.is_authenticated:
        return False
    
    allowed_roles = PERMISSION_MATRIX.get(action, [])
    return user.role in allowed_roles
