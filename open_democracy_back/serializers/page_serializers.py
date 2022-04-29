from rest_framework import serializers

from open_democracy_back.models import HomePage, EvaluationIntroPage, ReferentialPage
from open_democracy_back.models.pages_models import EvaluationInitPage


PAGE_FIELDS = ["id", "title", "introduction", "locale_code"]


class PageSerialiserWithLocale(serializers.ModelSerializer):
    locale_code = serializers.SerializerMethodField()

    @staticmethod
    def get_locale_code(obj):
        return obj.locale.language_code

    class Meta:
        abstract = True


class HomePageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = HomePage
        fields = PAGE_FIELDS + [
            "tag_line",
            "feedback_block_title",
            "feedback_block_intro",
            "blog_block_title",
            "blog_block_intro",
            "resources_block_title",
            "resources_block_intro",
            "partner_block_title",
            "partner_block_intro",
        ]
        read_only_fields = fields


class ReferentialPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = ReferentialPage
        fields = PAGE_FIELDS
        read_only_fields = fields


class EvaluationIntroPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = EvaluationIntroPage
        fields = PAGE_FIELDS + [
            "data_consent",
            "account_incentive",
            "account_incentive_title",
        ]
        read_only_fields = fields


class EvaluationInitPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = EvaluationInitPage
        fields = PAGE_FIELDS + [
            "public_name_question",
            "public_name_question_description",
            "representativity_title",
            "representativity_description",
            "initialization_validation",
        ]
        read_only_fields = fields
