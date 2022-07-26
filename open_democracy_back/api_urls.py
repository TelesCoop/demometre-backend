from django.urls import path, include
from rest_framework import routers
from open_democracy_back.views.animator_views import (
    CloseWorkshopView,
    FullWorkshopView,
    WorkshopParticipationResponseView,
    WorkshopParticipationView,
    WorkshopView,
)
from open_democracy_back.views.content_views import BlogPostView, ResourceView

from open_democracy_back.views.page_views import (
    EvaluationInitiationPageSerializerView,
    EvaluationQuestionnairePageView,
    HomePageView,
    ProjectPageView,
    ReferentialPageView,
    ResultsPageView,
    UsagePageView,
)
from open_democracy_back.views.participation_views import (
    ParticipationResponseView,
    ParticipationView,
    CompletedQuestionsParticipationView,
    CurrentParticipationView,
    CurrentParticipationResponseView,
)
from open_democracy_back.views.representativity_views import (
    RepresentativityCriteriaView,
)
from open_democracy_back.views.setting_views import (
    RGPDSettingsView,
)

from .views.assessment_views import (
    AnimatorAssessmentsView,
    AssessmentAddExpertView,
    AssessmentResponseView,
    AssessmentView,
    AssessmentsView,
    CompletedQuestionsInitializationView,
    ExpertView,
    PublishedAssessmentsView,
    initialize_assessment,
    AssessmentScoreView,
    CurrentAssessmentView,
    CurrentAssessmentResponseView,
    get_chart_data,
)
from .views.profiling_views import (
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
router.register(r"results-pages", ResultsPageView, basename="ResultsPage")
router.register(r"usage-pages", UsagePageView, basename="UsagePage")
router.register(r"project-pages", ProjectPageView, basename="UsagePage")
router.register(
    r"evaluation-initiation-pages",
    EvaluationInitiationPageSerializerView,
    basename="EvaluationInitiationPage",
)
router.register(
    r"evaluation-questionnaire-pages",
    EvaluationQuestionnairePageView,
    basename="EvaluationQuestionnairePage",
)
router.register(r"settings", RGPDSettingsView, basename="Settings")
router.register(r"blog-posts", BlogPostView, basename="BlogPost")
router.register(r"resources", ResourceView, basename="Resources")

router.register(r"participations", ParticipationView, basename="Participation")
router.register(
    r"participation-responses/current",
    CurrentParticipationResponseView,
    basename="CurrentParticipationResponse",
)
router.register(
    r"participation-responses",
    ParticipationResponseView,
    basename="ParticipationResponse",
)
router.register(
    r"assessment-responses/current",
    CurrentAssessmentResponseView,
    basename="CurrentAssessmentResponse",
)
router.register(
    r"assessment-responses", AssessmentResponseView, basename="AssessmentResponse"
)
router.register(
    r"profiling-questions", ProfilingQuestionView, basename="ProfilingQuestion"
)
router.register(
    r"questionnaire-questions",
    QuestionnaireQuestionView,
    basename="QuestionnaireQuestion",
)
router.register(r"workshops", WorkshopView, basename="Workshop")
router.register(r"full-workshops", FullWorkshopView, basename="FullWorkshop")
router.register(r"experts", ExpertView, basename="Workshop")


urlpatterns = [
    path("assessments/", AssessmentsView.as_view({"get": "list"})),
    path("assessments/by-animator/", AnimatorAssessmentsView.as_view({"get": "list"})),
    path("assessments/by-locality/", AssessmentsView.as_view({"get": "get_or_create"})),
    path("assessments/current", CurrentAssessmentView.as_view()),
    path("assessments/<int:pk>/", AssessmentView.as_view({"get": "retrieve"})),
    path("assessments/<int:pk>/initialization/", initialize_assessment),
    path("assessments/published/", PublishedAssessmentsView.as_view({"get": "list"})),
    path(
        "questionnaire-structure/", QuestionnaireStructureView.as_view({"get": "list"})
    ),
    path("pillars/", PillarView.as_view({"get": "list"})),
    path("pillars/<int:pk>/", PillarView.as_view({"get": "retrieve"})),
    path("markers/", MarkerView.as_view({"get": "list"})),
    path("markers/<int:pk>/", MarkerView.as_view({"get": "retrieve"})),
    path("criterias/", CriteriaView.as_view({"get": "list"})),
    path("criterias/<int:pk>/", CriteriaView.as_view({"get": "retrieve"})),
    path("definitions/", DefinitionView.as_view({"get": "list"})),
    path("definitions/<int:pk>/", DefinitionView.as_view({"get": "retrieve"})),
    path("roles/", RoleView.as_view({"get": "list"})),
    path(
        "participations/current",
        CurrentParticipationView.as_view(),
    ),
    path("", include(router.urls)),
    path(
        "representativity-criterias/",
        RepresentativityCriteriaView.as_view({"get": "list"}),
    ),
    path(
        "participations/<int:pk>/questions/completed/",
        CompletedQuestionsParticipationView.as_view(),
    ),
    path(
        "assessments/<int:assessment_id>/questions/completed/",
        CompletedQuestionsInitializationView.as_view(),
    ),
    path(
        "assessments/<int:assessment_id>/scores/",
        AssessmentScoreView.as_view(),
    ),
    path(
        "assessments/<int:assessment_id>/questions/<int:question_id>/chart-data/",
        get_chart_data,
    ),
    path(
        "assessments/<int:assessment_pk>/add-expert/",
        AssessmentAddExpertView.as_view(),
    ),
    path(
        "workshops/<int:workshop_pk>/participation/",
        WorkshopParticipationView.as_view({"post": "create"}),
    ),
    path(
        "workshops/<int:workshop_pk>/participation/<int:participation_pk>/response/",
        WorkshopParticipationResponseView.as_view({"post": "create"}),
    ),
    path(
        "workshops/<int:workshop_pk>/closed/",
        CloseWorkshopView.as_view(),
    ),
]
