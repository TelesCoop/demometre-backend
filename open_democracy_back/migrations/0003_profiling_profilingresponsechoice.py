# Generated by Django 3.2.11 on 2022-02-15 10:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import modelcluster.fields
import uuid
import wagtail.search.index


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('open_democracy_back', '0002_auto_20220211_1642'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profiling',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(default='', max_length=125)),
                ('question', models.TextField(default='')),
                ('type', models.CharField(choices=[('open', 'Ouverte'), ('unique_choice', 'Choix unique'), ('multiple_choice', 'Choix multiple'), ('closed_with_ranking', 'Fermée avec classement'), ('closed_with_scale', 'Fermée à échelle'), ('boolean', 'Binaire oui / non'), ('numerical', 'Numérique')], default='open', help_text='Choisir le type de question', max_length=32)),
                ('min', models.IntegerField(blank=True, null=True, verbose_name='Valeur minimale')),
                ('max', models.IntegerField(blank=True, null=True, verbose_name='Valeur maximale')),
                ('order', models.IntegerField(help_text="Donne l'ordre d'affichage des questions de profilage", verbose_name='N°')),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale')),
            ],
            options={
                'verbose_name': 'Question de Profilage',
                'verbose_name_plural': 'Questions de Profilage',
                'ordering': ['order'],
                'abstract': False,
                'unique_together': {('translation_key', 'locale')},
            },
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
        migrations.CreateModel(
            name='ProfilingResponseChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('translation_key', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('response_choice', models.CharField(default='', max_length=510, verbose_name='Réponse possible')),
                ('locale', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='wagtailcore.locale')),
                ('profiling_question', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='response_choices', to='open_democracy_back.profiling')),
            ],
            options={
                'verbose_name': 'Choix de réponse',
                'verbose_name_plural': 'Choix de réponse',
                'abstract': False,
                'unique_together': {('translation_key', 'locale')},
            },
        ),
    ]