import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserResetKey(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reset_key"
    )
    reset_key = models.UUIDField(default=uuid.uuid4, null=True)
    reset_key_datetime = models.DateTimeField(null=True, blank=True)


class UserExtraData(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="extra_data"
    )
    is_anonymous = models.BooleanField(default=False)


# TODO create migration to force user to have extra_data
@receiver(post_save, sender=get_user_model())
def create_user_extra_data(sender, instance, created, **kwargs):
    try:
        instance.extra_data
    except UserExtraData.DoesNotExist:
        UserExtraData.objects.create(user=instance)
