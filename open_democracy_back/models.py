from django.db import models
from model_utils.models import TimeStampedModel
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField

from wagtail.core.models import Page
from wagtail.snippets.models import register_snippet


class HomePage(Page):
    # HomePage can be created only on the root
    parent_page_types = ["wagtailcore.Page"]

    tagline = models.CharField(max_length=127, default="")
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("tagline"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField('title'),
        APIField('tagline'),
        APIField('body'),
    ]


class BlogPage(Page):
    published_date = models.DateTimeField()
    body = RichTextField()
    private_field = models.CharField(max_length=255)

    content_panels = Page.content_panels + [
        FieldPanel("published_date"),
        FieldPanel("body"),
        FieldPanel("private_field"),
    ]

    # Export fields over the API
    api_fields = [
        APIField('published_date'),
        APIField('body'),
    ]


@register_snippet
class Question(TimeStampedModel):
    question = models.CharField(max_length=510, default="")
    objective = models.BooleanField(default=False)

    panels = [
        FieldPanel('question'),
        FieldPanel('objective'),
    ]
