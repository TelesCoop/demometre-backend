# Generated by Django 3.2.11 on 2022-09-14 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0021_auto_20220912_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluationinitiationpage',
            name='cgu_consent_description_loggedin',
            field=models.TextField(blank=True, default='', verbose_name='Description pour un utilisateur connecté'),
        ),
        migrations.AlterField(
            model_name='evaluationinitiationpage',
            name='cgu_consent_description_loggedout',
            field=models.TextField(blank=True, default='', verbose_name='Description pour un utilisateur NON connecté'),
        ),
        migrations.AlterField(
            model_name='evaluationinitiationpage',
            name='cgv_consent_description',
            field=models.TextField(blank=True, default='', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='blog_block_intro',
            field=models.TextField(blank=True, verbose_name='Intro du bloc Blog'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='feedback_block_intro',
            field=models.TextField(blank=True, verbose_name="Intro du bloc retours d'expérience"),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='partner_block_intro',
            field=models.TextField(blank=True, verbose_name='Intro du bloc Partenaires'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='resources_block_intro',
            field=models.TextField(blank=True, verbose_name='Intro du bloc Ressources'),
        ),
        migrations.AlterField(
            model_name='referentialpage',
            name='introduction',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='usagepage',
            name='tag_line',
            field=models.TextField(default='', verbose_name="Phrase d'accroche"),
        ),
    ]