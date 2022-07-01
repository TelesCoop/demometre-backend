from rest_framework.permissions import BasePermission


class IsExpert(BasePermission):
    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        # TODO : check the user is an expert
        return bool(is_authenticated)
