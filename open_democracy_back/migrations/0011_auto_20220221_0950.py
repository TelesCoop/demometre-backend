# Generated by Django 3.2.11 on 2022-02-21 09:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0010_auto_20220217_1350'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=125)),
            ],
            options={
                'verbose_name': 'Type de profil',
                'verbose_name_plural': 'Types de profil',
            },
        ),
        migrations.CreateModel(
            name='QuestionFilterByProfileType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('intersection_operator', models.CharField(blank=True, choices=[('and', 'et'), ('or', 'ou')], max_length=8)),
                ('conditional_profile_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions_that_depend_on_me', to='open_democracy_back.profiletype', verbose_name='Filtre par type de profile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='profilingresponsechoice',
            name='profiling_question',
        ),
        migrations.CreateModel(
            name='ProfilingQuestion',
            fields=[
            ],
            options={
                'verbose_name': 'Question de Profilage',
                'verbose_name_plural': 'Questions de Profilage',
                'abstract': False,
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('open_democracy_back.question',),
        ),
        migrations.CreateModel(
            name='QuestionnaireQuestion',
            fields=[
            ],
            options={
                'verbose_name': '4. Question',
                'verbose_name_plural': '4. Questions',
                'abstract': False,
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('open_democracy_back.question',),
        ),
        migrations.AlterModelOptions(
            name='criteria',
            options={'ordering': ['code'], 'verbose_name': '3. Critère', 'verbose_name_plural': '3. Critères'},
        ),
        migrations.AlterModelOptions(
            name='marker',
            options={'ordering': ['code'], 'verbose_name': '2. Marqueur', 'verbose_name_plural': '2. Marqueurs'},
        ),
        migrations.AlterModelOptions(
            name='pillar',
            options={'ordering': ['code'], 'verbose_name': '1. Pilier', 'verbose_name_plural': '1. Piliers'},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['code']},
        ),
        migrations.RenameField(
            model_name='question',
            old_name='question',
            new_name='question_statement',
        ),
        migrations.AddField(
            model_name='question',
            name='profiling_question',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='question',
            name='code',
            field=models.CharField(help_text='Correspond au numéro (ou lettre) de cette question, détermine son ordre', max_length=2, verbose_name='Code'),
        ),
        migrations.DeleteModel(
            name='Profiling',
        ),
        migrations.DeleteModel(
            name='ProfilingResponseChoice',
        ),
        migrations.AddField(
            model_name='questionfilterbyprofiletype',
            name='question',
            field=modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_filters_by_profile_type', to='open_democracy_back.question'),
        ),
    ]