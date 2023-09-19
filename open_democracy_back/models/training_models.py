from django.db import models
from model_utils.models import TimeStampedModel
from wagtail.documents.models import Document


class Training(TimeStampedModel):
    class Meta:
        verbose_name = "Formation"

    name = models.CharField(verbose_name="nom", max_length=100)
    audience = models.CharField(
        verbose_name="public ciblé pour la formation", max_length=200
    )
    description = models.CharField(max_length=300, verbose_name="description courte")
    duration = models.CharField(
        verbose_name="durée de la formation",
        help_text="ex une journée, une heure...",
        max_length=50,
    )
    file = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name="Document lié",
        help_text="Ce document est ignoré si le lien externe est défini",
    )
    is_available_soon = models.BooleanField(
        default=False,
        verbose_name="bientôt disponible",
        help_text="si cette case est cochée, la formation ne sera pas accessible, mais l'utilisateur sera informé de sa publication prochaine",
    )
    link = models.URLField(verbose_name="Lien externe", blank=True, null=True)

    def __str__(self):
        return self.name
