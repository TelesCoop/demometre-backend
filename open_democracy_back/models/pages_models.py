from typing import List
from django import forms
from django.db import models
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
    FieldRowPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.core.models import Page
from wagtailsvg.blocks import SvgChooserBlock
from open_democracy_back.models.contents_models import Partner
from open_democracy_back.utils import (
    SIMPLE_RICH_TEXT_FIELD_FEATURE,
    ManagedAssessmentType,
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

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Page d'accueil"


class UsagePage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    tag_line = models.CharField(
        max_length=510, default="", verbose_name="Phrase d'accroche"
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
    )

    step_of_use_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide les étapes d'utilisation du DémoMètre ne s'afficheront pas",
    )
    step_of_use_intro = models.CharField(
        max_length=510, verbose_name="Intro", blank=True
    )
    steps_of_use = StreamField(
        [
            (
                "step",
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(label="Image")),
                        ("title", blocks.CharBlock(label="Titre")),
                        ("description", blocks.TextBlock(label="Description")),
                    ],
                    label_format="Etape : {title}",
                    label="Etape",
                ),
            )
        ],
        blank=True,
        verbose_name="Etapes d'utilisation",
    )

    participate_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide les étapes d'utilisation du DémoMètre ne s'afficheront pas",
    )
    participate_block_intro = models.CharField(
        max_length=510, verbose_name="Intro", blank=True
    )
    participate_left_paragraph = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de gauche",
        blank=True,
    )
    participate_right_paragraph = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de droite",
        blank=True,
    )

    start_assessment_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide les étapes d'utilisation du DémoMètre ne s'afficheront pas",
    )
    start_assessment_block_intro = models.CharField(
        max_length=510, verbose_name="Intro", blank=True
    )
    start_assessment_block_data = StreamField(
        [
            (
                "assessment_type",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(label="Titre")),
                        (
                            "type",
                            blocks.ChoiceBlock(
                                choices=ManagedAssessmentType.choices, label="Type"
                            ),
                        ),
                        (
                            "pdf_button",
                            blocks.CharBlock(label="Label du bouton pour le pdf"),
                        ),
                    ],
                    label_format="Evaluation : {title}",
                    label="Type d'évaluation",
                ),
            )
        ],
        blank=True,
        verbose_name="Descriptif des différents types d'évaluation",
        help_text="Pour modifier le descriptif de chaque type d'évaluation il faut directement aller dans le type d'évaluation correspondant",
    )

    content_panels = Page.content_panels + [
        FieldPanel("tag_line"),
        FieldPanel("introduction"),
        ImageChooserPanel("intro_image"),
        MultiFieldPanel(
            [
                FieldPanel("step_of_use_title"),
                FieldPanel("step_of_use_intro"),
                StreamFieldPanel("steps_of_use", classname="full"),
            ],
            heading="Etapes d'utilisation du DémoMètre",
        ),
        MultiFieldPanel(
            [
                FieldPanel("participate_block_title"),
                FieldPanel("participate_block_intro", widget=forms.Textarea),
                FieldRowPanel(
                    [
                        FieldPanel("participate_left_paragraph"),
                        FieldPanel("participate_right_paragraph"),
                    ],
                    heading="Description",
                ),
            ],
            heading="Participer à une évaluation en cours",
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_assessment_block_title"),
                FieldPanel("start_assessment_block_intro", widget=forms.Textarea),
                StreamFieldPanel("start_assessment_block_data", classname="full"),
            ],
            heading="Lancer une nouvelle évaluation",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Page des utilisations possibles"


class ReferentialPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    introduction = models.CharField(max_length=255, default="")

    description = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
    )

    pillar_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="si ce champs est vide l'explication des piliers ne s'affichera pas",
    )
    pillar_block_left_content = RichTextField(
        default="",
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de gauche",
    )
    pillar_block_right_content = RichTextField(
        default="",
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de droite",
    )
    pillar_block_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    marker_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="si ce champs est vide l'explication des marqueurs ne s'affichera pas",
    )
    marker_block_content = RichTextField(
        default="",
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Contenu",
    )

    criteria_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="si ce champs est vide l'explication des critères d'évaluation ne s'affichera pas",
    )
    criteria_block_left_content = RichTextField(
        default="",
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de gauche",
    )
    criteria_block_right_content = RichTextField(
        default="",
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Paragraphe de droite",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("description"),
        MultiFieldPanel(
            [
                FieldPanel("pillar_block_title"),
                FieldRowPanel(
                    [
                        FieldPanel("pillar_block_left_content"),
                        FieldPanel("pillar_block_right_content"),
                    ],
                    heading="Contenu",
                ),
                ImageChooserPanel("pillar_block_image"),
            ],
            heading="Explication des piliers",
        ),
        MultiFieldPanel(
            [
                FieldPanel("marker_block_title"),
                FieldPanel("marker_block_content"),
            ],
            heading="Explication des marqueurs",
        ),
        MultiFieldPanel(
            [
                FieldPanel("criteria_block_title"),
                FieldRowPanel(
                    [
                        FieldPanel("criteria_block_left_content"),
                        FieldPanel("criteria_block_right_content"),
                    ],
                    heading="Contenu",
                ),
            ],
            heading="Explication des critères d'évaluation",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Référentiel"


class ProjectPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    tag_line = models.CharField(
        max_length=510, default="", verbose_name="Phrase d'accroche"
    )
    introduction = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Introduction",
        blank=True,
    )
    intro_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    why_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    why_block_data = StreamField(
        [
            (
                "richtext",
                blocks.RichTextBlock(
                    label="Paragraphe",
                    features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
                ),
            ),
            ("image", ImageChooserBlock(label="Image")),
        ],
        blank=True,
        verbose_name="Texte",
    )

    objective_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    objective_block_data = StreamField(
        [
            (
                "objective",
                blocks.StructBlock(
                    [
                        (
                            "svg",
                            SvgChooserBlock(
                                label="Icon au format svg",
                                help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG",
                            ),
                        ),
                        ("title", blocks.CharBlock(label="Titre")),
                    ],
                    label_format="Objectif : {title}",
                    label="Objectif",
                ),
            )
        ],
        blank=True,
        verbose_name="Les objectifs",
    )

    impact_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    impact_block_data = StreamField(
        [
            (
                "impact",
                blocks.StructBlock(
                    [
                        ("image", ImageChooserBlock(label="Image")),
                        ("title", blocks.CharBlock(label="Titre")),
                    ],
                    label_format="Impact : {title}",
                    label="Impact",
                ),
            )
        ],
        blank=True,
        verbose_name="Les impacts",
    )

    who_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    who_partner_sub_block_title = models.CharField(
        max_length=68,
        verbose_name="Partenaires - titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    who_partner_sub_block_data = StreamField(
        [
            (
                "group_partners",
                blocks.StructBlock(
                    [
                        ("title", blocks.CharBlock(label="Titre")),
                        ("description", blocks.CharBlock(label="Description")),
                        ("partners", blocks.ListBlock(SnippetChooserBlock(Partner))),
                    ],
                    label_format="{title}",
                    label="Type de partenaires",
                ),
            )
        ],
        blank=True,
        verbose_name="Partenaires - contenu",
    )

    how_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    how_block_data = StreamField(
        [
            ("title", blocks.CharBlock(label="Titre")),
            (
                "richtext",
                blocks.RichTextBlock(
                    label="Paragraphe",
                    features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
                ),
            ),
            (
                "step",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "svg",
                                SvgChooserBlock(
                                    label="Icon au format svg",
                                    help_text="Pour ajouter un SVG d'abord l'ajouter dans le menu SVG",
                                ),
                            ),
                            ("title", blocks.CharBlock(label="Titre")),
                            (
                                "richtext",
                                blocks.RichTextBlock(
                                    label="Descriptif",
                                    features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
                                ),
                            ),
                            (
                                "link",
                                blocks.CharBlock(
                                    label="Lien en savoir plus", required=False
                                ),
                            ),
                        ]
                    ),
                    label_format="Carte : {title}",
                    label="Etapes",
                ),
            ),
        ],
        blank=True,
        verbose_name="Contenu",
    )

    content_panels = Page.content_panels + [
        FieldPanel("tag_line", widget=forms.Textarea),
        FieldPanel("introduction"),
        ImageChooserPanel("intro_image"),
        MultiFieldPanel(
            [
                FieldPanel("why_block_title"),
                StreamFieldPanel("why_block_data", classname="full"),
            ],
            heading="Bloc pourquoi",
        ),
        MultiFieldPanel(
            [
                FieldPanel("objective_block_title"),
                StreamFieldPanel("objective_block_data", classname="full"),
            ],
            heading="Bloc objectif",
        ),
        MultiFieldPanel(
            [
                FieldPanel("impact_block_title"),
                StreamFieldPanel("impact_block_data", classname="full"),
            ],
            heading="Bloc Impact",
        ),
        MultiFieldPanel(
            [
                FieldPanel("who_block_title"),
                MultiFieldPanel(
                    [
                        FieldPanel("who_partner_sub_block_title"),
                        StreamFieldPanel(
                            "who_partner_sub_block_data", classname="full"
                        ),
                    ],
                    heading="Sous bloc : Partenaire",
                ),
            ],
            heading="Bloc Avec Qui",
        ),
        MultiFieldPanel(
            [
                FieldPanel("how_block_title"),
                StreamFieldPanel("how_block_data", classname="full"),
            ],
            heading="Bloc Comment",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Page du projet"


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

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

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

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Initialisation d'une évaluation"


class EvaluationQuestionnairePage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    role_question_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
        default="",
    )
    role_question_description = models.TextField(
        verbose_name="Description",
        default="",
    )

    start_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    start_text = models.TextField(
        verbose_name="Texte",
        default="",
    )

    intermediate_step_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    is_intermediate_step_title_with_pillar_names = models.BooleanField(
        default=True,
        verbose_name="Afficher dans le titre le liste des piliers terminés",
    )
    intermediate_step_text_logged_in = models.TextField(
        verbose_name="Texte pour un utilisateur connecté",
        default="",
    )
    intermediate_step_text_logged_out = models.TextField(
        verbose_name="Texte pour un utilisateur non connecté",
        default="",
    )

    finished_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    finished_text_logged_in = models.TextField(
        verbose_name="Texte pour un utilisateur connecté",
        default="",
    )
    finished_text_logged_out = models.TextField(
        verbose_name="Texte pour un utilisateur non connecté",
        default="",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("role_question_title"),
                FieldPanel("role_question_description"),
            ],
            heading="Enoncé de la question concernant les rôles",
        ),
        MultiFieldPanel(
            [
                FieldPanel("start_title"),
                FieldPanel("start_text"),
            ],
            heading="Commencement de l'évaluation",
        ),
        MultiFieldPanel(
            [
                FieldPanel("intermediate_step_title"),
                FieldPanel("intermediate_step_text_logged_in"),
                FieldPanel("intermediate_step_text_logged_out"),
                FieldPanel("is_intermediate_step_title_with_pillar_names"),
            ],
            heading="Etape intermédiaire (évaluation en cours et au moins un pilier terminé)",
        ),
        MultiFieldPanel(
            [
                FieldPanel("finished_title"),
                FieldPanel("finished_text_logged_in"),
                FieldPanel("finished_text_logged_out"),
            ],
            heading="L'Evaluation est terminée, toutes les questions ont été répondu",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Déroulement de l'évaluation"
