from collections import OrderedDict

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class CurrentUserField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, _):
        id = self.context.get("request").user.id
        try:
            return User.objects.get(id=id)
        except ObjectDoesNotExist:
            self.fail("does_not_exist", pk_value=id)

    def get_choices(self, cutoff=None):
        user = self.context.get("request").user
        return OrderedDict([(self.to_representation(user), self.display_value(user))])
