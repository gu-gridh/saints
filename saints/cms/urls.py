from django.urls import path
from .views import ContentPageDetailView, FooterSettingsView

urlpatterns = [
    path("content-pages/<slug:slug>/", ContentPageDetailView.as_view()),
    path("footer/", FooterSettingsView.as_view()),
]
