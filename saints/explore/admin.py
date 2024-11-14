from typing import Any
from django.contrib import admin
from .models import *
from .forms import CultTypeForm
#from formset.richtext import controls
#from formset.richtext.widgets import RichTextarea
from django.contrib.gis import admin as gis_admin
from django.conf import settings
from django.utils.html import format_html


#richtext_widget = RichTextarea(control_elements=[
#    controls.Bold(),
#    controls.Italic(),
#    controls.TextColor(['text-red', 'text-green', 'text-blue']),
#])


# Register your models here.
class EntityAdminMixin:
    readonly_fields = ["created_by", "modified_by", "updated"]

    def created_by(self, instance):
        return instance.created.get_full_name()

    def modified_by(self, instance):
        return instance.modified.get_full_name()

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created = request.user
        else:
            obj.modified = request.user
        super().save_model(request, obj, form, change)


class ImageMixin:
    list_per_page = 25

    def image_preview(self, obj):
        return format_html('<img src="{}/{}" height="300"/>',
                           settings.DATA_URL,
                           obj.filename)

    def thumbnail_preview(self, obj):
        return format_html('<img src="{}thumbs/{}" height="100" />',
                           settings.DATA_URL,
                           obj.filename)


class ModelAdmin(admin.ModelAdmin):
    save_as = True


@admin.register(AgentName)
class AgentNameAdmin(ModelAdmin):
    list_display = ["id", "name", "language", "not_before", "updated"]
    search_fields = ["name"]
    autocomplete_fields = ["agent"]


class AgentNameInline(admin.TabularInline):
    extra = 0
    model = AgentName


@admin.register(OrganizationName)
class OrganizationNameAdmin(ModelAdmin):
    list_display = ["id", "name", "language", "not_before", "updated"]
    search_fields = ["name"]
    autocomplete_fields = ["organization"]


class OrganizationNameInline(admin.TabularInline):
    extra = 0
    model = OrganizationName


@admin.register(PlaceName)
class PlaceNameAdmin(ModelAdmin):
    list_display = ["id", "name", "language", "not_before", "updated"]
    search_fields = ["name"]
    autocomplete_fields = ["place"]


class PlaceNameInline(admin.TabularInline):
    extra = 0
    model = PlaceName


@admin.register(ParishName)
class ParishNameAdmin(ModelAdmin):
    list_display = ["id", "name", "language", "not_before", "updated"]
    search_fields = ["name"]
    autocomplete_fields = ["parish"]


class ParishNameInline(admin.TabularInline):
    extra = 0
    model = ParishName


class CultInline(admin.TabularInline):
    extra = 0
    model = Cult
    fields = ["id", "cult_type", "place", "not_before", "not_after"]


class PlaceInline(admin.TabularInline):
    extra = 0
    model = Place
    fields = ["id", "name", "place_type"]


class QuoteInline(admin.StackedInline):
    extra = 0
    model = Quote
    fields = ["quote_transcription", "transcribed_by", "translation",
              "translated_by", "page", "not_before", "not_after", "date_note",
              "notes"]


class RelationQuoteInline(admin.TabularInline):
    extra = 0
    model = RelationQuote
    fields = ["quote", "quote_uncertainty"]
    autocomplete_fields = ["quote"]


class RelationQuotePlaceInline(admin.TabularInline):
    extra = 0
    model = RelationQuote
    fields = ["place", "quote_uncertainty"]
    autocomplete_fields = ["place"]


class RelationCultQuoteInline(admin.TabularInline):
    extra = 0
    model = Cult


class RelationOfficeInline(admin.TabularInline):
    extra = 0
    model = RelationOffice
    fields = ["role", "organization"]
    autocomplete_fields = ["role", "organization"]


class RelationOtherPlaceInline(admin.TabularInline):
    extra = 0
    model = RelationOtherPlace
    fields = ["role", "place", "place_uncertainty"]
    autocomplete_fields = ["role", "place"]


class RelationOtherPlaceInline2(admin.TabularInline):
    extra = 0
    model = RelationOtherPlace
    fields = ["role", "cult", "place_uncertainty"]
    autocomplete_fields = ["role", "cult"]


class RelationCultAgentInline(admin.TabularInline):
    extra = 0
    model = RelationCultAgent
    fields = ["agent", "agent_main", "agent_alternative"]
    autocomplete_fields = ["agent"]


class RelationOtherAgentInline(admin.TabularInline):
    extra = 0
    model = RelationOtherAgent
    fields = ["role", "agent", "agent_uncertainty"]
    autocomplete_fields = ["agent"]


class RelationOtherCultInline(admin.TabularInline):
    extra = 0
    model = RelationOtherAgent
    fields = ["role", "cult", "agent_uncertainty"]
    autocomplete_fields = ["cult"]


class RelationDigitalResourceInline(admin.TabularInline):
    extra = 0
    model = RelationDigitalResource
    fields = ["resource_uri", "resource_uncertainty"]


class RelationIconographicInline(ImageMixin, admin.TabularInline):
    extra = 0
    model = RelationIconographic
    autocomplete_fields = ["iconographic"]
    fields = ["thumbnail_preview", "iconographic", "icon_uncertainty"]
    readonly_fields = ["thumbnail_preview"]


class RelationMBResourceInline(admin.TabularInline):
    extra = 0
    model = RelationMBResource
    fields = ["resource_uri"]


class FeastDayInline(admin.TabularInline):
    extra = 0
    model = FeastDay


@admin.register(Agent)
class AgentAdmin(EntityAdminMixin, ModelAdmin):
    model = Agent
    #formfield_overrides = {
    #    models.TextField: {"widget": richtext_widget},
    #}
    list_display = ["id", "name", "gender", "not_before", "saint", "updated"]
    search_fields = ["id", "name", "agentname__name"]
    filter_horizontal = ["agent_type"]
    fieldsets = [
        (
            None,
            {
                "fields": ["name", "saint", "agent_type", "gender",
                           "attributes"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs",
            {
                "fields": ["uri", "iconclass", "wikidata"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        AgentNameInline,
        FeastDayInline,
        RelationOfficeInline,
        RelationOtherCultInline,
    ]
    ordering = ["name"]


@admin.register(Place)
class PlaceAdmin(EntityAdminMixin, ModelAdmin, gis_admin.GISModelAdmin):
    model = Place
    list_display = ["id", "name", "place_type", "parish", "updated"]
    search_fields = ["id", "name", "placename__name"]
    autocomplete_fields = ["parent", "parish"]
    # raw_id_fields = ["quote"]
    readonly_fields = ["id", "children", "created_by", "modified_by", "updated"]

    fieldsets = [
        (
            None,
            {
                "fields": ["id", "name", "place_type", "certainty_type",
                           "type_indication", "municipality", "county",
                           "country", "certainty", "exclude", "geometry"],
            }
        ),
        (
            "Place relations",
            {
                "fields": ["parent", "parish", "children"],
            },
        ),
        (
            "Date information",
            {
                "fields": ["construction_date", "not_before", "not_after"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs / IDs",
            {
                "fields": ["bebr_id", "fmis_id", "wikidata"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        PlaceNameInline,
        CultInline,
        RelationOtherPlaceInline2,
        RelationQuoteInline
    ]
    ordering = ["name"]

    @admin.display(description="Children")
    def children(self, obj):
        return obj.place_children.all()


@admin.register(Cult)
class CultAdmin(EntityAdminMixin, ModelAdmin):
    model = Cult
    list_display = ["id", "cult_type", "place", "time_period", "updated"]
    search_fields = ["id", "cult_type__name", "place__name"]
    autocomplete_fields = ["place", "parent", "associated", "cult_type", "quote"]
    raw_id_fields = ["relation_cult_agent", "quote", "relation_other_place"]
    readonly_fields = ["created_by", "modified_by", "updated", "children"]
    fieldsets = [
        (
            None,
            {
                "fields": ["cult_uncertainty", "cult_type", "type_uncertainty",
                           "extant", "place", "place_uncertainty", "placement", "placement_uncertainty",
                           "in_parish", "feast_day"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after", "production_date",
                           "date_note", "time_period", "minyear", "maxyear"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "Relations",
            {
                "fields": ["parent", "associated", "children", "quote"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        RelationOtherPlaceInline,
        RelationCultAgentInline,
        RelationOtherAgentInline,
        RelationDigitalResourceInline,
        RelationIconographicInline,
        RelationMBResourceInline,
    ]
    ordering = ["place__name"]

    def children(self, obj):
        children = obj.cult_children.all()
        print(children)
        children_list = [child.__str__() for child in children]
        return "; ".join(children_list)


@admin.register(Organization)
class OrganizationAdmin(EntityAdminMixin, ModelAdmin):
    model = Organization
    list_display = ["id", "name", "organization_type", "updated"]
    search_fields = ["id", "name", "organizationname__name"]
    autocomplete_fields = ["parent"]
    readonly_fields = ["id", "created_by", "modified_by", "updated"]
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "name", "organization_type", "parent"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs",
            {
                "fields": ["wikidata"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        OrganizationNameInline
    ]
    ordering = ["name"]

@admin.register(Parish)
class ParishAdmin(EntityAdminMixin, ModelAdmin):
    model = Parish
    list_display = ["id", "name", "organization", "medival_organization", "updated"]
    search_fields = ["id", "name", "parishname__name"]
    autocomplete_fields = ["parent", "origin", "organization", "medival_organization"]
    readonly_fields = ["id", "created_by", "modified_by", "updated"]
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "name", "snid_4"],
            }
        ),
        (
            "Relations",
            {
                "fields": ["parent", "origin", "organization", "medival_organization"],
            },
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after", "date_note"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs",
            {
                "fields": ["wikidata"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        ParishNameInline,
        PlaceInline,
    ]
    ordering = ["name"]


@admin.register(Source)
class SourceAdmin(EntityAdminMixin, ModelAdmin):
    model = Source
    list_display = ["id", "name", "author", "pub_year", "source_type", "updated"]
    search_fields = ["id", "name", "title", "author"]
    readonly_fields = ["id", "created_by", "modified_by", "updated"]
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "name", "title", "source_type", 
                           "specific_type", "archive", "archive_name",
                           "author", "publisher", "pub_place", "pub_year", "pages",
                           "insource"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after", "date_note"],
            },
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs",
            {
                "fields": ["uri", "libris_uri"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        QuoteInline
    ]
    ordering = ["name"]


@admin.register(Quote)
class QuoteAdmin(EntityAdminMixin, ModelAdmin):
    model = Quote
    list_display = ["id", "source", "page", "updated"]
    search_fields = ["id", "source__name", "source__title"]
    autocomplete_fields = ["source"]
    readonly_fields = ["id", "created_by", "modified_by", "updated"]
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "source", "page", "language"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after", "date_note"],
            },
        ),
        (
            "Quote",
            {
                "fields": ["quote_transcription", "transcribed_by",
                           "translation", "translated_by"],
            }
        ),
        (
            "Comments",
            {
                "fields": ["comment", "notes"],
            }
        ),
        (
            "URIs",
            {
                "fields": ["uri"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]
    inlines = [
        RelationQuotePlaceInline
    ]
    ordering = ["source__name"]


@admin.register(FeastDay)
class FeastDayAdmin(EntityAdminMixin, ModelAdmin):
    list_display = ["id", "day", "type", "agent", "updated"]
    search_fields = ["id", "day", "type", "agent__name"]
    autocomplete_fields = ["agent"]


@admin.register(Iconographic)
class IconographicAdmin(ImageMixin, ModelAdmin):
    model = Iconographic
    list_display = ["id", "thumbnail_preview", "card", "church", "motif2", "saints"]
    search_fields = ["id", "church", "motif2", "saints"]
    autocomplete_fields = ["parish", "place"]
    readonly_fields = ["image_preview", "id", "card", "card_type", "filename", "front_back",
                       "volume", "uri", "church", "subject1", "subject2",
                       "subject3", "motif1", "motif2", "bebr_id", "site_no",
                       "raa_no", "description", "filename2", "note", "ocr",
                       "aat", "site_uri", "toe", "technique", "saints",
                       "date_note", "not_before", "not_after"]
    ordering = ["filename"]


@admin.register(RelationCultAgent)
class RelationCultAgentAdmin(ModelAdmin):
    model = RelationCultAgent
    list_display = ["id", "cult", "agent", "agent_main", "agent_alternative", "updated"]
    autocomplete_fields = ["cult", "agent"]
    search_fields = ["cult__place__name", "cult__cult_type__name", "agent__name"]


@admin.register(RelationOffice)
class RelationOfficeAdmin(EntityAdminMixin, ModelAdmin):
    model = RelationOffice
    list_display = ["id", "agent", "role", "organization", "updated"]
    autocomplete_fields = ["agent", "organization", "role"]
    search_fields = ["agent__name", "organization__name", "role__name"]
    readonly_fields = ["id", "created_by", "modified_by", "updated"]
    fieldsets = [
        (
            None,
            {
                "fields": ["id", "agent", "role", "organization"],
            }
        ),
        (
            "Date information",
            {
                "fields": ["not_before", "not_after", "date_note"],
            },
        ),
        (
            "Editing information",
            {
                "fields": ["created_by", "modified_by", "updated"],
            },

        ),
    ]


@admin.register(RelationDigitalResource)
class RelationDigitalResourceAdmin(EntityAdminMixin, ModelAdmin):
    model = RelationDigitalResource
    list_display = ["id", "cult", "resource_uri", "updated"]
    autocomplete_fields = ["cult"]
    search_fields = ["cult__place__name", "cult__cult_type__name", "resource_uri"]


@admin.register(RelationMBResource)
class RelationMBResourceAdmin(EntityAdminMixin, ModelAdmin):
    model = RelationMBResource
    list_display = ["id", "cult", "resource_uri", "updated"]
    autocomplete_fields = ["cult"]
    search_fields = ["cult__place__name", "cult__cult_type__name", "resource_uri"]


@admin.register(RelationIconographic)
class RelationIconographicAdmin(EntityAdminMixin, ImageMixin, ModelAdmin):
    model = RelationIconographic
    list_display = ["id", "cult", "thumbnail_preview", "iconographic", "updated"]
    autocomplete_fields = ["cult", "iconographic"]
    search_fields = ["cult__place__name", "cult__cult_type__name", "iconographic__church", "iconographic__motif2"]
    readonly_fields = ["thumbnail_preview"]


@admin.register(RelationOtherPlace)
class RelationOtherPlaceAdmin(ModelAdmin):
    model = RelationOtherPlace
    list_display = ["id", "place", "role", "cult", "updated"]
    autocomplete_fields = ["place", "cult", "role"]
    search_fields = ["place__name", "cult__place__name", "cult__cult_type__name", "role__name"]


@admin.register(RelationOtherAgent)
class RelationOtherAgentAdmin(ModelAdmin):
    model = RelationOtherAgent
    list_display = ["id", "cult", "role", "agent", "updated"]
    autocomplete_fields = ["agent", "cult", "role"]
    search_fields = ["agent__name", "cult__place__name", "cult__cult_type__name", "role__name"]


@admin.register(AgentType)
class AgentTypeAdmin(ModelAdmin):
    list_display = ["id", "name", "name_sv", "name_fi", "level", "updated"]
    search_fields = ["name", "name_sv", "name_fi"]
    ordering = ["name"]


@admin.register(OrganizationType)
class OrganizationTypeAdmin(ModelAdmin):
    list_display = ["id", "name", "name_sv", "name_fi", "updated"]
    search_fields = ["name", "name_sv", "name_fi"]


@admin.register(PlaceType)
class PlaceTypeAdmin(ModelAdmin):
    list_display = ["id", "name", "name_sv", "name_fi", "level", "updated"]
    search_fields = ["name", "name_sv", "name_fi"]


@admin.register(CultType)
class CultTypeAdmin(ModelAdmin):
    list_display = ["id", "name", "name_sv", "name_fi", "level", "updated"]
    search_fields = ["name", "name_sv", "name_fi"]
    ordering = ["name"]
    form = CultTypeForm
