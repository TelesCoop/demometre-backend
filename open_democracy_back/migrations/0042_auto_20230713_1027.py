# Generated by Django 3.2.19 on 2023-07-13 10:27

from django.db import migrations
import open_democracy_back.models.contents_models
import wagtail.blocks
import wagtail.documents.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
import wagtailsvg.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('open_democracy_back', '0041_auto_20230713_0758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='content',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'h3', 'h4', 'ol', 'ul', 'document-link', 'h2'], label='Contenu', required=True)), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(label='légende'))])), ('pdf', wagtail.blocks.StructBlock([('document', wagtail.documents.blocks.DocumentChooserBlock()), ('title', wagtail.blocks.TextBlock(label='titre'))]))], blank=True, help_text="Corps de l'article", use_json_field=True, verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='criteria',
            name='explanatory',
            field=wagtail.fields.StreamField([('category', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(label='Titre')), ('description', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Description'))], label='Catégorie', label_format='Catégorie : {title}'))], blank=True, use_json_field=True, verbose_name='Explicatif du critère (sources, exemples, obligations légales ...)'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='how_block_data',
            field=wagtail.fields.StreamField([('title', wagtail.blocks.CharBlock(label='Titre')), ('richtext', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Paragraphe')), ('step', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('svg', wagtailsvg.blocks.SvgChooserBlock(help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG", label='Icon au format svg')), ('title', wagtail.blocks.CharBlock(label='Titre')), ('richtext', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Descriptif')), ('link', wagtail.blocks.CharBlock(label='Lien en savoir plus', required=False))]), label='Etapes', label_format='Carte : {title}'))], blank=True, use_json_field=True, verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='impact_block_data',
            field=wagtail.fields.StreamField([('impact', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Image')), ('title', wagtail.blocks.CharBlock(label='Titre'))], label='Impact', label_format='Impact : {title}'))], blank=True, use_json_field=True, verbose_name='Les impacts'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='objective_block_data',
            field=wagtail.fields.StreamField([('objective', wagtail.blocks.StructBlock([('svg', wagtailsvg.blocks.SvgChooserBlock(help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG", label='Icon au format svg')), ('title', wagtail.blocks.CharBlock(label='Titre'))], label='Objectif', label_format='Objectif : {title}'))], blank=True, use_json_field=True, verbose_name='Les objectifs'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='who_committee_sub_block_data',
            field=wagtail.fields.StreamField([('group_committees', wagtail.blocks.StructBlock([('committee', wagtail.blocks.CharBlock(label='Nom')), ('committee_members', wagtail.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock(open_democracy_back.models.contents_models.Person), label='Membre'))], label='Groupe du Comité d’orientation', label_format='{title}'))], blank=True, use_json_field=True, verbose_name='Membres du Comité - contenu'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='who_partner_sub_block_data',
            field=wagtail.fields.StreamField([('group_partners', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(label='Titre')), ('description', wagtail.blocks.CharBlock(label='Description')), ('partners', wagtail.blocks.ListBlock(wagtail.snippets.blocks.SnippetChooserBlock(open_democracy_back.models.contents_models.Partner)))], label='Type de partenaires', label_format='{title}'))], blank=True, use_json_field=True, verbose_name='Partenaires - contenu'),
        ),
        migrations.AlterField(
            model_name='projectpage',
            name='why_block_data',
            field=wagtail.fields.StreamField([('richtext', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'ol', 'ul'], label='Paragraphe')), ('image', wagtail.images.blocks.ImageChooserBlock(label='Image'))], blank=True, use_json_field=True, verbose_name='Texte'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='content',
            field=wagtail.fields.StreamField([('rich_text', wagtail.blocks.RichTextBlock(features=['bold', 'italic', 'link', 'h3', 'h4', 'ol', 'ul', 'document-link', 'h2'], label='Contenu', required=True)), ('image', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock()), ('caption', wagtail.blocks.TextBlock(label='légende'))])), ('pdf', wagtail.blocks.StructBlock([('document', wagtail.documents.blocks.DocumentChooserBlock()), ('title', wagtail.blocks.TextBlock(label='titre'))]))], blank=True, help_text="Corps de l'article", use_json_field=True, verbose_name='Contenu'),
        ),
        migrations.AlterField(
            model_name='usagepage',
            name='start_assessment_block_data',
            field=wagtail.fields.StreamField([('assessment_type', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(label='Titre')), ('type', wagtail.blocks.ChoiceBlock(choices=[('quick', 'Diagnostic rapide'), ('participative', 'Evaluation participative'), ('with_expert', 'Evaluation avec expert')], label='Type')), ('pdf_button', wagtail.blocks.CharBlock(label='Label du bouton pour le pdf'))], label="Type d'évaluation", label_format='Evaluation : {title}'))], blank=True, help_text="Pour modifier le descriptif de chaque type d'évaluation il faut directement aller dans le type d'évaluation correspondant", use_json_field=True, verbose_name="Descriptif des différents types d'évaluation"),
        ),
        migrations.AlterField(
            model_name='usagepage',
            name='steps_of_use',
            field=wagtail.fields.StreamField([('step', wagtail.blocks.StructBlock([('image', wagtail.images.blocks.ImageChooserBlock(label='Image')), ('title', wagtail.blocks.CharBlock(label='Titre')), ('description', wagtail.blocks.TextBlock(label='Description'))], label='Etape', label_format='Etape : {title}'))], blank=True, use_json_field=True, verbose_name="Etapes d'utilisation"),
        ),
    ]
