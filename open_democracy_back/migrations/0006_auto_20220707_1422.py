# Generated by Django 3.2.11 on 2022-07-07 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0005_rgpdsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationquestionnairepage',
            name='role_question_description',
            field=models.TextField(default='', verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='evaluationquestionnairepage',
            name='role_question_title',
            field=models.CharField(default='', max_length=128, verbose_name='Titre'),
        ),
    ]