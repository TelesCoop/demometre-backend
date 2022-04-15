from django.utils import timezone
from rest_framework import serializers

from open_democracy_back.models import Participation


class ParticipationField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return Participation.objects.filter(
            user_id=self.context.get("request").user.id,
            assessment__initialization_date__lt=timezone.now(),
        )
