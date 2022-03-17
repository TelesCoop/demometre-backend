from rest_framework import serializers

from open_democracy_back.models import HomePage, EvaluationIntroPage, ReferentialPage


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
        fields = PAGE_FIELDS
        read_only_fields = fields


class ReferentialPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = ReferentialPage
        fields = PAGE_FIELDS
        read_only_fields = fields


class EvaluationIntroPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = EvaluationIntroPage
        fields = PAGE_FIELDS + ["data_consent"]
        read_only_fields = fields
