from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from wagtail.models import Site

from .models import ContentPage, FooterSettings
from .serializers import ContentPageSerializer, FooterSettingsSerializer


class ContentPageDetailView(RetrieveAPIView):
    serializer_class = ContentPageSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return ContentPage.objects.live().public()


class FooterSettingsView(APIView):
    serializer_class = FooterSettingsSerializer

    def get_queryset(self):
        return FooterSettings.objects.all()

    def get(self, request):
        site = Site.find_for_request(request)
        footer = FooterSettings.for_site(site)
        serializer = FooterSettingsSerializer(footer)
        return Response(serializer.data)
