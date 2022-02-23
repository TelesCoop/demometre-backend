from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from .api import api_router
from .views import RuleView, intersection_operator_view, rules_definition_view

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v2/", api_router.urls),
    path(
        "admin/question/<int:pk>/edit-intersection-operator/",
        intersection_operator_view,
        name="question-intersection-operator",
    ),
    path(
        "admin/question/<int:pk>/rules/", rules_definition_view, name="question-filter"
    ),
    path(
        "admin/question/<int:pk>/rule/<int:rule_pk>/delete",
        RuleView.as_view(),
        name="delete-question-filter",
    ),
    path(
        "admin/profile-type/<int:pk>/edit-intersection-operator/",
        intersection_operator_view,
        name="profile-type-intersection-operator",
    ),
    path(
        "admin/profile-type/<int:pk>/rules/",
        rules_definition_view,
        name="profile-type-definition",
    ),
    path(
        "admin/profile-type/<int:pk>/rule/<int:rule_pk>/delete",
        RuleView.as_view(),
        name="delete-profile-type-definition",
    ),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Translatable URLs
# These will be available under a language code prefix. For example /en/search/
urlpatterns += i18n_patterns(
    path("search/", search_views.search, name="search"),
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
)
