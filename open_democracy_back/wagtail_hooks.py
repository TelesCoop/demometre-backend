from django.utils.html import format_html_join
from django.templatetags.static import static

from wagtail.core import hooks

from wagtail.snippets import widgets as wagtailsnippets_widgets

from open_democracy_back.models import ProfileType, Question


@hooks.register("register_snippet_listing_buttons")
def snippet_listing_buttons(snippet, user, next_url=None):
    if isinstance(snippet, Question):
        yield wagtailsnippets_widgets.SnippetListingButton(
            "Condition d'affichage de la question",
            "/admin/question/" + str(snippet.id) + "/rules/",
            priority=10,
        )
    if isinstance(snippet, ProfileType):
        yield wagtailsnippets_widgets.SnippetListingButton(
            "Définir ce profil",
            "/admin/profile-type/" + str(snippet.id) + "/rules/",
            priority=10,
        )


@hooks.register("insert_editor_js", order=100)
def editor_js():
    js_files = [
        "js/questions.js",
    ]
    js_includes = format_html_join(
        "\n",
        '<script type="module" src="{0}"></script>',
        ((static(filename),) for filename in js_files),
    )

    return js_includes