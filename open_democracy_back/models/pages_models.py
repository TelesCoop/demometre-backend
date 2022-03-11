from typing import List
from django.db import models
from wagtail.admin.edit_handlers import (
    FieldPanel,
)
from wagtail.api import APIField

from wagtail.core.models import Page


class HomePage(Page):
    # HomePage can be created only on the root
    parent_page_types = ["wagtailcore.Page"]
    preview_modes = None

    introduction = models.CharField(max_length=255, default="")

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    api_fields = [
        APIField("title"),
        APIField("introduction"),
    ]

    class Meta:
        verbose_name = "Page d'accueil"


class ReferentialPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    introduction = models.CharField(max_length=255, default="")

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
    ]

    class Meta:
        verbose_name = "Référentiel"
