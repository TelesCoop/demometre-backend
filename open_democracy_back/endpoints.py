from wagtail.api.v2.views import BaseAPIViewSet

from open_democracy_back.models import Question


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
