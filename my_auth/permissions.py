from rest_framework.permissions import BasePermission
from my_auth.models import User


class IsAuthenticatedOrAnonymous(BasePermission):
    """
    Allows access only to authenticated users or anonymous code.
    """

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        is_anonymous = bool(
            User.objects.filter(username=request.query_params.get("anonymous")).count()
            == 1
        )
        return bool(is_authenticated or is_anonymous)
