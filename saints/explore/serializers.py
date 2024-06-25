from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Agent, AgentType, AgentName, Place, PlaceName, PlaceType, \
    Cult, CultType, \
    Source, Parish, Quote, Organization, RelationCultAgent, RelationOffice


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


class OrganizationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Organization
        exclude = ['created', 'modified', 'updated', 'notes']


class RelationOfficeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationOffice
        fields = '__all__'


class AgentSerializer(serializers.ModelSerializer):
    created = UserSerializer(read_only=True)
    modified = UserSerializer(read_only=True)
    agent_type = AgentTypeSerializer(read_only=True, many=True)
    held_office = OrganizationMiniSerializer(read_only=True, many=True)
    agent_names = serializers.SerializerMethodField()

    def get_agent_names(self, obj):
        return obj.agentname_set.all()

    class Meta:
        model = Agent
        exclude = ['notes']


class AgentMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = ['id', 'name']


class CultAgentRelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RelationCultAgent
        fields = '__all__'


class PlaceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        exclude = ['updated', 'aat']


class PlaceTypeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlaceType
        fields = ['id', 'name']


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        exclude = ['created', 'modified', 'notes']


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


class PlaceMiniSerializer(serializers.ModelSerializer):
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)

    class Meta:
        model = Place
        fields = ['id', 'name', 'municipality', 'parish', 'place_type']


class CultTypeMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = CultType
        exclude = ['updated', 'aat', 'wikidata']


class CultTypeSerializer(serializers.ModelSerializer):
    parent = CultTypeMiniSerializer(read_only=True)

    class Meta:
        model = CultType
        fields = '__all__'


class CultSerializer(serializers.ModelSerializer):
    place = PlaceMiniSerializer(read_only=True)
    cult_type = CultTypeSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True, many=True)
    # relation_cult_agent = CultAgentRelationSerializer(read_only=True, many=True)
    relation_other_place = PlaceMiniSerializer(read_only=True, many=True)

    class Meta:
        model = Cult
        exclude = ['created', 'modified', 'notes']


class PlaceSerializer(serializers.ModelSerializer):
    parish = ParishMiniSerializer(read_only=True)
    place_type = PlaceTypeMiniSerializer(read_only=True)
    parent = PlaceMiniSerializer(read_only=True)
    quote = QuoteSerializer(read_only=True, many=True)
    place_name = PlaceNameSerializer(read_only=True, many=True)
    place_children = PlaceMiniSerializer(read_only=True, many=True)
    # cult_relations = CultSerializer(read_only=True)

    class Meta:
        model = Place
        exclude = ['created', 'modified', 'updated', 'notes']
