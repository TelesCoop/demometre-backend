from rest_framework import mixins, viewsets

from open_democracy_back.models.questionnaire_and_profiling_models import (
    ProfilingQuestion,
)
from open_democracy_back.serializers.questionnaire_and_profiling_serializers import (
    ProfilingQuestionSerializer,
)


class ProfilingQuestionView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProfilingQuestionSerializer
    queryset = ProfilingQuestion.objects.all()
