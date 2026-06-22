from rest_framework import serializers


class ContentPageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    show_banner = serializers.BooleanField()
    slug = serializers.CharField()
    body = serializers.SerializerMethodField()

    def get_body(self, page):
        return page.body.get_prep_value()


class FooterSettingsSerializer(serializers.Serializer):
    partner_links = serializers.SerializerMethodField()

    def get_partner_links(self, footer):
        return footer.partner_links.get_prep_value()
