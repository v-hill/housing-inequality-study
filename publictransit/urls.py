from django.urls import path

from . import views

urlpatterns = [
    path("home", views.index, name="index"),
    path("enter_locations", views.enter_locations, name="enter_locations"),
]
