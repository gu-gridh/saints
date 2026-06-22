from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HeadlessPage(Page):
    preview_modes = []

    class Meta:
        abstract = True


class ContentPage(HeadlessPage):

    body = StreamField(
        [
            ("heading", blocks.CharBlock()),
            ("text", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("body"),
    ]
