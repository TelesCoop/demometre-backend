from typing import List
from django import forms
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel,
    MultiFieldPanel,
    StreamFieldPanel,
    FieldRowPanel,
    ObjectList,
    TabbedInterface,
    InlinePanel,
)

from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.core.models import Page
from wagtailsvg.blocks import SvgChooserBlock
from open_democracy_back.models.contents_models import Partner, Person
from open_democracy_back.utils import (
    SIMPLE_RICH_TEXT_FIELD_FEATURE,
    ManagedAssessmentType,
)
from modelcluster.fields import ParentalKey


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
    feedback_block_intro = models.TextField(
        verbose_name="Intro du bloc retours d'expérience", blank=True
    )
    blog_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Blog",
        blank=True,
        help_text="Si ce champ est vide les articles de blog ne s'afficheront pas sur l'accueil",
    )
    blog_block_intro = models.TextField(verbose_name="Intro du bloc Blog", blank=True)
    resources_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Ressources",
        blank=True,
        help_text="Si ce champ est vide bloc Ressources ne s'afficheront pas sur l'accueil",
    )
    resources_block_intro = models.TextField(
        verbose_name="Intro du bloc Ressources", blank=True
    )
    partner_block_title = models.CharField(
        max_length=68,
        verbose_name="Titre du bloc Partenaires",
        blank=True,
        help_text="Si ce champ est vide le bloc Partenaires ne s'afficheront pas sur l'accueil",
    )
    partner_block_intro = models.TextField(
        verbose_name="Intro du bloc Partenaires", blank=True
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

    tag_line = models.TextField(default="", verbose_name="Phrase d'accroche")
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

    introduction = models.TextField(default="")

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


class ResultsPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    tag_line = models.CharField(max_length=510, default="", verbose_name="Consigne")
    tag_line_no_results = models.CharField(
        max_length=510, default="", verbose_name="Consigne si aucun résultat publié"
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

    content_panels = Page.content_panels + [
        FieldPanel("tag_line"),
        FieldPanel("tag_line_no_results"),
        FieldPanel("introduction"),
        ImageChooserPanel("intro_image"),
    ]

    class Meta:
        verbose_name = "Page de résultats"


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
    who_crew_sub_block_title = models.CharField(
        max_length=68,
        verbose_name="Equipe Démocratie Ouverte - titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    who_crew_sub_block_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name="Logo Démocratie Ouverte",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    who_committee_sub_block_title = models.CharField(
        max_length=68,
        verbose_name="Le Comité d’orientation - titre",
        blank=True,
        help_text="Si ce champ est vide le bloc ne s'affichera pas",
    )
    who_committee_sub_block_description = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Le Comité d’orientation - description",
        blank=True,
    )
    who_committee_sub_block_data = StreamField(
        [
            (
                "group_committees",
                blocks.StructBlock(
                    [
                        ("committee", blocks.CharBlock(label="Nom")),
                        (
                            "committee_members",
                            blocks.ListBlock(
                                SnippetChooserBlock(Person), label="Membre"
                            ),
                        ),
                    ],
                    label_format="{title}",
                    label="Groupe du Comité d’orientation",
                ),
            )
        ],
        blank=True,
        verbose_name="Membres du Comité - contenu",
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
                        FieldPanel("who_crew_sub_block_title"),
                        ImageChooserPanel("who_crew_sub_block_image"),
                        InlinePanel(
                            "who_crew_sub_block_members",
                            label="Membres de Démocratie Ouverte",
                        ),
                    ],
                    heading="Sous bloc : Equipe Démocratie Ouverte",
                ),
                MultiFieldPanel(
                    [
                        FieldPanel("who_committee_sub_block_title"),
                        FieldPanel("who_committee_sub_block_description"),
                        StreamFieldPanel(
                            "who_committee_sub_block_data", classname="full"
                        ),
                    ],
                    heading="Sous bloc : Equipe Comité d’orientation",
                ),
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


class ProjectPagePerson(models.Model):
    page = ParentalKey(
        ProjectPage, on_delete=models.CASCADE, related_name="who_crew_sub_block_members"
    )
    person = models.ForeignKey(Person, on_delete=models.CASCADE, verbose_name="Membre")

    panels = [
        SnippetChooserPanel("person"),
    ]

    class Meta:
        unique_together = ("page", "person")


class EvaluationInitiationPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    search_assessment_title = models.CharField(
        verbose_name=_("title"),
        max_length=255,
    )
    search_assessment_description = models.TextField(
        default="", verbose_name="Description", blank=True
    )

    cgu_consent_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    cgu_consent_description_loggedin = models.TextField(
        default="",
        verbose_name="Description pour un utilisateur connecté",
        blank=True,
    )
    cgu_consent_description_loggedout = models.TextField(
        default="",
        verbose_name="Description pour un utilisateur NON connecté",
        blank=True,
    )

    cgv_consent_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    cgv_consent_description = models.TextField(
        default="",
        verbose_name="Description",
        blank=True,
    )
    royalty_description = models.TextField(
        default="", verbose_name="Texte sur redevance d'utilisation", blank=True
    )

    no_assessment_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    no_assessment_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )

    one_quick_assessment_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    one_quick_assessment_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )

    one_assessment_with_expert_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    one_assessment_with_expert_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )

    one_participation_assessment_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    one_participation_assessment_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )
    add_expert_title = models.CharField(
        max_length=255, default="", verbose_name="Ajout d'un expert - Titre"
    )
    add_expert_description = models.TextField(
        default="", verbose_name="Ajout d'un expert - Description", blank=True
    )
    add_expert_button_yes = models.CharField(
        max_length=68, default="", verbose_name="Ajout d'un expert - Bouton OUI"
    )
    add_expert_button_no = models.CharField(
        max_length=68, default="", verbose_name="Ajout d'un expert - Bouton NON"
    )

    must_be_connected_to_create_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    must_be_connected_to_create_description = models.TextField(
        default="", verbose_name="Description", blank=True
    )

    create_quick_assessment_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    create_quick_assessment_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )

    create_participation_assessment_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    create_participation_assessment_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )

    create_assessment_with_expert_title = models.CharField(
        max_length=255, default="", verbose_name="Titre"
    )
    create_assessment_with_expert_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )
    choose_expert_text = models.CharField(
        max_length=255, default="", verbose_name="Choisir un expert dans la liste"
    )
    if_no_expert_text = models.CharField(
        max_length=255,
        default="",
        verbose_name="Si il n'y a pas mon expert, contactez-nous",
    )

    init_title = models.CharField(max_length=255, default="", verbose_name="Titre")
    init_description = RichTextField(
        verbose_name="Description",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )
    initiator_name_question = models.CharField(
        max_length=255,
        verbose_name="Enoncé de la question sur le nom de l'initateur qui sera affiché publiquement",
        default="",
    )
    initiator_name_description = models.TextField(
        verbose_name="Description de la question sur le nom de l'initateur qui sera affiché publiquement",
        default="",
        blank=True,
    )

    representativity_title = models.TextField(
        verbose_name="Titre - page des seuils d'acceptabilité de la représentativité",
        default="",
        help_text="Correspond à la partie où seront posées les questions sur les seuils d'acceptabilité de la représentativité",
    )
    representativity_description = RichTextField(
        verbose_name="Description - page des seuils d'acceptabilité de la représentativité",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        help_text="Permet à la personne de mieux comprendre les questions sur les représentativités, et lui donne des éléments de réponse",
        blank=True,
    )

    objective_questions_title = models.CharField(
        max_length=255,
        default="",
        verbose_name="Titre - Répondre aux questions objectives",
    )
    objective_questions_description = RichTextField(
        verbose_name="Description - Répondre aux questions objectives",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )
    objective_questions_call_to_action = models.CharField(
        max_length=32,
        verbose_name="Call to action - Répondre aux questions objectives",
        default="Commencer",
    )

    initialization_validation_title = models.CharField(
        max_length=255,
        default="",
        verbose_name="Titre - page de validation",
        help_text="S'affichera une fois l'initialisation de l'évaluation terminée",
    )
    initialization_validation_description = RichTextField(
        verbose_name="Description - page de validation",
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        blank=True,
    )
    initialization_validation_call_to_action = models.CharField(
        max_length=32,
        verbose_name="Call to action - page de validation",
        default="Commencer l'évaluation",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("search_assessment_title"),
                FieldPanel("search_assessment_description"),
            ],
            heading="Recherche d'une évaluation",
        ),
        MultiFieldPanel(
            [
                FieldPanel("no_assessment_title"),
                FieldPanel("no_assessment_description"),
            ],
            heading="Aucune évaluation ne correspond",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cgu_consent_title"),
                FieldPanel("cgu_consent_description_loggedin"),
                FieldPanel("cgu_consent_description_loggedout"),
            ],
            heading="Consentement aux CGU",
        ),
        MultiFieldPanel(
            [
                FieldPanel("cgv_consent_title"),
                FieldPanel("cgv_consent_description"),
                FieldPanel("royalty_description"),
            ],
            heading="Consentement aux CGV",
        ),
        MultiFieldPanel(
            [
                FieldPanel("one_quick_assessment_title"),
                FieldPanel("one_quick_assessment_description"),
            ],
            heading="Un diagnostic rapide correspond",
        ),
        MultiFieldPanel(
            [
                FieldPanel("one_participation_assessment_title"),
                FieldPanel("one_participation_assessment_description"),
                FieldPanel("add_expert_title"),
                FieldPanel("add_expert_description"),
                FieldPanel("add_expert_button_yes"),
                FieldPanel("add_expert_button_no"),
            ],
            heading="Une évaluation participative correspond",
        ),
        MultiFieldPanel(
            [
                FieldPanel("must_be_connected_to_create_title"),
                FieldPanel("must_be_connected_to_create_description"),
            ],
            heading="Un utilisateur non connecté ne peut pas initaliser une évaluation",
        ),
        MultiFieldPanel(
            [
                FieldPanel("one_assessment_with_expert_title"),
                FieldPanel("one_assessment_with_expert_description"),
            ],
            heading="Une évaluation avec expert correspond",
        ),
        MultiFieldPanel(
            [
                FieldPanel("create_quick_assessment_title"),
                FieldPanel("create_quick_assessment_description"),
            ],
            heading="Créer un diagnostic rapide",
        ),
        MultiFieldPanel(
            [
                FieldPanel("create_participation_assessment_title"),
                FieldPanel("create_participation_assessment_description"),
            ],
            heading="Créer une évaluation participative",
        ),
        MultiFieldPanel(
            [
                FieldPanel("create_assessment_with_expert_title"),
                FieldPanel("create_assessment_with_expert_description"),
                FieldPanel("choose_expert_text"),
                FieldPanel("if_no_expert_text"),
            ],
            heading="Créer une évaluation avec un expert",
        ),
        MultiFieldPanel(
            [
                FieldPanel("init_title"),
                FieldPanel("init_description"),
                FieldPanel("initiator_name_question"),
                FieldPanel("initiator_name_description"),
                FieldPanel("representativity_title"),
                FieldPanel("representativity_description"),
                FieldPanel("objective_questions_title"),
                FieldPanel("objective_questions_description"),
                FieldPanel("objective_questions_call_to_action"),
                FieldPanel("initialization_validation_title"),
                FieldPanel("initialization_validation_description"),
                FieldPanel("initialization_validation_call_to_action"),
            ],
            heading="Initialisation de l'évaluation",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Lancement d'une évaluation"


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
    role_question_description = RichTextField(
        null=True,
        blank=True,
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
    )

    end_of_profiling_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
        default="",
    )
    end_of_profiling_description = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Description",
        help_text="Expliquer qu'il ne sera pas possible de revenir en arrière, puisque les questions du questionnaire dépendent du profilage",
    )
    end_of_profiling_call_to_action = models.CharField(
        max_length=32,
        verbose_name="Call to action",
        default="Valider",
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
                FieldPanel("end_of_profiling_title"),
                FieldPanel("end_of_profiling_description"),
                FieldPanel("end_of_profiling_call_to_action"),
            ],
            heading="Page de confirmation du profilage",
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


class AnimatorPage(Page):
    parent_page_types = ["HomePage"]
    subpage_types: List[str] = []
    max_count_per_parent = 1
    preview_modes = None

    list_workshops_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    list_workshop_intro = models.TextField(
        verbose_name="Introduction",
        default="",
    )

    close_workshop_validation = RichTextField(
        default="",
        features=SIMPLE_RICH_TEXT_FIELD_FEATURE,
        verbose_name="Explication du la clôture d'un workshop",
        help_text="Après clôture l'expert ne pourra plus accéder aux réponses des participants et donc ne pourra plus les modifier, leurs réponses seront alors pris en compte pour le calcul des résultats",
    )

    add_participants_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    add_participants_intro = models.TextField(
        verbose_name="Introduction",
        default="",
    )

    responses_title = models.CharField(
        max_length=128,
        verbose_name="Titre",
    )
    responses_intro = models.TextField(
        verbose_name="Introduction",
        default="",
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("list_workshops_title"),
                FieldPanel("list_workshop_intro"),
                FieldPanel("close_workshop_validation"),
            ],
            heading="Page ateliers",
        ),
        MultiFieldPanel(
            [
                FieldPanel("add_participants_title"),
                FieldPanel("add_participants_intro"),
            ],
            heading="Page participants",
        ),
        MultiFieldPanel(
            [
                FieldPanel("responses_title"),
                FieldPanel("responses_intro"),
            ],
            heading="Page réponses",
        ),
    ]

    # Admin tabs list (Remove promotion and settings tabs)
    edit_handler = TabbedInterface([ObjectList(content_panels, heading="Content")])

    class Meta:
        verbose_name = "Espace Expert"
