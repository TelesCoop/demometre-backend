from django.db import models
from django import forms
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    FieldRowPanel,
    MultiFieldPanel,
)
from wagtail.core.fields import RichTextField

from wagtail.core.models import TranslatableMixin, Orderable
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from open_democracy_back.constants import NUMERICAL_OPERATOR

SIMPLE_RICH_TEXT_FIELD_FEATURE = [
    "bold",
    "italic",
    "link",
    "ol",
    "ul",
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

    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Description pour le référentiel",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("code"),
        FieldPanel("description"),
    ]

    def __str__(self):
        return f"{self.code}: {self.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        [child_marker.save() for child_marker in self.markers.all()]

    class Meta:
        verbose_name_plural = "1. Piliers"
        verbose_name = "1. Pilier"
        ordering = ["code"]


class ReferentielFields(models.Model):
    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Description pour le référentiel",
    )
    score_1 = models.TextField(
        blank=True,
        verbose_name="Score = 1",
        help_text="Description pour le référentiel",
        default="",
    )
    score_2 = models.TextField(
        blank=True,
        verbose_name="Score = 2",
        help_text="Description pour le référentiel",
        default="",
    )
    score_3 = models.TextField(
        blank=True,
        verbose_name="Score = 3",
        help_text="Description pour le référentiel",
        default="",
    )
    score_4 = models.TextField(
        blank=True,
        verbose_name="Score = 4",
        help_text="Description pour le référentiel",
        default="",
    )

    panels = [
        FieldPanel("description"),
        FieldPanel("score_1"),
        FieldPanel("score_2"),
        FieldPanel("score_3"),
        FieldPanel("score_4"),
    ]

    class Meta:
        abstract = True


@register_snippet
class Marker(index.Indexed, ReferentielFields):
    pillar = models.ForeignKey(
        Pillar, null=True, blank=True, on_delete=models.SET_NULL, related_name="markers"
    )
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce marqueur dans son pilier",
    )
    concatenated_code = models.CharField(max_length=4, default="")

    panels = [
        FieldPanel("pillar"),
        FieldPanel("name"),
        FieldPanel("code"),
    ] + ReferentielFields.panels

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return f"{self.concatenated_code}: {self.name}"

    def save(self, *args, **kwargs):
        self.concatenated_code = (self.pillar.code if self.pillar else "") + self.code
        super().save(*args, **kwargs)
        [child_criteria.save() for child_criteria in self.criterias.all()]

    class Meta:
        verbose_name_plural = "2. Marqueurs"
        verbose_name = "2. Marqueur"
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
class ThematicTag(TagBase):
    class Meta:
        verbose_name = "Thématique"
        verbose_name_plural = "Thématiques"


@register_snippet
class Criteria(index.Indexed, ReferentielFields):
    marker = models.ForeignKey(
        Marker,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="criterias",
    )
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce critère dans son marqueur",
    )
    concatenated_code = models.CharField(max_length=6, default="")
    thematic_tags = models.ManyToManyField(
        ThematicTag, blank=True, verbose_name="Thématiques"
    )

    panels = [
        FieldPanel("marker"),
        FieldPanel("name"),
        FieldPanel("code"),
        FieldPanel("thematic_tags", widget=forms.CheckboxSelectMultiple),
    ] + ReferentielFields.panels

    search_fields = [index.SearchField("name", partial_match=True)]

    def __str__(self):
        return f"{self.concatenated_code}: {self.name}"

    def save(self, *args, **kwargs):
        self.concatenated_code = (
            self.marker.concatenated_code + "." if self.marker else ""
        ) + self.code
        super().save(*args, **kwargs)
        print(self.questions.all())
        # Use proxy QuestionnaireQuestion
        child_questions = QuestionnaireQuestion.objects.filter(criteria_id=self.id)
        [child_question.save() for child_question in child_questions]

    class Meta:
        verbose_name_plural = "3. Critères"
        verbose_name = "3. Critère"
        ordering = ["code"]


class QuestionType(models.TextChoices):
    OPEN = "open", "Ouverte"
    UNIQUE_CHOICE = "unique_choice", "Choix unique"
    MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
    CLOSED_WITH_RANKING = "closed_with_ranking", "Fermée avec classement"
    CLOSED_WITH_SCALE = "closed_with_scale", "Fermée à échelle"
    BOOLEAN = "boolean", "Binaire oui / non"
    NUMERICAL = "numerical", "Numérique"


class BooleanOperator(models.TextChoices):
    AND = "and", "et"
    OR = "or", "ou"


@register_snippet
class Definition(models.Model):
    word = models.CharField(max_length=255, verbose_name="mot")
    explanation = RichTextField(
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE, verbose_name="explication"
    )

    def __str__(self):
        return f"Définition de {self.word}"

    class Meta:
        verbose_name = "Définition"
        verbose_name_plural = "Définitions"


class Question(index.Indexed, TimeStampedModel, ClusterableModel):
    rules_intersection_operator = models.CharField(
        max_length=8, choices=BooleanOperator.choices, default=BooleanOperator.AND
    )

    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de cette question, détermine son ordre",
    )
    concatenated_code = models.CharField(max_length=8, default="")

    name = models.CharField(verbose_name="Nom", max_length=125, default="")
    question_statement = models.TextField(
        verbose_name="Enoncé de la question", default=""
    )

    type = models.CharField(
        max_length=32,
        choices=QuestionType.choices,
        default=QuestionType.OPEN,
        help_text="Choisir le type de question",
    )

    min = models.IntegerField(verbose_name="Valeur minimale", blank=True, null=True)
    max = models.IntegerField(verbose_name="Valeur maximale", blank=True, null=True)
    min_label = models.CharField(
        max_length=32,
        verbose_name="Label de la valeur minimale",
        default="",
        blank=True,
    )
    max_label = models.CharField(
        max_length=32,
        verbose_name="Label de la valeur maximale",
        default="",
        blank=True,
    )
    min_associated_score = models.IntegerField(
        verbose_name="Score associé à la valeur minimale",
        blank=True,
        null=True,
    )
    max_associated_score = models.IntegerField(
        verbose_name="Score associé à la valeur maximale",
        blank=True,
        null=True,
    )

    false_associated_score = models.IntegerField(
        verbose_name="Score associé à une réponse négative",
        blank=True,
        null=True,
    )

    true_associated_score = models.IntegerField(
        verbose_name="Score associé à une réponse positive",
        blank=True,
        null=True,
    )

    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Texte précisant la question et pourquoi elle est posée.",
    )

    legal_frame = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Cadre légal",
    )
    use_case = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Cas d'usage",
    )
    resources = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Ressources",
    )
    comments = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Commentaires",
        help_text="Indication affichée uniquement pour les administrateurs.",
    )

    # Questionnary questions fields

    # TODO : question : how to behave when you delete a criteria?
    #  Delete all question or not authorize if questions are linked ?
    criteria = models.ForeignKey(
        Criteria,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="questions",
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

    # Profiling questions fields
    profiling_question = models.BooleanField(default=False)

    roles = models.ManyToManyField(Role, blank=True)

    search_fields = [
        index.SearchField("question_statement", partial_match=True),
        index.SearchField("name", partial_match=True),
    ]

    explanation_panels = [
        InlinePanel("related_definition_ordered", label="Définitions"),
        FieldPanel("use_case"),
        FieldPanel("legal_frame"),
        FieldPanel("resources"),
        FieldPanel("comments"),
    ]

    def __str__(self):
        if self.profiling_question:
            return f"Profilage: {self.name}"
        return f"{self.concatenated_code}: {self.name}"

    class Meta:
        ordering = ["code"]


class QuestionDefinition(Orderable):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="related_definition_ordered"
    )
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE)
    panels = [
        SnippetChooserPanel("definition"),
    ]


class QuestionnaireQuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(profiling_question=False)


@register_snippet
class QuestionnaireQuestion(Question):
    objects = QuestionnaireQuestionManager()

    panels = [
        FieldPanel("criteria"),
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("question_statement"),
        FieldPanel("objectivity"),
        FieldPanel("method"),
        FieldPanel("description"),
        FieldPanel("type"),
        InlinePanel(
            "response_choices",
            label="Choix de réponses possibles",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("min"),
                        FieldPanel("max"),
                    ],
                ),
                FieldRowPanel(
                    [
                        FieldPanel("min_label"),
                        FieldPanel("max_label"),
                    ],
                ),
                FieldRowPanel(
                    [
                        FieldPanel("min_associated_score"),
                        FieldPanel("max_associated_score"),
                    ],
                ),
            ],
            heading="Valeurs extrêmes possibles",
        ),
        FieldRowPanel(
            [
                FieldPanel("true_associated_score"),
                FieldPanel("false_associated_score"),
            ],
            heading="Scores associés aux réponses d'une question binaire",
        ),
        *Question.explanation_panels,
    ]

    search_fields = [
        *Question.search_fields,
        index.FilterField("profiling_question"),
    ]

    def save(self, *args, **kwargs):
        self.profiling_question = False
        self.concatenated_code = (
            self.criteria.concatenated_code + self.code if self.criteria else self.code
        )
        super().save(*args, **kwargs)

    class Meta(Question.Meta):
        verbose_name_plural = "4. Questions"
        verbose_name = "4. Question"
        proxy = True


class ProfilingQuestionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(profiling_question=True)


@register_snippet
class ProfilingQuestion(Question):
    objects = ProfilingQuestionManager()

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("question_statement"),
        FieldPanel("roles", widget=forms.CheckboxSelectMultiple),
        FieldPanel("description"),
        FieldPanel("type"),
        InlinePanel(
            "response_choices",
            label="Choix de réponses possibles",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("min"),
                        FieldPanel("max"),
                    ],
                ),
                FieldRowPanel(
                    [
                        FieldPanel("min_label"),
                        FieldPanel("max_label"),
                    ],
                ),
            ],
            heading="Valeurs extrêmes possibles",
        ),
        *Question.explanation_panels,
    ]

    # TODO : the search not works because filter on profiling_question=True
    search_fields = [
        *Question.search_fields,
        index.FilterField("profiling_question"),
    ]

    def save(self, *args, **kwargs):
        self.profiling_question = True
        super().save(*args, **kwargs)

    class Meta(Question.Meta):
        verbose_name_plural = "Questions de Profilage"
        verbose_name = "Question de Profilage"
        proxy = True


class ResponseChoice(TimeStampedModel, Orderable):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="response_choices"
    )

    response_choice = models.CharField(
        max_length=510, default="", verbose_name="Réponse possible"
    )

    associated_score = models.IntegerField(
        verbose_name="Score associé",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.response_choice

    class Meta:
        verbose_name_plural = "Choix de réponse"
        verbose_name = "Choix de réponse"


@register_snippet
class ProfileType(models.Model):
    name = models.CharField(max_length=125, default="")

    rules_intersection_operator = models.CharField(
        max_length=8, choices=BooleanOperator.choices, default=BooleanOperator.AND
    )

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Types de profil"
        verbose_name = "Type de profil"


class Rule(TimeStampedModel, Orderable, ClusterableModel):
    """
    Manage filtering of question (if the question must be shown) depending on conditional question answer or conditional profile type
    OR
    Define profile type depending on conditional question answer
    """

    # Only one of question or profile_type must be filled
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="question_filters",
        null=True,
        blank=True,
    )

    profile_type = models.ForeignKey(
        ProfileType,
        on_delete=models.CASCADE,
        related_name="definitions",
        null=True,
        blank=True,
    )

    # Only one of conditional_question or conditional_profile_type conditional_role must be filled
    conditional_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Filtre par question",
        related_name="rules_that_depend_on_me",
        null=True,
        blank=True,
    )

    conditional_profile_type = models.ForeignKey(
        ProfileType,
        on_delete=models.CASCADE,
        verbose_name="Filtre par type de profile",
        related_name="rules_that_depend_on_me",
        null=True,
        blank=True,
    )

    conditional_role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Filtre par rôle",
        related_name="rules_that_depend_on_me",
        null=True,
        blank=True,
    )

    # if conditional question is unique or multiple choices type
    response_choices = models.ManyToManyField(ResponseChoice)

    # if conditional question is numerical or close with scale
    numerical_operator = models.CharField(
        max_length=8, choices=NUMERICAL_OPERATOR, blank=True, null=True
    )
    numerical_value = models.IntegerField(blank=True, null=True)

    # if conditional question is boolean
    boolean_response = models.BooleanField(blank=True, null=True)

    def __str__(self):
        conditional = (
            self.conditional_profile_type
            if self.conditional_profile_type
            else self.conditional_question
        )
        detail = ""
        if self.conditional_question:
            if self.boolean_response:
                detail = "réponse=" + str(self.boolean_response)
            elif self.numerical_operator:
                detail = (
                    f"réponse{str(self.numerical_operator)}{str(self.numerical_value)}"
                )
            elif self.response_choices:
                for response_choice in self.response_choices.all():
                    detail += f"réponse={str(response_choice)}, "

        return f"(ID: {str(self.id)}) {str(conditional)}, {detail}"

    def save(self, *args, **kwargs):
        # clean data when save it
        if self.conditional_profile_type or self.conditional_role:
            self.conditional_question = None
            self.numerical_operator = None
            self.numerical_value = None
            self.boolean_response = None
            if self.conditional_role:
                self.conditional_profile_type = None
            if self.conditional_profile_type:
                self.conditional_role = None
        elif self.conditional_question:
            self.conditional_profile_type = None
            self.conditional_role = None
            if (
                self.conditional_question.type == QuestionType.MULTIPLE_CHOICE
                or self.conditional_question.type == QuestionType.UNIQUE_CHOICE
            ):
                self.numerical_operator = None
                self.numerical_value = None
                self.boolean_response = None
            elif (
                self.conditional_question.type == QuestionType.NUMERICAL
                or self.conditional_question.type == QuestionType.CLOSED_WITH_SCALE
            ):
                self.boolean_response = None
            elif self.conditional_question.type == QuestionType.BOOLEAN:
                self.numerical_value = None
                self.boolean_response = None
        super().save(*args, **kwargs)