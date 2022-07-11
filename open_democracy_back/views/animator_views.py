from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import mixins, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response as RestResponse
from my_auth.models import User
from open_democracy_back.mixins.update_or_create_mixin import UpdateOrCreateModelMixin

from open_democracy_back.models.animator_models import Participant, Workshop
from open_democracy_back.models.participation_models import (
    Participation,
    ParticipationResponse,
)
from open_democracy_back.permissions import IsWorkshopExpert
from open_democracy_back.serializers.animator_serializers import (
    FullWorkshopSerializer,
    WorkshopParticipationResponseSerializer,
    WorkshopParticipationWithProfilingResponsesSerializer,
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


class WorkshopParticipationView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsWorkshopExpert]
    serializer_class = WorkshopParticipationWithProfilingResponsesSerializer

    def get_queryset(self, workshop_pk) -> QuerySet:
        user = User.objects.get(pk=self.request.user.id)
        return Participation.objects.filter(
            workshop__animator_id=user.id, workshop_id=workshop_pk
        )

    def create(self, request, *args, **kwargs):
        # Create or update a workshop participation with all its profiling responses

        # 1 - Retrieve Participant if exists or create new one
        email = request.data["participant_email"]
        name = request.data["participant_name"]
        try:
            if "id" in request.data.keys():
                participationId = request.data["id"]
                participant = Participation.objects.get(id=participationId).participant
            else:
                participant = Participant.objects.get(name=name)
            participant.name = name
            participant.email = email
            participant.save()
        except ObjectDoesNotExist:
            participant = Participant.objects.create(name=name, email=email)
        # Add participant_id in data dict before create or update participation
        request.data["participant_id"] = participant.id

        # 2 - Pop responses from data before create or update participation (Otherwise serializer will reject it)
        responses_data = []
        if "responses" in request.data.keys():
            responses_data = request.data.pop("responses")

        # 3 - Create or update participation
        response = super().create(request, *args, **kwargs)
        participation = self.get_or_update_object(request, *args, **kwargs)

        # 4 - Create or update all profiling responses of participation
        for item in responses_data:
            if "participation_id" not in item:
                item["participation_id"] = participation.id
            try:
                participationResponse = participation.responses.get(
                    question_id=item["question_id"]
                )
                serializer = WorkshopParticipationResponseSerializer(
                    participationResponse, data=item
                )
            except ObjectDoesNotExist:
                serializer = WorkshopParticipationResponseSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        # 5 - Update htmlResponse data to respond with all participation responses data
        response.data = WorkshopParticipationWithProfilingResponsesSerializer(
            participation
        ).data
        return response

    def get_or_update_object(self, request, workshop_pk):
        return self.get_queryset(workshop_pk).get(
            user_id=request.data.get("participation_id"),
        )


class WorkshopParticipationResponseView(
    mixins.ListModelMixin,
    UpdateOrCreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsWorkshopExpert]
    serializer_class = WorkshopParticipationResponseSerializer

    def get_queryset(self, workshop_pk, participation_pk) -> QuerySet:
        return ParticipationResponse.objects.filter(
            participation__workshop__animator_id=self.request.user.id,
            participation__workshop_id=workshop_pk,
            participation_id=participation_pk,
        )

    def get_or_update_object(self, request, workshop_pk, participation_pk):
        return self.get_queryset(workshop_pk, participation_pk).get(
            participation_id=request.data.get("participation_id"),
            question_id=request.data.get("question_id"),
        )


class CloseWorkshopView(APIView):
    permission_classes = [IsWorkshopExpert]

    def patch(self, request, workshop_pk):
        workshop = Workshop.objects.get(
            animator_id=self.request.user.id, id=workshop_pk
        )
        workshop.closed = True
        workshop.save()

        for participation in workshop.participations.all():
            # if there is a email create user or retrieve existing user and attribut him the participation
            if participation.participant.email:
                user = User.objects.get_or_create(
                    email=participation.participant.email,
                    defaults={"username": participation.participant.email},
                )
                participation.user = user
                participation.save()
                # TODO : what append if there is a participation with this user and this assessment (like this it breaks)

        serializer = WorkshopSerializer(workshop)
        return RestResponse(serializer.data, status=status.HTTP_200_OK)
