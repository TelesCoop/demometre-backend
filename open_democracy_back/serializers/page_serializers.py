from rest_framework import serializers

from open_democracy_back.models import HomePage, EvaluationIntroPage, ReferentialPage
from open_democracy_back.models.assessment_models import AssessmentType
from open_democracy_back.models.contents_models import (
    BlogPost,
    Feedback,
    Partner,
    Resource,
)
from open_democracy_back.models.pages_models import (
    EvaluationInitPage,
    EvaluationQuestionnairePage,
    ProjectPage,
    ResultsPage,
    UsagePage,
)
from open_democracy_back.serializers.assessment_serializers import (
    AssessmentTypeSerializer,
)
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
            if partner.show_in_home_page:
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
    pillar_block_image_url = serializers.SerializerMethodField()

    @staticmethod
    def get_pillar_block_image_url(obj: ReferentialPage):
        if obj.pillar_block_image:
            return obj.pillar_block_image.file.url
        return None

    class Meta:
        model = ReferentialPage
        fields = PAGE_FIELDS + [
            "description",
            "pillar_block_title",
            "pillar_block_left_content",
            "pillar_block_right_content",
            "pillar_block_image_url",
            "marker_block_title",
            "marker_block_content",
            "criteria_block_title",
            "criteria_block_left_content",
            "criteria_block_right_content",
        ]
        read_only_fields = fields


class ResultsPageSerializer(PageSerialiserWithLocale):
    intro_image_url = serializers.SerializerMethodField()

    @staticmethod
    def get_intro_image_url(obj: ResultsPage):
        if obj.intro_image:
            return obj.intro_image.file.url
        return None

    class Meta:
        model = ResultsPage
        fields = PAGE_FIELDS + ["tag_line", "intro_image_url"]
        read_only_fields = fields


class UsagePageSerializer(PageSerialiserWithLocale):
    intro_image_url = serializers.SerializerMethodField()
    steps_images_url = serializers.SerializerMethodField()
    assessment_types_details = serializers.SerializerMethodField()

    @staticmethod
    def get_intro_image_url(obj: UsagePage):
        if obj.intro_image:
            return obj.intro_image.file.url
        return None

    @staticmethod
    def get_steps_images_url(obj: UsagePage):
        to_return = []
        for step in obj.steps_of_use:
            to_return.append(
                {"id": step.value["image"].id, "url": step.value["image"].file.url}
            )
        return to_return

    @staticmethod
    def get_assessment_types_details(_):
        return AssessmentTypeSerializer(AssessmentType.objects.all(), many=True).data

    class Meta:
        model = UsagePage
        fields = PAGE_FIELDS + [
            "tag_line",
            "intro_image_url",
            "step_of_use_title",
            "step_of_use_intro",
            "steps_of_use",
            "steps_images_url",
            "participate_block_title",
            "participate_block_intro",
            "participate_left_paragraph",
            "participate_right_paragraph",
            "start_assessment_block_title",
            "start_assessment_block_intro",
            "start_assessment_block_data",
            "assessment_types_details",
        ]
        read_only_fields = fields


class ProjectPageSerializer(PageSerialiserWithLocale):
    intro_image_url = serializers.SerializerMethodField()
    images_url = serializers.SerializerMethodField()
    svgs_url = serializers.SerializerMethodField()
    partners = serializers.SerializerMethodField()

    @staticmethod
    def get_intro_image_url(obj: ProjectPage):
        if obj.intro_image:
            return obj.intro_image.file.url
        return None

    @staticmethod
    def get_images_url(obj: ProjectPage):
        images = []
        ids = []
        for impact in obj.impact_block_data:
            if impact.value["image"].id not in ids:
                images.append(
                    {
                        "id": impact.value["image"].id,
                        "url": impact.value["image"].file.url,
                    }
                )
                ids.append(impact.value["image"].id)
        for why in obj.why_block_data:
            if why.block.name == "image" and why.value.id not in ids:
                images.append(
                    {
                        "id": why.value.id,
                        "url": why.value.file.url,
                    }
                )
                ids.append(why.value.id)
        return images

    @staticmethod
    def get_svgs_url(obj: ProjectPage):
        svgs = []
        ids = []
        for objective in obj.objective_block_data:
            if objective.value["svg"].id not in ids:
                svgs.append(
                    {
                        "id": objective.value["svg"].id,
                        "url": objective.value["svg"].file.url,
                    }
                )
                ids.append(objective.value["svg"].id)
        for how in obj.how_block_data:
            if how.block.name == "cards":
                for card in how.value:
                    if card["svg"].id not in ids:
                        svgs.append({"id": card["svg"].id, "url": card["svg"].file.url})
                        ids.append(card["svg"].id)
        return svgs

    @staticmethod
    def get_partners(obj: ProjectPage):
        partners = []
        ids = []
        for group in obj.who_partner_sub_block_data:
            for partner in group.value["partners"]:
                if partner.id not in ids:
                    partners.append(PartnerSerializer(partner, read_only=True).data)
                    ids.append(partner.id)
        return partners

    class Meta:
        model = ProjectPage
        fields = PAGE_FIELDS + [
            "tag_line",
            "intro_image_url",
            "why_block_title",
            "why_block_data",
            "objective_block_title",
            "objective_block_data",
            "impact_block_title",
            "impact_block_data",
            "who_block_title",
            "who_partner_sub_block_title",
            "who_partner_sub_block_data",
            "how_block_title",
            "how_block_data",
            "images_url",
            "svgs_url",
            "partners",
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


class EvaluationQuestionnairePageSerializer(PageSerialiserWithLocale):
    class Meta:
        model = EvaluationQuestionnairePage
        fields = [
            "id",
            "locale_code",
            "start_title",
            "start_text",
            "intermediate_step_title",
            "intermediate_step_text_logged_in",
            "intermediate_step_text_logged_out",
            "is_intermediate_step_title_with_pillar_names",
            "finished_title",
            "finished_text_logged_in",
            "finished_text_logged_out",
        ]
        read_only_fields = fields
