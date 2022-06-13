from typing import List
from django.db import models
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.models import Page

from open_democracy_back.models.questionnaire_and_profiling_models import (
    SIMPLE_RICH_TEXT_FIELD_FEATURE,
)


class HomePage(Page):
    # HomePage can be created only on the root
    parent_page_types = ["wagtailcore.Page"]
    preview_modes = None

    tag_line = models.CharField(
        max_length=255, default="", verbose_name="Phrase d'accroche"
    )
    introduction = RichTextField(
        default="", features=SIMPLE_RICH_TEXT_FIELD_FEATURE, verbose_name="Introduction"
    )
    intro_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Si l'id d'une vidéo youtube est indiqué alors l'image ne sera pas affiché sur la page d'accueil",
    )
    intro_youtube_video_id = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Vidéo Youtube (id)",
        help_text="Indiquer ici seulement l'id de la video youtube, celui-ci est indiqué dans l'url après 'v='. Exemple : pour https://www.youtube.com/watch?v=xMQMvVIB0vM renseigner xMQMvVIB0vM",
    )
    feedback_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc retours d'expérience",
        blank=True,
        help_text="Si ce champ est vide les retours d'expérience ne s'afficheront pas sur l'accueil",
    )
    feedback_block_intro = models.CharField(
        max_length=255, verbose_name="Intro du bloc retours d'expérience", blank=True
    )
    blog_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Blog",
        blank=True,
        help_text="Si ce champ est vide les articles de blog ne s'afficheront pas sur l'accueil",
    )
    blog_block_intro = models.CharField(
        max_length=255, verbose_name="Intro du bloc Blog", blank=True
    )
    resources_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Ressources",
        blank=True,
        help_text="Si ce champ est vide bloc Ressources ne s'afficheront pas sur l'accueil",
    )
    resources_block_intro = models.CharField(
        max_length=255, verbose_name="Intro du bloc Ressources", blank=True
    )
    partner_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Partenaires",
        blank=True,
        help_text="Si ce champ est vide le bloc Partenaires ne s'afficheront pas sur l'accueil",
    )
    partner_block_intro = models.CharField(
        max_length=255, verbose_name="Intro du bloc Partenaires", blank=True
    )

    content_panels = Page.content_panels + [
        FieldPanel("tag_line"),
        FieldPanel("introduction"),
        MultiFieldPanel(
            [
                ImageChooserPanel("intro_image"),
                FieldPanel("intro_youtube_video_id"),
            ],
            heading="Image ou Vidéo d'introduction",
        ),
        MultiFieldPanel(
            [
                FieldPanel("feedback_block_title"),
                FieldPanel("feedback_block_intro"),
            ],
            heading="Retour d'expérience",
        ),
        MultiFieldPanel(
            [
                FieldPanel("blog_block_title"),
                FieldPanel("blog_block_intro"),
            ],
            heading="Blog",
        ),
        MultiFieldPanel(
            [
                FieldPanel("resources_block_title"),
                FieldPanel("resources_block_intro"),
            ],
            heading="Ressources",
        ),
        MultiFieldPanel(
            [
                FieldPanel("partner_block_title"),
                FieldPanel("partner_block_intro"),
            ],
            heading="Partenaires",
        ),
    ]

    class Meta:
        verbose_name = "Page d'accueil"


class ReferentialPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    introduction = models.CharField(max_length=255, default="")

    pillar_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre explication pilier",
        blank=True,
        help_text="si ce champs est vide l'explication des piliers ne s'affichera pas",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("pillar_block_title"),
    ]

    class Meta:
        verbose_name = "Référentiel"


class EvaluationIntroPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    account_incentive_title = models.CharField(
        max_length=68, default="", verbose_name="Titre pour l'incitation à la connexion"
    )
    account_incentive = models.CharField(
        max_length=255, default="", verbose_name="Incitation à la connexion"
    )
    introduction = models.TextField(default="")
    data_consent = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Consentement sur les données personnelles",
        help_text="Demande de consentement à conserver les données personnelles demandées, RGPD",
    )

    content_panels = Page.content_panels + [
        FieldPanel("account_incentive_title"),
        FieldPanel("account_incentive"),
        FieldPanel("introduction"),
        FieldPanel("data_consent"),
    ]

    class Meta:
        verbose_name = "Intro à l'évaluation"


class EvaluationInitPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    introduction = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Explication de l'initialisation",
        help_text="Expliquer qu'aucune évaluation n'existe dans cette localité là, que des questions sur la vie politique de la ville précise seront posées, qu'il faut être connecté pour pouvoir initer une évaluation etc",
    )

    public_name_question = models.TextField(
        verbose_name="Enoncé de la question sur la publication ou non du nom de l'initateur",
        default="",
        help_text="Question RGPD - La réponse est oui / non - Si l'évaluation est faite au nom d'une association alors c'est le nom de cette association qui sera affichée",
    )

    public_name_question_description = models.TextField(
        verbose_name="Description de la question sur la publication ou non du nom de l'initateur",
        default="",
        help_text="Expliciter à l'utilisateur ce qu'implique ou non d'autoriser à publier son nom",
    )

    representativity_title = models.TextField(
        verbose_name="Titre pour les questions sur les seuils d'acceptabilité de la représentativité",
        default="",
        help_text="Correspond à la partie où seront posées les questions sur les seuils d'acceptabilité de la représentativité",
    )

    representativity_description = RichTextField(
        verbose_name="Description de la question sur la limite de représentativité",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        help_text="Permet à la personne de mieux comprendre les questions sur les représentativités, et lui donne des éléments de réponse",
    )

    initialization_validation = RichTextField(
        verbose_name="Texte de validation de l'initialisation d'une évaluation",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        help_text="S'affichera une fois l'initialisation de l'évaluation terminée",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("public_name_question"),
        FieldPanel("public_name_question_description"),
        FieldPanel("representativity_title"),
        FieldPanel("representativity_description"),
        FieldPanel("initialization_validation"),
    ]

    class Meta:
        verbose_name = "Initialisation d'une évaluation"
