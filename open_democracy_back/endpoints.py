from wagtail.api.v2.views import BaseAPIViewSet, PagesAPIViewSet

from open_democracy_back.models import (
    ProfilingQuestion,
    QuestionnaireQuestion,
    HomePage,
)


QUESTION_FIELDS = [
    "code",
    "name",
    "question_statement",
    "description",
    "type",
    "objectivity",
]


class QuestionnaireQuestionModelAPIEndpoint(BaseAPIViewSet):

    model = QuestionnaireQuestion

    body_fields = BaseAPIViewSet.body_fields + QUESTION_FIELDS

    listing_default_fields = BaseAPIViewSet.listing_default_fields + QUESTION_FIELDS


class ProfilingQuestionModelAPIEndpoint(BaseAPIViewSet):

    model = ProfilingQuestion

    body_fields = BaseAPIViewSet.body_fields + QUESTION_FIELDS

    listing_default_fields = BaseAPIViewSet.listing_default_fields + QUESTION_FIELDS


class HomePagesAPIEndpoint(PagesAPIViewSet):
    def __init__(self):
        super(HomePagesAPIEndpoint, self).__init__()
        self.model = HomePage
        self.name = "Home pages"

    def get_queryset(self):
        return HomePage.objects.filter(
            id__in=self.get_base_queryset().values_list("id", flat=True)
        )

    body_fields = PagesAPIViewSet.body_fields + [
        "introduction",
    ]

    listing_default_fields = PagesAPIViewSet.listing_default_fields + [
        "introduction",
    ]
