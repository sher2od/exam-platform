from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    """
    Faqat role='ADMIN' bo'lgan foydalanuvchilarga ruxsat beradi.
    """
    message = "Sizda bu amalni bajarish uchun SuperAdmin huquqi yo'q!"

    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'ADMIN'
        )
