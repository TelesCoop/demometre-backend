from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from model_utils.models import TimeStampedModel
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from wagtail.core.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class LocalityType(models.TextChoices):
    MUNICIPALITY = "municipality", "Commune"
    INTERCOMMUNALITY = "intercommunality", "Intercommunalité"


@register_snippet
class Region(index.Indexed, models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=64, verbose_name="Nom")

    search_fields = [
        index.SearchField("name", partial_match=True),
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
        index.SearchField("name", partial_match=True),
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
        index.SearchField("name", partial_match=True),
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
        index.SearchField("name", partial_match=True),
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
        SnippetChooserPanel("municipality"),
    ]


@register_snippet
class Assessment(TimeStampedModel, ClusterableModel):
    type = models.CharField(
        max_length=32,
        choices=LocalityType.choices,
        default=LocalityType.MUNICIPALITY,
    )
    municipality = models.ForeignKey(
        Municipality,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Commune",
    )
    epci = models.ForeignKey(
        EPCI,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Intercommunalité",
    )
    initiated_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Initialisé par",
        related_name="initiated_assessments",
        help_text="Si l'évaluation est initié au nom de la localité, quelqu'un peut tout de même être à la source",
    )
    is_initiated_by_locality = models.BooleanField(
        default=False, verbose_name="Est initialisé par la localité ?"
    )
    carried_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Porté par",
        related_name="carried_assessments",
        help_text="Si l'évaluation est porté par la localité, qui en est responsable",
    )
    is_carried_by_locality = models.BooleanField(
        default=False, verbose_name="Est porté par la localité ?"
    )
    initialization_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date d'initialisation",
        help_text="Si il n'y a pas de date d'initialisation, c'est que le début de l'évaluation n'a pas été confirmée",
    )
    last_participation_date = models.DateTimeField(
        default=timezone.now, verbose_name="Date de dernière participation"
    )
    end_date = models.DateField(null=True, blank=True, verbose_name="Date de fin")

    @property
    def population(self):
        if self.type == LocalityType.MUNICIPALITY:
            return self.municipality.population
        if self.type == LocalityType.INTERCOMMUNALITY:
            return self.epci.population

    panels = [
        FieldPanel("type"),
        SnippetChooserPanel("municipality"),
        SnippetChooserPanel("epci"),
        FieldPanel("initiated_by"),
        FieldPanel("is_initiated_by_locality"),
        FieldPanel("carried_by"),
        FieldPanel("is_carried_by_locality"),
        FieldPanel("initialization_date"),
        FieldPanel("end_date"),
    ]

    def __str__(self):
        return f"{self.type} {self.municipality}"

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
