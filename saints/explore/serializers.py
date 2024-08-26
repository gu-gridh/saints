from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer
from django.contrib.auth.models import User
from .models import Agent, AgentType, AgentName, Place, PlaceName, PlaceType, \
    Cult, CultType, Source, Parish, Quote, Organization, FeastDay, \
    OrganizationType, RelationCultAgent, RelationOffice, \
    RelationDigitalResource, Iconographic, RelationMBResource, \
    RelationOtherAgent, RelationOtherPlace


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

    class Meta:
        model = RelationOffice
        fields = '__all__'


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

    class Meta:
        model = RelationMBResource
        fields = ['resource_uri']


class PlaceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        exclude = ['updated', 'aat']


class PlaceTypeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        fields = ['id', 'name', 'parent']


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        exclude = ['created', 'modified', 'notes']


class FeastDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = FeastDay
        fields = ['day', 'type']


class SourceMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = ['id', 'name']


class QuoteSerializer(serializers.ModelSerializer):
    source = SourceMiniSerializer(read_only=True)

    class Meta:
        model = Quote
        exclude = ['created', 'modified', 'notes']


class ParishMiniSerializer(serializers.ModelSerializer):
    medival_organization = OrganizationMiniSerializer(read_only=True)

    class Meta:
        model = Parish
        fields = ['id', 'name', 'medival_organization']


# class PlaceMiniSerializer(GeoFeatureModelSerializer):
class PlaceMiniSerializer(serializers.ModelSerializer):
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)

#   def to_representation(self, instance):
#       ret = super().to_representation(instance)
#       ret['geometry'] = ret['geometry']['coordinates']
#       return ret

    class Meta:
        model = Place
        fields = ['id', 'name', 'municipality', 'parish', 'place_type', 'geometry']
#        geo_field = 'geometry'


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

    class Meta:
        model = Iconographic
        fields = ['id', 'motif2', 'filename']


class CultRelationSerializer(serializers.ModelSerializer):
    place = serializers.CharField(source='place.name')
    cult_type = serializers.CharField(source='cult_type.name')

    class Meta:
        model = Cult
        fields = ['id', 'place', 'cult_type', 'minyear', 'maxyear']


class RelationOtherAgentSerializer(serializers.ModelSerializer):
    agent = AgentMiniSerializer(read_only=True)
    role = AgentTypeSerializer(read_only=True)

    class Meta:
        model = RelationOtherAgent
        fields = ['agent', 'agent_uncertainty', 'role']


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
    quote = QuoteSerializer(read_only=True, many=True)
    relation_cult_agent = AgentRelationSerializer(read_only=True, many=True, source='relationcultagent_set')
    relation_other_agent = RelationOtherAgentSerializer(read_only=True, many=True, source='relationotheragent_set')
    relation_other_place = RelationOtherPlaceSerializer(read_only=True, many=True, source='relationotherplace_set')
    relation_digital_resource = DigitalResourceRelationSerializer(read_only=True, many=True, source='relationdigitalresource_set')
    relation_mb_resource = MBResourceRelationSerializer(read_only=True, many=True, source='relationmbresource_set')
    relation_iconographic = IconicMiniSerializer(read_only=True, many=True)

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


class AgentSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    agent_type = AgentTypeSerializer(read_only=True, many=True)
    feast_day = FeastDaySerializer(read_only=True, many=True, source='feastday_set')
    held_office = OrganizationMiniSerializer(read_only=True, many=True)
    agent_names = serializers.SerializerMethodField()
    relation_cult_agent = CultAgentRelationSerializer(read_only=True, many=True, source='relationcultagent_set')
    relation_other_agent = RelationOtherCultSerializer(read_only=True, many=True, source='relationotheragent_set')

    def get_agent_names(self, obj):
        return obj.agentname_set.all().values('name', 'language', 'not_before')

    class Meta:
        model = Agent
        exclude = ['notes']


# class PlaceSerializer(GeoFeatureModelSerializer):
class PlaceSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)
    parent = PlaceMiniSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True, many=True)
    place_children = PlaceMiniSerializer(read_only=True, many=True)
    relation_cult_place = CultMiniSerializer(read_only=True, many=True)
    relation_other_place = RelationOtherPlaceCultSerializer(read_only=True, many=True, source='relationotherplace_set')
    place_names = serializers.SerializerMethodField()

    def get_place_names(self, obj):
        return obj.placename_set.all().values('name', 'language', 'not_before')

#    def to_representation(self, instance):
#        ret = super().to_representation(instance)
#        ret['geometry'] = ret['geometry']['coordinates']
#        return ret

    class Meta:
        model = Place
        exclude = ['notes']
#        geo_field = 'geometry'
