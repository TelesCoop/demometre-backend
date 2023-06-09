# Generated by Django 3.2.11 on 2022-11-17 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0066_collection_management_permissions'),
        ('open_democracy_back', '0032_alter_question_objectivity'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvaluationBoardPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
            ],
            options={
                'verbose_name': 'Tableau de bord de la participation',
            },
            bases=('wagtailcore.page',),
        ),
    ]
