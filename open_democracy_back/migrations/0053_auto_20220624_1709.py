# Generated by Django 3.2.13 on 2022-06-24 15:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.blocks
import wagtail.core.fields
import wagtailsvg.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailimages', '0023_add_choose_permissions'),
        ('open_democracy_back', '0052_auto_20220623_1311'),
    ]

    operations = [
        migrations.RenameField(
            model_name='referentialpage',
            old_name='criteria_block_content',
            new_name='criteria_block_left_content',
        ),
        migrations.AlterField(
            model_name='referentialpage',
            name='criteria_block_left_content',
            field=wagtail.core.fields.RichTextField(blank=True, default='', verbose_name='Paragraphe de gauche'),
        ),
        migrations.RenameField(
            model_name='referentialpage',
            old_name='pillar_block_content',
            new_name='pillar_block_left_content',
        ),
        migrations.AlterField(
            model_name='referentialpage',
            name='pillar_block_left_content',
            field=wagtail.core.fields.RichTextField(blank=True, default='', verbose_name='Paragraphe de gauche'),
        ),
        migrations.AddField(
            model_name='partner',
            name='height',
            field=models.IntegerField(default=60, help_text='Choisir la hauteur du logo (min 40px / max 120px)', validators=[django.core.validators.MinValueValidator(40), django.core.validators.MaxValueValidator(120)], verbose_name='Hauteur'),
        ),
        migrations.AddField(
            model_name='referentialpage',
            name='criteria_block_right_content',
            field=wagtail.core.fields.RichTextField(blank=True, default='', verbose_name='Paragraphe de droite'),
        ),
        migrations.AddField(
            model_name='referentialpage',
            name='pillar_block_right_content',
            field=wagtail.core.fields.RichTextField(blank=True, default='', verbose_name='Paragraphe de droite'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='logo_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='wagtailimages.image', verbose_name='Logo'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='how_block_data',
            field=wagtail.core.fields.StreamField([('title', wagtail.core.blocks.CharBlock(label='Titre')), ('richtext', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Paragraphe')), ('step', wagtail.core.blocks.ListBlock(wagtail.core.blocks.StructBlock([('svg', wagtailsvg.blocks.SvgChooserBlock(help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG", label='Icon au format svg')), ('title', wagtail.core.blocks.CharBlock(label='Titre')), ('richtext', wagtail.core.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Descriptif')), ('link', wagtail.core.blocks.CharBlock(label='Lien en savoir plus', required=False))]), label='Etapes', label_format='Carte : {title}'))], blank=True, verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='objective_block_data',
            field=wagtail.core.fields.StreamField([('objective', wagtail.core.blocks.StructBlock([('svg', wagtailsvg.blocks.SvgChooserBlock(help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG", label='Icon au format svg')), ('title', wagtail.core.blocks.CharBlock(label='Titre'))], label='Objectif', label_format='Objectif : {title}'))], blank=True, verbose_name='Les objectifs'),
        ),
    ]