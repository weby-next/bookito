from rest_framework import permissions


class IsBusinessOwner(permissions.BasePermission):
    message = "شما مجوز دسترسی به این بخش را ندارید"

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name="owner").exists()
        )

    def has_object_permission(self, request, view, obj):
            return obj.owner_id == request.user.id