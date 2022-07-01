from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, viewsets
from my_auth.permissions import IsExpert
from my_auth.models import User
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models.animator_models import Workshop
from open_democracy_back.models.participation_models import Participation
from open_democracy_back.serializers.animator_serializers import (
    FullWorkshopSerializer,
    ParticipantResponseSerializer,
    ParticipantWithProfilingResponsesSerializer,
    WorkshopSerializer,
)


class WorkshopView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsExpert]
    serializer_class = WorkshopSerializer

    def get_queryset(self) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Workshop.objects.filter(animator_id=user.id)

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            id=request.data.get("id"),
        )


class FullWorkshopView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsExpert]
    serializer_class = FullWorkshopSerializer

    def get_queryset(self) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Workshop.objects.filter(animator_id=user.id)


class WorkshopParticipantView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsExpert]
    serializer_class = ParticipantWithProfilingResponsesSerializer

    def get_queryset(self, workshop_pk) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Participation.objects.filter(
            workshop__animator_id=user.id, workshop_id=workshop_pk
        )

    def create(self, request, *args, **kwargs):
        email = request.data["user_email"]
        username = request.data["user_username"]
        # TODO : if username change but same exists id --> update username (regarder l'id du user envoyé par le frontend)
        try:
            user = User.objects.get(username=username)
            # TODO : changer l'adresse mail si elle a été changé
        except ObjectDoesNotExist:
            user = User.objects.create(username=username, email=email)
        request.data["user_id"] = user.id
        responses_data = []
        if "responses" in request.data.keys():
            responses_data = request.data.pop("responses")
        htmlResponse = super().create(request, *args, **kwargs)
        participation = self.get_or_update_object(request, *args, **kwargs)

        for item in responses_data:
            if "participation_id" not in item:
                item["participation_id"] = participation.id
            try:
                participationResponse = participation.responses.get(
                    question_id=item["question_id"]
                )
                serializer = ParticipantResponseSerializer(
                    participationResponse, data=item
                )
            except ObjectDoesNotExist:
                serializer = ParticipantResponseSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        htmlResponse.data = ParticipantWithProfilingResponsesSerializer(
            participation
        ).data
        return htmlResponse

    def get_or_update_object(self, request, workshop_pk):
        return self.get_queryset(workshop_pk).get(
            user_id=request.data.get("user_id"),
        )
