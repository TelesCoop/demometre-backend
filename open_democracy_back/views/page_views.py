from rest_framework import mixins, viewsets
from open_democracy_back.models.pages_models import (
    AnimatorPage,
    EvaluationInitiationPage,
    EvaluationQuestionnairePage,
    HomePage,
    ProjectPage,
    ReferentialPage,
    ResultsPage,
    UsagePage,
)

from open_democracy_back.serializers.page_serializers import (
    AnimatorPageSerializer,
    EvaluationInitiationPageSerializer,
    EvaluationQuestionnairePageSerializer,
    HomePageSerializer,
    ProjectPageSerializer,
    ReferentialPageSerializer,
    ResultsPageSerializer,
    UsagePageSerializer,
)


class HomePageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = HomePageSerializer
    queryset = HomePage.objects.all()


class UsagePageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UsagePageSerializer
    queryset = UsagePage.objects.all()


class ReferentialPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ReferentialPageSerializer
    queryset = ReferentialPage.objects.all()


class ResultsPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ResultsPageSerializer
    queryset = ResultsPage.objects.all()


class ProjectPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ProjectPageSerializer
    queryset = ProjectPage.objects.all()


class EvaluationInitiationPageSerializerView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EvaluationInitiationPageSerializer
    queryset = EvaluationInitiationPage.objects.all()


class EvaluationQuestionnairePageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EvaluationQuestionnairePageSerializer
    queryset = EvaluationQuestionnairePage.objects.all()


class AnimatorPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = AnimatorPageSerializer
    queryset = AnimatorPage.objects.all()
