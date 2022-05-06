from django.urls import path, include
from rest_framework import routers

from open_democracy_back.views.page_views import (
    EvaluationInitPageView,
    EvaluationIntroPageView,
    HomePageView,
    ReferentialPageView,
)
from open_democracy_back.views.participation_views import (
    ResponseView,
    ParticipationView,
)
from open_democracy_back.views.representativity_views import (
    RepresentativityCriteriaView,
)

from .views.assessment_views import (
    AssessmentView,
    AssessmentsView,
    initialize_assessment,
)
from .views.profiling_views import (
    ParticipationProfilingQuestionView,
    ProfilingQuestionView,
    RoleView,
)
from .views.questionnaire_views import (
    CriteriaView,
    MarkerView,
    PillarView,
    QuestionnaireQuestionView,
    QuestionnaireStructureView,
    DefinitionView,
)

router = routers.DefaultRouter()
router.register(r"home-pages", HomePageView, basename="HomePage")
router.register(r"referential-pages", ReferentialPageView, basename="ReferentialPage")
router.register(
    r"evaluation-intro-pages", EvaluationIntroPageView, basename="EvaluationIntroPage"
)
router.register(
    r"evaluation-init-pages", EvaluationInitPageView, basename="EvaluationInitPage"
)
router.register(r"participations", ParticipationView, basename="Participation")
router.register(r"responses", ResponseView, basename="Response")


urlpatterns = [
    path("assessments/", AssessmentsView.as_view({"get": "list"})),
    path("assessments/by-locality/", AssessmentsView.as_view({"get": "get_or_create"})),
    path("assessments/<int:pk>/", AssessmentView.as_view({"get": "retrieve"})),
    path("assessments/<int:pk>/initialization/", initialize_assessment),
    path(
        "questionnaire-structure/", QuestionnaireStructureView.as_view({"get": "list"})
    ),
    path("pillars/", PillarView.as_view({"get": "list"})),
    path("pillars/<int:pk>/", PillarView.as_view({"get": "retrieve"})),
    path("markers/", MarkerView.as_view({"get": "list"})),
    path("markers/<int:pk>/", MarkerView.as_view({"get": "retrieve"})),
    path("criterias/", CriteriaView.as_view({"get": "list"})),
    path("criterias/<int:pk>/", CriteriaView.as_view({"get": "retrieve"})),
    path(
        "questionnaire-questions/", QuestionnaireQuestionView.as_view({"get": "list"})
    ),
    path(
        "questionnaire-questions/<int:pk>/",
        QuestionnaireQuestionView.as_view({"get": "retrieve"}),
    ),
    path("profiling-questions/", ProfilingQuestionView.as_view({"get": "list"})),
    path(
        "profiling-questions/<int:pk>/",
        ProfilingQuestionView.as_view({"get": "retrieve"}),
    ),
    path(
        "profiling-questions/participation/<int:participation_pk>/",
        ParticipationProfilingQuestionView.as_view({"get": "list"}),
    ),
    path("definitions/", DefinitionView.as_view({"get": "list"})),
    path("definitions/<int:pk>/", DefinitionView.as_view({"get": "retrieve"})),
    path("roles/", RoleView.as_view({"get": "list"})),
    path("", include(router.urls)),
    path(
        "representativity-criterias/",
        RepresentativityCriteriaView.as_view({"get": "list"}),
    ),
]
