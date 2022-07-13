from django.db import models
from django.db.models import Count, F, Q
from django.core.validators import MaxValueValidator, MinValueValidator

from wagtail.search import index
from wagtail.snippets.models import register_snippet
from open_democracy_back.models.assessment_models import Assessment

from open_democracy_back.models.questionnaire_and_profiling_models import (
    ProfilingQuestion,
    QuestionType,
    ResponseChoice,
)


@register_snippet
class RepresentativityCriteria(index.Indexed, models.Model):
    name = models.CharField(max_length=64, verbose_name="Nom")
    profiling_question = models.OneToOneField(
        ProfilingQuestion,
        on_delete=models.CASCADE,
        verbose_name="Question de profilage reliée",
        related_name="representativity_criteria",
        limit_choices_to={"type": QuestionType.UNIQUE_CHOICE},
    )
    min_rate = models.IntegerField(
        default=0,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Taux (en %) minimum acceptable pour la publication des résultats",
        help_text="En dessous de ce taux (%) la publication des résultats est interdite",
    )

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        to_create_assessment_representativity = False
        if not self.id:
            to_create_assessment_representativity = True
        super().save(*args, **kwargs)
        if to_create_assessment_representativity:
            for assessment in Assessment.objects.all():
                AssessmentRepresentativity.objects.create(
                    assessment=assessment, representativity_criteria_id=self.id
                )

    class Meta:
        verbose_name = "Critère de représentativité"
        verbose_name_plural = "Critères de représentativité"


class RepresentativityCriteriaRule(models.Model):
    representativity_criteria = models.ForeignKey(
        RepresentativityCriteria,
        on_delete=models.CASCADE,
        related_name="rules",
    )

    response_choice = models.OneToOneField(
        ResponseChoice,
        on_delete=models.CASCADE,
        verbose_name="Réponse",
        related_name="representativity_criteria_rule",
    )

    ignore_for_acceptability_threshold = models.BooleanField(
        default=False,
        verbose_name="Ne pas compter pour le seuil d'acceptabilité minimal",
        help_text="Ex: binaire pour la parité",
    )
    totally_ignore = models.BooleanField(
        default=False,
        verbose_name="Ignorer totalement",
    )

    def __str__(self):
        return f"{self.representativity_criteria} - {self.response_choice}"

    class Meta:
        unique_together = ["representativity_criteria", "response_choice"]


class AssessmentRepresentativity(models.Model):
    assessment = models.ForeignKey(
        Assessment, on_delete=models.CASCADE, related_name="representativities"
    )
    representativity_criteria = models.ForeignKey(
        RepresentativityCriteria,
        on_delete=models.CASCADE,
        related_name="representativities",
    )
    acceptability_threshold = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Seuil d'acceptabilité",
    )

    @property
    def count_by_response_choice(self):
        # annotate() : rename fields
        # values() : specifies which columns are going to be used to "group by"
        # annotate() : specifies an operation over the grouped values
        return (
            self.representativity_criteria.profiling_question.response_choices.all()
            .exclude(representativity_criteria_rule__totally_ignore=True)
            .annotate(
                response_choice_name=F("response_choice"),
                response_choice_id=F("id"),
                ignore_for_acceptability_threshold=F(
                    "representativity_criteria_rule__ignore_for_acceptability_threshold"
                ),
            )
            .values(
                "response_choice_id",
                "response_choice_name",
                "ignore_for_acceptability_threshold",
                "sort_order",
            )
            .annotate(
                total=Count(
                    "unique_choice_participationresponses",
                    filter=Q(
                        unique_choice_participationresponses__participation__assessment_id=self.assessment_id
                    ),
                )
            )
            .order_by("sort_order")
        )

    @property
    def total_responses(self):
        return (
            self.representativity_criteria.profiling_question.participationresponses.filter(
                participation__assessment_id=self.assessment_id
            )
            .exclude(unique_choice_response=None)
            .count()
        )

    @property
    def acceptability_threshold_considered(self):

        if self.acceptability_threshold and (
            self.acceptability_threshold > self.representativity_criteria.min_rate
        ):
            return self.acceptability_threshold
        else:
            return self.representativity_criteria.min_rate

    @property
    def respected(self):
        total_response = self.total_responses
        if total_response == 0:
            return False
        return all(
            [
                (
                    (response_choice_count["total"] / total_response) * 100
                    > self.acceptability_threshold_considered
                )
                if not response_choice_count["ignore_for_acceptability_threshold"]
                else True
                for response_choice_count in self.count_by_response_choice
            ]
        )
