from .base import *  # noqa: F401,F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-35rbfpb*$*g#+za7iz0*w1+$80)@*le31f--mv3287c*th273p"

BASE_URL = "http://localhost:8000"

FRONT_END_URL = "http://localhost:3000"
SESSION_COOKIE_SAMESITE = None
CORS_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = ("http://localhost:3000",)

CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]


EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@telescoop.fr"

INSTALLED_APPS.append("django_extensions")
