from django.urls import include, path

from . import views

app_name = "publictransit"

# URL patterns for HTML views
html_patterns = [
    path(
        "boundary_overview", views.boundary_overview, name="boundary_overview"
    ),
    path(
        "boundary/<int:boundary_id>/",
        views.boundary_details,
        name="boundary_details",
    ),
    path("main", views.main, name="main"),
    path("stations_map", views.stations_map, name="stations_map"),
]

# URL patterns for JSON API views
api_patterns = [
    path("add_boundary", views.add_boundary, name="add_boundary"),
    path(
        "boundary/<int:boundary_id>/",
        include(
            [
                path(
                    "download_stations_data",
                    views.download_stations_data,
                    name="download_stations_data",
                ),
                path(
                    "remove_stations",
                    views.remove_stations,
                    name="remove_stations",
                ),
                path(
                    "stations_in_db",
                    views.stations_in_db,
                    name="stations_in_db",
                ),
            ]
        ),
    ),
    path("check_boundary", views.check_boundary, name="check_boundary"),
    path("delete_boundary", views.delete_boundary, name="delete_boundary"),
    path("get_osm_url", views.get_osm_url, name="get_osm_url"),
    path("list_boundaries", views.list_boundaries, name="list_boundaries"),
    path("main", views.main, name="main"),
    path("search", views.search, name="search"),
]

# Combined URL patterns
urlpatterns = html_patterns + api_patterns
