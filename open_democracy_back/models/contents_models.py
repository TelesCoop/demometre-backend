import datetime

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet


@register_snippet
class Feedback(index.Indexed, models.Model):
    picture = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Photo",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    person_name = models.CharField(max_length=64, verbose_name="Prénom et nom")
    person_context = models.CharField(
        max_length=64,
        verbose_name="Context de la personne",
        help_text="Exemple : Elu de Strasbourg, Membre de Démocratie Ouverte, Habitant de Toulouse ... ",
    )
    quote = models.CharField(max_length=255, default="", verbose_name="Citation")
    publish = models.BooleanField(
        default=False, verbose_name="Publier dans la page d'accueil"
    )

    panels = [
        FieldPanel("person_name"),
        ImageChooserPanel("picture"),
        FieldPanel("person_context"),
        FieldPanel("quote"),
        FieldPanel("publish"),
    ]

    search_fields = [
        index.SearchField("person_name", partial_match=True),
    ]

    def __str__(self):
        return self.person_name + " (publié)" if self.publish else ""

    class Meta:
        verbose_name = "Retour d'expériences"
        verbose_name_plural = "Retours d'expériences"


class Article(index.Indexed, models.Model):
    image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    title = models.CharField(max_length=64, verbose_name="Title")
    publication_date = models.DateTimeField(
        verbose_name="Date de publication",
        default=datetime.datetime.now,
        help_text="Permet de trier l'ordre d'affichage des articles de blog",
    )
    short_description = models.CharField(
        max_length=510, blank=True, null=True, verbose_name="Description courte"
    )
    external_link = models.CharField(
        verbose_name="lien externe", blank=True, null=True, max_length=300
    )

    panels = [
        FieldPanel("title"),
        ImageChooserPanel("image"),
        FieldPanel("publication_date"),
        FieldPanel("short_description"),
        FieldPanel("external_link"),
    ]

    search_fields = [
        index.SearchField("title", partial_match=True),
    ]

    def __str__(self):
        return self.title

    class Meta:
        abstract = True


@register_snippet
class BlogPost(Article):
    class Meta:
        verbose_name = "Article de blog"
        verbose_name_plural = "Articles de blog"
        ordering = ["-publication_date"]


@register_snippet
class Resource(Article):
    class Meta:
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"


@register_snippet
class Partner(index.Indexed, models.Model):
    name = models.CharField(max_length=64, verbose_name="Nom")
    logo_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Logo du partenaire",
        on_delete=models.CASCADE,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        ImageChooserPanel("logo_image"),
    ]

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Partenaire"
        verbose_name_plural = "Partenaires"
