from rest_framework import permissions


class JobAccessPermission(permissions.BasePermission):
    """
    Object-level permission for jobs.
    - Owners can view/manage their own jobs
    - Users with view_all_jobs can view any job
    - Users with manage_all_jobs can modify any job
    - Superusers can do anything
    - Admin role (profile.role == "admin") is treated as view/manage-all
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        profile = getattr(user, "profile", None)
        role = getattr(profile, "role", None)

        if request.method in permissions.SAFE_METHODS:
            if role in {"admin", "super_admin"} or user.has_perm("posts.view_all_jobs"):
                return True
            return obj.created_by_id == user.id

        if role in {"admin", "super_admin"} or user.has_perm("posts.manage_all_jobs"):
            return True

        return obj.created_by_id == user.id
