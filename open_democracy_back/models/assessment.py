from django.db import models
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
)

from wagtail.core.models import Orderable
from wagtail.snippets.models import register_snippet


class AssessmentType(models.TextChoices):
    MUNICIPALITY = "municipality", "Commune"
    INTERCOMMUNALITY = "intercommunality", "Intercommunalité"


@register_snippet
class Assessment(TimeStampedModel, ClusterableModel):
    name = models.CharField(max_length=125, default="")
    type = models.CharField(
        max_length=32,
        choices=AssessmentType.choices,
        default=AssessmentType.MUNICIPALITY,
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("type"),
        InlinePanel(
            "zip_codes",
            label="Code postaux",
        ),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Évaluation"
        verbose_name_plural = "Évaluations"


class AssessmentZipCode(Orderable):
    assessment = ParentalKey(
        Assessment, related_name="zip_codes", on_delete=models.CASCADE
    )
    zip_code = models.CharField(max_length=32, verbose_name="Code postal")

    def __str__(self):
        return self.zip_code

    class Meta:
        verbose_name_plural = "Code postaux"
        verbose_name = "Code postal"
