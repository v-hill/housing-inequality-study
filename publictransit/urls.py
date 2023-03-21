from django.urls import path

from . import views

app_name = "publictransit"
urlpatterns = [
    path("main", views.main, name="main"),
    path("second", views.second, name="second"),
    path("search", views.search, name="search"),
]
