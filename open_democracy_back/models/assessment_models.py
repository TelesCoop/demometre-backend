from django.db import models
from model_utils.models import TimeStampedModel
from modelcluster.models import ClusterableModel

from wagtail.snippets.models import register_snippet


class AssessmentType(models.TextChoices):
    MUNICIPALITY = "municipality", "Commune"
    INTERCOMMUNALITY = "intercommunality", "Intercommunalité"


@register_snippet
class Region(models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=3, verbose_name="Nom")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"


@register_snippet
class Department(models.Model):
    code = models.CharField(max_length=3, verbose_name="Code")
    name = models.CharField(max_length=3, verbose_name="Nom")
    region = models.ForeignKey(
        Region, verbose_name="Région", on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Département"
        verbose_name_plural = "Départements"


@register_snippet
class Municipality(models.Model):
    code = models.CharField(max_length=100, verbose_name="Code insee")
    name = models.CharField(max_length=255, verbose_name="Nom")
    department = models.ForeignKey(
        Department, verbose_name="Département", on_delete=models.SET_NULL, null=True
    )
    population = models.IntegerField(verbose_name="Population", default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"


@register_snippet
class ZipCode(models.Model):
    code = models.CharField(max_length=100, verbose_name="Code")
    municipality = models.ForeignKey(
        Municipality, verbose_name="Municipalité", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = "Code postal"
        verbose_name_plural = "Code postaux"


@register_snippet
class EPCI(models.Model):
    code = models.CharField(max_length=100, verbose_name="Code insee")
    name = models.CharField(max_length=255, verbose_name="Nom")
    population = models.IntegerField(verbose_name="Population", default=0)
    municipalities = models.ManyToManyField(Municipality, verbose_name="Municipalités")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Intercommunalité"
        verbose_name_plural = "Intercommunalités"


@register_snippet
class Assessment(TimeStampedModel, ClusterableModel):
    type = models.CharField(
        max_length=32,
        choices=AssessmentType.choices,
        default=AssessmentType.MUNICIPALITY,
    )
    municipality = models.ForeignKey(
        Municipality, blank=True, null=True, on_delete=models.SET_NULL
    )
    epci = models.ForeignKey(EPCI, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.type} {self.municipality}"

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"
