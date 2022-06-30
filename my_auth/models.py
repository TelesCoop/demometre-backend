import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_unknown_user = models.BooleanField(default=False)


class UserResetKey(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reset_key"
    )
    reset_key = models.UUIDField(default=uuid.uuid4, null=True)
    reset_key_datetime = models.DateTimeField(null=True, blank=True)
