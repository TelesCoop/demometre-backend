from django.contrib.auth.models import User
from django.utils.html import format_html_join
from django.templatetags.static import static
from wagtail.contrib.modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup,
)
from wagtail.contrib.modeladmin.helpers import PermissionHelper

from wagtail.core import hooks

from wagtail.snippets import widgets as wagtailsnippets_widgets

from open_democracy_back.models import (
    Assessment,
    Criteria,
    ProfileType,
    Question,
    Role,
    ThematicTag,
    Definition,
    Pillar,
    Marker,
    QuestionnaireQuestion,
    ProfilingQuestion,
    Region,
    Department,
    Municipality,
    EPCI,
)

from wagtail.contrib.modeladmin.helpers import ButtonHelper


class RulesButtonHelper(ButtonHelper):

    # Define classes for our button, here we can set an icon for example
    view_button_classnames = ["button-small", "icon", "icon-cogs"]

    def view_button(self, obj):
        # Define a label for our button
        if isinstance(obj, Question):
            text = "Condition d'affichage de la question"
            url = "/admin/question/" + str(obj.id) + "/rules/"
        if isinstance(obj, ProfileType):
            text = "Définir ce profil"
            url = "/admin/profile-type/" + str(obj.id) + "/rules/"
        return {
            "url": url,
            "label": text,
            "classname": self.finalise_classname(self.view_button_classnames),
            "title": text,
        }

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        """
        This function is used to gather all available buttons.
        We append our custom button to the btns list.
        """
        btns = super().get_buttons_for_obj(
            obj, exclude, classnames_add, classnames_exclude
        )
        if "view" not in (exclude or []):
            btns.append(self.view_button(obj))
        return btns


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
    menu_order = 200
    form_fields_exclude = ("slug",)
    add_to_settings_menu = False
    search_fields = ("name",)


class DefinitionsModelAdmin(ModelAdmin):
    model = Definition
    menu_label = "Définitions"
    menu_icon = "openquote"
    menu_order = 201
    add_to_settings_menu = False
    search_fields = ("word",)


class PillarModelAdmin(ModelAdmin):
    model = Pillar
    menu_label = "Pillier"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name", "code")


class MarkerModelAdmin(ModelAdmin):
    model = Marker
    menu_label = "Marqueur"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name", "concatenated_code", "pillar__name")


class CriteriaModelAdmin(ModelAdmin):
    model = Criteria
    menu_label = "Critère"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = (
        "name",
        "concatenated_code",
        "marker__name",
        "marker__pillar__name",
    )


class QuestionnaireQuestionModelAdmin(ModelAdmin):
    model = QuestionnaireQuestion
    button_helper_class = RulesButtonHelper
    menu_label = "Question"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = (
        "name",
        "question_statement",
        "concatenated_code",
        "criteria__name",
        "criteria__marker__name",
        "criteria__marker__pillar__name",
    )


class SurveyAdminGroup(ModelAdminGroup):
    menu_label = "Questionnaire"
    menu_order = 202
    menu_icon = "list-ol"
    items = (
        PillarModelAdmin,
        MarkerModelAdmin,
        CriteriaModelAdmin,
        QuestionnaireQuestionModelAdmin,
    )


class RoleModelAdmin(ModelAdmin):
    model = Role
    menu_label = "Rôle"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name",)


class ProfileTypeModelAdmin(ModelAdmin):
    model = ProfileType
    button_helper_class = RulesButtonHelper
    menu_label = "Type de profil"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name",)


class ProfilingQuestionModelAdmin(ModelAdmin):
    model = ProfilingQuestion
    button_helper_class = RulesButtonHelper
    menu_label = "Question de profilage"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name", "question_statement")


class ProfilingAdminGroup(ModelAdminGroup):
    menu_label = "Profilage"
    menu_order = 203
    menu_icon = "group"
    items = (
        RoleModelAdmin,
        ProfileTypeModelAdmin,
        ProfilingQuestionModelAdmin,
    )


class RegionModelAdmin(ModelAdmin):
    model = Region
    menu_label = "Régions"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name",)


class DepartmentModelAdmin(ModelAdmin):
    model = Department
    menu_label = "Départements"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name", "code")


class CommuneModelAdmin(ModelAdmin):
    model = Municipality
    menu_label = "Communes"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name",)


class EPCIModelAdmin(ModelAdmin):
    model = EPCI
    menu_label = "Intercommunalités"
    menu_icon = "folder-inverse"
    add_to_settings_menu = False
    search_fields = ("name",)


class LocalityAdminGroup(ModelAdminGroup):
    menu_label = "Localités"
    menu_order = 204
    menu_icon = "home"
    items = (
        RegionModelAdmin,
        DepartmentModelAdmin,
        CommuneModelAdmin,
        EPCIModelAdmin,
    )


class AssessmentModelAdmin(ModelAdmin):
    model = Assessment
    menu_label = "Évaluation"
    menu_icon = "date"
    menu_order = 205


class MyPermissionHelper(PermissionHelper):
    def user_can_edit_obj(self, user, obj):
        return False


class UserAdmin(ModelAdmin):
    model = User
    menu_label = "Administrateurs"
    menu_icon = "user"
    menu_order = 200
    add_to_settings_menu = True
    exclude_from_explorer = True
    list_display = (
        "username",
        "email",
        "last_login",
    )
    search_fields = "username"

    permission_helper_class = MyPermissionHelper

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Only show admin user
        return qs.filter(is_superuser=True)


modeladmin_register(ThematicTagModelAdmin)
modeladmin_register(DefinitionsModelAdmin)
modeladmin_register(SurveyAdminGroup)
modeladmin_register(ProfilingAdminGroup)
modeladmin_register(LocalityAdminGroup)
modeladmin_register(AssessmentModelAdmin)
modeladmin_register(UserAdmin)
