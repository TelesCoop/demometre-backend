from django.db import models
from my_auth.models import User


class Workshop(models.Model):
    assessment = models.ForeignKey(
        "open_democracy_back.Assessment",
        on_delete=models.CASCADE,
        related_name="workshops",
    )
    date = models.DateField(null=True, blank=True, verbose_name="Date")
    animator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="workshops",
        limit_choices_to={"groups__name": "Experts"},
    )
    name = models.CharField(max_length=128, verbose_name="Nom", default="")

    class Meta:
        verbose_name = "Atelier"
