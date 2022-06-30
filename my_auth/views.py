import uuid
import re
from datetime import datetime

from django.conf.global_settings import AUTHENTICATION_BACKENDS
from django.contrib.auth import authenticate, login, logout
from my_auth.models import User

from django.http import HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from my_auth.emails import email_reset_password_link
from my_auth.models import UserResetKey
from open_democracy_back.exceptions import ErrorCode, ValidationFieldError

from .serializers import AuthSerializer

# Regular expression for validating an Email
regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"


@api_view(["POST"])
def frontend_signup(request):
    """
    Sign up user. If unknown user, change it to known user

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
    if User.objects.filter(email=data["email"]).count():
        raise ValidationFieldError("email", code=ErrorCode.EMAIL_ALREADY_EXISTS.value)
    if not re.fullmatch(regex, data["email"]):
        raise ValidationFieldError("email", code=ErrorCode.EMAIL_NOT_VALID.value)
    data["username"] = data["email"]

    if request.user.is_authenticated and request.user.is_unknown_user:
        user = request.user
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.email = data["email"]
        user.username = data["username"]
        user.set_password(data["password"])
        user_extra_data = user.extra_data
        user_extra_data.is_unknown_user = False
        user_extra_data.save()
    else:
        user = AuthSerializer(data=data)
        user.is_valid(raise_exception=True)

    user.save()

    login(request, user)

    return Response(status=201, data=AuthSerializer(user).data)


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
    if not re.fullmatch(regex, data["email"]):
        raise ValidationFieldError("email", code=ErrorCode.EMAIL_NOT_VALID.value)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise ValidationFieldError("email", code=ErrorCode.NO_EMAIL.value)

    user_auth = authenticate(username=user.username, password=password)

    if user_auth is not None:
        user_auth.backend = AUTHENTICATION_BACKENDS[0]
        login(request, user_auth)
        return Response(AuthSerializer(user_auth).data)
    else:
        raise ValidationFieldError(
            "password", code=ErrorCode.WRONG_PASSWORD_FOR_EMAIL.value
        )


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

    if not request.user.is_authenticated:
        raise NotAuthenticated()

    return Response(AuthSerializer(request.user).data)


@api_view(["POST"])
def front_end_reset_password_link(request):
    """Send a reset password link"""
    try:
        user = User.objects.get(email=request.data.get("email"), is_unknown_user=False)
    except User.DoesNotExist:
        raise ValidationFieldError("email", code=ErrorCode.NO_EMAIL.value)
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
            detail="The reset password key is wrong or already used.",
            code=ErrorCode.WRONG_PASSWORD_RESET_KEY.value,
        )

    is_valid_key = datetime.now() - user.reset_key.reset_key_datetime
    if is_valid_key.days != 0:
        raise PermissionDenied(
            detail="The reset password key is outdated (24h max).",
            code=ErrorCode.PASSWORD_RESET_KEY_OUTDATE.value,
        )

    user.set_password(request.data.get("password"))
    user.save()
    user.reset_key.reset_key = None
    user.reset_key.save()
    return Response(status=200)


@api_view(["POST"])
def front_end_create_unknown_user(request):
    """Create unknown user without email and password to save data related"""
    anonymous_name = "anonymous-" + str(User.objects.last().id + 1)
    user = User.objects.create(
        username=anonymous_name, email=anonymous_name, is_unknown_user=True
    )
    user.save()

    # log user
    login(request, user)

    return Response(status=201, data=AuthSerializer(user).data)
