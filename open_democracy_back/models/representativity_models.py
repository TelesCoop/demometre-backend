from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from wagtail.search import index
from wagtail.snippets.models import register_snippet

from open_democracy_back.models.questionnaire_and_profiling_models import (
    ProfilingQuestion,
    QuestionType,
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
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        verbose_name="Taux (en %) minimum acceptable pour la publication des résultats",
        help_text="En dessous de ce taux (%) la publication des résultats est interdite",
    )

    search_fields = [
        index.SearchField("name", partial_match=True),
    ]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Critère de représentativité"
        verbose_name_plural = "Critères de représentativité"
