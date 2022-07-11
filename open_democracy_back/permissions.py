from django.utils import timezone
from rest_framework.permissions import BasePermission
from open_democracy_back.models.animator_models import Workshop

from open_democracy_back.models import Participation
from open_democracy_back.models.assessment_models import Assessment


class IsAssessmentAdminOrReadOnly(BasePermission):
    """
    Allows access only to the assessment initiator and the assessment expert if there is one.
    """

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        assessment_id = (
            request.data.get("assessment_id")
            or request.query_params.get("assessment_id")
            or view.kwargs.get("assessment_pk", None)
        )
        initiator_assessment_queryset = Assessment.objects.filter(
            initiated_by_user_id=request.user.id
        )

        expert_assessment_queryset = Assessment.objects.filter(experts=request.user)

        if assessment_id:
            is_initator = initiator_assessment_queryset.filter(
                id=assessment_id
            ).exists()
            is_expert = expert_assessment_queryset.filter(id=assessment_id).exists()
        else:
            current_participation = Participation.objects.filter_current_available(
                request.user.id, timezone.now()
            )
            is_initator = initiator_assessment_queryset.filter(
                participations__in=current_participation
            ).exists()
            is_expert = expert_assessment_queryset.filter(
                participations__in=current_participation
            ).exists()

        return bool(
            (is_authenticated and (is_initator or is_expert)) or request.method == "GET"
        )


class IsWorkshopExpert(BasePermission):
    """
    Allows access only to the workshop expert.
    """

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        workshop_id = (
            request.data.get("workshop_id")
            or request.query_params.get("workshop_id")
            or view.kwargs.get("workshop_pk", None)
            or view.kwargs.get("pk", None)
        )
        is_expert = bool(Workshop.objects.get(id=workshop_id).animator == request.user)
        return bool(is_authenticated and is_expert)
