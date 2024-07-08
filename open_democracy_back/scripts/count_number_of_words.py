from open_democracy_back.models import *
import django.apps
from django.db import models as django_models


def is_one_of_subclasses(model, classes):
    for cls in classes:
        if issubclass(model, cls):
            return True
    return False


# count words in all pages
models = list(django.apps.apps.get_models())
word_count = 0
for model in models:
    if not issubclass(model, Page):
        continue
    for field in model._meta.get_fields():
        if not is_one_of_subclasses(
            field.__class__, [StreamField, RichTextField, django_models.CharField]
        ):
            continue
        print(f"Model: {model.__name__}, Field: {field.name}")
        for instance in model.objects.all():
            if issubclass(field.__class__, StreamField):
                word_count += 0.8 * len(str(e._raw_data).split(" "))
            else:
                word_count += len(str(getattr(instance, field.name)).split(" "))

# count words in questionnaire
res = []
for model in models:
    if model._meta.model_name == "questionnairequestion":
        # QuestionnaireQuestion is a proxy models, translated fields are defined
        # in the Question model
        translated_fields = getattr(Question, "translated_fields", None)
    elif not (translated_fields := getattr(model, "translated_fields", None)):
        continue
    for instance in model.objects.all():
        for field in translated_fields:
            res.append(getattr(instance, f"{field}_fr"))
print(len(res))
word_count = 0
for words in res:
    word_count += len(words.split(" ")) if words else 0
