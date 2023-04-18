from django.urls import include, path
from rest_framework import routers

from . import views

app_name = "publictransit"
router = routers.DefaultRouter()
router.register(r"polygon", views.BoundaryPointViewSet)
router.register(r"map_boundaries", views.MapBoundaryViewSet)
router.register(r"stations", views.StationViewSet)

# URL patterns for HTML views
html_patterns = [
    path(
        "boundary_overview",
        views.BoundaryOverviewView.as_view(),
        name="boundary_overview",
    ),
    path(
        "boundary",
        views.BoundaryDetailsView.as_view(),
        name="boundary_details",
    ),
    path(
        "stations_map",
        views.StationsMapView.as_view(),
        name="stations_map",
    ),
]

# URL patterns for JSON API views
api_patterns = [
    path("", include(router.urls)),
    path(
        "check_boundary/",
        views.CheckBoundaryView.as_view(),
        name="check_boundary",
    ),
]

# Combined URL patterns
urlpatterns = html_patterns + api_patterns
