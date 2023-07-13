from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.documents.models import Document


@register_setting
class StructureSettings(BaseSiteSetting):
    email = models.EmailField(verbose_name="Adresse mail de contact", blank=True)

    class Meta:
        verbose_name = "Paramètre de la structure"


@register_setting
class RGPDSettings(BaseSiteSetting):
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
    content_license = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Licence Contenu",
    )

    panels = [
        FieldPanel("legal_mention"),
        FieldPanel("terms_of_use"),
        FieldPanel("terms_of_sale"),
        FieldPanel("confidentiality_policy"),
        FieldPanel("content_license"),
    ]

    class Meta:
        verbose_name = "RGPD"


@register_setting
class ImportantPagesSettings(BaseSiteSetting):
    class Meta:
        verbose_name = "Pages importantes"

    faq_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="FAQ",
    )

    panels = [
        FieldPanel("faq_page"),
    ]
