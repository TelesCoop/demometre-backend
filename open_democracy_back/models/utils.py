from wagtail.core import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.blocks import ImageChooserBlock


def rich_text_block(additional_field, required):
    return (
        "rich_text",
        blocks.RichTextBlock(
            label="Contenu",
            features=SIMPLE_RICH_TEXT_FIELD_FEATURE
            + ["h3", "h4", "ol", "ul", "document-link"]
            + additional_field,
            required=required,
        ),
    )


SIMPLE_RICH_TEXT_FIELD_FEATURE = ["bold", "italic", "link"]

BODY_FIELD_PARAMS = [
    rich_text_block(["h2"], True),
    (
        "image",
        blocks.StructBlock(
            [
                ("image", ImageChooserBlock()),
                ("caption", blocks.TextBlock(label="légende")),
            ]
        ),
    ),
    (
        "pdf",
        blocks.StructBlock(
            [
                ("document", DocumentChooserBlock()),
                ("title", blocks.TextBlock(label="titre")),
            ]
        ),
    ),
]
