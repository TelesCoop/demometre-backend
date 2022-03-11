from django.urls import path

from .views.assessment_views import get_assessment_view
from .views.questionnaire_views import (
    CriteriaView,
    MarkerView,
    PillarView,
    ProfilingQuestionView,
    QuestionnaireQuestionView,
)

urlpatterns = [
    path("assessments/", get_assessment_view),
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
]
