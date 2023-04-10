from django.urls import path

from . import views

app_name = "publictransit"
urlpatterns = [
    path("add_boundary", views.add_boundary, name="add_boundary"),
    path(
        "boundary_overview", views.boundary_overview, name="boundary_overview"
    ),
    path(
        "boundary/<int:boundary_id>/stations_data_exists",
        views.stations_data_exists,
        name="stations_data_exists",
    ),
    path(
        "boundary/<int:boundary_id>/remove_stations",
        views.remove_stations,
        name="remove_stations",
    ),
    path(
        "boundary/<int:boundary_id>/download_stations_data",
        views.download_stations_data,
        name="download_stations_data",
    ),
    path(
        "boundary/<int:boundary_id>/",
        views.boundary_details,
        name="boundary_details",
    ),
    path("check_boundary", views.check_boundary, name="check_boundary"),
    path("delete_boundary", views.delete_boundary, name="delete_boundary"),
    path("get_osm_url", views.get_osm_url, name="get_osm_url"),
    path("list_boundaries", views.list_boundaries, name="list_boundaries"),
    path("main", views.main, name="main"),
    path("search", views.search, name="search"),
]
