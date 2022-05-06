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

SIMPLE_RICH_TEXT_FIELD_FEATURE = [
    "bold",
    "italic",
    "link",
    "ol",
    "ul",
]

NUMERICAL_OPERATOR = [
    ("<", "<"),
    (">", ">"),
    ("<=", "<="),
    (">=", ">="),
    ("!=", "!="),
    ("=", "="),
]


class BooleanOperator(models.TextChoices):
    AND = "and", "et"
    OR = "or", "ou"


@register_snippet
class Role(TranslatableMixin, ClusterableModel):
    name = models.CharField(verbose_name="Nom", max_length=125)

    description = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name="Description du rôle",
        help_text="Texte précisant le rôle (définition, exemple, reformulation).",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
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


@register_snippet
class Pillar(models.Model):
    name = models.CharField(verbose_name="Nom", max_length=125)
    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de ce pilier",
    )
    order = models.IntegerField(
        verbose_name="Ordre",
        help_text="Permet de ranger dans l'ordre voulu les piliers",
        default="1",
    )

    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Description pour le référentiel",
    )

    panels = [
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
        ordering = ["order"]


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
    concatenated_code = models.CharField(max_length=5, default="")

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
        self.concatenated_code = (
            self.pillar.code + "." if self.pillar else ""
        ) + self.code
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
    concatenated_code = models.CharField(max_length=8, default="")
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
        # Use proxy QuestionnaireQuestion
        child_questions = QuestionnaireQuestion.objects.filter(criteria_id=self.id)
        [child_question.save() for child_question in child_questions]

    class Meta:
        verbose_name_plural = "3. Critères"
        verbose_name = "3. Critère"
        ordering = ["code"]


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


class QuestionType(models.TextChoices):
    OPEN = "open", "Ouverte"
    UNIQUE_CHOICE = "unique_choice", "Choix unique"
    MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
    CLOSED_WITH_RANKING = "closed_with_ranking", "Fermée avec classement"
    CLOSED_WITH_SCALE = "closed_with_scale", "Fermée à échelle"
    BOOLEAN = "boolean", "Binaire oui / non"
    PERCENTAGE = "percentage", "Pourcentage"


@register_snippet
class Question(index.Indexed, TimeStampedModel, ClusterableModel):
    rules_intersection_operator = models.CharField(
        max_length=8, choices=BooleanOperator.choices, default=BooleanOperator.AND
    )

    code = models.CharField(
        verbose_name="Code",
        max_length=2,
        help_text="Correspond au numéro (ou lettre) de cette question, détermine son ordre",
    )
    concatenated_code = models.CharField(max_length=11, default="")

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

    population_lower_bound = models.IntegerField(
        verbose_name="Borne inférieure (population min)",
        blank=True,
        null=True,
        help_text="Si aucune valeur n'est renseignée, aucune borne inférieur ne sera prise en compte",
    )
    population_upper_bound = models.IntegerField(
        verbose_name="Borne suppérieur (population max)",
        blank=True,
        null=True,
        help_text="Si aucune valeur n'est renseignée, aucune borne suppérieur ne sera prise en compte",
    )

    allows_to_explain = models.OneToOneField(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="explained_by",
        verbose_name="Permet d'expliciter une autre question",
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

    max_multiple_choices = models.IntegerField(
        verbose_name="Nombre maximal de choix possible",
        blank=True,
        null=True,
        help_text="Pour une question à choix multiple, indiquer le nombre maximum de choix possible",
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
        verbose_name="Exemples inspirants",
    )
    sources = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Sources",
    )
    to_go_further = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Pour aller plus loin",
    )
    comments = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Commentaires (pour l'interne)",
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
        verbose_name="Objective / Subjective",
    )
    method = models.CharField(
        max_length=32,
        choices=[("quantitative", "Quantitative"), ("qualitative", "Qualitative")],
        blank=True,
        verbose_name="Methode",
    )
    profiles = models.ManyToManyField(
        ProfileType,
        verbose_name="Profils concernés",
        related_name="questions_that_depend_on_me",
        blank=True,
    )

    # Profiling questions fields
    profiling_question = models.BooleanField(default=False)

    roles = models.ManyToManyField(
        Role,
        blank=True,
        verbose_name="Rôles concernés",
        help_text="Si aucun rôle n'est sélectionné c'est comme si tous l'étaient",
    )

    @property
    def survey_type(self):
        return "profiling" if self.profiling_question else "questionnaire"

    search_fields = [
        index.SearchField("question_statement", partial_match=True),
        index.SearchField("name", partial_match=True),
    ]

    principal_panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("question_statement"),
        FieldPanel("description"),
        FieldRowPanel(
            [
                FieldPanel("population_lower_bound"),
                FieldPanel("population_upper_bound"),
            ],
            heading="Taille des collectivités concernées",
        ),
        FieldPanel("roles", widget=forms.CheckboxSelectMultiple),
    ]

    commun_types_panels = [
        FieldPanel("type"),
        InlinePanel(
            "response_choices",
            label="Choix de réponses possibles",
        ),
        FieldPanel("max_multiple_choices"),
        InlinePanel(
            "categories",
            label="Catégories pour une question fermée à échelle",
        ),
    ]

    explanation_panels = [
        SnippetChooserPanel("allows_to_explain"),
        InlinePanel("related_definition_ordered", label="Définitions"),
        FieldPanel("legal_frame"),
        FieldPanel("sources"),
        FieldPanel("to_go_further"),
        FieldPanel("use_case"),
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
        *Question.principal_panels,
        FieldPanel("profiles", widget=forms.CheckboxSelectMultiple),
        FieldPanel("objectivity"),
        FieldPanel("method"),
        *Question.commun_types_panels,
        InlinePanel(
            "percentage_ranges",
            label="Score associé aux réponses d'une question de pourcentage",
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
            self.criteria.concatenated_code + "." if self.criteria else ""
        ) + self.code

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
        *Question.principal_panels,
        *Question.commun_types_panels,
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

    description = models.TextField(
        default="",
        null=True,
        blank=True,
        verbose_name="Description de la réponse",
        help_text="Texte précisant la réponse (définition, exemple, reformulation). Si la question est fermée à échelle la description ne s'affichera pas.",
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


class PercentageRange(TimeStampedModel, Orderable):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="percentage_ranges"
    )

    lower_bound = models.IntegerField(
        verbose_name="Borne inférieure",
        help_text="Si la réponse est suppérieur ou égale à",
    )

    upper_bound = models.IntegerField(
        verbose_name="Borne suppérieure",
        help_text="Si la réponse est inférieur ou égale à",
    )

    associated_score = models.IntegerField(
        verbose_name="Score associé",
        help_text="Le score sera alors de",
    )
    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [FieldPanel("lower_bound"), FieldPanel("upper_bound")],
                ),
                FieldPanel("associated_score"),
            ],
            heading="Score associé à une fourchette de pourcentage",
        ),
    ]

    def __str__(self):
        return f"{self.question} : [{self.lower_bound}%,{self.upper_bound}%] = {self.associated_score}"

    class Meta:
        verbose_name_plural = "Scores pour les différentes fourchettes"
        verbose_name = "Score pour une fourcette donnée"


class Category(TimeStampedModel, Orderable):
    question = ParentalKey(
        Question, on_delete=models.CASCADE, related_name="categories"
    )

    category = models.CharField(
        max_length=64,
        default="",
        verbose_name="Categorie",
        help_text="Permet de répondre à la même question pour différentes catégories",
    )

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = "Catégorie"


class GenericRule(TimeStampedModel, Orderable, ClusterableModel):
    """
    GenericRule define the response that must be done to a conditional question
    """

    class Meta:
        abstract = True

    conditional_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name="Filtre par question",
        related_name="%(class)s_that_depend_on_me",
        null=True,
        blank=True,
    )

    # if conditional question is unique or multiple choices type
    response_choices = models.ManyToManyField(ResponseChoice)

    # if conditional question is percentage
    numerical_operator = models.CharField(
        max_length=8, choices=NUMERICAL_OPERATOR, blank=True, null=True
    )
    numerical_value = models.IntegerField(blank=True, null=True)

    # if conditional question is boolean
    boolean_response = models.BooleanField(blank=True, null=True)

    @property
    def type(self):
        return self.conditional_question.type

    def __str__(self):
        condition_question_str = ""
        if self.conditional_question:
            if self.boolean_response:
                condition_question_str = "réponse=" + str(self.boolean_response)
            elif self.numerical_operator:
                condition_question_str = (
                    f"réponse{str(self.numerical_operator)}{str(self.numerical_value)}"
                )
            elif self.response_choices:
                for response_choice in self.response_choices.all():
                    condition_question_str += f"réponse={str(response_choice)}, "

        return f"(ID: {str(self.id)}) {str(self.conditional_question)}, {condition_question_str}"

    def save(self, *args, **kwargs):
        # Make sure the data is consistent
        if (
            self.conditional_question.type == QuestionType.MULTIPLE_CHOICE
            or self.conditional_question.type == QuestionType.UNIQUE_CHOICE
        ):
            self.numerical_operator = None
            self.numerical_value = None
            self.boolean_response = None
        elif self.conditional_question.type == QuestionType.PERCENTAGE:
            self.boolean_response = None
        elif self.conditional_question.type == QuestionType.BOOLEAN:
            self.numerical_operator = None
            self.numerical_value = None
        super().save(*args, **kwargs)


class QuestionRule(GenericRule):
    """
    Manage drawer questions :
    A QuestionRule can define if a profiling question must be show depending on another profiling question answer
    A QuestionRule can define if a questionnaire question must be show depending on another questionnaire question answer
    A QuestionRule can define if a questionnaire question must be show depending on profile type
    """

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="rules",
        null=True,
        blank=True,
    )


class ProfileDefinition(GenericRule):
    """
    Define profile type :
    A ProfileDefinition can define the definition of a profile type depending on profiling question answer
    """

    profile_type = models.ForeignKey(
        ProfileType,
        on_delete=models.CASCADE,
        related_name="rules",
        null=True,
        blank=True,
    )
