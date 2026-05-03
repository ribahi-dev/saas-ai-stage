from rest_framework.permissions import BasePermission

class IsAdminUserRole(BasePermission):
    """
    Permet l'accès uniquement aux utilisateurs ayant le rôle 'admin' ou étant 'is_staff'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.role == 'admin' or request.user.is_staff)
        )
