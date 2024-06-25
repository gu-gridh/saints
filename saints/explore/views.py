from rest_framework import viewsets, filters
from django.db.models import Q
from . import models
from rest_framework.decorators import action
from .serializers import AgentSerializer, CultSerializer, PlaceSerializer, \
    AgentTypeSerializer, PlaceTypeSerializer, CultTypeSerializer, \
    SourceSerializer, OrganizationSerializer, OrganizationMiniSerializer, \
    AgentNameSerializer


# Create your views here.
# ViewSets define the view behavior.

class AgentsViewSet(viewsets.ReadOnlyModelViewSet):    
    def get_queryset(self):        
        gender = self.request.query_params.get('gender')
        agent_type = self.request.query_params.get('type')
        queryset = models.Agent.objects.all()
        if gender is not None:
            queryset = queryset.filter(gender=gender)
        if agent_type is not None:
            queryset = queryset.filter(relation_type__in=agent_type.split(','))
        return queryset
    serializer_class = AgentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'agentname__name']
    ordering_fields = ['name']
    ordering = ['name']


class SaintsViewSet(AgentsViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(saint=True)
        return queryset


class PeopleViewSet(AgentsViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(saint=False)
        return queryset


class OrganizationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class AgentNamesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.AgentName.objects.all()
    serializer_class = AgentNameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class CultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Cult.objects.all()
    serializer_class = CultSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['place__name']
    ordering_fields = ['place__name']
    ordering = ['place__name']


class PlacesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned places to a type
        by filtering against a `type` query parameter in the URL.
        """
        queryset = models.Place.objects.all()
        place_type = self.request.query_params.get('type')
        if place_type is not None:
            queryset = queryset.filter(place_type=place_type)
        return queryset

    # def retrieve(self, request, pk=None):
    #    obj = super().retrieve(request, pk)
    #   return obj

    serializer_class = PlaceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class SourcesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned sources to a type
        and/or the first letter, by filtering against a `type`
        and/or `letter` query parameter in the URL.
        """
        queryset = models.Source.objects.all()
        source_type = self.request.query_params.get('type')
        first_letter = self.request.query_params.get('letter')
        if source_type is not None:
            queryset = queryset.filter(source_type=source_type)
        if first_letter is not None:
            queryset = queryset.filter(Q(name__startswith=first_letter)
                                       | Q(title__startswith=first_letter)
                                       | Q(author__startswith=first_letter))
        return queryset

    serializer_class = SourceSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'title', 'author']
    ordering_fields = ['name', 'author']
    ordering = ['name']


class PlaceTypesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned sources to a type
        and/or the first letter, by filtering against a `type`
        and/or `letter` query parameter in the URL.
        """
        queryset = models.PlaceType.objects.all()
        parent = self.request.query_params.get('parent')
        if parent is not None:
            queryset = queryset.filter(parent=parent)
        else:
            queryset = queryset.filter(parent=None)
        return queryset
    serializer_class = PlaceTypeSerializer


class CultTypesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned cult types to
        a certain parent type, by filtering against a `parent`
        query parameter in the URL which can be a list.
        """
        queryset = models.CultType.objects.all()
        parent = self.request.query_params.get('parent')
        if parent is not None:
            queryset = queryset.filter(parent__in=parent.split(','))
        else:
            queryset = queryset.filter(parent=None)
        return queryset
    serializer_class = CultTypeSerializer


class AgentTypesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned agent types
        depending if it is a saint or not, by filtering 
        against a 'saint' query parameter in the URL.
        """
        queryset = models.AgentType.objects.all()
        saint = self.request.query_params.get('saint')
        if saint is not None:
            queryset = queryset.filter(agent__saint=saint)
        return queryset
    serializer_class = AgentTypeSerializer
