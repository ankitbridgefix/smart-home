from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return getattr(obj, "user", getattr(getattr(obj, "device", None), "user", None)) == request.user
