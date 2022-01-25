from django.db import models
from model_utils.models import TimeStampedModel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField

from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet


class HomePage(Page):
    body = RichTextField()

    api_fields = [
        APIField('body')
    ]


@register_snippet
class Question(TimeStampedModel):
    question = models.CharField(max_length=510, default="")
    objective = models.BooleanField(default=False)

    panels = [
        FieldPanel('question'),
        FieldPanel('objective'),
    ]
