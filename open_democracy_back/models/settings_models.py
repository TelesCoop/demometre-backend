from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.documents.models import Document
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.admin.edit_handlers import PageChooserPanel


@register_setting
class StructureSettings(BaseSetting):
    email = models.EmailField(verbose_name="Adresse mail de contact", blank=True)

    class Meta:
        verbose_name = "Paramètre de la structure"


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
    content_license = models.ForeignKey(
        Document,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Licence Contenu",
    )

    panels = [
        DocumentChooserPanel("legal_mention"),
        DocumentChooserPanel("terms_of_use"),
        DocumentChooserPanel("terms_of_sale"),
        DocumentChooserPanel("confidentiality_policy"),
        DocumentChooserPanel("content_license"),
    ]

    class Meta:
        verbose_name = "RGPD"


@register_setting
class ImportantPagesSettings(BaseSetting):
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
        PageChooserPanel("faq_page"),
    ]
