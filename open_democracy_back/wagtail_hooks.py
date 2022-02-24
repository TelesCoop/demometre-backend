from django.utils.html import format_html_join
from django.templatetags.static import static
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)

from wagtail.core import hooks

from wagtail.snippets import widgets as wagtailsnippets_widgets

from open_democracy_back.models import (
    ProfileType,
    Question,
    ThematicTag,
    Definition,
    Pillar,
    Marker,
    QuestionnaireQuestion,
    ProfilingQuestion,
)


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


class ThematicTagModelAdmin(ModelAdmin):
    model = ThematicTag
    menu_label = "Thématiques"
    menu_icon = "pilcrow"
    menu_order = 100
    form_fields_exclude = ("slug",)
    add_to_settings_menu = False
    list_display = ["name"]
    search_fields = ("name",)


class DefinitionsModelAdmin(ModelAdmin):
    model = Definition
    menu_label = "Définitions"
    menu_icon = "openquote"
    menu_order = 200
    add_to_settings_menu = False
    list_display = ["word"]
    search_fields = ("word",)


class PillarModelAdmin(ModelAdmin):
    model = Pillar
    menu_label = "Pillier"
    menu_icon = "folder-inverse"
    menu_order = 1
    add_to_settings_menu = False
    list_display = ["name"]
    search_fields = ("name",)


class MarkerModelAdmin(ModelAdmin):
    model = Marker
    menu_label = "Marqueur"
    menu_icon = "folder-inverse"
    menu_order = 2
    add_to_settings_menu = False
    list_display = ["name"]
    search_fields = ("name",)


class QuestionnaireQuestionModelAdmin(ModelAdmin):
    model = QuestionnaireQuestion
    menu_label = "Question"
    menu_icon = "folder-inverse"
    menu_order = 3
    add_to_settings_menu = False
    list_display = ["name"]
    search_fields = ("name",)


class ProfilingQuestionModelAdmin(ModelAdmin):
    model = ProfilingQuestion
    menu_label = "Question de profilage"
    menu_icon = "folder-inverse"
    menu_order = 4
    add_to_settings_menu = False
    list_display = ["name"]
    search_fields = ("name",)


class Survey(ModelAdminGroup):
    menu_label = "Questionnaire"
    menu_order = 300
    menu_icon = "folder-inverse"
    items = (
        PillarModelAdmin,
        MarkerModelAdmin,
        QuestionnaireQuestionModelAdmin,
        ProfilingQuestionModelAdmin,
    )


modeladmin_register(ThematicTagModelAdmin)
modeladmin_register(DefinitionsModelAdmin)
modeladmin_register(Survey)
