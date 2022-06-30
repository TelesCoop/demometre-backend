from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.documents.models import Document
from wagtail.documents.edit_handlers import DocumentChooserPanel


@register_setting
class RGPDSettings(BaseSetting):
    legal_mention = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Mentions légales",
    )
    terms_of_use = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Conditions Générales d'utilisation",
    )
    terms_of_sale = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Conditions Générales de vente",
    )
    confidentiality_policy = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Politique de confidentialité",
    )

    panels = [
        DocumentChooserPanel("legal_mention"),
        DocumentChooserPanel("terms_of_use"),
        DocumentChooserPanel("terms_of_sale"),
        DocumentChooserPanel("confidentiality_policy"),
    ]

    class Meta:
        verbose_name = "RGPD"
