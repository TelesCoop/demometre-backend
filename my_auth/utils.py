from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound

from open_democracy_back.exceptions import ErrorCode


def get_authenticated_or_anonymous_user_from_request(request):
    if request.user:
        return User.objects.get(id=request.user.id)
    if request.query_params.get("anonymous"):
        return User.objects.get(username=request.query_params.get("anonymous"))
    raise NotFound(
        detail="The user were not found", code=ErrorCode.USER_NOT_FOUND.value
    )
