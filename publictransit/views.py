from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from .models import Location


def index(request):
    return HttpResponse("Hello, world!")


def enter_locations(request):
    if request.method == "POST":
        location1 = request.POST["location1"]
        location2 = request.POST["location2"]
        Location.objects.create(location1=location1, location2=location2)
        return HttpResponseRedirect("/success/")
    else:
        return render(request, "enter_locations.html")
