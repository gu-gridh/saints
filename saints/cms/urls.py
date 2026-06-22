from django.urls import path
from .views import ContentPageDetailView

urlpatterns = [
    path("content-pages/<slug:slug>/", ContentPageDetailView.as_view()),
]
