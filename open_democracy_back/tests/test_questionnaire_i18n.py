from http.cookies import SimpleCookie

from django.conf import settings
from django.test import TestCase
from rest_framework.reverse import reverse

from open_democracy_back.factories import PillarFactory


class TestQuestionnaireI18n(TestCase):
    def set_locale_on_cookie(self, locale):
        self.client.cookies = SimpleCookie({settings.LANGUAGE_COOKIE_NAME: locale})

    def test_questionnaire_i18n(self):
        pillar = PillarFactory.create()
        pillar.description_fr = "French description"
        pillar.description_en = "English description"
        pillar.save()

        self.set_locale_on_cookie("fr")
        res = self.client.get(
            reverse("pillars-detail", args=[pillar.pk]),
        ).json()
        self.assertEqual(res["description"], "French description")
        self.set_locale_on_cookie("en")
        res = self.client.get(reverse("pillars-detail", args=[pillar.pk])).json()
        self.assertEqual(res["description"], "English description")
