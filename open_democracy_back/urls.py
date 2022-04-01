from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from .wagtail_api import api_router
from .views.wagtail_rule_views import (
    ProfileDefinitionView,
    QuestionRuleView,
    profile_definition_view,
    profile_intersection_operator_view,
    question_intersection_operator_view,
    question_rules_view,
)

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/cms/", api_router.urls),
    path("api/auth/", include("my_auth.urls")),
    path("api/", include("open_democracy_back.api_urls")),
    path(
        "admin/question/<int:pk>/edit-intersection-operator/",
        question_intersection_operator_view,
        name="question-intersection-operator",
    ),
    path("admin/question/<int:pk>/rules/", question_rules_view, name="question-filter"),
    path(
        "admin/question/<int:pk>/rule/<int:rule_pk>/delete",
        QuestionRuleView.as_view(),
        name="delete-question-filter",
    ),
    path(
        "admin/profile-type/<int:pk>/edit-intersection-operator/",
        profile_intersection_operator_view,
        name="profile-type-intersection-operator",
    ),
    path(
        "admin/profile-type/<int:pk>/rules/",
        profile_definition_view,
        name="profile-type-definition",
    ),
    path(
        "admin/profile-type/<int:pk>/rule/<int:rule_pk>/delete",
        ProfileDefinitionView.as_view(),
        name="delete-profile-type-definition",
    ),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("backup/", include("telescoop_backup.urls")),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
