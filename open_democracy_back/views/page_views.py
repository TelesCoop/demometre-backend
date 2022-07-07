from rest_framework import mixins, viewsets
from open_democracy_back.models.pages_models import (
    EvaluationInitPage,
    EvaluationIntroPage,
    EvaluationQuestionnairePage,
    HomePage,
    ProjectPage,
    ReferentialPage,
    ResultsPage,
    UsagePage,
)

from open_democracy_back.serializers.page_serializers import (
    EvaluationInitPageSerializer,
    EvaluationIntroPageSerializer,
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


class EvaluationIntroPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EvaluationIntroPageSerializer
    queryset = EvaluationIntroPage.objects.all()


class EvaluationInitPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EvaluationInitPageSerializer
    queryset = EvaluationInitPage.objects.all()


class EvaluationQuestionnairePageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = EvaluationQuestionnairePageSerializer
    queryset = EvaluationQuestionnairePage.objects.all()
