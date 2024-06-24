import os


from django.utils.functional import cached_property
from django.utils.html import format_html
from wagtail.blocks import ChooserBlock
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from wagtail.models import CollectionMember
from wagtail.admin.panels import TabbedInterface
from wagtail.admin.panels import ObjectList
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from taggit.managers import TaggableManager


def get_svg_upload_to_folder(instance, filename):
    folder = settings.WAGTAILSVG_UPLOAD_FOLDER or "media"
    return os.path.join(folder, filename)


class Svg(CollectionMember, index.Indexed, models.Model):
    title = models.CharField(max_length=255, verbose_name=_("title"))
    file = models.FileField(upload_to=get_svg_upload_to_folder, verbose_name=_("file"))
    tags = TaggableManager(help_text=None, blank=True, verbose_name=_("tags"))

    class Meta:
        ordering = ["-id"]

    admin_form_fields = (
        "title",
        "file",
        "collection",
        "tags",
    )

    edit_handler = TabbedInterface(
        [
            ObjectList(
                [
                    FieldPanel("collection"),
                    FieldPanel("title"),
                    FieldPanel("file"),
                    FieldPanel("tags"),
                ],
                heading="General",
            ),
        ]
    )

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def url(self):
        return self.file.url


class SvgChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        return Svg

    @cached_property
    def widget(self):
        from wagtailsvg.widgets import AdminSvgChooser

        return AdminSvgChooser()

    def get_form_state(self, value):
        return self.widget.get_value_data(value)

    def render_basic(self, value, context=None):
        if value:
            return format_html("<img src='{0}' alt='{1}'>", value.url, value.title)
        else:
            return ""
