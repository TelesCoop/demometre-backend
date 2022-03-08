from .base import *  # noqa: F401,F403
import rollbar

DEBUG = False

SECRET_KEY = config.getstr("security.secret_key")  # noqa: F405
ALLOWED_HOSTS = config.getlist("security.allowed_hosts")  # noqa: F405
STATIC_ROOT = config.getstr("staticfiles.static_root")  # noqa: F405

# rollbar
MIDDLEWARE.append(  # noqa: F405
    "rollbar.contrib.django.middleware.RollbarNotifierMiddleware"
)

ROLLBAR = {
    "access_token": config.getstr("bugs.rollbar_access_token"),  # noqa: F405
    "environment": "production",
    "root": BASE_DIR,  # noqa: F405
}

rollbar.init(**ROLLBAR)
