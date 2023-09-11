from django import forms
from django.db import models
from django.utils import timezone
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import InlinePanel, FieldPanel
from wagtail.documents.models import Document
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from my_auth.models import User
from open_democracy_back.constants import ASSESSMENT_DOCUMENT_CATEGORIES_CHOICES
from open_democracy_back.models.participation_models import Response
from open_democracy_back.models.utils import FrontendRichText
from open_democracy_back.utils import InitiatorType, LocalityType, ManagedAssessmentType


@register_snippet
class Region(index.Indexed, models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=64, verbose_name="Nom")

    search_fields = [
        index.SearchField(
            "name",
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"


@register_snippet
class Department(index.Indexed, models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=64, verbose_name="Nom")
    region = models.ForeignKey(
        Region, verbose_name="Région", on_delete=models.SET_NULL, null=True
    )

    search_fields = [
        index.SearchField(
            "name",
        ),
    ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"


@register_snippet
class Municipality(index.Indexed, ClusterableModel):
    code = models.CharField(max_length=100, verbose_name="Code insee")
    name = models.CharField(max_length=255, verbose_name="Nom")
    department = models.ForeignKey(
        Department, verbose_name="Département", on_delete=models.SET_NULL, null=True
    )
    population = models.IntegerField(verbose_name="Population", default=0)

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("department"),
        FieldPanel("population"),
        InlinePanel(
            "zip_codes",
            label="Code postal",
        ),
    ]

    search_fields = [
        index.SearchField(
            "name",
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"


class ZipCode(models.Model):
    code = models.CharField(max_length=100, verbose_name="Code")
    municipality = ParentalKey(
        Municipality,
        verbose_name="Municipalité",
        on_delete=models.CASCADE,
        related_name="zip_codes",
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Code postal"
        verbose_name_plural = "Code postaux"


@register_snippet
class EPCI(index.Indexed, ClusterableModel):
    code = models.CharField(max_length=100, verbose_name="Code siren")
    name = models.CharField(max_length=255, verbose_name="Nom")
    population = models.IntegerField(verbose_name="Population", default=0)

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("population"),
        InlinePanel("related_municipalities_ordered", label="Liste des communes"),
    ]

    search_fields = [
        index.SearchField(
            "name",
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Intercommunalité"
        verbose_name_plural = "Intercommunalités"


class MunicipalityOrderByEPCI(Orderable):
    epci = ParentalKey(
        EPCI, on_delete=models.CASCADE, related_name="related_municipalities_ordered"
    )
    municipality = models.ForeignKey(
        Municipality, on_delete=models.CASCADE, verbose_name="Commune"
    )
    panels = [
        FieldPanel("municipality"),
    ]


@register_snippet
class AssessmentType(models.Model):
    assessment_type = models.CharField(
        max_length=32,
        choices=ManagedAssessmentType.choices,
        verbose_name="Evaluation géré par le code",
        unique=True,
        editable=False,
    )
    for_who = models.CharField(
        max_length=510, blank=True, verbose_name="A qui c'est adressé"
    )
    what = models.CharField(
        max_length=510, blank=True, verbose_name="Ce que ça contient"
    )
    for_what = models.CharField(
        max_length=510, blank=True, verbose_name="Ce que ça permet"
    )
    results = models.CharField(max_length=510, blank=True, verbose_name="Les résultats")
    price = models.CharField(max_length=510, blank=True, verbose_name="Le prix")
    pdf = models.ForeignKey(
        Document,
        verbose_name="Pdf du questionnaire",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("for_who", widget=forms.Textarea),
        FieldPanel("what", widget=forms.Textarea),
        FieldPanel("for_what", widget=forms.Textarea),
        FieldPanel("results", widget=forms.Textarea),
        FieldPanel("price", widget=forms.Textarea),
        FieldPanel("pdf"),
    ]

    def __str__(self):
        return self.get_assessment_type_display()

    class Meta:
        verbose_name = "Type d'évaluation"
        verbose_name_plural = "Types d'évaluation"


@register_snippet
class Assessment(TimeStampedModel, ClusterableModel):
    assessment_type = models.ForeignKey(
        AssessmentType,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Type d'évaluation",
    )
    conditions_of_sale_consent = models.BooleanField(default=False)
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    epci = models.ForeignKey(
        EPCI,
        unique=True,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Intercommunalité",
    )
    experts = models.ManyToManyField(
        User,
        blank=True,
        verbose_name="Experts",
        related_name="assessments",
        limit_choices_to={"groups__name": "Experts"},
        help_text="Pour ajouter un expert à la liste il faut créer / modifier l'utilisateur correspondant, aller dans l'onglet rôles et cocher la case Experts",
    )
    initiated_by_user = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Initialisé par",
        related_name="initiated_assessments",
        help_text="Si l'évaluation est initié au nom de la localité, quelqu'un peut tout de même être à la source",
    )
    initiator_type = models.CharField(
        "type d'initilisateur",
        max_length=32,
        choices=InitiatorType.choices,
        blank=True,
        null=True,
    )
    initiator_usage_consent = models.BooleanField(default=False)
    initialized_to_the_name_of = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Initialisé au nom de",
    )
    initialization_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'initialisation",
        help_text="Si il n'y a pas de date d'initialisation, c'est que le début de l'évaluation n'a pas été confirmée",
    )
    is_initialization_questions_completed = models.BooleanField(default=False)
    last_participation_date = models.DateTimeField(
        default=timezone.now, verbose_name="Date de dernière participation"
    )
    locality_type = models.CharField(
        max_length=32,
        choices=LocalityType.choices,
        default=LocalityType.MUNICIPALITY,
        verbose_name="Type de localité",
    )
    municipality = models.ForeignKey(
        Municipality,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Commune",
        unique=True,
    )
    name = models.CharField(verbose_name="nom", max_length=80, blank=True, null=True)
    royalty_payed = models.BooleanField(default=False, verbose_name="Redevance payée")

    # details
    context = FrontendRichText(verbose_name="contexte", blank=True, default="")
    objectives = FrontendRichText(verbose_name="objectifs", blank=True, default="")
    stakeholders = FrontendRichText(
        verbose_name="parties prenantes", blank=True, default=""
    )
    calendar = FrontendRichText(verbose_name="calendrier", blank=True, default="")

    @property
    def published_results(self):
        return all(
            [
                representativity.respected
                for representativity in self.representativities.all()
            ]
        )

    @property
    def population(self):
        if self.locality_type == LocalityType.MUNICIPALITY:
            return self.municipality.population
        if self.locality_type == LocalityType.INTERCOMMUNALITY:
            return self.epci.population

    @property
    def collectivity_name(self):
        if self.locality_type == LocalityType.MUNICIPALITY:
            return self.municipality.name
        if self.locality_type == LocalityType.INTERCOMMUNALITY:
            return self.epci.name

    @property
    def code(self):
        if self.locality_type == LocalityType.MUNICIPALITY:
            return self.municipality.code
        if self.locality_type == LocalityType.INTERCOMMUNALITY:
            return self.epci.code

    panels = [
        FieldPanel("name"),
        FieldPanel("assessment_type"),
        FieldPanel("experts"),
        FieldPanel("royalty_payed"),
        FieldPanel("locality_type"),
        FieldPanel("municipality"),
        FieldPanel("epci"),
        FieldPanel("initiated_by_user"),
        FieldPanel("initiator_type"),
        FieldPanel("initialized_to_the_name_of"),
        FieldPanel("initialization_date"),
        FieldPanel("end_date"),
        FieldPanel("context"),
        FieldPanel("objectives"),
        FieldPanel("stakeholders"),
        FieldPanel("calendar"),
        InlinePanel("documents", label="documents"),
        InlinePanel("payment", label="paiement"),
    ]

    def __str__(self):
        return f"{self.get_locality_type_display()} {self.municipality if self.locality_type == LocalityType.MUNICIPALITY else self.epci}"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.collectivity_name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"


class AssessmentResponseQuerySet(models.QuerySet):
    def accounted_in_assessment(self, assessment_pk):
        # filter responses to include only those from target assessment and ignore those from anonymous users and passed responses
        return self.filter(
            answered_by__is_unknown_user=False,
            assessment_id=assessment_pk,
        ).exclude(has_passed=True)


# All questionnaire objective responses are assessment responses
class AssessmentResponse(Response):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="responses"
    )
    answered_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="assessment_responses", null=True
    )

    objects = AssessmentResponseQuerySet.as_manager()

    class Meta:
        unique_together = ["assessment", "question"]


class AssessmentDocument(TimeStampedModel):
    assessment = ParentalKey(
        Assessment, on_delete=models.CASCADE, related_name="documents"
    )
    category = models.CharField(
        verbose_name="catégorie",
        max_length=20,
        choices=ASSESSMENT_DOCUMENT_CATEGORIES_CHOICES,
    )
    file = models.FileField(verbose_name="fichier")
    name = models.CharField(verbose_name="nom", max_length=80)

    panels = [
        FieldPanel("category"),
        FieldPanel("file"),
        FieldPanel("name"),
    ]


class AssessmentPayment(TimeStampedModel):
    assessment = ParentalKey(
        Assessment, on_delete=models.CASCADE, unique=True, related_name="payment"
    )
    author = models.ForeignKey(
        User,
        verbose_name="auteur du paiement",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    amount = models.FloatField(verbose_name="amount")

    panels = [
        FieldPanel("amount"),
        FieldPanel("author"),
    ]

    def __str__(self):
        return (
            f"assessment id {self.assessment.pk}, amount {self.amount},"
            f"by {self.author.email}"
        )
