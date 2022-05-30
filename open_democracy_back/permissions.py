from rest_framework.permissions import BasePermission

from open_democracy_back.models.participation_models import Participation


class IsAssessmentAdmin(BasePermission):
    """
    Allows access only to the assessment initiator.
    TODO : access to expert
    """

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        participation_id = request.data.get(
            "participation_id"
        ) or request.query_params.get("participation_id")
        is_initator = bool(
            Participation.objects.get(id=participation_id).assessment.initiated_by_user
            == request.user
        )
        return bool(is_authenticated and is_initator)
