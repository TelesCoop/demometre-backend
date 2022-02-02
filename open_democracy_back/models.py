from django.db import models
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    FieldRowPanel,
)
from wagtail.api import APIField
from wagtail.core.fields import RichTextField

from wagtail.core.models import Page, TranslatableMixin, Orderable
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
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
        APIField("title"),
        APIField("tagline"),
        APIField("body"),
    ]


@register_snippet
class Role(TranslatableMixin, ClusterableModel):
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("name"),
        InlinePanel("related_markers_ordered", label="Ordre des marqueurs"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Rôles"
        verbose_name = "Rôle"


@register_snippet
class Pillar(TranslatableMixin):
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Piliers"
        verbose_name = "Pilier"


@register_snippet
class Marker(TranslatableMixin):
    pillar = models.ForeignKey(Pillar, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("pillar"),
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Marqueurs"
        verbose_name = "Marqueur"


class MarkerOrderByRole(Orderable):
    role = ParentalKey(
        Role, on_delete=models.CASCADE, related_name="related_markers_ordered"
    )
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    panels = [
        SnippetChooserPanel("marker"),
    ]


@register_snippet
class Criteria(TranslatableMixin):
    marker = models.ForeignKey(Marker, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(
        verbose_name="N°",
        help_text="Place que doit occuper ce critère dans son marqueur",
    )
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("marker"),
        FieldPanel("order"),
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Critères"
        verbose_name = "Critère"
        ordering = ["order"]


@register_snippet
class Question(index.Indexed, TranslatableMixin, TimeStampedModel, ClusterableModel):
    # TODO : question : how to behave when you delete a criteria?
    #  Delete all question or not authorize if questions are linked ?
    criteria = models.ForeignKey(
        Criteria, null=True, blank=True, on_delete=models.SET_NULL
    )
    order = models.IntegerField(
        verbose_name="N°",
        help_text="Place que doit occuper cette question dans son critère",
    )
    title = models.CharField(max_length=125, default="")
    question = models.TextField(default="")
    objectivity = models.CharField(
        max_length=32,
        choices=[("objective", "objective"), ("subjective", "subjective")],
        default="subjective",
    )
    method = models.CharField(
        max_length=32,
        choices=[("quantitative", "quantitative"), ("qualitative", "qualitative")],
        blank=True,
    )

    class QuestionType(models.TextChoices):
        OPEN = "open", "Ouverte"
        UNIQUE_CHOICE = "unique_choice", "Choix unique"
        MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
        CLOSED_WITH_RANKING = "closed_with_ranking", "Fermée avec classement"
        CLOSED_WITH_SCALE = "closed_with_scale", "Fermée à échelle"
        BOOLEAN = "boolean", "Binaire oui / non"
        NUMERICAL = "numerical", "Numérique"

    type = models.CharField(
        max_length=32,
        choices=QuestionType.choices,
        default=QuestionType.OPEN,
        help_text="Choisir le type de question",
    )

    min = models.IntegerField(verbose_name="Valeur minimale", blank=True, null=True)
    max = models.IntegerField(verbose_name="Valeur maximale", blank=True, null=True)

    search_fields = [
        index.SearchField("question", partial_match=True),
    ]

    panels = [
        FieldPanel("criteria"),
        FieldPanel("order"),
        FieldPanel("title"),
        FieldPanel("question"),
        FieldPanel("objectivity"),
        FieldPanel("method"),
        FieldPanel("type"),
        InlinePanel(
            "response_choices",
            label="Choix de réponses possibles",
            help_text="Ne renseigner que si cela à un sens par rapport au type de question",
        ),
        FieldRowPanel(
            [
                FieldPanel("min"),
                FieldPanel("max"),
            ],
            heading="Valeurs extrêmes possibles",
            help_text="Ne renseigner que si cela à un sens par rapport au type de question",
        ),
        InlinePanel(
            "question_filters",
            label="Conditions d'affichage de la question",
        ),
    ]

    def __str__(self):
        return self.question

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Questions"
        verbose_name = "Question"
        ordering = ["order"]


class ResponseChoice(TranslatableMixin, TimeStampedModel, Orderable):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="response_choices"
    )
    response_choice = models.CharField(
        max_length=510, default="", verbose_name="Réponse possible"
    )

    def __str__(self):
        return self.response_choice

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Choix de réponse"
        verbose_name = "Choix de réponse"


class QuestionFilter(TimeStampedModel, Orderable, ClusterableModel):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="question_filters"
    )

    conditional_question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name="Filtre par question"
    )

    def get_possible_response(self):
        possible_responses = ResponseChoice.objects.filter(
            question_id=self.conditional_question.id
        )
        return {
            "question__in": [
                possible_responses,
            ]
        }

    response = models.ForeignKey(
        ResponseChoice,
        # limit_choices_to=get_possible_response,
        on_delete=models.CASCADE,
    )
