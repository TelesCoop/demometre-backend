from django.db import models
from my_auth.models import User
from django.utils.translation import gettext_lazy as _


class Participant(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(_("email address"), blank=True, unique=True, null=True)


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
    closed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Atelier"
