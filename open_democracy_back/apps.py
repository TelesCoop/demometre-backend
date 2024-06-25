from typing import Dict

from django.apps import AppConfig
from django.conf import settings
from django.utils.datastructures import ImmutableList

POSSIBLE_ARGS = ["help_text", "max_length", "features"]
NUMBER_LARGER_THAN_LOCALES_COUNT = 100


class AuthConfig(AppConfig):
    name = "open_democracy_back"
    label = "open_democracy_back"
    verbose_name = "Démomètre"

    def ready(self):
        from wagtail.admin.panels import FieldPanel

        locales_for_translated_fields = settings.LOCALES_FOR_TRANSLATED_FIELDS

        # loop through all models, find models that inherit ModelWithTranslatedFields
        # and programmatically create the translated fields
        for model in self.get_models():
            if model._meta.model_name == "questionnairequestion":
                translated_fields = getattr(
                    self.get_model("Question"), "translated_fields", None
                )
            elif not (translated_fields := getattr(model, "translated_fields", None)):
                continue

            field_order: Dict[str, float] = {
                field.name: ix for ix, field in enumerate(model._meta.fields)
            }
            for field_name in translated_fields:
                if not model._meta.proxy:
                    for locale_ix, locale in enumerate(locales_for_translated_fields):
                        translated_field_name = f"{field_name}_{locale}"
                        original_field = model._meta.get_field(field_name)
                        field_class = type(original_field)
                        args = {
                            key: value
                            for key, value in original_field.__dict__.items()
                            if key in POSSIBLE_ARGS
                        }
                        model.add_to_class(
                            translated_field_name,
                            field_class(
                                **args,
                                blank=True,
                                null=True,
                                verbose_name=f"{original_field.verbose_name or field_name} ({locale})",
                            ),
                        )
                        field_order[translated_field_name] = (
                            field_order[field_name]
                            + locale_ix / NUMBER_LARGER_THAN_LOCALES_COUNT
                        )

                # replace field in model.panels for wagtail admin
                if panels := getattr(model, "panels", None):
                    try:
                        panel_index = [
                            panel.field_name
                            if isinstance(panel, FieldPanel)
                            else "__not_field_panel"
                            for panel in panels
                        ].index(field_name)
                    except ValueError:
                        # field not in panels
                        continue
                    model.panels = (
                        model.panels[:panel_index]
                        + [
                            FieldPanel(f"{field_name}_{locale}")
                            for locale in locales_for_translated_fields
                        ]
                        + model.panels[panel_index + 1 :]
                    )

            # reorder fields so that translated fields are
            # in the same place as the original field
            model._meta.fields = sorted(
                model._meta.fields, key=lambda field: field_order[field.name]
            )
            model._meta.fields = ImmutableList(model._meta.fields)
