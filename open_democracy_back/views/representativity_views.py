from rest_framework import mixins, viewsets

from open_democracy_back.models.representativity_models import (
    RepresentativityCriteria,
)
from open_democracy_back.serializers.representativity_serializers import (
    RepresentativityCriteriaSerializer,
)


class RepresentativityCriteriaView(
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = RepresentativityCriteriaSerializer
    queryset = RepresentativityCriteria.objects.all()


# def publish_results_if_is_ready(assessment):
#     can_be_published = all(
#             [
#                 RuleContext(rule).does_respect_rule(
#                     profilingQuestionResponses.filter(
#                         question=rule.conditional_question
#                     ).first(),
#                 )
#                 for assessment_representativity in assessment.representativities.all()
#             ]
#         )
