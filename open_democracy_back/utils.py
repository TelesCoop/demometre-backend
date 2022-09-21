from django.db import models


EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"

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
    INDIVIDUAL = "individual", "Un particulier"
    OTHER = "other", "Autre"


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


class SerializerContext:
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {"request": self.request, "format": self.format_kwarg, "view": self}
