import os

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from open_democracy_back.factories import (
    AssessmentFactory,
    ParticipationFactory,
    UserFactory,
)
from open_democracy_back.models import Assessment
from open_democracy_back.tests.utils import authenticate


class TestScoring(TestCase):
    def get_role(self, assessment: Assessment):
        url = reverse("assessments-detail", args=[assessment.pk])
        return self.client.get(url).data["details"]["role"]

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


class TestAssessmentsEdits(TestCase):
    @authenticate
    def test_assessment_edits(self):
        assessment = AssessmentFactory.create()
        url = reverse("assessments-detail", args=[assessment.pk])
        res = self.client.patch(
            url,
            {"context": "new context"},
            content_type="application/json",
        )
        # we don't have write access to this assessment
        self.assertEqual(res.status_code, 403)
        assessment.initiated_by_user = authenticate.user
        assessment.save()
        res = self.client.patch(
            url,
            {"context": "new context"},
            content_type="application/json",
        )
        # now it's fine
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["context"], "new context")

    @authenticate
    def test_upload_and_edit_assessment_document(self):
        assessment = AssessmentFactory.create(initiated_by_user=authenticate.user)
        url = reverse("assessment-documents-list")

        # upload document
        with open(
            os.path.join(
                settings.BASE_DIR, "open_democracy_back", "tests", "document.pdf"
            ),
            "rb",
        ) as fh:
            data = self.client.post(
                url,
                {
                    "category": "invoices",
                    "name": "my name",
                    "file": fh,
                    "assessment": assessment.pk,
                },
            ).json()
        self.assertDictEqual(
            {
                "assessment": assessment.pk,
                "category": "invoices",
                "name": "my name",
            },
            {k: v for k, v in data.items() if k in ["assessment", "category", "name"]},
        )

        # test editing document name
        document_pk = data["id"]
        url = reverse("assessment-documents-detail", args=[document_pk])
        data = self.client.patch(
            url,
            {"name": "modified name"},
            content_type="application/json",
        ).json()
        self.assertEqual(data["name"], "modified name")

        # test editing does not work when no right access
        assessment.initiated_by_user = UserFactory.create()
        assessment.save()
        res = self.client.patch(url, {"name": "0"}, content_type="application/json")
        self.assertEqual(res.status_code, 403)

    @authenticate
    def test_assessment_detail_access(self):
        # has detail access
        assessment = AssessmentFactory.create(initiated_by_user=authenticate.user)
        url = reverse("assessments-detail", args=[assessment.pk])
        data = self.client.get(url).json()
        self.assertEqual(data["details"]["hasDetailAccess"], True)
        self.assertEqual(data["context"], assessment.context)

        # no detail access
        assessment.initiated_by_user = UserFactory.create()
        assessment.save()
        data = self.client.get(url).json()
        self.assertEqual(data["details"]["hasDetailAccess"], False)
        self.assertFalse("context" in data)
