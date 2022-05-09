from django.contrib.auth.models import User


def get_authenticated_or_anonymous_user_from_request(request):
    if request.user:
        return User.objects.get(id=request.user.id)
    if request.query_params.get("anonymous"):
        return User.objects.get(username=request.query_params.get("anonymous"))
    return None
