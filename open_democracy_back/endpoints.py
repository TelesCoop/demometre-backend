from wagtail.api.v2.views import BaseAPIViewSet, PagesAPIViewSet

from open_democracy_back.models import Question, HomePage


class QuestionModelAPIEndpoint(BaseAPIViewSet):

    model = Question

    body_fields = BaseAPIViewSet.body_fields + [
        'question',
        'objective',
    ]

    listing_default_fields = BaseAPIViewSet.listing_default_fields + [
        'question',
        'objective',
    ]


class HomePagesAPIEndpoint(PagesAPIViewSet):
    def __init__(self):
        super(HomePagesAPIEndpoint, self).__init__()
        self.model = HomePage
        self.name = 'Home pages'

    def get_queryset(self):
        return HomePage.objects.filter(id__in=self.get_base_queryset().values_list('id', flat=True))

    body_fields = PagesAPIViewSet.body_fields + [
        'tagline',
        'body',
    ]

    listing_default_fields = PagesAPIViewSet.listing_default_fields + [
        'tagline',
        'body',
    ]

