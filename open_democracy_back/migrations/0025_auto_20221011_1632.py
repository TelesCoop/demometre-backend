# Generated by Django 3.2.11 on 2022-10-11 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0024_auto_20220923_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='evaluationinitiationpage',
            name='search_assessment_locality_type_description',
            field=models.TextField(blank=True, default='', verbose_name='Description de la question Commune / Interco'),
        ),
        migrations.AddField(
            model_name='evaluationinitiationpage',
            name='search_assessment_locality_type_question',
            field=models.TextField(blank=True, default='', verbose_name='Question Commune / Interco'),
        ),
        migrations.AddField(
            model_name='evaluationinitiationpage',
            name='search_assessment_no_result',
            field=models.TextField(blank=True, default='', verbose_name='Aucun résultat'),
        ),
        migrations.AddField(
            model_name='evaluationinitiationpage',
            name='search_assessment_zip_code_description',
            field=models.TextField(blank=True, default='', verbose_name='Description de la question du code postal'),
        ),
        migrations.AddField(
            model_name='evaluationinitiationpage',
            name='search_assessment_zip_code_question',
            field=models.TextField(blank=True, default='', verbose_name='Question du code postal'),
        ),
    ]
