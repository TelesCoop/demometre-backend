# Generated by Django 3.2.19 on 2023-06-28 08:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0036_auto_20230627_0935'),
    ]

    operations = [
        migrations.AlterField(
            model_name='percentagerange',
            name='associated_score',
            field=models.IntegerField(blank=True, help_text='Si pertinent', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Score associé'),
        ),
        migrations.AlterField(
            model_name='responsechoice',
            name='associated_score',
            field=models.IntegerField(blank=True, help_text='Si pertinent', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Score associé'),
        ),
    ]
