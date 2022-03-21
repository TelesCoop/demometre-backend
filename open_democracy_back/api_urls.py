from django.urls import path

from open_democracy_back.views.page_views import (
    EvaluationIntroPageView,
    HomePageView,
    ReferentialPageView,
)

from .views.assessment_views import get_assessment_view
from .views.profiling_views import ProfilingQuestionView
from .views.questionnaire_views import (
    CriteriaView,
    MarkerView,
    PillarView,
    QuestionnaireQuestionView,
    QuestionnaireStructureView,
    DefinitionView,
)

urlpatterns = [
    path("assessments/", get_assessment_view),
    path(
        "questionnaire-structure/", QuestionnaireStructureView.as_view({"get": "list"})
    ),
    path(
        "pillars/",
        PillarView.as_view({"get": "list"}),
    ),
    path(
        "pillars/<int:pk>/",
        PillarView.as_view({"get": "retrieve"}),
    ),
    path(
        "markers/",
        MarkerView.as_view({"get": "list"}),
    ),
    path(
        "markers/<int:pk>/",
        MarkerView.as_view({"get": "retrieve"}),
    ),
    path(
        "criterias/",
        CriteriaView.as_view({"get": "list"}),
    ),
    path(
        "criterias/<int:pk>/",
        CriteriaView.as_view({"get": "retrieve"}),
    ),
    path(
        "questionnaire-questions/",
        QuestionnaireQuestionView.as_view({"get": "list"}),
    ),
    path(
        "questionnaire-questions/<int:pk>/",
        QuestionnaireQuestionView.as_view({"get": "retrieve"}),
    ),
    path(
        "profiling-questions/",
        ProfilingQuestionView.as_view({"get": "list"}),
    ),
    path(
        "profiling-questions/<int:pk>/",
        ProfilingQuestionView.as_view({"get": "retrieve"}),
    ),
    path(
        "home-pages/",
        HomePageView.as_view({"get": "list"}),
    ),
    path(
        "referential-pages/",
        ReferentialPageView.as_view({"get": "list"}),
    ),
    path(
        "evaluation-intro-pages/",
        EvaluationIntroPageView.as_view({"get": "list"}),
    ),
    path("definitions/", DefinitionView.as_view({"get": "list"})),
    path("definitions/<int:pk>/", DefinitionView.as_view({"get": "retrieve"})),
]
