from django.db import models


SIMPLE_RICH_TEXT_FIELD_FEATURE = [
    "bold",
    "italic",
    "link",
    "ol",
    "ul",
]

NUMERICAL_OPERATOR = [
    ("<", "<"),
    (">", ">"),
    ("<=", "<="),
    (">=", ">="),
    ("!=", "!="),
    ("=", "="),
]


# NB : use get_<field_name>_display() to retrieve the second argument of TextChoices
class LocalityType(models.TextChoices):
    MUNICIPALITY = "municipality", "Commune"
    INTERCOMMUNALITY = "intercommunality", "Intercommunalité"


class InitiatorType(models.TextChoices):
    COLLECTIVITY = "collectivity", "La collectivité"
    ASSOCIATION = "association", "Une association"


class ManagedAssessmentType(models.TextChoices):
    QUICK = "quick", "Diagnostic rapide"
    PARTICIPATIVE = "participative", "Evaluation participative"
    WITH_EXPERT = "with_expert", "Evaluation avec experts"


class BooleanOperator(models.TextChoices):
    AND = "and", "et"
    OR = "or", "ou"


class QuestionType(models.TextChoices):
    OPEN = "open", "Ouverte"
    UNIQUE_CHOICE = "unique_choice", "Choix unique"
    MULTIPLE_CHOICE = "multiple_choice", "Choix multiple"
    CLOSED_WITH_SCALE = "closed_with_scale", "Fermée à échelle"
    BOOLEAN = "boolean", "Binaire oui / non"
    PERCENTAGE = "percentage", "Pourcentage"
    # Inactive question type
    # CLOSED_WITH_RANKING = "closed_with_ranking", "Fermée avec classement"
