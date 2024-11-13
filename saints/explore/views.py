from rest_framework import viewsets, filters, pagination
from rest_framework.settings import api_settings
from rest_framework_gis.filters import InBBoxFilter
# from rest_framework_gis.pagination import GeoJsonPagination
from django.contrib.gis.gdal.envelope import Envelope
from django.db.models import Q, Prefetch
from django.views.generic.detail import DetailView
from . import models
from .serializers import AgentSerializer, CultSerializer, PlaceSerializer, \
    AgentTypeSerializer, PlaceTypeSerializer, CultTypeSerializer, \
    SourceSerializer, OrganizationSerializer, PlaceMiniSerializer, \
    AgentNameSerializer, AgentMiniSerializer, PlaceMapSerializer, \
    CultMapSerializer, SaintsMapSerializer, PeopleMapSerializer, \
    CultMiniSerializer, QuoteSerializer, QuoteMiniSerializer, \
    PlaceChildrenSerializer, SourceMediumSerializer, SourceMiniSerializer, \
    OrganizationMiniSerializer


class MediumResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    max_page_size = 100


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
        # range = options.get('range')
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


class DiocesesViewSet(OrderingMixin):

    def get_queryset(self):
        type = self.request.query_params.get('type')
        if type is not None:
            if type == "Modern":
                queryset = models.Organization.objects.filter(organization_type=9).order_by('name')
            else:
                queryset = models.Organization.objects.filter(organization_type=2).order_by('name')
        else:
            queryset = models.Organization.objects.filter(organization_type__in=[2,9]).order_by('name')
        return queryset

    serializer_class = OrganizationMiniSerializer
    pagination_class = LargeResultsSetPagination


class CultsViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        options = self.request.query_params
        cult_type = options.get('type')
        uncertainty = options.get('uncertainty')
        extant = options.get('extant')
        source = options.get('source')
        range = options.get('range')
        diocese = options.get('diocese')
        med_diocese = options.get('med_diocese')
        mini = options.get('mini')
        queryset = models.Cult.objects.select_related("cult_type").select_related("cult_type__parent").select_related("place").select_related("created").select_related("modified").all()
        queryset = queryset.prefetch_related("relationcultagent_set__agent")
        if mini is None:
            queryset = queryset.prefetch_related("place__parish__medival_organization").prefetch_related("place__place_type").prefetch_related("cult_children").prefetch_related("quote").prefetch_related("associated").prefetch_related("relationotheragent_set")
        if diocese is not None:
            if mini is not None:
                queryset = queryset.prefetch_related("place__parish")
            queryset = queryset.filter(place__parish__organization_id=diocese)
        if med_diocese is not None:
            if mini is not None:
                queryset = queryset.prefetch_related("place__parish")
            queryset = queryset.filter(place__parish__medival_organization_id=med_diocese)
        if uncertainty is not None:
            queryset = queryset.filter(place_uncertainty=uncertainty)
        if extant is not None:
            queryset = queryset.filter(extant=extant)
        if source is not None:
            queryset = queryset.filter(quote__source_id=source)
        if range is not None and range != '':
            years = range.split(',')
            minyear = int(years[0])
            maxyear = int(years[1])
            queryset = queryset.filter(minyear__gte=minyear,
                                       maxyear__lte=maxyear)
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
        queryset = models.Place.objects.filter(exclude=False).select_related("place_type").select_related("created").select_related("modified").select_related("parish").select_related("parent")
        queryset = queryset.prefetch_related("relation_cult_place__cult_type").order_by('name')
        options = self.request.query_params
        place_type = options.get('type')
        diocese = options.get('diocese')
        med_diocese = options.get('med_diocese')
        if place_type is not None:
            types = place_type.split(',')
            queryset = queryset.filter(Q(place_type__in=types) | Q(place_type__parent__in=types)).order_by('name')
        if diocese is not None:
            queryset = queryset.filter(parish__organization_id=diocese).order_by('name')
        if med_diocese is not None:
            queryset = queryset.filter(parish__medival_organization_id=med_diocese).order_by('name')
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


class PlaceChildrenViewSet(OrderingMixin):
    def get_queryset(self):
        """
        Optionally restrict the returned places to a type
        by filtering against a `type` query parameter in the URL.
        """
        # optimize for mini search
        queryset = models.Place.objects.filter(exclude=False).select_related("parent").prefetch_related("relation_cult_place__cult_type").prefetch_related("place_type").select_related("parent__place_type")
        id = self.request.query_params.get('id')
        if id is not None:
            queryset = queryset.filter(parent=id).order_by('name')
        else:
            queryset = queryset.order_by('name')
        return queryset

    serializer_class = PlaceChildrenSerializer
    pagination_class = LargeResultsSetPagination


class SourcesViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        """
        Optionally restrict the returned sources to a type
        and/or the first letter, by filtering against a `type`
        and/or `letter` query parameter in the URL.
        """
        if self.detail is True and self.request.query_params.get('mini') is None:
            queryset = models.Source.objects.prefetch_related("source_quote__cult_quote__place").prefetch_related("source_quote__cult_quote__cult_type").prefetch_related("source_quote__cult_quote")
        # .prefetch_related(Prefetch(
        #   'source_quote__cult_quote',
        #     'agent')
        #  )).all()
        else:
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

    def get_serializer_class(self):
        if self.detail is True:
            if self.request.query_params.get('mini') is not None:
                return SourceMediumSerializer
            else:
                return SourceSerializer
        else:
            return SourceMediumSerializer

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
            queryset = queryset.prefetch_related('cult_quote__relation_cult_agent').prefetch_related("cult_quote__place").prefetch_related("cult_quote__cult_type")
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
        return MediumResultsSetPagination

    pagination_class = property(fget=get_pagination_class)
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
        if parent is not None and parent != '':
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
                diocese = options.get('diocese')
                med_diocese = options.get('med_diocese')
                if search is not None:
                    cultset = models.Cult.objects.filter(place__name__icontains=search)
                else:
                    cultset = models.Cult.objects.all()
                if uncertainty is not None:
                    cultset = cultset.filter(place_uncertainty=uncertainty)
                if extant is not None:
                    cultset = cultset.filter(extant=extant)
                if diocese is not None:
                    queryset = queryset.select_related("parish").filter(parish__organization_id=diocese)
                if med_diocese is not None:
                    queryset = queryset.select_related("parish").filter(parish__medival_organization_id=med_diocese)
                if ids is not None and ids != 'null':
                    types = ids.split(',')
                    cultset = cultset.filter(Q(cult_type__in=types)
                                             | Q(cult_type__parent__in=types)
                                             | Q(cult_type__parent__parent__in=types))
                queryset = queryset.filter(relation_cult_place__in=cultset).distinct()
            else:
                gender = options.get('gender')
                agents = options.get('agent')
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

            if range is not None:
                years = range.split(',')
                minyear = int(years[0])
                maxyear = int(years[1])
                queryset = queryset.filter(relation_cult_place__minyear__gte=minyear,
                                           relation_cult_place__maxyear__lte=maxyear)

        elif layer == 'place':
            diocese = options.get('diocese')
            med_diocese = options.get('med_diocese')
            if search is not None:
                queryset = queryset.filter(name__icontains=search).order_by('name')
            if zoom is not None and zoom != 'null' and zoom < 13 and ids is None:
                if zoom < 9:
                    queryset = queryset.filter(place_type__parent__in=[1,2])
                elif zoom < 11:
                    queryset = queryset.filter(place_type__parent__in=[1,2,3,6])
                else:
                    queryset = queryset.filter(place_type__parent__in=[1,2,3,4,6])
            else:
                # Show all places but modern church, altar and chapel in church (former 18,46,49)
                queryset = queryset.exclude(place_type__in=[30,58,61])
            if ids is not None and ids != 'null':
                types = ids.split(',')
                queryset = queryset.filter(Q(place_type__in=types) | Q(place_type__parent__in=types)).order_by('name')
            if diocese is not None:
                queryset = queryset.select_related("parish").filter(parish__organization_id=diocese)
            if med_diocese is not None:
                queryset = queryset.select_related("parish").filter(parish__medival_organization_id=med_diocese)

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
