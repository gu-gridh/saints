from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Agent, AgentType, AgentName, Place, PlaceName, PlaceType, \
    Cult, CultType, Source, Parish, Quote, Organization, FeastDay, \
    OrganizationType, RelationCultAgent, RelationOffice, \
    RelationDigitalResource, Iconographic, RelationMBResource, \
    RelationOtherAgent, RelationOtherPlace
import requests


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class AgentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgentType
        exclude = ['updated', 'level']


class AgentNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = AgentName
        fields = '__all__'


class PlaceNameSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceName
        fields = '__all__'


class OrganizationMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name']


class OrganizationMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name']


class OrganizationTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrganizationType
        exclude = ['updated']


class OrganizationSerializer(serializers.ModelSerializer):
    organization_type = OrganizationTypeSerializer(read_only=True)
    organization_names = serializers.SerializerMethodField()

    def get_organization_names(self, obj):
        return obj.organizationname_set.all().values('name', 'language', 'not_before')

    class Meta:
        model = Organization
        exclude = ['created', 'modified', 'updated', 'notes']


class RelationOfficeSerializer(serializers.ModelSerializer):
    organization = OrganizationMiniSerializer(read_only=True)
    role = AgentTypeSerializer(read_only=True)

    class Meta:
        model = RelationOffice
        fields = ['organization', 'role', 'not_before', 'not_after', 'date_note']


class AgentMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ['id', 'name']


class AgentRelationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='agent.id')
    name = serializers.ReadOnlyField(source='agent.name')

    class Meta:
        model = RelationCultAgent
        fields = ['id', 'name', 'agent_uncertainty', 'agent_main', 'agent_alternative']


class DigitalResourceRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationDigitalResource
        fields = ['resource_uri', 'resource_uncertainty']


class MBResourceRelationSerializer(serializers.ModelSerializer):
    samsoek = serializers.SerializerMethodField()

    def get_samsoek(self, obj):
        res = {'images': [], 'name': '', 'main_thumb': ''}
        parts = obj.resource_uri.split('/')
        id = parts.pop()
        json_uri = '/'.join(parts) + '/jsonld/' + id
        response = requests.get(json_uri, timeout=10)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            return print("Error: " + str(e))

        json_obj = response.json()
        for item in json_obj['@graph']:
            if item['@type'] == 'Image':
                res['images'].append({'filename': item['lowresSource'], 'thumbnail': item['thumbnailSource']})
            elif item['@type'] == 'ItemName':
                if 'name' in item:
                    res['name'] = item['name'].title()
            elif item['@type'] == 'Entity':
                res['main_thumb'] = item['thumbnail']
        # find higher resolution version
        for image in res['images']:
            if image['thumbnail'] == res['main_thumb']:
                res['main_thumb'] = image['filename']
        res['images'] = sorted(res['images'], key=lambda d: d['filename'])
        return res

    class Meta:
        model = RelationMBResource
        fields = ['resource_uri', 'samsoek']


class PlaceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        exclude = ['updated', 'aat']


class PlaceTypeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        fields = ['id', 'name', 'parent']


class DioceseMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        fields = ['id', 'name']


class QuoteMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Quote
        exclude = ['created', 'modified', 'notes', 'updated']


class SourceMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id', 'name']


class SourceMediumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        exclude = ['created', 'modified', 'notes', 'updated']


class FeastDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = FeastDay
        fields = ['day', 'type']


class ParishMiniSerializer(serializers.ModelSerializer):
    medival_organization = OrganizationMiniSerializer(read_only=True)

    class Meta:
        model = Parish
        fields = ['id', 'name', 'medival_organization']


class PlaceMiniSerializer(serializers.ModelSerializer):
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)

    class Meta:
        model = Place
        fields = ['id', 'name', 'municipality', 'parish', 'place_type', 'geometry']


class PlaceMapSerializer(GeoFeatureModelSerializer):
    place_type = PlaceTypeMiniSerializer(read_only=True)

    # flatten for easier access for frontend
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        properties = representation.pop('properties')
        new_properties = {}

        for key, value in properties.items():
            if isinstance(value, dict) and (key != "ids" and key != "agents"):
                for k2, val2 in value.items():
                    new_key = key + "_" + k2
                    new_properties[new_key] = val2
            else:
                new_properties[key] = value

        representation['properties'] = new_properties

        return representation

    class Meta:
        model = Place
        fields = ['id', 'name', 'place_type', 'geometry']
        geo_field = 'geometry'


class CultTypeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = CultType
        exclude = ['updated', 'aat', 'wikidata']


class CultTypeSerializer(serializers.ModelSerializer):
    parent = CultTypeMiniSerializer(read_only=True)

    class Meta:
        model = CultType
        fields = '__all__'


class IconicMiniSerializer(serializers.ModelSerializer):
    additional = serializers.SerializerMethodField()

    def get_additional(self, obj):
        additional = Iconographic.objects.all().filter(card=obj.card, volume=obj.volume).exclude(id=obj.id).values('id', 'motif2', 'filename', 'uri')
        return additional

    class Meta:
        model = Iconographic
        fields = ['id', 'motif2', 'filename', 'uri', 'additional']


class CultRelationSerializer(serializers.ModelSerializer):
    place = serializers.CharField(source='place.name')
    cult_type = serializers.CharField(source='cult_type.name')

    class Meta:
        model = Cult
        fields = ['id', 'place', 'cult_type', 'minyear', 'maxyear']


class RelationOtherAgentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='agent.id')
    name = serializers.ReadOnlyField(source='agent.name')
    role = AgentTypeSerializer(read_only=True)

    class Meta:
        model = RelationOtherAgent
        fields = ['id', 'name', 'agent_uncertainty', 'role']


class RelationOtherPlaceSerializer(serializers.ModelSerializer):
    place = PlaceMiniSerializer(read_only=True)
    role = PlaceTypeMiniSerializer(read_only=True)

    class Meta:
        model = RelationOtherPlace
        fields = ['place', 'place_uncertainty', 'role']


class CultMiniSerializer(serializers.ModelSerializer):
    place = serializers.CharField(source='place.name')
    cult_type = serializers.CharField(source='cult_type.name')
    relation_cult_agent = serializers.SerializerMethodField()

    def get_relation_cult_agent(self, obj):
        relations = obj.relationcultagent_set.all()
        if relations:
            if len(relations) > 1:
                return relations[0].agent.name + " and others"
            else:
                return relations[0].agent.name

    class Meta:
        model = Cult
        fields = ['id', 'place', 'cult_type', 'relation_cult_agent', 'minyear', 'maxyear']


class CultSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    place = PlaceMiniSerializer(read_only=True)
    cult_type = CultTypeSerializer(read_only=True)
    quote = QuoteMiniSerializer(read_only=True, many=True)
    parent = CultMiniSerializer(read_only=True)
    associated = CultMiniSerializer(read_only=True, many=True)
    dependent = CultMiniSerializer(read_only=True, many=True, source='cult_children')
    relation_cult_agent = serializers.SerializerMethodField() # AgentRelationSerializer(read_only=True, many=True, source='relationcultagent_set')
    relation_other_agent = RelationOtherAgentSerializer(read_only=True, many=True, source='relationotheragent_set')
    relation_other_place = RelationOtherPlaceSerializer(read_only=True, many=True, source='relationotherplace_set')
    relation_digital_resource = DigitalResourceRelationSerializer(read_only=True, many=True, source='relationdigitalresource_set')
    relation_mb_resource = MBResourceRelationSerializer(read_only=True, many=True, source='relationmbresource_set')
    relation_iconographic = IconicMiniSerializer(read_only=True, many=True)

    def get_relation_cult_agent(self, obj):
        relations = obj.relationcultagent_set.all().order_by('agent_alternative')
        return AgentRelationSerializer(relations, read_only=True, many=True).data

    class Meta:
        model = Cult
        exclude = ['notes']


class CultAgentRelationSerializer(serializers.ModelSerializer):
    cult = CultRelationSerializer(read_only=True)

    class Meta:
        model = RelationCultAgent
        fields = ['cult', 'agent_uncertainty', 'agent_main', 'agent_alternative']


class RelationOtherCultSerializer(serializers.ModelSerializer):
    cult = CultMiniSerializer(read_only=True)
    role = AgentTypeSerializer(read_only=True)

    class Meta:
        model = RelationOtherAgent
        fields = ['cult', 'agent_uncertainty', 'role']


class RelationOtherPlaceCultSerializer(serializers.ModelSerializer):
    cult = CultMiniSerializer(read_only=True)
    role = PlaceTypeMiniSerializer(read_only=True)

    class Meta:
        model = RelationOtherPlace
        fields = ['cult', 'place_uncertainty', 'role']


class QuoteSourceSerializer(serializers.ModelSerializer):
    cult = CultMiniSerializer(read_only=True, many=True, source='cult_quote')

    class Meta:
        model = Quote
        fields = ['id', 'comment', 'not_after', 'not_before', 'date_note',
                  'page', 'language', 'uri', 'quote_transcription',
                  'transcribed_by', 'translation', 'translated_by', 'cult']


class SourceSerializer(serializers.ModelSerializer):
    quote = QuoteSourceSerializer(many=True, source="source_quote")

    class Meta:
        model = Source
        exclude = ['notes', 'created', 'modified', 'updated']


class QuoteSerializer(serializers.ModelSerializer):
    source = SourceMiniSerializer(read_only=True)
    cult = CultMiniSerializer(read_only=True, many=True, source='cult_quote')

    class Meta:
        model = Quote
        fields = ['id', 'source', 'cult', 'comment', 'not_after', 'not_before',
                  'date_note', 'page', 'language', 'uri', 'quote_transcription',
                  'transcribed_by', 'translation', 'translated_by']


class AgentSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    agent_type = AgentTypeSerializer(read_only=True, many=True)
    feast_day = FeastDaySerializer(read_only=True, many=True, source='feastday_set')
    held_office = RelationOfficeSerializer(read_only=True, many=True, source='relationoffice_set')
    agent_names = serializers.SerializerMethodField()
    relation_cult_agent = CultAgentRelationSerializer(read_only=True, many=True, source='relationcultagent_set')
    relation_other_agent = RelationOtherCultSerializer(read_only=True, many=True, source='relationotheragent_set')

    def get_agent_names(self, obj):
        return obj.agentname_set.values('name', 'language', 'not_before')

    class Meta:
        model = Agent
        exclude = ['notes']


class PlaceChildrenSerializer(serializers.ModelSerializer):
    """ Allow only church related places to show related child places
    """
    relation_cult_place = serializers.SerializerMethodField()
    relation_other_place = serializers.SerializerMethodField()

    def get_relation_cult_place(obj, self):
        if self.parent.place_type.parent.id in [3, 4, 5, 7, 10, 11]:
            relations = self.relation_cult_place.all()
        else:
            relations = None
        return CultMiniSerializer(relations, read_only=True, many=True).data

    def get_relation_other_place(obj, self):
        if self.parent.place_type.parent.id in [3, 4, 5, 7, 10, 11]:
            relations = self.relation_other_place.all()
        else:
            relations = None
        return CultMiniSerializer(relations, read_only=True, many=True).data

    class Meta:
        model = Place
        fields = ['id', 'name', 'relation_cult_place', 'relation_other_place']


class PlaceSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)
    parent = PlaceMiniSerializer(read_only=True)
    quote = QuoteMiniSerializer(read_only=True, many=True)
    relation_cult_place = CultMiniSerializer(read_only=True, many=True)
    relation_other_place = RelationOtherPlaceCultSerializer(read_only=True, many=True, source='relationotherplace_set')
    place_names = serializers.SerializerMethodField()

    def get_place_names(self, obj):
        return obj.placename_set.all().values('name', 'language', 'not_before')

    class Meta:
        model = Place
        exclude = ['notes']


class CultMapSerializer(PlaceMapSerializer):
    ids = serializers.SerializerMethodField()

    def get_ids(self, obj):
        type = self.context['request'].query_params.get('ids')
        res = {}
        if type is not None and type != 'null':
            types = type.split(',')
            ids = obj.relation_cult_place.all().filter(Q(cult_type__in=types)
                                                       | Q(cult_type__parent__in=types)
                                                       | Q(cult_type__parent__parent__in=types)).values('id', 'cult_type', 'cult_type__parent', 'cult_type__parent__parent')
            for type in types:
                res[type] = 0
            for id in ids:
                cult_type = str(id['cult_type'])
                parent_type = str(id['cult_type__parent'])
                parentp_type = str(id['cult_type__parent__parent'])
                if cult_type != '' and cult_type in res:
                    res[cult_type] += 1
                if parent_type != '' and parent_type in res:
                    res[parent_type] += 1
                if parentp_type != '' and parentp_type in res:
                    res[parentp_type] += 1
            # for type in types:
            #    res[type] = len(list((filter(lambda x: x["cult_type"] == int(type) or x["cult_type__parent"] or x["cult_type__parent__parent"] == int(type), ids))))
        else:
            ids = obj.relation_cult_place.all().values('id', 'cult_type')
            for id in ids:
                cult_type = id['cult_type']
                if cult_type in res:
                    res[cult_type] += 1
                elif cult_type is not None:
                    res[cult_type] = 1
        return res

    class Meta:
        model = Place
        fields = ['id', 'name', 'place_type', 'ids', 'geometry']
        geo_field = 'geometry'


class AdvancedCultMapSerializer(PlaceMapSerializer):
    ids = serializers.SerializerMethodField()

    def get_ids(self, obj):
        res = {}
        type = self.context['request'].query_params.get('type')
        agent_type = self.context['request'].query_params.get('agent_type')
        agent = self.context['request'].query_params.get('agent')
        ids = obj.relation_cult_place.all()
        if type is not None and type != '':
            types = type.split(',')
            ids = ids.filter(Q(cult_type__in=types)
                             | Q(cult_type__parent__in=types)
                             | Q(cult_type__parent__parent__in=types)).distinct()
        if agent_type is not None and agent_type != '':
            agent_types = agent_type.split(',')
            ids = ids.filter(Q(relation_cult_agent__agent_type__in=agent_types)
                             | Q(relationotheragent__agent__agent_type__in=agent_types)).distinct()
        if agent is not None and agent != '':
            agents = agent.split(',')
            ids = ids.filter(Q(relation_cult_agent__in=agents) | Q(relationotheragent__agent__in=agents)).distinct()

        ids = ids.values('cult_type')
        for id in ids:
            cult = id['cult_type']
            if cult in res:
                res[cult] += 1
            elif cult is not None:
                res[cult] = 1
        return res

    class Meta:
        model = Place
        fields = ['id', 'name', 'place_type', 'ids', 'geometry']
        geo_field = 'geometry'


class SaintsMapSerializer(PlaceMapSerializer):
    ids = serializers.SerializerMethodField()

    def get_ids(self, obj):
        type = self.context['request'].query_params.get('ids')
        agent = self.context['request'].query_params.get('agent')
        res = {}
        if type is not None and type != 'null':
            types = type.split(',')
            ids = obj.relation_cult_place.filter(relationcultagent__agent__agent_type__in=types).values('relationcultagent__agent__agent_type')
        elif type is None and agent is not None:
            agents = agent.split(',')
            ids = obj.relation_cult_place.filter(relationcultagent__agent_id__in=agents).values('relationcultagent__agent_id')
        else:
            ids = obj.relation_cult_place.all().values('relationcultagent__agent__agent_type')        
        for id in ids:
            if agent is not None:
                agent_id = id['relationcultagent__agent_id']
            else:
                agent_id = id['relationcultagent__agent__agent_type']
            if agent_id in res:
                res[agent_id] += 1
            elif agent_id is not None:
                res[agent_id] = 1
        return res

    class Meta:
        model = Place
        fields = ['id', 'name', 'place_type', 'ids', 'geometry']
        geo_field = 'geometry'


class PeopleMapSerializer(PlaceMapSerializer):
    ids = serializers.SerializerMethodField()

    def get_ids(self, obj):
        type = self.context['request'].query_params.get('ids')
        agent = self.context['request'].query_params.get('agent')
        res = {}
        if type is not None and type != 'null':
            types = type.split(',')
            ids = obj.relation_cult_place.filter(relationotheragent__agent__agent_type__in=types).values('relationotheragent__agent__agent_type')
        elif type is None and agent is not None:
            agents = agent.split(',')
            ids = obj.relation_cult_place.filter(relationotheragent__agent_id__in=agents).values('relationotheragent__agent_id')
        else:
            ids = obj.relation_cult_place.all().values('relationotheragent__agent__agent_type')
        for id in ids:
            if agent is not None:
                agent_id = id['relationotheragent__agent_id']
            else:
                agent_id = id['relationotheragent__agent__agent_type']
            if agent_id in res:
                res[agent_id] += 1
            elif agent_id is not None:
                res[agent_id] = 1
        return res

    class Meta:
        model = Place
        fields = ['id', 'name', 'place_type', 'ids', 'geometry']
        geo_field = 'geometry'
