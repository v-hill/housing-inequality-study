from django.urls import path

from . import views

app_name = "publictransit"
urlpatterns = [
    path("add_boundary", views.add_boundary, name="add_boundary"),
    path("boundary_page", views.boundary_page, name="boundary_page"),
    path("check_boundary", views.check_boundary, name="check_boundary"),
    path("delete_boundary", views.delete_boundary, name="delete_boundary"),
    path("list_boundaries", views.list_boundaries, name="list_boundaries"),
    path("main", views.main, name="main"),
    path("search", views.search, name="search"),
]
