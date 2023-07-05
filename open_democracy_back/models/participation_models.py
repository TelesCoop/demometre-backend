from django.db import models
from my_auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from open_democracy_back.models.animator_models import Participant, Workshop

from open_democracy_back.models.questionnaire_and_profiling_models import (
    Category,
    ProfileType,
    Question,
    ResponseChoice,
    Role,
    Pillar,
)


class ParticipationQuerySet(models.QuerySet):
    def filter_available(self, user_id, date):
        return self.filter(
            user_id=user_id,
            assessment__initialization_date__lte=date,
        )

    def filter_current(self):
        return self.filter(is_current=True)

    def filter_current_available(self, user_id, date):
        return self.filter_available(user_id, date).filter_current()


class Participation(models.Model):
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name="participations",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="participations",
        blank=True,
        null=True,
    )

    is_current = models.BooleanField(default=True)
    assessment = models.ForeignKey(
        "open_democracy_back.Assessment",
        on_delete=models.CASCADE,
        related_name="participations",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="participations",
    )
    profiles = models.ManyToManyField(ProfileType, related_name="participations")
    consent = models.BooleanField(default=False)
    is_profiling_questions_completed = models.BooleanField(default=False)
    is_pillar_questions_completed = models.ManyToManyField(
        Pillar, through="ParticipationPillarCompleted"
    )
    workshop = models.ForeignKey(
        Workshop,
        related_name="participations",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    objects = ParticipationQuerySet.as_manager()

    def __str__(self):
        return (
            f"{str(self.assessment)} - {self.user.username}"
            if self.user
            else f"{str(self.assessment)} - Atelier {self.workshop.name} - {self.participant.name}"
        )

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            for pillar in Pillar.objects.all():
                self.is_pillar_questions_completed.add(pillar)

    class Meta:
        unique_together = ["user", "participant", "assessment"]


class ParticipationPillarCompleted(models.Model):
    completed = models.BooleanField(default=False)
    pillar = models.ForeignKey(Pillar, on_delete=models.CASCADE)
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE)


class Response(models.Model):
    # related_name is participationresponses or assessmentresponses
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="%(class)ss"
    )
    has_passed = models.BooleanField(default=False)
    unique_choice_response = models.ForeignKey(
        ResponseChoice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="unique_choice_%(class)ss",
    )
    multiple_choice_response = models.ManyToManyField(
        ResponseChoice,
        related_name="multiple_choice_%(class)ss",
    )
    boolean_response = models.BooleanField(blank=True, null=True)
    percentage_response = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    number_response = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True


class ParticipationResponseQuerySet(models.QuerySet):
    """
    This queryset class override ParticipationResponseQuerySet manager, it is used to filter participation responses.
    https://docs.djangoproject.com/fr/4.2/topics/db/managers/
    """

    def accounted_in_assessment(self, assessment_pk):
        return (
            self.filter(
                participation__user__is_unknown_user=False,
                participation__assessment_id=assessment_pk,
                question__profiling_question=False,
            )
            .exclude(has_passed=True)
            .exclude(question__criteria=None)
        )


# All subjective and profiling responses are participation responses
class ParticipationResponse(Response):
    participation = models.ForeignKey(
        Participation, on_delete=models.CASCADE, related_name="responses"
    )

    objects = ParticipationResponseQuerySet.as_manager()

    class Meta:
        unique_together = ["participation", "question"]


class ClosedWithScaleCategoryResponse(models.Model):
    participation_response = models.ForeignKey(
        ParticipationResponse,
        on_delete=models.CASCADE,
        related_name="closed_with_scale_response_categories",
        null=True,
        blank=True,
    )
    assessment_response = models.ForeignKey(
        "open_democracy_back.AssessmentResponse",
        on_delete=models.CASCADE,
        related_name="closed_with_scale_response_categories",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="closed_with_scale_category_responses",
        null=True,
        blank=True,
    )
    response_choice = models.ForeignKey(
        ResponseChoice, on_delete=models.SET_NULL, null=True, blank=True
    )
