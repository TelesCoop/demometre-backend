from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


def paragraph_block(additional_field, required):
    return (
        "paragraph",
        blocks.RichTextBlock(
            label="Contenu",
            features=SIMPLE_RICH_TEXT_FIELD_FEATURE
            + ["h3", "h4", "ol", "ul", "document-link"]
            + additional_field,
            required=required,
        ),
    )


SIMPLE_RICH_TEXT_FIELD_FEATURE = ["bold", "italic", "link"]
COLOR_CHOICES = (
    ("blue-light", "Bleue"),
    ("secondary-light", "Rose"),
    ("white", "Blanche"),
    ("", "Sans couleur"),
)

BODY_FIELD_PARAMS = [
    # Is h1
    (
        "heading",
        blocks.CharBlock(form_classname="full title", label="Titre de la page"),
    ),
    (
        "section",
        blocks.StructBlock(
            [
                paragraph_block(["h2"], True),
            ],
            label="Section",
        ),
    ),
    ("image", ImageChooserBlock()),
    ("pdf", DocumentChooserBlock()),
]
