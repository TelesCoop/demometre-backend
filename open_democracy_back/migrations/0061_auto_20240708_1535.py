# Generated by Django 5.0.6 on 2024-07-08 15:35

from django.db import migrations


fr_fields = {
    "RGPDSettings": ["confidentiality_policy", "content_license", "legal_mention", "terms_of_sale", "terms_of_use"],
}


def fill_models_fr_fields(apps, schema_editor):
    for model_name, fields in fr_fields.items():
        Model = apps.get_model("open_democracy_back", model_name)
        for field in fields:
            field_fr = f"{field}_fr"
            for instance in Model.objects.all():
                setattr(instance, field_fr, getattr(instance, field))
                instance.save()


class Migration(migrations.Migration):
    dependencies = [
        ("open_democracy_back", "0060_rgpdsettings_confidentiality_policy_en_and_more"),
    ]

    operations = [
        migrations.RunPython(fill_models_fr_fields, migrations.RunPython.noop),
    ]
