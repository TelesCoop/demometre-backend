from importlib.resources import Resource
from rest_framework import serializers
from open_democracy_back.models.contents_models import BlogPost, Feedback, Partner


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "person_name", "person_context", "quote", "publish"]


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["id", "title", "publication_date", "short_description"]


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["id", "title", "publication_date", "short_description"]


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = ["id", "name"]
