from django.contrib import admin
from .models import *


# Register your models here.
class EntityAdminMixin:
    readonly_fields = ["created", "modified", "updated"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created = request.user
        else:
            obj.modified = request.user
        super().save_model(request, obj, form, change)


@admin.register(Agent)
class AgentAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Agent
    list_display = ["id", "name", "updated"]


@admin.register(Place)
class PlaceAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Place
    list_display = ["id", "name", "updated"]


@admin.register(Cult)
class CultAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Cult
    list_display = ["id", "updated"]


@admin.register(Organization)
class OrganizationAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Organization
    list_display = ["id", "name", "updated"]


@admin.register(Parish)
class ParishAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Parish
    list_display = ["id", "name", "updated"]


@admin.register(Source)
class SourceAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Source
    list_display = ["id"]


@admin.register(Quote)
class QuoteAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Quote
    list_display = ["id"]


@admin.register(FeastDay)
class FeastDayAdmin(admin.ModelAdmin):
    list_display = ["id", "day", "type", "updated"]


@admin.register(Office)
class OfficeAdmin(EntityAdminMixin, admin.ModelAdmin):
    model = Office
    list_display = ["id", "agent_id", "organization_id", "updated"]


@admin.register(AgentType)
class AgentTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "updated"]


@admin.register(OrganizationType)
class OrganizationTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "updated"]


@admin.register(PlaceType)
class PlaceTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "level", "updated"]


@admin.register(CultType)
class CultTypeAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "level", "updated"]


@admin.register(AgentName)
class AgentNameAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "language", "updated"]


@admin.register(OrganizationName)
class OrganizationNameAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "language", "updated"]


@admin.register(PlaceName)
class PlaceNameAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "language", "updated"]


@admin.register(ParishName)
class ParishNameAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "language", "updated"]