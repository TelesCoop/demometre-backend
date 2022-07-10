from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django import forms
from django.db.models import Q
from django.db.models.signals import pre_save
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    FieldRowPanel,
    MultiFieldPanel,
    StreamFieldPanel,
)
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField

from wagtail.core.models import TranslatableMixin, Orderable
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from open_democracy_back.utils import (
    NUMERICAL_OPERATOR,
    SIMPLE_RICH_TEXT_FIELD_FEATURE,
    BooleanOperator,
    QuestionType,
)


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


class StrengthsAndWeaknessesFields(models.Model):
    weakness_1 = models.TextField(
        blank=True,
        verbose_name="Point faible",
        help_text="Point faible relevé pour une évaluation si le calcul de son score est de 1",
        default="",
    )
    weakness_2 = models.TextField(
        blank=True,
        verbose_name="Point faible",
        help_text="Point faible relevé pour une évaluation si le calcul de son score est de 2",
        default="",
    )
    strength_3 = models.TextField(
        blank=True,
        verbose_name="Point fort",
        help_text="Point fort relevé pour une évaluation si le calcul de son score est de 3",
        default="",
    )
    strength_4 = models.TextField(
        blank=True,
        verbose_name="Point fort",
        help_text="Point fort relevé pour une évaluation si le calcul de son score est de 4",
        default="",
    )
    panels = [
        FieldPanel("weakness_1"),
        FieldPanel("weakness_2"),
        FieldPanel("strength_3"),
        FieldPanel("strength_4"),
    ]

    class Meta:
        abstract = True


class ScoreFields(StrengthsAndWeaknessesFields):
    score_1 = models.TextField(
        blank=True,
        verbose_name="Signification",
        help_text="Signification du résultat 1 dans le DémoMètre",
        default="",
    )
    score_2 = models.TextField(
        blank=True,
        verbose_name="Signification",
        help_text="Signification du résultat 2 dans le DémoMètre",
        default="",
    )
    score_3 = models.TextField(
        blank=True,
        verbose_name="Signification",
        help_text="Signification du résultat 3 dans le DémoMètre",
        default="",
    )
    score_4 = models.TextField(
        blank=True,
        verbose_name="Signification",
        help_text="Signification du résultat 4 dans le DémoMètre",
        default="",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("score_1"),
                FieldPanel("weakness_1"),
            ],
            heading="Score = 1",
        ),
        MultiFieldPanel(
            [
                FieldPanel("score_2"),
                FieldPanel("weakness_2"),
            ],
            heading="Score = 2",
        ),
        MultiFieldPanel(
            [
                FieldPanel("score_3"),
                FieldPanel("strength_3"),
            ],
            heading="Score = 3",
        ),
        MultiFieldPanel(
            [
                FieldPanel("score_4"),
                FieldPanel("strength_4"),
            ],
            heading="Score = 4",
        ),
    ]

    class Meta:
        abstract = True


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


@register_snippet
class Marker(index.Indexed, ScoreFields):
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
    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Description pour le référentiel",
    )

    panels = [
        FieldPanel("pillar"),
        FieldPanel("name"),
        FieldPanel("code"),
        FieldPanel("description"),
    ] + ScoreFields.panels

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
class Criteria(index.Indexed, ClusterableModel, StrengthsAndWeaknessesFields):
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
    description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Description pour le référentiel",
    )

    explanatory = StreamField(
        [
            (
                "category",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(label="Titre")),
                        (
                            "description",
                            blocks.RichTextBlock(
                                label="Description",
                                features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
                            ),
                        ),
                    ],
                    label_format="Catégorie : {title}",
                    label="Catégorie",
                ),
            )
        ],
        blank=True,
        verbose_name="Explicatif du critère (sources, exemples, obligations légales ...)",
    )

    panels = [
        FieldPanel("marker"),
        FieldPanel("name"),
        FieldPanel("code"),
        FieldPanel("thematic_tags", widget=forms.CheckboxSelectMultiple),
        FieldPanel("description"),
        InlinePanel("related_definition_ordered", label="Définitions"),
        StreamFieldPanel("explanatory"),
    ] + StrengthsAndWeaknessesFields.panels

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


class CriteriaDefinition(Orderable):
    criteria = ParentalKey(
        Criteria, on_delete=models.CASCADE, related_name="related_definition_ordered"
    )
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE)
    panels = [
        SnippetChooserPanel("definition"),
    ]


class QuestionQuerySet(models.QuerySet):
    def filter_by_population(self, population):
        return self.filter(
            Q(population_lower_bound__lte=population) | Q(population_lower_bound=None),
            Q(population_upper_bound__gte=population) | Q(population_upper_bound=None),
        )

    def filter_by_role(self, role):
        return self.filter(Q(roles=role) | Q(roles=None))


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def filter_by_population(self, population):
        return self.get_queryset().filter_by_population(population)

    def filter_by_role(self, role):
        return self.get_queryset().filter_by_role(role)


@register_snippet
class Question(index.Indexed, TimeStampedModel, ClusterableModel):
    objects = QuestionManager()

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

    mandatory = models.BooleanField(default=False, verbose_name="Obligatoire")

    type = models.CharField(
        max_length=32,
        choices=QuestionType.choices,
        default=QuestionType.BOOLEAN,
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
    assessment_types = models.ManyToManyField(
        "open_democracy_back.AssessmentType",
        verbose_name="Types d'évaluation concernés",
        related_name="questions",
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
        FieldPanel("mandatory"),
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
        FieldPanel("comments"),
    ]

    def __str__(self):
        if self.profiling_question:
            return f"Profilage: {self.name}"
        return f"{self.concatenated_code}: {self.name}"

    class Meta:
        ordering = ["code"]


class QuestionnaireQuestionManager(QuestionManager):
    def get_queryset(self):
        return super().get_queryset().filter(profiling_question=False)


@register_snippet
class QuestionnaireQuestion(Question):
    objects = QuestionnaireQuestionManager()

    panels = [
        FieldPanel("criteria"),
        *Question.principal_panels,
        FieldPanel("profiles", widget=forms.CheckboxSelectMultiple),
        FieldPanel("assessment_types", widget=forms.CheckboxSelectMultiple),
        FieldPanel("objectivity"),
        FieldPanel("method"),
        *Question.commun_types_panels,
        InlinePanel(
            "percentage_ranges",
            label="Score associé aux réponses d'une question de pourcentage",
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


class ProfilingQuestionManager(QuestionManager):
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


SCORE_MAP = {
    4: 1,
    3: 0.66,
    2: 0.33,
    1: 0,
}


class Score(models.Model):
    associated_score = models.IntegerField(
        verbose_name="Score associé",
        blank=True,
        null=True,
        help_text="Si pertinant",
        validators=[MinValueValidator(1), MaxValueValidator(4)],
    )

    linearized_score = models.FloatField(
        verbose_name="Score associé linéarisé",
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
    )

    @staticmethod
    def update_score(sender, **kwargs):
        instance = kwargs.get("instance")
        if instance.associated_score is not None:
            instance.linearized_score = SCORE_MAP[instance.associated_score]

    class Meta:
        abstract = True


class ResponseChoice(TimeStampedModel, Orderable, Score):
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
    panels = [
        FieldPanel("response_choice"),
        FieldPanel("description"),
        FieldPanel("associated_score"),
    ]

    def __str__(self):
        return self.response_choice

    class Meta:
        verbose_name_plural = "Choix de réponse"
        verbose_name = "Choix de réponse"
        ordering = ["sort_order"]


# Update linearized score on save
pre_save.connect(Score.update_score, sender=ResponseChoice)


class PercentageRange(TimeStampedModel, Orderable, Score):
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
        ordering = ["sort_order"]


# Update linearized score on save
pre_save.connect(Score.update_score, sender=PercentageRange)


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
        ordering = ["sort_order"]


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
