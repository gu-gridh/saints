from rest_framework import viewsets, filters, pagination
from rest_framework.settings import api_settings
from rest_framework_gis.filters import InBBoxFilter
# from rest_framework_gis.pagination import GeoJsonPagination
from django.contrib.gis.gdal.envelope import Envelope
from django.db.models import Q
from . import models
from .serializers import AgentSerializer, CultSerializer, PlaceSerializer, \
    AgentTypeSerializer, PlaceTypeSerializer, CultTypeSerializer, \
    SourceSerializer, OrganizationSerializer, PlaceMiniSerializer, \
    AgentNameSerializer, AgentMiniSerializer, PlaceMapSerializer, \
    CultMapSerializer, SaintsMapSerializer, PeopleMapSerializer, \
    CultMiniSerializer, QuoteSerializer, QuoteMiniSerializer


class LargeResultsSetPagination(pagination.PageNumberPagination):
    page_size = 200
    max_page_size = 200


class OrderingMixin(viewsets.ReadOnlyModelViewSet):
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['name']
    ordering = ['name']


# Create your views here.
# ViewSets define the view behavior.
class AgentsViewSet(OrderingMixin):
    def get_queryset(self):
        options = self.request.query_params
        gender = options.get('gender')
        agent_type = options.get('type')
        operator = options.get('op')
        mini = options.get('mini')
        queryset = models.Agent.objects.all().prefetch_related("agent_type").order_by('name')
        if mini is None:
            queryset = queryset.prefetch_related("agentname_set").prefetch_related("relationcultagent_set__cult__cult_type").prefetch_related("relationcultagent_set__cult__place").prefetch_related("feastday_set")
            queryset = queryset.select_related("created").select_related("modified")
            queryset = queryset.prefetch_related("relationoffice_set__organization").prefetch_related("relationoffice_set__role")
            queryset = queryset.prefetch_related("relationotheragent_set__role").prefetch_related("relationotheragent_set__cult__cult_type").prefetch_related("relationotheragent_set__cult__place").prefetch_related("relationotheragent_set__cult__relationcultagent_set")
        if gender is not None and gender != '':
            queryset = queryset.filter(gender=gender).order_by('name')
        if agent_type is not None:
            types = agent_type.split(',')
            if operator == "AND" and len(types) < 5:
                for t in types:
                    if queryset:
                        queryset = queryset.filter(agent_type=t)
                queryset = queryset.order_by('name')
            else:
                queryset = queryset.filter(agent_type__in=types).order_by('name')
        return queryset.distinct()

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

    pagination_class = property(fget=get_pagination_class)
    search_fields = ['name', 'agentname__name']


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


class OrganizationViewSet(OrderingMixin):
    queryset = models.Organization.objects.select_related("organization_type").prefetch_related("organizationname_set").all()
    serializer_class = OrganizationSerializer
    search_fields = ['name']


class AgentNamesViewSet(OrderingMixin):
    queryset = models.AgentName.objects.all()
    serializer_class = AgentNameSerializer
    search_fields = ['name']


class CultsViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        options = self.request.query_params
        cult_type = options.get('type')
        uncertainty = options.get('uncertainty')
        extant = options.get('extant')
        source = options.get('source')
        queryset = models.Cult.objects.select_related("cult_type").select_related("cult_type__parent").select_related("place").all()
        queryset = queryset.prefetch_related("relationcultagent_set__agent")
        if uncertainty is not None:
            queryset = queryset.filter(place_uncertainty=uncertainty)
        if extant is not None:
            queryset = queryset.filter(extant=extant)
        if source is not None:
            queryset = queryset.filter(quote__source_id=source)
        if cult_type is not None:
            types = cult_type.split(',')
            # queryset = queryset.prefetch_related("cult_type__parent")
            queryset = queryset.filter(Q(cult_type__in=types) | Q(cult_type__parent__in=types) | Q(cult_type__parent__parent__in=types))
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


class PlacesViewSet(OrderingMixin):
    def get_queryset(self):
        """
        Optionally restrict the returned places to a type
        by filtering against a `type` query parameter in the URL.
        """
        # optimize for mini search
        queryset = models.Place.objects.filter(exclude=False).select_related("place_type").select_related("parish").select_related("parish__medival_organization")
        place_type = self.request.query_params.get('type')
        if place_type is not None:
            types = place_type.split(',')
            queryset = queryset.filter(Q(place_type__in=types) | Q(place_type__parent__in=types)).order_by('name')
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

    pagination_class = property(fget=get_pagination_class)
    search_fields = ['name']


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
    pagination_class = LargeResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'title', 'author']
    ordering_fields = ['title', 'author']
    ordering = ['title']


class QuotesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned quotes against a `source`
        query parameter in the URL.
        """
        queryset = models.Quote.objects.select_related("source").all()
        options = self.request.query_params
        source = options.get('source')
        mini = options.get('mini')
        if source is not None:
            queryset = queryset.filter(source=source)
        if mini is None:
            queryset = queryset.prefetch_related("cult_quote__place").prefetch_related("cult_quote__cult_type")
        return queryset.order_by('page')

    def get_serializer_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return QuoteMiniSerializer
        else:
            return QuoteSerializer

    def get_pagination_class(self):
        mini = self.request.query_params.get('mini')
        if mini is not None:
            return LargeResultsSetPagination
        return api_settings.DEFAULT_PAGINATION_CLASS

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['quote_transcription', 'translation']
    ordering_fields = ['quote_transcription']
    ordering = ['quote_transcription']


class PlaceTypesViewSet(OrderingMixin):
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
    search_fields = ['name','name_sv','name_fi']


class CultTypesViewSet(OrderingMixin):
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
    search_fields = ['name', 'name_sv', 'name_fi']


class AgentTypesViewSet(OrderingMixin):
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
    search_fields = ['name', 'name_sv', 'name_fi']


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        options = self.request.query_params
        layer = options.get('layer')
        ids = options.get('ids')
        zoom = options.get('zoom')
        if zoom is not None and zoom.isnumeric():
            zoom = int(zoom)
        bbox = options.get('bbox')
        search = options.get('search')

        queryset = models.Place.objects.filter(exclude=False).prefetch_related("place_type").order_by('name')

        if layer != 'place' and layer is not None:
            range = options.get('range')
            if layer == 'cult':
                uncertainty = options.get('uncertainty')
                extant = options.get('extant')
                if search is not None:
                    cultset = models.Cult.objects.filter(place__name__icontains=search)
                else:
                    cultset = models.Cult.objects.all()
                if uncertainty is not None:
                    cultset = cultset.filter(place_uncertainty=uncertainty)
                if extant is not None:
                    cultset = cultset.filter(extant=extant)
                if ids is not None and ids != 'null':
                    types = ids.split(',')
                    cultset = cultset.filter(Q(cult_type__in=types)
                                             | Q(cult_type__parent__in=types)
                                             | Q(cult_type__parent__parent__in=types))
                queryset = queryset.filter(relation_cult_place__in=cultset).distinct()
            else:
                gender = options.get('gender')
                agents = options.get('agents')
                operator = options.get('op')
                if search is not None:
                    agentset = models.Agent.objects.filter(Q(name__icontains=search) | Q(agentname__name__icontains=search))
                else:
                    agentset = models.Agent.objects.all()
                if gender is not None and gender != '':
                    agentset = agentset.filter(gender=gender).order_by('name')
                if ids is not None and ids != 'null':
                    types = ids.split(',')
                    if operator == "AND" and len(types) < 5:
                        for t in types:
                            agentset = agentset.filter(agent_type=t)
                    else:
                        agentset = agentset.filter(agent_type__in=types)
                if agents is not None and agents != 'null':
                    agentids = agents.split(',')
                    if operator == "AND" and len(agentids) < 5:
                        for id in agentids:
                            agentset = agentset.get(id=id)
                    else:
                        agentset = agentset.filter(id__in=agentids)
                if (layer == 'saints'):
                    agentset = agentset.filter(saint=True).order_by('name')
                    agentset = agentset.prefetch_related("relation_cult_place__relation_cult_agent__agent_type")
                    queryset = queryset.filter(relation_cult_place__relation_cult_agent__in=agentset).distinct()
                elif (layer == 'people'):
                    agentset = agentset.filter(saint=False).order_by('name')
                    queryset = queryset.filter(relation_cult_place__relationotheragent__agent_id__in=agentset).distinct()

            if range is not None and range != 'undefined':
                years = range.split(',')
                minyear = int(years[0])
                maxyear = int(years[1])
                queryset = queryset.filter(relation_cult_place__minyear__gte=minyear,
                                           relation_cult_place__maxyear__lte=maxyear)

        elif layer == 'place':
            if search is not None:
                queryset = queryset.filter(name__icontains=search).order_by('name')
            if zoom is not None and zoom != 'null' and zoom < 13 and ids == 'null':
                if zoom < 9:
                    queryset = queryset.filter(place_type__parent__in=[1,2])
                elif zoom < 11:
                    queryset = queryset.filter(place_type__parent__in=[1,2,3,6])
                else:
                    queryset = queryset.filter(place_type__parent__in=[1,2,3,4,6])
            else:
                # Show all places but modern church, altar and chapel in church
                queryset = queryset.exclude(place_type__parent__in=[18,46,49])
            if ids is not None and ids != 'null':
                types = ids.split(',')
                queryset = queryset.filter(Q(place_type__in=types) | Q(place_type__parent__in=types)).order_by('name')

        if bbox is not None:
            bbox = bbox.strip().split(',')
            bbox_coords = [
                float(bbox[0]), float(bbox[1]),
                float(bbox[2]), float(bbox[3]),
            ]
            bounding_box = Envelope((bbox_coords))
            queryset = queryset.filter(geometry__within=bounding_box.wkt).order_by('name')

        return queryset

    def get_serializer_class(self):
        layer = self.request.query_params.get('layer')
        if layer == 'place':
            return PlaceMapSerializer
        elif layer == 'cult':
            return CultMapSerializer
        elif layer == 'saints':
            return SaintsMapSerializer
        else:
            return PeopleMapSerializer

    filter_backends = [InBBoxFilter, filters.SearchFilter]
    bbox_filter_field = 'geometry'
    page_size = 25
