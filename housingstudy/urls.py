from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("publictransit/", include("publictransit.urls")),
    path("admin/", admin.site.urls),
]
