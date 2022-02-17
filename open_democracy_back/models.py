import operator
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
    name = models.CharField(verbose_name="Nom", max_length=125)

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
class Pillar(models.Model):
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce pilier",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("code"),
    ]

    def __str__(self):
        return self.get_code() + ": " + self.name

    def get_code(self):
        return self.code

    class Meta:
        verbose_name_plural = "1. Piliers"
        verbose_name = "Pilier"
        ordering = ["code"]


@register_snippet
class Marker(index.Indexed, models.Model):
    pillar = models.ForeignKey(Pillar, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce marqueur dans son pilier",
    )

    panels = [
        FieldPanel("pillar"),
        FieldPanel("name"),
        FieldPanel("code"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.get_code() + ": " + self.name

    def get_code(self):
        return self.pillar.get_code() + self.code

    class Meta:
        verbose_name_plural = "2. Marqueurs"
        verbose_name = "Marqueur"
        ordering = ["code"]


class MarkerOrderByRole(Orderable):
    role = ParentalKey(
        Role, on_delete=models.CASCADE, related_name="related_markers_ordered"
    )
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    panels = [
        SnippetChooserPanel("marker"),
    ]


@register_snippet
class Criteria(index.Indexed, models.Model):
    marker = models.ForeignKey(Marker, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce critère dans son marqueur",
    )

    panels = [
        FieldPanel("marker"),
        FieldPanel("name"),
        FieldPanel("code"),
    ]

    search_fields = [index.SearchField("name", partial_match=True)]

    def __str__(self):
        return self.get_code() + ": " + self.name

    def get_code(self):
        return self.marker.get_code() + "." + self.code

    class Meta:
        verbose_name_plural = "3. Critères"
        verbose_name = "Critère"
        ordering = ["code"]


class QuestionType(models.TextChoices):
    OPEN = "open", "Ouverte"
    UNIQUE_CHOICE = "unique_choice", "Choix unique"
    MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
    CLOSED_WITH_RANKING = "closed_with_ranking", "Fermée avec classement"
    CLOSED_WITH_SCALE = "closed_with_scale", "Fermée à échelle"
    BOOLEAN = "boolean", "Binaire oui / non"
    NUMERICAL = "numerical", "Numérique"


class QuestionBase(index.Indexed, TimeStampedModel, ClusterableModel):
    name = models.CharField(max_length=125, default="")
    question = models.TextField(default="")

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
        index.SearchField("name", partial_match=True),
    ]

    panels = [
        FieldPanel("name"),
        FieldPanel("question"),
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
    ]

    class Meta:
        abstract = True


class ResponseChoiceBase(TimeStampedModel, Orderable):
    response_choice = models.CharField(
        max_length=510, default="", verbose_name="Réponse possible"
    )

    def __str__(self):
        return self.response_choice

    class Meta:
        verbose_name_plural = "Choix de réponse"
        verbose_name = "Choix de réponse"
        abstract = True


@register_snippet
class Question(QuestionBase):
    # TODO : question : how to behave when you delete a criteria?
    #  Delete all question or not authorize if questions are linked ?
    criteria = models.ForeignKey(
        Criteria, null=True, blank=True, on_delete=models.SET_NULL
    )
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de cette question dans son critère",
    )

    objectivity = models.CharField(
        max_length=32,
        choices=[("objective", "Objective"), ("subjective", "Subjective")],
        default="subjective",
    )
    method = models.CharField(
        max_length=32,
        choices=[("quantitative", "Quantitative"), ("qualitative", "Qualitative")],
        blank=True,
    )

    panels = [
        FieldPanel("criteria"),
        FieldPanel("code"),
        FieldPanel("objectivity"),
        FieldPanel("method"),
    ] + QuestionBase.panels

    search_fields = QuestionBase.search_fields + [
        index.SearchField("__str__", partial_match=True),
    ]

    def __str__(self):
        return self.get_code() + ": " + self.name

    def get_code(self):
        return self.criteria.get_code() + self.code

    class Meta(QuestionBase.Meta):
        verbose_name_plural = "4. Questions"
        verbose_name = "Question"
        ordering = ["code"]


class ResponseChoice(ResponseChoiceBase):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="response_choices"
    )

    class Meta(ResponseChoiceBase.Meta):
        pass


@register_snippet
class Profiling(QuestionBase):
    order = models.IntegerField(
        verbose_name="N°",
        help_text="Donne l'ordre d'affichage des questions de profilage",
    )

    panels = [
        FieldPanel("order"),
    ] + QuestionBase.panels

    def __str__(self):
        return self.name

    class Meta(QuestionBase.Meta):
        verbose_name_plural = "Questions de Profilage"
        verbose_name = "Question de Profilage"
        ordering = ["order"]


class ProfilingResponseChoice(ResponseChoiceBase):
    profiling_question = ParentalKey(
        Profiling, on_delete=models.CASCADE, related_name="response_choices"
    )

    class Meta(ResponseChoiceBase.Meta):
        pass


NUMERICAL_OPERATOR = [
    ("<", "<"),
    (">", ">"),
    ("<=", "<="),
    (">=", ">="),
    ("!=", "!="),
    ("=", "="),
]
BOOLEAN_OPERATOR = [("and", "et"), ("or", "ou")]
NUMERICAL_OPERATOR_CONVERSION = {
    "<": operator.lt,
    ">": operator.gt,
    "<=": operator.le,
    ">=": operator.ge,
    "!=": operator.ne,
    "=": operator.eq,
}


class QuestionFilter(TimeStampedModel, Orderable, ClusterableModel):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="question_filters"
    )

    conditional_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Filtre par question",
        related_name="questions_that_depend_on_me",
    )

    intersection_operator = models.CharField(
        max_length=8, choices=BOOLEAN_OPERATOR, blank=True
    )

    # if conditional question is unique or multiple choices type
    response_choices = models.ManyToManyField(ResponseChoice)

    # if conditional question is numerical or close with scale
    numerical_operator = models.CharField(
        max_length=8, choices=NUMERICAL_OPERATOR, blank=True
    )
    numerical_value = models.IntegerField(blank=True, null=True)

    # if conditional question is boolean
    boolean_response = models.BooleanField(blank=True, null=True)


# @register_snippet
# class ProfileType(models.Model):
#     name = models.CharField(max_length=125, default="")

#     class Meta():
#         verbose_name_plural = "Types de profil"
#         verbose_name = "Type de profil"
