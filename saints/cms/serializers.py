from rest_framework import serializers


class ContentPageSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    slug = serializers.CharField()
    body = serializers.SerializerMethodField()

    def get_body(self, page):
        return page.body.get_prep_value()
