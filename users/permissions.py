from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allow access if user is owner of the profile or admin.
    """

    def has_object_permission(self, request, view, obj):
        # obj will be UserProfile instance
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        return obj.user == user
