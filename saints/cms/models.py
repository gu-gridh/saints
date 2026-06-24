from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField

from wagtail import blocks
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


class TextBlockColumns(blocks.StructBlock):
    text = blocks.RichTextBlock(features=["h3", "bold", "italic", "link", "hr",
                                          "ol", "ul", "blockquote", 
                                          "document-link", "image"])
    two_columns = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "doc-full"
        label = "Text"


class HeadlessPage(Page):
    preview_modes = []

    class Meta:
        abstract = True


class ContentPage(HeadlessPage):
    FULL = "full"
    HALF = "half"

    CONTENT_WIDTH_CHOICES = [
        (FULL, "Full width"),
        (HALF, "Half width"),
    ]

    content_width = models.CharField(
        max_length=10,
        choices=CONTENT_WIDTH_CHOICES,
        default=FULL,
    )
    show_banner = models.BooleanField(default=False)

    body = StreamField(
        [
            ("heading", blocks.CharBlock()),
            ("text", TextBlockColumns()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("show_banner"),
        FieldPanel("content_width"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("show_banner"),
        APIField("content_width"),
        APIField("body"),
    ]


@register_setting
class FooterSettings(BaseSiteSetting):
    partner_links = StreamField(
        [
            (
                "link",
                blocks.StructBlock(
                    [
                        ("label", blocks.CharBlock()),
                        ("url", blocks.URLBlock()),
                    ]
                ),
            ),
        ],
        use_json_field=True,
        blank=True,
    )
