from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("saints", views.SaintsViewSet, basename="saints")
router.register("people", views.PeopleViewSet, basename="people")
router.register("cult", views.CultViewSet, basename="cult")
router.register("place", views.PlacesViewSet, basename="place")
router.register("organization", views.OrganizationViewSet, basename="organization")
router.register("source", views.SourcesViewSet, basename="source")
router.register("agenttype", views.AgentTypesViewSet, basename="agenttype")
router.register("culttype", views.CultTypesViewSet, basename="culttype")
router.register("placetype", views.PlaceTypesViewSet, basename="placetype")

urlpatterns = [
    path("", include(router.urls)),
    # path("api-auth/", include("rest_framework.urls", namespace='rest_framework')),
]
