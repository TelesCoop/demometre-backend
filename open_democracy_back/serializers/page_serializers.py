from rest_framework import serializers

from open_democracy_back.models import HomePage, EvaluationIntroPage, ReferentialPage
from open_democracy_back.models.contents_models import (
    BlogPost,
    Feedback,
    Partner,
    Resource,
)
from open_democracy_back.models.pages_models import EvaluationInitPage
from open_democracy_back.serializers.content_serializers import (
    BlogPostSerializer,
    FeedbackSerializer,
    PartnerSerializer,
    ResourceSerializer,
)


PAGE_FIELDS = ["id", "title", "introduction", "locale_code"]


class PageSerialiserWithLocale(serializers.ModelSerializer):
    locale_code = serializers.SerializerMethodField()

    @staticmethod
    def get_locale_code(obj):
        return obj.locale.language_code

    class Meta:
        abstract = True


class HomePageSerializer(PageSerialiserWithLocale):
    intro_image_url = serializers.SerializerMethodField()
    feedbacks = serializers.SerializerMethodField()
    blog_posts = serializers.SerializerMethodField()
    resources = serializers.SerializerMethodField()
    partners = serializers.SerializerMethodField()

    @staticmethod
    def get_intro_image_url(obj: HomePage):
        if obj.intro_image:
            return obj.intro_image.file.url
        return None

    @staticmethod
    def get_feedbacks(_):
        feedbacks = []
        for feedback in Feedback.objects.all():
            if feedback.publish:
                feedbacks.append(FeedbackSerializer(feedback, read_only=True).data)
        return feedbacks

    @staticmethod
    def get_blog_posts(_):
        blog_posts = []
        for blog_post in BlogPost.objects.all()[:6]:
            blog_posts.append(BlogPostSerializer(blog_post, read_only=True).data)
        return blog_posts

    @staticmethod
    def get_resources(_):
        resources = []
        for resource in Resource.objects.all()[:6]:
            resources.append(ResourceSerializer(resource, read_only=True).data)
        return resources

    @staticmethod
    def get_partners(_):
        partners = []
        for partner in Partner.objects.all():
            partners.append(PartnerSerializer(partner, read_only=True).data)
        return partners

    class Meta:
        model = HomePage
        fields = PAGE_FIELDS + [
            "tag_line",
            "intro_image_url",
            "intro_youtube_video_id",
            "feedback_block_title",
            "feedback_block_intro",
            "feedbacks",
            "blog_block_title",
            "blog_block_intro",
            "blog_posts",
            "resources_block_title",
            "resources_block_intro",
            "resources",
            "partner_block_title",
            "partner_block_intro",
            "partners",
        ]
        read_only_fields = fields


class ReferentialPageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = ReferentialPage
        fields = PAGE_FIELDS + [
            "pillar_block_title",
        ]
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
