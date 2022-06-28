from abc import ABC, abstractmethod
import operator
import rollbar
from django.utils import timezone
from django.db.models import QuerySet
from rest_framework import mixins, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from my_auth.utils import get_authenticated_or_anonymous_user_from_request
from my_auth.permissions import IsAuthenticatedOrAnonymous

from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin
from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
    Response,
)
from open_democracy_back.models.questionnaire_and_profiling_models import (
    BooleanOperator,
    ProfileDefinition,
    ProfileType,
)

from open_democracy_back.serializers.participation_serializers import (
    ParticipationSerializer,
    ParticipationResponseSerializer,
)

NUMERICAL_OPERATOR_CONVERSION = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne,
    "=": operator.eq,
}


class QuestionStrategy(ABC):
    @abstractmethod
    def does_respect_rule(self, rule: ProfileDefinition, response: Response):
        pass


class UniqueChoiceStrategy(QuestionStrategy):
    def does_respect_rule(self, rule: ProfileDefinition, response: Response):
        return response.unique_choice_response in rule.response_choices.all()


class MultipleChoiceStrategy(QuestionStrategy):
    def does_respect_rule(self, rule: ProfileDefinition, response: Response):
        return any(
            [
                response in rule.response_choices.all()
                for response in response.multiple_choice_response
            ]
        )


class BooleanStrategy(QuestionStrategy):
    def does_respect_rule(self, rule: ProfileDefinition, response: Response):
        return response.boolean_response == rule.boolean_response


class PercentageStrategy(QuestionStrategy):
    def does_respect_rule(self, rule: ProfileDefinition, response: Response):
        return NUMERICAL_OPERATOR_CONVERSION[rule.numerical_operator](
            response.percentage_response, rule.numerical_value
        )


RULES_STRATEGY = {
    "unique_choice": UniqueChoiceStrategy(),
    "multiple_choice": MultipleChoiceStrategy(),
    "boolean": BooleanStrategy(),
    "percentage": PercentageStrategy(),
}


class RuleContext:
    def __init__(self, rule: ProfileDefinition) -> None:
        self._strategy = RULES_STRATEGY[rule.type]
        self.rule = rule

    def does_respect_rule(self, response: Response) -> bool:
        if not response:
            return False
        return self._strategy.does_respect_rule(self.rule, response)


def isProfileRelevant(profileType, profilingQuestionResponses):
    if profileType.rules_intersection_operator == BooleanOperator.AND.value:
        return all(
            [
                RuleContext(rule).does_respect_rule(
                    profilingQuestionResponses.filter(
                        question=rule.conditional_question
                    ).first(),
                )
                for rule in profileType.rules.all()
            ]
        )
    if profileType.rules_intersection_operator == BooleanOperator.OR.value:
        return any(
            [
                RuleContext(rule).does_respect_rule(
                    profilingQuestionResponses.filter(
                        question=rule.conditional_question
                    ).first(),
                )
                for rule in profileType.rules.all()
            ]
        )


def assignProfilesToParticipation(participation):
    profilingQuestionResponses = participation.responses.filter(
        question__profiling_question=True
    )
    profileTypes = ProfileType.objects.all()
    for profileType in profileTypes:
        if isProfileRelevant(profileType, profilingQuestionResponses):
            participation.profiles.add(profileType)


class ParticipationView(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrAnonymous]
    serializer_class = ParticipationSerializer

    def get_queryset(self) -> QuerySet:
        user = get_authenticated_or_anonymous_user_from_request(self.request)
        return Participation.objects.filter(
            user_id=user.id,
            assessment__initialization_date__lte=timezone.now(),
        )

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            assessment_id=request.data.get("assessment_id"),
        )


class ParticipationResponseView(
    mixins.ListModelMixin, UpdateOrCreateModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticatedOrAnonymous]
    serializer_class = ParticipationResponseSerializer

    def get_queryset(self):
        user = get_authenticated_or_anonymous_user_from_request(self.request)
        query = ParticipationResponse.objects.filter(participation__user_id=user.id)

        context = self.request.query_params.get("context")
        if context:
            is_profiling_question = context == "profiling"
            query = query.filter(question__profiling_question=is_profiling_question)

        participation_id = self.request.query_params.get("participation_id")
        if participation_id and type(participation_id) is int:
            query = query.filter(participation_id=participation_id)
        else:
            rollbar.report_message(
                f"Need participation_id to retrieve participation responses of user {user.email} but got {participation_id} in {context} context",
                "warning",
            )

        return query

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            participation_id=request.data.get("participation_id"),
            question_id=request.data.get("question_id"),
        )


class CompletedQuestionsParticipationView(APIView):
    permission_classes = [IsAuthenticatedOrAnonymous]

    def patch(self, request, pk):
        participation = Participation.objects.get(user_id=request.user.id, id=pk)
        pillard_id = request.data.get("pillar_id")

        if request.data.get("profiling_question"):
            participation.is_profiling_questions_completed = True
            participation.save()
            assignProfilesToParticipation(participation)
        elif participation.is_profiling_questions_completed and pillard_id:
            participation_pillar_completed = (
                participation.participationpillarcompleted_set.get(pillar=pillard_id)
            )
            participation_pillar_completed.completed = True
            participation_pillar_completed.save()
        else:
            return RestResponse(status=status.HTTP_400_BAD_REQUEST)
        serializer = ParticipationSerializer(participation)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)
