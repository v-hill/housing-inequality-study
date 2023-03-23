from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from rest_framework import status

from publictransit.models import MapBoundary


def main(request: HttpRequest) -> HttpResponse:
    """Render the 'main.html' template.

    The main page displays a map with a latitude and longitude input. When the
    'Search' button is pressed a marker is added to the map at that point and
    the map recenters to that point.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered 'main.html' template.
    """
    return render(request, "main.html")


def second(request: HttpRequest) -> HttpResponse:
    """Render the 'second.html' template.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered 'second.html' template.
    """
    return render(request, "second.html")


def search(request):
    """Search for a location based on coordinates provided in the GET request.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object containing the GET parameters.

    Returns
    -------
    JsonResponse
        If the lat and lng values are valid, a JSON response containing the
        latitude and longitude values from the GET request is returned. The
        response has the following format:

        {
            "lat": float,   # The latitude value.
            "lng": float,   # The longitude value.
        }

        If either lat or lng value cannot be coerced into a floating-point
        number, a JSON error response is returned with a status code of 400
        (Bad Request) and the following format:

        {
            "error": "Invalid latitude or longitude value."
        }

        Note that the error response is returned if either lat or lng value is
        invalid. Both values must be valid for a successful response.
    """
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return JsonResponse(
            {"error": "Invalid latitude or longitude value."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return JsonResponse({"lat": lat, "lng": lng})


def add_map_boundary(request):
    if request.method == "POST":
        admin_level = request.POST.get("admin_level")
        iso31662 = request.POST.get("iso31662")
        name = request.POST.get("name")
        osm_id = request.POST.get("osm_id")
        ref_gss = request.POST.get("ref_gss")

        # Do any necessary pre-processing here

        map_boundary = MapBoundary(
            admin_level=admin_level,
            iso31662=iso31662,
            name=name,
            osm_id=osm_id,
            ref_gss=ref_gss,
        )
        map_boundary.save()

    return render(request, "map_boundary_form.html")


def boundaries(request):
    map_boundaries = MapBoundary.objects.all().values()
    return JsonResponse(list(map_boundaries), safe=False)


@require_http_methods(["DELETE"])
def delete_card(request):
    if request.method == "DELETE":
        delete_data = QueryDict(request.body)
        boundary_id = delete_data.get("boundary_id")
        try:
            boundary = MapBoundary.objects.get(id=boundary_id)
            boundary.delete()
        except:
            pass
        print("deleting")
    return JsonResponse({}, safe=False)
