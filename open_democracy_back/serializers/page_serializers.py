from rest_framework import serializers

from open_democracy_back.models import HomePage, EvaluationIntroPage, ReferentialPage


PAGE_FIELDS = ["id", "title", "introduction", "locale"]


class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = PAGE_FIELDS
        read_only_fields = fields


class ReferentialPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferentialPage
        fields = PAGE_FIELDS
        read_only_fields = fields


class EvaluationIntroPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationIntroPage
        fields = PAGE_FIELDS + ["data_consent"]
        read_only_fields = fields
