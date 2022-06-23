from django.contrib.auth.models import User, AnonymousUser
from django.core import exceptions
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from rest_framework import serializers


class AuthSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=100)
    password = serializers.CharField(write_only=True, required=True, max_length=100)

    is_anonymous = serializers.BooleanField(source="extra_data.is_anonymous")

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "is_anonymous",
        )

    def validate_password(self, value):
        errors = None
        try:
            password_validation.validate_password(password=value, user=User)
        except exceptions.ValidationError as e:
            errors = {"password": list(e.messages)}

        if errors:
            raise serializers.ValidationError(errors)
        return make_password(value)


# TODO clean this function
class CurrentUserOrAnonymousField(serializers.CurrentUserDefault):
    def __call__(self, serializer_field):
        if isinstance(serializer_field.context["request"].user, AnonymousUser):
            anonymous_username = serializer_field.context["request"].query_params.get(
                "anonymous"
            )
            return User.objects.get(username=anonymous_username)
        return serializer_field.context["request"].user
