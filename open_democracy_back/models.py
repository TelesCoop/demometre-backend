from django.db import models
from model_utils.models import TimeStampedModel
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField

from wagtail.core.models import Page, TranslatableMixin, Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet


class HomePage(Page):
    # HomePage can be created only on the root
    parent_page_types = ["wagtailcore.Page"]

    tagline = models.CharField(max_length=127, default="")
    body = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("tagline"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("tagline"),
        APIField("body"),
    ]


@register_snippet
class Role(TranslatableMixin, ClusterableModel):
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("name"),
        InlinePanel("related_markers_ordered", label="Ordre des marqueurs"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Rôles"
        verbose_name = "Rôle"


@register_snippet
class Pillar(TranslatableMixin):
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Piliers"
        verbose_name = "Pilier"


@register_snippet
class Marker(TranslatableMixin):
    pillar = models.ForeignKey(Pillar, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("pillar"),
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Marqueurs"
        verbose_name = "Marqueur"


class MarkerOrderByRole(Orderable):
    role = ParentalKey(
        Role, on_delete=models.CASCADE, related_name="related_markers_ordered"
    )
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE)
    panels = [
        FieldPanel("marker"),
    ]


@register_snippet
class Criteria(TranslatableMixin):
    marker = models.ForeignKey(Marker, null=True, blank=True, on_delete=models.SET_NULL)
    order = models.IntegerField(
        verbose_name="N°",
        help_text="Place que doit occuper ce critère dans son marqueur",
    )
    name = models.CharField(verbose_name="nom", max_length=125)

    panels = [
        FieldPanel("marker"),
        FieldPanel("order"),
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Critères"
        verbose_name = "Critère"
        ordering = ["order"]


@register_snippet
class Question(index.Indexed, TranslatableMixin, TimeStampedModel):
    # TODO : question : how to behave when you delete a criteria?
    #  Delete all question or not authorize if questions are linked ?
    criteria = models.ForeignKey(
        Criteria, null=True, blank=True, on_delete=models.SET_NULL
    )
    order = models.IntegerField(
        verbose_name="N°",
        help_text="Place que doit occuper cette question dans son critère",
    )
    question = models.CharField(max_length=510, default="")
    objective = models.BooleanField(default=False)

    search_fields = [
        index.SearchField("question", partial_match=True),
    ]

    panels = [
        FieldPanel("criteria"),
        FieldPanel("order"),
        FieldPanel("question"),
        FieldPanel("objective"),
    ]

    def __str__(self):
        return self.question

    def __init__(self, *args, **kwargs):
        """Fixes a bug when trying to translate."""
        if "index_entries" in kwargs:
            kwargs.pop("index_entries")
        super().__init__(*args, **kwargs)

    class Meta(TranslatableMixin.Meta):
        verbose_name_plural = "Questions"
        verbose_name = "Question"
        ordering = ["order"]
