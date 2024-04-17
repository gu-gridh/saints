from django.db import models
from django.conf import settings
# from django.contrib.gis.geos import Point


# Create your models here.

# Abstract Choices
LANGUAGES = {
    "dan": "Danish",
    "deu": "German",
    "eng": "English",
    "fin": "Finnish",
    "fra": "French",
    "gutn": "Gutnish",
    "isl": "Icelandic",
    "ita": "Italian",
    "lat": "Latin",
    "nds": "Lower German",
    "non": "Old Norse",
    "nor": "Norwegian",
    "rus": "Russian",
    "swe": "Swedish",
}


# Abstract Models
class EntityMixin(models.Model):
    notes = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    created = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False, related_name="%(app_label)s_%(class)s_created")
    modified = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False, related_name="%(app_label)s_%(class)s_modified")
    updated = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class DatesMixin(models.Model):
    not_after = models.CharField(max_length=21, blank=True)
    not_before = models.CharField(max_length=21, blank=True)
    date_note = models.TextField(blank=True)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(max_length=4, choices=LANGUAGES)
    # not only dates, so needs to be a charfield
    not_before = models.CharField(max_length=21, blank=True)
    updated = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class TypeMixin(models.Model):
    name = models.CharField(max_length=255)
    name_sv = models.CharField(max_length=255, blank=True)
    name_fi = models.CharField(max_length=255, blank=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


# Type models
class AgentType(TypeMixin):
    pass


class OrganizationType(TypeMixin):
    pass


class PlaceType(TypeMixin):
    PLACE_TYPES = {
        "T": "Type of Place",
        "S": "Subcategory",
    }
    level = models.CharField(max_length=1, choices=PLACE_TYPES)
    aat_code = models.URLField(blank=True)


class CultType(TypeMixin):
    CULT_TYPES = {
        "T": "Type of Evidence",
        "I": "Intermediate",
        "S": "Subcategory",
    }
    level = models.CharField(max_length=1, choices=CULT_TYPES)
    aat_code = models.URLField(blank=True)
    wikidata = models.URLField(blank=True)


# Relation models
class Office(EntityMixin, DatesMixin):
    agent = models.ForeignKey("Agent", on_delete=models.CASCADE)
    organization = models.ForeignKey("Organization", on_delete=models.CASCADE)
    type = models.ForeignKey(AgentType, on_delete=models.RESTRICT)


# Core models
class Organization(EntityMixin, DatesMixin):
    name = models.CharField(max_length=255, help_text="Name in English")
    wikidata = models.URLField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.RESTRICT)

    def __str__(self):
        return "|".join([self.name, self.organization_type.name])


class Agent(EntityMixin):
    AGENT_TYPES = {
        "S": "Saint",
        "P": "Person"
    }
    GENDER_TYPES = {
        "M": "Man",
        "W": "Woman",
        "N": "N/A",
    }
    name = models.CharField(max_length=255, help_text="Name in English")
    agent_type = models.CharField(max_length=1, choices=AGENT_TYPES)
    rel_type = models.ManyToManyField(AgentType)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_TYPES)
    held_office = models.ManyToManyField(Organization, through=Office)
    not_before = models.CharField(max_length=21, blank=True)
    attributes = models.TextField(blank=True)
    uri = models.URLField(blank=True)
    iconclass = models.CharField(max_length=255, blank=True)
    wikidata = models.URLField(blank=True)

    def __str__(self):
        return "|".join([self.name, self.gender, self.not_before])


class Place(EntityMixin, DatesMixin):
    name = models.CharField(max_length=255, help_text="Name in English")
    place_type = models.ForeignKey(PlaceType, on_delete=models.RESTRICT,
                                   limit_choices_to={"level": "S"})
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    # geom = models.PointField(geography=True, default=Point(0.0, 0.0))
    municipality = models.CharField(max_length=255, help_text="Modern Location")
    county = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    # exclude = models.BooleanField(null=True, help_text="")
    # type_indication =
    construction_date = models.CharField(max_length=21, blank=True)
    bebr_id = models.URLField(blank=True)
    fmis_id = models.URLField(blank=True)
    wikidata = models.URLField(blank=True)

    def __str__(self):
        return "|".join([self.name, self.municipality, self.place_type.name])


class Cult(EntityMixin, DatesMixin):
    EXTANT_TYPES = {
        "E": "Extant",
        "L": "Lost",
        "N": "N/A",
    }
    COLOUR = {
        "R": "Red",
        "U": "Blue",
        "G": "Green",
        "B": "Black",
        "Y": "Yellow",
        "P": "Purple",
        "O": "Brown",
        "W": "White",
    }
    time_period = models.CharField(max_length=255, blank=True)
    # minyear = models.DateField()
    # maxyear = models.DateField()
    production_date = models.CharField(max_length=21, blank=True)
    extant = models.CharField(max_length=1, choices=EXTANT_TYPES)
    colour = models.CharField(max_length=1, choices=COLOUR)
    placement = models.CharField(max_length=255, blank=True)
    placement_uncertainty = models.BooleanField(null=True, help_text="Is placement uncertain?")
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)
    place_uncertainty = models.BooleanField(null=True, help_text="Is place uncertain?")
    in_parish = models.BooleanField(help_text="Is cult located in a parish?")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="cult_parent")
    associated = models.ForeignKey("self", on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name="cult_associated")    
    cult_uncertainty = models.BooleanField(null=True, help_text="Is cult uncertain?")
    type_uncertainty = models.BooleanField(null=True, help_text="Is type uncertain?")
    cult_type = models.ForeignKey(CultType, on_delete=models.RESTRICT,
                                  limit_choices_to={"level": "S"})
    feast_day = models.CharField(max_length=21, blank=True)
    agent = models.ManyToManyField(Agent, blank=True)
    quote = models.ManyToManyField("Quote", blank=True)

    def __str__(self):
        return "|".join([self.place.name, self.cult_type.name])


class Parish(EntityMixin, DatesMixin):
    name = models.CharField(max_length=255, help_text="Name in English")
    parish_number = models.PositiveSmallIntegerField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name="parish_organization")
    medival_organization = models.ForeignKey(Organization, on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name="medival_organization")
    wikidata = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "parishes"
    
    def __str__(self):
        return "|".join([self.name, self.organization.name])


class Source(EntityMixin, DatesMixin):
    SOURCE_TYPES = {
        "T": "Tryckt",
        "M": "Ms",
        "D": "Digital",
        "O": "Oral",
        "N": "N/A"
    }
    name = models.CharField(max_length=255, help_text="Shortname")
    title = models.CharField(max_length=255, blank=True)
    source_type = models.CharField(max_length=1, choices=SOURCE_TYPES)
    specific_type = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    pub_place = models.CharField(max_length=255, blank=True)
    pub_year = models.DateField(blank=True)
    archive = models.CharField(max_length=255, blank=True)
    archive_name = models.CharField(max_length=255, blank=True)
    pages = models.CharField(max_length=10, blank=True)
    uri = models.URLField(blank=True)
    libris_uri = models.URLField(blank=True)


class Quote(EntityMixin, DatesMixin):
    source = models.ForeignKey(Source, on_delete=models.RESTRICT, null=True)
    page = models.CharField(max_length=255, blank=True)
    language = models.CharField(max_length=4, blank=True, choices=LANGUAGES)
    uri = models.URLField(blank=True)
    transcription = models.TextField(blank=True)
    transcribed_by = models.CharField(max_length=255, blank=True)
    translation = models.TextField(blank=True)
    translated_by = models.CharField(max_length=255, blank=True)


class FeastDay(EntityMixin):
    day = models.CharField(max_length=5, help_text="Day in format 00-00")
    type = models.CharField(max_length=255, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)


# Name models
class AgentName(NameMixin):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)


class OrganizationName(NameMixin):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)


class PlaceName(NameMixin):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)


class ParishName(NameMixin):
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
