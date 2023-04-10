from django.contrib import admin

from .models import MapBoundary, Station


@admin.register(MapBoundary)
class MapBoundaryAdmin(admin.ModelAdmin):
    list_display = ("name", "admin_level", "iso31662", "osm_id", "ref_gss")
    list_filter = ("admin_level",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("name", "boundary", "osm_id", "isin_boundary")
    list_filter = ("boundary",)
    search_fields = ("name",)
    ordering = ("isin_boundary", "name")
