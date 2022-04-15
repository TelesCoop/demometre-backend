from typing import List
from django.db import models
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import (
    FieldPanel,
)
from wagtail.api import APIField

from wagtail.core.models import Page

from open_democracy_back.models.questionnaire_and_profiling_models import (
    SIMPLE_RICH_TEXT_FIELD_FEATURE,
)


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


class EvaluationIntroPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    account_incentive_title = models.CharField(max_length=68, default="")
    account_incentive = models.CharField(max_length=255, default="")
    introduction = models.TextField(default="")
    data_consent = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Consentement sur les données personnelles",
        help_text="Demande de consentement à conserver les données personnelles demandées, RGPD",
    )

    content_panels = Page.content_panels + [
        FieldPanel("account_incentive_title"),
        FieldPanel("account_incentive"),
        FieldPanel("introduction"),
        FieldPanel("data_consent"),
    ]

    class Meta:
        verbose_name = "Intro à l'évaluation"


class EvaluationInitPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    introduction = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Explication de l'initialisation",
        help_text="Expliquer qu'aucune évaluation n'existe dans cette localité là, que des questions sur la vie politique de la ville précise seront posées, qu'il faut être connecté pour pouvoir initer une évaluation etc",
    )

    public_name_question = models.TextField(
        verbose_name="Enoncé de la question pour la publication ou non du nom de l'initateur",
        default="",
        help_text="Question RGPD - La réponse est oui / non - Si l'évaluation est faite au nom d'une association alors c'est le nom de cette association qui sera affichée",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("public_name_question"),
    ]

    class Meta:
        verbose_name = "Initialisation d'une évaluation"
