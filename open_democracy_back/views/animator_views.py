from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, viewsets
from my_auth.models import User
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models.animator_models import Workshop
from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
)
from open_democracy_back.permissions import IsWorkshopExpert
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
    serializer_class = WorkshopSerializer

    def get_queryset(self) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)

        return Workshop.objects.filter(
            animator_id=user.id,
            assessment__royalty_payed=True,
        )

    def get_or_update_object(self, request):
        return self.get_queryset().get(
            id=request.data.get("id"),
        )


class FullWorkshopView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsWorkshopExpert]
    serializer_class = FullWorkshopSerializer

    def get_queryset(self) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Workshop.objects.filter(animator_id=user.id)


class WorkshopParticipantView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsWorkshopExpert]
    serializer_class = ParticipantWithProfilingResponsesSerializer

    def get_queryset(self, workshop_pk) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Participation.objects.filter(
            workshop__animator_id=user.id, workshop_id=workshop_pk
        )

    def create(self, request, *args, **kwargs):
        email = request.data["user_email"]
        username = request.data["user_username"]
        try:
            if "id" in request.data.keys():
                participantId = request.data["id"]
                user = Participation.objects.get(id=participantId).user
            else:
                user = User.objects.get(username=username)
            user.username = username
            user.email = email
            user.save()
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


class WorkshopParticipantResponseView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsWorkshopExpert]
    serializer_class = ParticipantResponseSerializer

    def get_queryset(self, workshop_pk, participant_pk) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return ParticipationResponse.objects.filter(
            participation__workshop__animator_id=user.id,
            participation__workshop_id=workshop_pk,
            participation_id=participant_pk,
        )

    def get_or_update_object(self, request, workshop_pk, participant_pk):
        return self.get_queryset(workshop_pk, participant_pk).get(
            participation_id=request.data.get("participation_id"),
            question_id=request.data.get("question_id"),
        )
