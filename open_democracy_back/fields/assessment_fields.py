from django.utils import timezone
from rest_framework import serializers

from open_democracy_back.models import Assessment


class AssessmentField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return Assessment.objects.filter(initialization_date__lt=timezone.now())
