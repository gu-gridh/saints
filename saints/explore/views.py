from rest_framework import viewsets, filters, pagination
from rest_framework.settings import api_settings
from django.db.models import Q
from . import models
from rest_framework.decorators import action
from .serializers import AgentSerializer, CultSerializer, PlaceSerializer, \
    AgentTypeSerializer, PlaceTypeSerializer, CultTypeSerializer, \
    SourceSerializer, OrganizationSerializer, \
    AgentNameSerializer, AgentMiniSerializer, PlaceMiniSerializer, \
    CultMiniSerializer


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 200
    max_page_size = 200


# Create your views here.
# ViewSets define the view behavior.
class AgentsViewSet(viewsets.ReadOnlyModelViewSet):    
    def get_queryset(self):        
        gender = self.request.query_params.get('gender')
        agent_type = self.request.query_params.get('type')
        queryset = models.Agent.objects.all().order_by('name')
        if gender is not None:
            queryset = queryset.filter(gender=gender).order_by('name')
        if agent_type is not None:
            queryset = queryset.filter(agent_type__in=agent_type.split(',')).order_by('name')
        queryset = queryset.prefetch_related('relation_cult_agent')
        return queryset

    def get_serializer_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return AgentMiniSerializer
        else:
            return AgentSerializer
    
    def get_pagination_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return LargeResultsSetPagination
        return api_settings.DEFAULT_PAGINATION_CLASS 
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = property(fget=get_pagination_class)
    search_fields = ['name', 'agentname__name']
    ordering_fields = ['name']
    ordering = ['name']


class SaintsViewSet(AgentsViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(saint=True).order_by('name')
        return queryset


class PeopleViewSet(AgentsViewSet):
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(saint=False).order_by('name')
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
    def get_queryset(self):        
        cult_type = self.request.query_params.get('type')
        uncertainty = self.request.query_params.get('uncertainty')
        queryset = models.Cult.objects.all()
        if cult_type is not None:
            queryset = queryset.filter(cult_type__in=cult_type.split(','))
        if uncertainty is not None:
            queryset = queryset.filter(cult_uncertainty=uncertainty)
        return queryset.order_by('place__name')

    def get_serializer_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return CultMiniSerializer
        else:
            return CultSerializer
    
    def get_pagination_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return LargeResultsSetPagination
        return api_settings.DEFAULT_PAGINATION_CLASS 

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = property(fget=get_pagination_class)
    search_fields = ['place__name']
    ordering_fields = ['place__name', 'cult_type__name']
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
            queryset = queryset.filter(place_type=place_type).order_by('name')
        else:
            queryset = queryset.order_by('name')
        return queryset

    def get_serializer_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return PlaceMiniSerializer
        else:
            return PlaceSerializer
    
    def get_pagination_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return LargeResultsSetPagination
        return api_settings.DEFAULT_PAGINATION_CLASS

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = property(fget=get_pagination_class)
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
        return queryset.order_by('name')

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
        queryset = models.PlaceType.objects.exclude(level="Cult Place Type").order_by('name')
        parent = self.request.query_params.get('parent')
        level = self.request.query_params.get('level')
        if parent is not None:
            queryset = queryset.filter(parent__in=parent.split(',')).order_by('name')
        if level is not None:
            queryset = queryset.filter(level=level).order_by('name')
        return queryset
    serializer_class = PlaceTypeSerializer
    pagination_class = LargeResultsSetPagination
    ordering_fields = ['name']
    ordering = ['name']


class CultTypesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned cult types to
        a certain parent type, by filtering against a `parent`
        query parameter in the URL which can be a list.
        """
        queryset = models.CultType.objects.all()
        parent = self.request.query_params.get('parent')
        level = self.request.query_params.get('level')
        if parent is not None:
            queryset = queryset.filter(parent__in=parent.split(','))
        if level is not None:
            queryset = queryset.filter(level=level)
        return queryset.order_by('name')
    serializer_class = CultTypeSerializer
    pagination_class = LargeResultsSetPagination
    ordering_fields = ['name']
    ordering = ['name']


class AgentTypesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned agent types
        depending if it is a saint or not, by filtering 
        against a 'saint' query parameter in the URL.
        """
        queryset = models.AgentType.objects.all()
        saint = self.request.query_params.get('saint')
        gender = self.request.query_params.get('gender')
        if saint is not None:
            if gender is not None:
                queryset = queryset.filter(agent__saint=saint, agent__gender=gender).distinct()
            else:
                queryset = queryset.filter(agent__saint=saint).distinct()
        return queryset.order_by('name')
    serializer_class = AgentTypeSerializer
    pagination_class = LargeResultsSetPagination
    ordering_fields = ['name']
    ordering = ['name']
