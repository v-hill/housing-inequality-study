from django.contrib import admin
from django.urls import include, path

from . import views

app_name = "housingstudy"

urlpatterns = [
    path("", views.home, name="home"),
    path("publictransit/", include("publictransit.urls")),
    path("admin/", admin.site.urls),
]
