# Generated by Django 3.2.12 on 2022-05-09 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0033_auto_20220429_0919_squashed_0037_auto_20220429_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='participation',
            name='is_profiling_questions_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ParticipationPillarCompleted',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.BooleanField(default=False)),
                ('participation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='open_democracy_back.participation')),
                ('pillar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='open_democracy_back.pillar')),
            ],
        ),
        migrations.AddField(
            model_name='participation',
            name='is_pillar_questions_completed',
            field=models.ManyToManyField(through='open_democracy_back.ParticipationPillarCompleted', to='open_democracy_back.Pillar'),
        ),
    ]