from rest_framework import serializers
from my_auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "username", "email")
        optional_fields = ("first_name", "last_name", "username", "email")
