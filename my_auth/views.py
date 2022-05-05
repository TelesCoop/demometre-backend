import uuid
from datetime import datetime

from django.conf.global_settings import AUTHENTICATION_BACKENDS
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from my_auth.emails import email_reset_password_link
from my_auth.models import UserResetKey
from open_democracy_back.exceptions import ValidationFieldError

from .serializers import AuthSerializer


@api_view(["POST"])
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
        raise ValidationFieldError("email", code="email_already_exists")
    data["username"] = request.data["email"]
    user = AuthSerializer(data=data)
    user.is_valid(raise_exception=True)
    user.save()

    userAuth = authenticate(username=data["username"], password=data["password"])
    userAuth.backend = AUTHENTICATION_BACKENDS[0]
    login(request, userAuth)

    return Response(status=201, data=AuthSerializer(userAuth).data)


@api_view(["POST"])
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
        raise ValidationFieldError("email", code="no_email")

    user_auth = authenticate(username=user.username, password=password)

    if user_auth is not None:
        user_auth.backend = AUTHENTICATION_BACKENDS[0]
        login(request, user_auth)
        return Response(AuthSerializer(user_auth).data)
    else:
        raise ValidationFieldError("password", code="wrong_password_for_email")


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def frontend_logout(request):
    """Log out view."""
    logout(request)
    return HttpResponse(status=200)


@api_view(["GET"])
@ensure_csrf_cookie
def who_am_i(request):
    """Returns information about the current user."""
    if request.user.is_anonymous:
        raise NotAuthenticated()

    return Response(AuthSerializer(request.user).data)


@api_view(["POST"])
def front_end_reset_password_link(request):
    """Send a reset password link"""
    try:
        user = User.objects.get(email=request.data.get("email"))
    except User.DoesNotExist:
        raise ValidationFieldError("email", code="no_email")
    if UserResetKey.objects.get(user=user):
        UserResetKey.objects.get(user=user).delete()
    UserResetKey.objects.create(
        user=user, reset_key=uuid.uuid4(), reset_key_datetime=datetime.now()
    )
    email_reset_password_link(request, user)
    return Response(status=200)


@api_view(["POST"])
def front_end_reset_password(request):
    """Send a reset password"""
    try:
        user = User.objects.get(
            reset_key__reset_key=request.data.get("reset_key"),
        )
    except User.DoesNotExist:
        raise PermissionDenied(
            detail="There is not user with this reset_key", code=None
        )

    is_valid_key = datetime.now() - user.reset_key.reset_key_datetime
    if is_valid_key.days != 0:
        raise PermissionDenied(
            detail="The reset_key do not correspond to last 24H", code=None
        )

    user.set_password(request.data.get("password"))
    user.save()
    user.reset_key.reset_key = None
    user.reset_key.save()
    return Response(status=200)
