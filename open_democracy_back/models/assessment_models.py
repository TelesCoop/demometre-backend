from django.db import models
from model_utils.models import TimeStampedModel
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel

from wagtail.core.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class AssessmentType(models.TextChoices):
    MUNICIPALITY = "municipality", "Commune"
    INTERCOMMUNALITY = "intercommunality", "Intercommunalité"


@register_snippet
class Region(index.Indexed, models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=3, verbose_name="Nom")

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
    name = models.CharField(max_length=3, verbose_name="Nom")
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
    code = models.CharField(max_length=100, verbose_name="Code insee")
    name = models.CharField(max_length=255, verbose_name="Nom")
    population = models.IntegerField(verbose_name="Population", default=0)

    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
        FieldPanel("population"),
        InlinePanel("related_municipalities_ordered", label="Ordre des marqueurs"),
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
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    panels = [
        SnippetChooserPanel("municipality"),
    ]


@register_snippet
class Assessment(TimeStampedModel, ClusterableModel):
    type = models.CharField(
        max_length=32,
        choices=AssessmentType.choices,
        default=AssessmentType.MUNICIPALITY,
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

    panels = [
        FieldPanel("type"),
        SnippetChooserPanel("municipality"),
        SnippetChooserPanel("epci"),
    ]

    def __str__(self):
        return f"{self.type} {self.municipality}"

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
