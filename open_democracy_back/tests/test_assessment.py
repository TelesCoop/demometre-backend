from django.test import TestCase
from django.urls import reverse

from open_democracy_back.factories import AssessmentFactory, ParticipationFactory
from open_democracy_back.models import Assessment
from open_democracy_back.tests.utils import authenticate


class TestScoring(TestCase):
    def get_role(self, assessment: Assessment):
        url = reverse("assessments-detail", args=[assessment.pk])
        return self.client.get(url).data["role"]

    @authenticate
    def test_assessment_role(self):
        assessment = AssessmentFactory.create()
        self.assertEqual(self.get_role(assessment), "")
        ParticipationFactory.create(assessment=assessment, user=authenticate.user)
        self.assertEqual(self.get_role(assessment), "participant")
        assessment.experts.add(authenticate.user)
        self.assertEqual(self.get_role(assessment), "expert")
        assessment.initiated_by_user = authenticate.user
        assessment.save()
        self.assertEqual(self.get_role(assessment), "initiator")
