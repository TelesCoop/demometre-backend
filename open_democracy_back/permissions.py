from rest_framework.permissions import BasePermission
from open_democracy_back.models.assessment_models import Assessment


class IsAssessmentAdminOrReadOnly(BasePermission):
    """
    Allows access only to the assessment initiator.
    TODO : access to expert
    """

    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        assessment_id = request.data.get("assessment_id") or request.query_params.get(
            "assessment_id"
        )
        is_initator = bool(
            Assessment.objects.get(id=assessment_id).initiated_by_user == request.user
        )
        return bool((is_authenticated and is_initator) or request.method == "GET")
