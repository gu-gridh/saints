from rest_framework.generics import RetrieveAPIView

from .models import ContentPage
from .serializers import ContentPageSerializer


class ContentPageDetailView(RetrieveAPIView):
    serializer_class = ContentPageSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return ContentPage.objects.live().public()
