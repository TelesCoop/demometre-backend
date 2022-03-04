from django.urls import path

from open_democracy_back.api_views import get_assessment_view

urlpatterns = [
    path("assessments", get_assessment_view),
]
