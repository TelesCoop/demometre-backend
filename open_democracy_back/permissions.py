from rest_framework.permissions import BasePermission
from open_democracy_back.models.animator_models import Workshop


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
