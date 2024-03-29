# Generated by Django 3.2.19 on 2023-09-05 06:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import modelcluster.fields
import open_democracy_back.models.utils


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('open_democracy_back', '0044_auto_20230904_0732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assessment',
            name='calendar',
            field=open_democracy_back.models.utils.FrontendRichText(blank=True, default='', verbose_name='calendrier'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='context',
            field=open_democracy_back.models.utils.FrontendRichText(blank=True, default='', verbose_name='contexte'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='objectives',
            field=open_democracy_back.models.utils.FrontendRichText(blank=True, default='', verbose_name='objectifs'),
        ),
        migrations.AlterField(
            model_name='assessment',
            name='stakeholders',
            field=open_democracy_back.models.utils.FrontendRichText(blank=True, default='', verbose_name='parties prenantes'),
        ),
        migrations.AlterField(
            model_name='assessmentdocument',
            name='category',
            field=models.CharField(choices=[('assessment_reports', "Rapports d'évaluation"), ('other', 'Autres documents'), ('invoices', 'Factures')], max_length=20, verbose_name='catégorie'),
        ),
        migrations.AlterField(
            model_name='assessmentdocument',
            name='file',
            field=models.FileField(upload_to='', verbose_name='fichier'),
        ),
        migrations.AlterField(
            model_name='assessmentdocument',
            name='name',
            field=models.CharField(max_length=80, verbose_name='nom'),
        ),
        migrations.CreateModel(
            name='AssessmentPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('amount', models.FloatField(verbose_name='amount')),
                ('assessment', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='open_democracy_back.assessment', unique=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='auteur du paiement')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
