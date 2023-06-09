# Generated by Django 3.2.11 on 2022-07-04 09:26

from django.db import migrations
from django.contrib.auth.models import Group


def create_expert_group(apps, _):
    Group.objects.create(name="Experts")


def remove_expert_group(apps, _):
    Group.objects.get(name="Experts").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("my_auth", "0002_user_is_unknown_user"),
    ]

    operations = [migrations.RunPython(create_expert_group, remove_expert_group)]
