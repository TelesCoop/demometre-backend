import uuid
from datetime import datetime, timezone

from django.conf.global_settings import AUTHENTICATION_BACKENDS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from my_auth.emails import email_reset_password_link
from my_auth.models import UserResetKey

from .serializers import AuthSerializer


@api_view(["POST"])
@permission_classes([])
def frontend_signup(request):
    """
    Sign up user

    Args:
        request:
            The request body should contain a JSON object such as::
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "email@ex.com",
                    "password": "secret_pa$$w0rD",
                }

    Returns:
        JSON object::
            AuthSerializer
    """
    data = request.data
    if User.objects.filter(email=request.data["email"]).count():
        return Response(
            data={"message": "Le mail est déjà utilisé", "field": "email"}, status=400
        )
    data["username"] = request.data["email"]
    user = AuthSerializer(data=data)
    user.is_valid(raise_exception=True)
    user.save()

    userAuth = authenticate(username=data["username"], password=data["password"])
    userAuth.backend = AUTHENTICATION_BACKENDS[0]
    login(request, userAuth)

    return Response(status=201, data=AuthSerializer(userAuth).data)


@api_view(["POST"])
@permission_classes([])
def frontend_login(request):
    """
    Log in a user

    Args:
        request:
            The request body should contain a JSON object such as::

              {"email": "email@ex.com",
               "password": "secret_pa$$w0rD"}

    Returns:
        JSON object::
            AuthSerializer
    """

    data = request.data
    email, password = data["email"].lower(), data["password"]
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            data={
                "message": "Cet email ne correspond à aucun utilisateur",
                "field": "email",
            },
            status=400,
        )

    user_auth = authenticate(username=user.username, password=password)

    if user_auth is not None:
        user_auth.backend = AUTHENTICATION_BACKENDS[0]
        login(request, user_auth)
        return Response(AuthSerializer(user_auth).data)
    else:
        return Response(
            data={"message": "Email et mot de passe ne correspondent pas"}, status=400
        )


@api_view(["POST"])
def frontend_logout(request):
    """Log out view."""
    logout(request)
    return HttpResponse(status=200)


@api_view(["GET"])
@ensure_csrf_cookie
@permission_classes([])
def who_am_i(request):
    """Returns information about the current user."""
    if request.user.is_anonymous:
        return Response(status=400)

    return Response(AuthSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([])
def front_end_reset_password_link(request):
    """Send a reset password link"""
    try:
        user = User.objects.get(email=request.data.get("email"))
    except User.DoesNotExist:
        return Response(status=404)
    if UserResetKey.objects.get(user=user):
        UserResetKey.objects.get(user=user).delete()
    UserResetKey.objects.create(
        user=user, reset_key=uuid.uuid4(), reset_key_datetime=datetime.now()
    )
    email_reset_password_link(request, user)
    return Response(status=200)


@api_view(["POST"])
@permission_classes([])
def front_end_reset_password(request):
    """Send a reset password"""
    try:
        user = User.objects.get(
            reset_key__reset_key=request.data.get("reset_key"),
        )
    except User.DoesNotExist:
        return Response(status=403)

    is_valid_key = datetime.now(timezone.utc) - user.reset_key.reset_key_datetime
    if is_valid_key.days != 0:
        return Response(status=400)

    user.set_password(request.data.get("password"))
    user.save()
    user.reset_key.reset_key = None
    user.reset_key.save()
    return Response(status=200)
