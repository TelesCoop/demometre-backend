from rest_framework import mixins, viewsets
from open_democracy_back.models.pages_models import (
    EvaluationInitPage,
    EvaluationIntroPage,
    HomePage,
    ReferentialPage,
)

from open_democracy_back.serializers.page_serializers import (
    EvaluationInitPageSerializer,
    EvaluationIntroPageSerializer,
    HomePageSerializer,
    ReferentialPageSerializer,
)


class HomePageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = HomePageSerializer
    queryset = HomePage.objects.all()


class ReferentialPageView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ReferentialPageSerializer
    queryset = ReferentialPage.objects.all()


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
