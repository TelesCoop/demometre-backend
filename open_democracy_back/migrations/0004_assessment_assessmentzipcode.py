# Generated by Django 3.2.12 on 2022-03-04 11:55

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0003_auto_20220304_0824'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('type', models.CharField(choices=[('municipality', 'Commune'), ('intercommunality', 'Intercommunalité')], default='municipality', max_length=32)),
            ],
            options={
                'verbose_name': 'Évaluation',
                'verbose_name_plural': 'Évaluations',
            },
        ),
        migrations.CreateModel(
            name='AssessmentZipCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('zip_code', models.CharField(max_length=32, verbose_name='Code postal')),
                ('assessment', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='zip_codes', to='open_democracy_back.assessment')),
            ],
            options={
                'verbose_name': 'Code postal',
                'verbose_name_plural': 'Code postaux',
            },
        ),
    ]