from rest_framework import serializers
from wagtail.rich_text import expand_db_html


class ContentPageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    show_banner = serializers.BooleanField()
    slug = serializers.CharField()
    body = serializers.SerializerMethodField()

    def get_body(self, page):
        blocks = []

        for block in page.body:
            value = block.value

            if block.block_type == "text":
                value = expand_db_html(str(value))

            blocks.append({
                "type": block.block_type,
                "value": value,
            })

        return blocks


class FooterSettingsSerializer(serializers.Serializer):
    partner_links = serializers.SerializerMethodField()

    def get_partner_links(self, footer):
        return footer.partner_links.get_prep_value()
