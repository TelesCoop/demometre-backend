from rest_framework import serializers
from open_democracy_back.models.assessment_models import Assessment

from open_democracy_back.models.participation_models import Participation
from open_democracy_back.models.questionnaire_and_profiling_models import Role
from django.contrib.auth.models import User


class ParticipationSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        source="user", queryset=User.objects.all()
    )
    assessment_id = serializers.PrimaryKeyRelatedField(
        source="assessment", queryset=Assessment.objects.all()
    )
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all()
    )

    class Meta:
        model = Participation
        fields = ["id", "user_id", "assessment_id", "role_id", "consent"]
