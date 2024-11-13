from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from ckeditor.fields import RichTextField

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
class NotesMixin(models.Model):
    comment = RichTextField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="For internal notes")

    class Meta:
        abstract = True


class EntityMixin(models.Model):
    created = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, editable=False, null=True, related_name="%(app_label)s_%(class)s_created")
    modified = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, editable=False, null=True, related_name="%(app_label)s_%(class)s_modified")
    updated = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class DatesMixin(models.Model):
    # original model allows not only date strigns, so dates need to be charfields
    not_after = models.CharField(max_length=30, blank=True, verbose_name="End date")
    not_before = models.CharField(max_length=30, blank=True, verbose_name="First indication date")
    date_note = models.TextField(blank=True)

    class Meta:
        abstract = True


class NameMixin(models.Model):
    name = models.CharField(max_length=255, verbose_name="Attested name")
    language = models.CharField(max_length=4, choices=LANGUAGES)
    not_before = models.CharField(max_length=21, blank=True, verbose_name="Attested date")
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
    # TODO: limit choices
    AGENT_TYPES = {
        "Type of Agent": "Type of Agent",
        "Type of Involvement": "Type of Involvement",
    }
    level = models.CharField(max_length=20, choices=AGENT_TYPES)


class OrganizationType(TypeMixin):
    pass


class PlaceType(TypeMixin):
    PLACE_TYPES = {
        "Place Type": "Place Type",
        "Subcategory": "Subcategory",
        "Cult Place Type": "Cult Place Type",
    }
    parent = models.ForeignKey("self", on_delete=models.RESTRICT,
                               # TODO: place type and cult place type can't have a parent
                               limit_choices_to={"level": "Place Type"}, null=True, blank=True)
    level = models.CharField(max_length=15, choices=PLACE_TYPES)
    aat = models.URLField(blank=True)


class CultType(TypeMixin):
    CULT_TYPES = {
        "Type of Evidence": "Type of Evidence",
        "Intermediate": "Intermediate",
        "Subcategory": "Subcategory",
    }
    level = models.CharField(max_length=20, choices=CULT_TYPES)
    parent = models.ForeignKey("self", on_delete=models.RESTRICT, null=True, blank=True)
    aat = models.URLField(blank=True)
    wikidata = models.URLField(blank=True)

    class Meta:
        verbose_name = "Cult Manifestation Type"
        verbose_name_plural = "Cult Manifestation Types"


# Relation models
class RelationCultAgent(models.Model):
    ALTERNATIVES = {
        "A.1": "A.1",
        "A.2": "A.2",
        "A.3": "A.3",
        "B.1": "B.1",
        "B.2": "B.2",
        "B.3": "B.3",
        "C.1": "C.1",
        "C.2": "C.2",
        "C.3": "C.3",
        # Keep for now
        "Yes": "Yes",
    }
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    agent = models.ForeignKey("Agent", on_delete=models.RESTRICT)
    agent_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is Agent uncertain?")
    agent_main = models.BooleanField(blank=True)
    agent_alternative = models.CharField(max_length=3, blank=True, null=True, choices=ALTERNATIVES)
    updated = models.DateField(auto_now=True)


class RelationOffice(EntityMixin, DatesMixin):
    agent = models.ForeignKey("Agent", on_delete=models.RESTRICT)
    organization = models.ForeignKey("Organization", on_delete=models.RESTRICT)
    role = models.ForeignKey(AgentType, limit_choices_to={"level": "Type of Involvement"}, on_delete=models.RESTRICT)


class RelationOtherAgent(models.Model):
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    agent = models.ForeignKey("Agent", on_delete=models.RESTRICT)
    agent_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is Agent uncertain?")
    role = models.ForeignKey(AgentType, limit_choices_to={"level": "Type of Involvement"}, on_delete=models.RESTRICT)
    updated = models.DateField(auto_now=True)

    class Meta:
        verbose_name = "Relation Cult Manifestation / Agent (Involvement)"
        verbose_name_plural = "Relations Cult Manifestation / Agent (Involvement)"


class RelationDigitalResource(EntityMixin):
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    resource_uri = models.URLField(blank=True)
    resource_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is digital resource uncertain?")


class RelationMBResource(EntityMixin):
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    resource_uri = models.URLField(blank=True)


class RelationIconographic(EntityMixin):
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    iconographic = models.ForeignKey("Iconographic", on_delete=models.RESTRICT)
    icon_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is relation uncertain?")

    @property
    def filename(self):
        return self.iconographic.filename

    def __str__(self):
        return "|".join(filter(None, [self.cult.place.name, self.cult.cult_type.name, self.iconographic.motif2]))


class RelationQuote(models.Model):
    place = models.ForeignKey("Place", on_delete=models.RESTRICT)
    quote = models.ForeignKey("Quote", on_delete=models.RESTRICT)
    quote_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is quote uncertain?")
    updated = models.DateField(auto_now=True)


class RelationOtherPlace(models.Model):
    cult = models.ForeignKey("Cult", on_delete=models.RESTRICT)
    place = models.ForeignKey("Place", on_delete=models.RESTRICT)
    role = models.ForeignKey(PlaceType, limit_choices_to={"level": "Cult Place Type"}, on_delete=models.RESTRICT)
    place_uncertainty = models.BooleanField(blank=True, null=True, help_text="Is place uncertain?")
    updated = models.DateField(auto_now=True)


# Core models
class Organization(EntityMixin, NotesMixin, DatesMixin):
    name = models.CharField(max_length=255, help_text="Name in English")
    wikidata = models.URLField(blank=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    organization_type = models.ForeignKey(OrganizationType, on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):
        if not self.organization_type:
            return ""
        return "|".join(filter(None, [self.name, self.organization_type.name]))


class Agent(EntityMixin, NotesMixin):
    GENDER_TYPES = {
        "Man": "Man",
        "Woman": "Woman",
        "N/A": "N/A",
    }
    name = models.CharField(max_length=255, help_text="Name in English")
    saint = models.BooleanField()
    agent_type = models.ManyToManyField(AgentType, blank=True, limit_choices_to={"level": "Type of Agent"})
    gender = models.CharField(max_length=10, null=True, blank=True, choices=GENDER_TYPES)
    held_office = models.ManyToManyField(Organization, through=RelationOffice)
    not_before = models.CharField(max_length=21, blank=True, verbose_name="Attested dates")
    attributes = models.TextField(blank=True)
    uri = models.URLField(blank=True)
    iconclass = models.CharField(max_length=255, blank=True)
    wikidata = models.URLField(blank=True)

    def __str__(self):
        return "|".join(filter(None, [self.name, self.gender, self.not_before]))


class Place(EntityMixin, NotesMixin, DatesMixin):
    INDICATION_TYPES = {
        "Written": "Written",
        "Artefact": "Artefact",
        "Oral": "Oral",
    }
    name = models.CharField(max_length=255, help_text="Name in English")
    # places do not neccessarily have a type in case of unknown places
    place_type = models.ForeignKey(PlaceType, on_delete=models.RESTRICT,
                                   limit_choices_to={"level": "Subcategory"}, blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="place_children")
    parish = models.ForeignKey("Parish", on_delete=models.RESTRICT, null=True, blank=True)
    quote = models.ManyToManyField("Quote", through=RelationQuote)
    geometry = gis_models.PointField(default=Point(0.0, 0.0))
    certainty_type = models.BooleanField(null=True, blank=True, help_text="Is type certain?")
    certainty = models.BooleanField(null=True, blank=True, help_text="Is location certain?")
    municipality = models.CharField(max_length=255, null=True, blank=True, help_text="Modern Location")
    county = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    exclude = models.BooleanField(null=True, help_text="")
    not_after = models.CharField(max_length=30, blank=True, verbose_name="Destruction date")
    type_indication = models.CharField(max_length=10, null=True, blank=True, choices=INDICATION_TYPES)
    construction_date = models.CharField(max_length=21, blank=True)
    bebr_id = models.URLField(blank=True)
    fmis_id = models.URLField(blank=True)
    wikidata = models.URLField(blank=True)

    def __str__(self):
        return "|".join(filter(None, [self.name, self.municipality, self.place_type.name]))


class Cult(EntityMixin, NotesMixin, DatesMixin):
    EXTANT_TYPES = {
        "Extant": "Extant",
        "Lost": "Lost",
        "N/A": "N/A",
    }
    COLOUR = {
        "Red": "Red",
        "Blue": "Blue",
        "Green": "Green",
        "Black": "Black",
        "Yellow": "Yellow",
        "Purple": "Purple",
        "Brown": "Brown",
        "White": "White",
    }
    time_period = models.CharField(max_length=255, blank=True, verbose_name="Function time-period")
    minyear = models.PositiveSmallIntegerField(default=0)
    maxyear = models.PositiveSmallIntegerField(default=0)
    production_date = models.CharField(max_length=21, blank=True)
    extant = models.CharField(max_length=10, choices=EXTANT_TYPES)
    colour = models.CharField(max_length=10, choices=COLOUR)
    placement = models.CharField(max_length=255, blank=True)
    placement_uncertainty = models.BooleanField(null=True, help_text="Is placement uncertain?")
    place = models.ForeignKey(Place, on_delete=models.RESTRICT, null=True, related_name="relation_cult_place")
    relation_other_place = models.ManyToManyField(Place, through=RelationOtherPlace, related_name="relation_other_place")
    relation_cult_agent = models.ManyToManyField(Agent, through=RelationCultAgent, related_name="relation_cult_agent")
    place_uncertainty = models.BooleanField(null=True, help_text="Is place uncertain?")
    in_parish = models.BooleanField(help_text="Is cult located in a parish?")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL,
                               null=True, blank=True, related_name="cult_children")
    associated = models.ManyToManyField("self", null=True, blank=True, related_name="cult_associated")
    cult_uncertainty = models.BooleanField(null=True, help_text="Is cult uncertain?")
    type_uncertainty = models.BooleanField(null=True, help_text="Is type uncertain?")
    cult_type = models.ForeignKey(CultType, on_delete=models.RESTRICT,
                                  limit_choices_to={"level": "Subcategory"})
    feast_day = models.CharField(max_length=21, blank=True)
    quote = models.ManyToManyField("Quote", blank=True, related_name="cult_quote")
    relation_iconographic = models.ManyToManyField("Iconographic", through=RelationIconographic, blank=True)

    def __str__(self):
        return "|".join(filter(None, [self.place.name, self.cult_type.name]))

    class Meta:
        verbose_name = "Cult Manifestation"
        verbose_name_plural = "Cult Manifestations"


class Parish(EntityMixin, NotesMixin, DatesMixin):
    name = models.CharField(max_length=255, help_text="Name in English")
    snid_4 = models.PositiveSmallIntegerField(default=0)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    origin = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="origin_parish")
    organization = models.ForeignKey(Organization, on_delete=models.RESTRICT,
                                     null=True, blank=True, related_name="parish_organization")
    medival_organization = models.ForeignKey(Organization, on_delete=models.RESTRICT,
                                             null=True, blank=True, related_name="medival_organization")
    wikidata = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = "parishes"

    def __str__(self):
        return "|".join(filter(None, [self.name]))


class Source(EntityMixin, NotesMixin, DatesMixin):
    SOURCE_TYPES = {
        "Tryckt": "Tryckt",
        "Ms": "Ms",
        "Digital": "Digital",
        "Oral": "Oral",
        "N/A": "N/A"
    }
    name = models.CharField(max_length=255, help_text="Shortname")
    title = models.CharField(max_length=300, blank=True)
    source_type = models.CharField(max_length=10, choices=SOURCE_TYPES)
    specific_type = models.CharField(max_length=255, blank=True)
    author = models.CharField(max_length=255, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    pub_place = models.CharField(max_length=255, blank=True)
    pub_year = models.CharField(max_length=255, blank=True)
    insource = models.TextField(blank=True)
    archive = models.CharField(max_length=255, blank=True)
    archive_name = models.CharField(max_length=255, blank=True)
    pages = models.CharField(max_length=10, blank=True)
    uri = models.URLField(blank=True)
    libris_uri = models.URLField(blank=True)

    def __str__(self):
        return "|".join(filter(None, [self.name, self.author, self.pub_year]))


class Quote(EntityMixin, NotesMixin, DatesMixin):
    source = models.ForeignKey(Source, on_delete=models.RESTRICT, null=True, related_name="source_quote")
    page = models.CharField(max_length=255, blank=True, help_text="Page or folio")
    language = models.CharField(max_length=4, blank=True, choices=LANGUAGES)
    uri = models.URLField(blank=True)
    quote_transcription = RichTextField(null=True, blank=True)
    transcribed_by = models.CharField(max_length=255, blank=True)
    translation = RichTextField(null=True, blank=True)
    translated_by = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.source:
            return "|".join(filter(None, [self.source.name, self.page]))
        else:
            return self.page


# needed here as we can't have foreign key in other database
# not going to change overly complicated data structure for now
class Iconographic(DatesMixin):
    CARD_TYPES = {
        "be": "be",
        "hk": "hk",
        "lb": "lb",
        "mb": "mb",
        "or": "or"
    }
    card = models.PositiveSmallIntegerField()
    card_type = models.CharField(max_length=2, choices=CARD_TYPES)
    filename = models.CharField(max_length=255)
    front_back = models.CharField(max_length=1)
    volume = models.PositiveSmallIntegerField()
    uri = models.URLField(blank=True, null=True)
    church = models.CharField(max_length=255, blank=True, null=True)
    subject1 = models.CharField(max_length=255, blank=True, null=True)
    subject2 = models.CharField(max_length=255, blank=True, null=True)
    subject3 = models.CharField(max_length=255, blank=True, null=True)
    motif1 = models.CharField(max_length=255, blank=True, null=True)
    motif2 = models.CharField(max_length=255, blank=True, null=True)
    bebr_id = models.CharField(max_length=255, blank=True, null=True)
    site_no = models.CharField(max_length=255, blank=True, null=True)
    raa_no = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255)
    filename2 = models.CharField(max_length=255)
    note = models.CharField(max_length=255, blank=True, null=True)
    ocr = models.TextField(blank=True)
    aat = models.CharField(max_length=255, blank=True, null=True)
    site_uri = models.URLField(blank=True, null=True)
    toe = models.CharField(max_length=255, blank=True, null=True)
    technique = models.CharField(max_length=255, blank=True, null=True)
    saints = models.CharField(max_length=255, blank=True, null=True)
    place = models.ForeignKey(Place, on_delete=models.RESTRICT, null=True)
    parish = models.ForeignKey(Parish, on_delete=models.RESTRICT, null=True)

    def __str__(self):
        return "|".join(filter(None, [self.church, self.motif2]))


class FeastDay(EntityMixin):
    day = models.CharField(max_length=5, help_text="Day in format 00-00 or * for recurring events")
    type = models.CharField(max_length=255, blank=True)
    agent = models.ForeignKey(Agent, on_delete=models.RESTRICT)

    def __str__(self):
        return "|".join(filter(None, [self.day, self.type]))


# Name models
class AgentName(NameMixin):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)


class OrganizationName(NameMixin):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False, related_name="%(app_label)s_%(class)s_created")
    modified = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, editable=False, related_name="%(app_label)s_%(class)s_modified")


class PlaceName(NameMixin):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)


class ParishName(NameMixin):
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
