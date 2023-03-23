from django.urls import path

from . import views

app_name = "publictransit"
urlpatterns = [
    path("add_map_boundary", views.add_map_boundary, name="add_map_boundary"),
    path("boundaries", views.boundaries, name="boundaries"),
    path("delete_card", views.delete_card, name="delete_card"),
    path("main", views.main, name="main"),
    path("search", views.search, name="search"),
]
