from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register("saints", views.SaintsViewSet, basename="saints")
router.register("people", views.PeopleViewSet, basename="people")
router.register("agents", views.AgentsViewSet, basename="agents")
router.register("cult", views.CultsViewSet, basename="cult")
router.register("advanced", views.CultAdvancedViewSet, basename="advanced")
router.register("place", views.PlacesViewSet, basename="place")
router.register("placechildren", views.PlaceChildrenViewSet, basename="placechildren")
router.register("organization", views.OrganizationViewSet, basename="organization")
router.register("source", views.SourcesViewSet, basename="source")
router.register("quote", views.QuotesViewSet, basename="quote")
router.register("diocese", views.DiocesesViewSet, basename="diocese")
router.register("agenttype", views.AgentTypesViewSet, basename="agenttype")
router.register("culttype", views.CultTypesViewSet, basename="culttype")
router.register("placetype", views.PlaceTypesViewSet, basename="placetype")
router.register("map", views.MapViewSet, basename="map")
router.register("advancedmap", views.AdvancedMapViewSet, basename="advancedmap")

urlpatterns = [
    path("", include(router.urls)),
    # path("api-auth/", include("rest_framework.urls", namespace='rest_framework')),
]
