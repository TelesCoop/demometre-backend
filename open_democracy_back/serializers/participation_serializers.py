from rest_framework import serializers

from open_democracy_back.models.participation_models import Participation


class ParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participation
        fields = ["id", "user_id", "assessment_id", "role_id", "consent"]
        read_only_fields = ["user_id", "assessment_id", "role_id"]
