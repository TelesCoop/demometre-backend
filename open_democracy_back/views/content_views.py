from rest_framework import mixins, viewsets
from open_democracy_back.models.contents_models import (
    BlogPost,
    Feedback,
    Partner,
    People,
    Resource,
)
from open_democracy_back.serializers.content_serializers import (
    BlogPostSerializer,
    FeedbackSerializer,
    PartnerSerializer,
    PeopleSerializer,
    ResourceSerializer,
)


class FeedbackView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()


class BlogPostView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BlogPostSerializer
    queryset = BlogPost.objects.all()


class ResourceView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = ResourceSerializer
    queryset = Resource.objects.all()


class PartnerView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PartnerSerializer
    queryset = Partner.objects.all()


class PeopleView(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PeopleSerializer
    queryset = People.objects.all()
