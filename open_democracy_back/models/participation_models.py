from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from open_democracy_back.models.assessment_models import Assessment
from open_democracy_back.models.questionnaire_and_profiling_models import (
    Category,
    ProfileType,
    Question,
    ResponseChoice,
    Role,
    Pillar,
)


class Participation(models.Model):
    # TODO : on delete : remove participation or clean personnal data and keep responses ?
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="participations"
    )
    assessment = models.ForeignKey(
        Assessment,
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

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new:
            for pillar in Pillar.objects.all():
                self.is_pillar_questions_completed.add(pillar)

    class Meta:
        unique_together = ["user", "assessment"]


class ParticipationPillarCompleted(models.Model):
    completed = models.BooleanField(default=False)
    pillar = models.ForeignKey(Pillar, on_delete=models.CASCADE)
    participation = models.ForeignKey(Participation, on_delete=models.CASCADE)


class Response(models.Model):
    participation = models.ForeignKey(
        Participation, on_delete=models.CASCADE, related_name="responses"
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="responses"
    )
    has_passed = models.BooleanField(default=False)
    unique_choice_response = models.ForeignKey(
        ResponseChoice,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="responses",
    )
    multiple_choice_response = models.ManyToManyField(ResponseChoice)
    boolean_response = models.BooleanField(blank=True, null=True)
    percentage_response = models.IntegerField(
        blank=True, null=True, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )

    class Meta:
        unique_together = ["participation", "question"]


class ClosedWithRankingResponse(models.Model):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name="closed_with_ranking_responses_ordered",
    )
    response_choice = models.ForeignKey(ResponseChoice, on_delete=models.CASCADE)

    class Meta:
        order_with_respect_to = "response"


class ClosedWithScaleCategoryResponse(models.Model):
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name="closed_with_scale_response_categories",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="closed_with_scale_category_responses",
        blank=True,
    )
    response_choice = models.ForeignKey(ResponseChoice, on_delete=models.CASCADE)
