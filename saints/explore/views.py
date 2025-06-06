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
    CultMiniSerializer, QuoteSerializer, QuoteMiniSerializer, \
    PlaceChildrenSerializer, SourceMediumSerializer, \
    OrganizationMiniSerializer, AdvancedCultMapSerializer


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
        queryset = models.Agent.objects.all().prefetch_related("agent_type").order_by('name')
        if mini is None:
            queryset = queryset.prefetch_related("agentname_set", "relationcultagent_set__cult__cult_type", "relationcultagent_set__cult__place", "feastday_set")
            queryset = queryset.select_related("created", "modified")
            queryset = queryset.prefetch_related("relationoffice_set__organization", "relationoffice_set__role")
            queryset = queryset.prefetch_related("relationotheragent_set__role", "relationotheragent_set__cult__cult_type", "relationotheragent_set__cult__place", "relationotheragent_set__cult__relationcultagent_set")
        if gender is not None and gender != '' and gender != 'all':
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
    search_fields = ['name', 'agentname__name', 'feastday__day']


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
        # only show those with connected cults. TODO: different for places
        if type is not None:
            if type == "Modern":
                existing = models.Cult.objects.prefetch_related("place__parish").values("place__parish__organization_id").distinct()
                queryset = models.Organization.objects.filter(organization_type=9, id__in=existing).order_by('name')
            else:
                existing_meds = models.Cult.objects.prefetch_related("place__parish").values("place__parish__medival_organization_id").distinct()
                queryset = models.Organization.objects.filter(organization_type=2, id__in=existing_meds).order_by('name')
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
        feastday = options.get('feastday')
        range = options.get('range')
        med_diocese = options.get('med_diocese')
        mini = options.get('mini')
        queryset = models.Cult.objects.select_related("cult_type", "cult_type__parent", "place", "created", "modified").all()
        queryset = queryset.prefetch_related("relationcultagent_set__agent")
        if mini is None:
            queryset = queryset.prefetch_related("place__parish__medival_organization", "place__place_type", "cult_children", "quote", "associated", "relationotheragent_set__agent")
        if med_diocese is not None and med_diocese != '':
            if mini is not None:
                queryset = queryset.prefetch_related("place__parish")
            queryset = queryset.filter(place__parish__medival_organization_id=med_diocese)
        if uncertainty is not None:
            queryset = queryset.filter(place_uncertainty=uncertainty)
        if extant is not None:
            queryset = queryset.filter(extant=extant)
        if source is not None:
            queryset = queryset.filter(quote__source_id=source)
        if feastday is not None and feastday == 'true':
            search = options.get('search')
            queryset = queryset.filter(feast_day__icontains=search)
        if range is not None and range != '':
            years = range.split(',')
            minyear = int(years[0])
            maxyear = int(years[1])
            queryset = queryset.filter(minyear__lte=maxyear, maxyear__gte=minyear)
        if cult_type is not None:
            types = cult_type.split(',')
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
    search_fields = ['place__name', 'cult_type__name', 'relation_cult_agent__name', 'relationotheragent__agent__name', 'feast_day']
    ordering_fields = ['place__name', 'cult_type__name']
    ordering = ['place__name']


class CultAdvancedViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        options = self.request.query_params
        cult_type = options.get('type')
        place_type = options.get('place_type')
        agent_type = options.get('agent_type')
        agent = options.get('agent')
        range = options.get('range')
        med_diocese = options.get('med_diocese')
        queryset = models.Cult.objects.select_related("place", "cult_type").prefetch_related("relation_other_place").all()
        # queryset = queryset.prefetch_related("place__parish__medival_organization").prefetch_related("place__place_type").prefetch_related("cult_children").prefetch_related("quote").prefetch_related("associated").prefetch_related("relationotheragent_set")
        if cult_type is not None and cult_type != '':
            types = cult_type.split(',')
            queryset = queryset.prefetch_related("cult_type__parent")
            queryset = queryset.filter(Q(cult_type__in=types) | Q(cult_type__parent__in=types) | Q(cult_type__parent__parent__in=types))
        if place_type is not None and place_type != '':
            place_types = place_type.split(',')
            queryset = queryset.prefetch_related("place__place_type", "relation_other_place__place_type")
            queryset = queryset.filter(Q(place__place_type__in=place_types) 
                                       | Q(place__place_type__parent__in=place_types)
                                       | Q(relation_other_place__place_type__in=place_types) 
                                       | Q(relation_other_place__place_type__parent__in=place_types))
        if med_diocese is not None and med_diocese != '':
            queryset = queryset.prefetch_related("place__parish__medival_organization", "relation_other_place__parish__medival_organization")
            queryset = queryset.filter(Q(place__parish__medival_organization_id=med_diocese) | Q(relation_other_place__parish__medival_organization_id=med_diocese))
        if agent_type is not None or agent is not None:
            queryset = queryset.prefetch_related("relationcultagent_set__agent", "relationotheragent_set__agent")
            if agent is not None and agent != '':
                agents = agent.split(',')
                queryset = queryset.filter(Q(relation_cult_agent__in=agents) | Q(relationotheragent__agent__in=agents)).distinct()
            if agent_type is not None and agent_type != '':
                agent_types = agent_type.split(',')
                queryset = queryset.filter(Q(relationcultagent__agent__agent_type__in=agent_types) | Q(relationotheragent__agent__agent_type__in=agent_types)).distinct()
        if range is not None and range != '':
            years = range.split(',')
            minyear = int(years[0])
            maxyear = int(years[1])
            queryset = queryset.filter(minyear__lte=maxyear, maxyear__gte=minyear)
        return queryset.order_by('place__name')

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = LargeResultsSetPagination
    serializer_class = CultMiniSerializer
    search_fields = ['place__name', 'cult_type__name', 'relation_cult_agent__name']
    ordering_fields = ['place__name', 'cult_type__name']
    ordering = ['place__name']


class PlacesViewSet(OrderingMixin):
    def get_queryset(self):
        """
        Optionally restrict the returned places to a type
        by filtering against a `type` query parameter in the URL.
        """
        # optimize for mini search
        queryset = models.Place.objects.filter(exclude=False).select_related("place_type", "created", "modified", "parish", "parent")
        queryset = queryset.prefetch_related("relation_cult_place__cult_type").order_by('name')
        options = self.request.query_params
        place_type = options.get('type')
        med_diocese = options.get('med_diocese')
        if place_type is not None:
            types = place_type.split(',')
            queryset = queryset.filter(Q(place_type__in=types) | Q(place_type__parent__in=types)).order_by('name')
        if med_diocese is not None and med_diocese != '':
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
    search_fields = ['name', 'placename__name']


class PlaceChildrenViewSet(OrderingMixin):
    def get_queryset(self):
        """
        Optionally restrict the returned places to a type
        by filtering against a `type` query parameter in the URL.
        """
        # optimize for mini search
        queryset = models.Place.objects.filter(exclude=False).select_related("parent", "parent__place_type").prefetch_related("relation_cult_place__cult_type", "place_type")
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
            queryset = models.Source.objects.prefetch_related("source_quote__cult_quote__place", "source_quote__cult_quote__cult_type", "source_quote__cult_quote")
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
        return queryset

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
            queryset = queryset.prefetch_related('cult_quote__relation_cult_agent', 'cult_quote__place', 'cult_quote__cult_type')
        return queryset.order_by('source__name')

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
    search_fields = ['quote_transcription', 'translation', 'comment']
    ordering_fields = ['source__name']
    ordering = ['source__name']


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
    search_fields = ['name', 'name_sv', 'name_fi']


class CultTypesViewSet(OrderingMixin):
    def get_queryset(self):
        """
        Optionally restrict the returned cult types to
        a certain parent type, by filtering against a `parent`
        query parameter in the URL which can be a list.
        """
        parent = self.request.query_params.get('parent')
        level = self.request.query_params.get('level')
        queryset = models.CultType.objects.prefetch_related("parent").all()
        if parent is not None and parent != '':
            queryset = queryset.filter(parent__in=parent.split(','))
            no_parent = queryset.prefetch_related("parent__parent").filter(parent__parent=None).exists()
            if no_parent is False:
                existing_types = models.Cult.objects.select_related("cult_type").values("cult_type").distinct()
                queryset = queryset.filter(id__in=existing_types).distinct()
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
                med_diocese = options.get('med_diocese')
                if search is not None:
                    queryset = queryset.prefetch_related("relation_cult_place").filter(Q(name__icontains=search)
                                                         | Q(relation_cult_place__cult_type__name__icontains=search)
                                                         | Q(relation_cult_place__relation_cult_agent__name__icontains=search)
                                                         | Q(relation_cult_place__relationotheragent__agent__name__icontains=search)).distinct()
                if uncertainty is not None:
                    queryset = queryset.prefetch_related("relation_cult_place").filter(relation_cult_place__cult_uncertainty=uncertainty)
                if extant is not None:
                    queryset = queryset.prefetch_related("relation_cult_place").filter(relation_cult_place__extant=extant)
                if med_diocese is not None and med_diocese != '':
                    queryset = queryset.select_related("parish").filter(parish__medival_organization_id=med_diocese)
                if ids is not None and ids != 'null':
                    types = ids.split(',')
                    queryset = queryset.prefetch_related("relation_cult_place").filter(Q(relation_cult_place__cult_type__in=types)
                                               | Q(relation_cult_place__cult_type__parent__in=types)
                                               | Q(relation_cult_place__cult_type__parent__parent__in=types)).distinct()
            else:
                gender = options.get('gender')
                agents = options.get('agent')
                operator = options.get('op')
                if search is not None:
                    agentset = models.Agent.objects.filter(Q(name__icontains=search) | Q(agentname__name__icontains=search)).distinct()
                else:
                    agentset = models.Agent.objects.all()
                if gender is not None and gender != '' and gender != 'all':
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
                    agentset = agentset.prefetch_related("relation_cult_place__relation_other_agent__agent_type")
                    queryset = queryset.filter(relation_cult_place__relationotheragent__agent_id__in=agentset).distinct()

            if range is not None and range != '':
                years = range.split(',')
                minyear = int(years[0])
                maxyear = int(years[1])
                queryset = queryset.filter(relation_cult_place__minyear__lte=maxyear,
                                           relation_cult_place__maxyear__gte=minyear)

        elif layer == 'place':
            med_diocese = options.get('med_diocese')
            if search is not None:
                queryset = queryset.filter(Q(name__icontains=search) | Q(placename__name__icontains=search)).distinct()
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
            if med_diocese is not None and med_diocese != '':
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
    pagination_class = LargeResultsSetPagination


class AdvancedMapViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        options = self.request.query_params
        zoom = options.get('zoom')
        if zoom is not None and zoom.isnumeric():
            zoom = int(zoom)
        bbox = options.get('bbox')
        range = options.get('range')
        cult_type = options.get('type')
        place_type = options.get('place_type')
        agent_type = options.get('agent_type')
        agent = options.get('agent')
        med_diocese = options.get('med_diocese')

        queryset = models.Cult.objects.all()
        place_set = models.Place.objects.prefetch_related("place_type").filter(exclude=False)
        if cult_type is not None and cult_type != '':
            types = cult_type.split(',')
            levels = models.CultType.objects.filter(id__in=types).values("level").distinct()
            if len(levels) == 1:
                level = levels[0]["level"]
                if level == "Subcategory":
                    queryset = queryset.prefetch_related("cult_type").filter(cult_type__in=types)
                elif level == "Intermediate":
                    queryset = queryset.prefetch_related("cult_type__parent").filter(cult_type__parent__in=types)
                else:
                    queryset = queryset.prefetch_related("cult_type__parent__parent").filter(cult_type__parent__parent__in=types)
            else:
                queryset = queryset.prefetch_related("cult_type", "cult_type__parent",
                                                     "cult_type__parent__parent").filter(Q(cult_type__in=types)
                                                                                         | Q(cult_type__parent__in=types)
                                                                                         | Q(cult_type__parent__parent__in=types)).distinct()

        if agent_type is not None and agent_type != '':
            agent_types = agent_type.split(',')
            queryset = queryset.prefetch_related("relation_cult_agent__agent_type",
                                                 "relationotheragent_set__agent__agent_type").filter(Q(relation_cult_agent__agent_type__in=agent_types)
                                                  | Q(relationotheragent__agent__agent_type__in=agent_types)).distinct()
        if agent is not None and agent != '':
            agents = agent.split(',')
            queryset = queryset.prefetch_related("relation_cult_agent",
                                                 "relationotheragent_set__agent").filter(Q(relation_cult_agent__in=agents)
                                                  | Q(relationotheragent__agent__in=agents)).distinct()

        if range is not None and range != '':
            years = range.split(',')
            minyear = int(years[0])
            maxyear = int(years[1])
            queryset = queryset.filter(minyear__lte=maxyear, maxyear__gte=minyear)

        if bbox is not None:
            bbox = bbox.strip().split(',')
            bbox_coords = [
                float(bbox[0]), float(bbox[1]),
                float(bbox[2]), float(bbox[3]),
            ]
            bounding_box = Envelope((bbox_coords))
            place_set = place_set.filter(geometry__within=bounding_box.wkt)

        if place_type is not None and place_type != '':
            place_types = place_type.split(',')
            place_set = place_set.prefetch_related("place_type__parent").filter(Q(place_type__in=place_types)
                                       | Q(place_type__parent__in=place_types)).order_by('name')

        if med_diocese is not None and med_diocese != '':
            place_set = place_set.select_related("parish").filter(parish__medival_organization_id=med_diocese)

        place_set = place_set.filter(Q(relation_cult_place__in=queryset)
                                     | Q(relation_other_place__in=queryset)).distinct()
        return place_set.order_by('name')

    filter_backends = [InBBoxFilter, filters.SearchFilter]
    serializer_class = AdvancedCultMapSerializer
    bbox_filter_field = 'geometry'
    pagination_class = LargeResultsSetPagination
