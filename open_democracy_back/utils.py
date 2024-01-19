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
    WITH_EXPERT = "with_expert", "Evaluation avec expert"


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
    NUMBER = "number", "Nombre"


class QuestionObjectivity(models.TextChoices):
    OBJECTIVE = "objective", "Objective"
    SUBJECTIVE = "subjective", "Subjective"


class QuestionMethod(models.TextChoices):
    QUANTITATIVE = "quantitative", "Quantitative"
    QUALITATIVE = "qualitative", "Qualitative"


QUESTION_TYPE_WITH_SCORE = [
    QuestionType.BOOLEAN,
    QuestionType.UNIQUE_CHOICE,
    QuestionType.MULTIPLE_CHOICE,
    QuestionType.PERCENTAGE,
    QuestionType.NUMBER,
    QuestionType.CLOSED_WITH_SCALE,
]


class SerializerContext:
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {"request": self.request, "format": self.format_kwarg, "view": self}


def generate_randon_string_char_and_digits(length):
    import random
    import string

    letters_and_digits = string.ascii_letters + string.digits
    result_str = "".join(random.choice(letters_and_digits) for i in range(length))
    return result_str


class PillarName(models.TextChoices):
    REPRESENTATION = "représentation", "Représentation"
    TRANSPARENCY = "transparence", "Transparence"
    PARTICIPATION = "participation", "Participation"
    COOPERATION = "coopération", "Coopération"
