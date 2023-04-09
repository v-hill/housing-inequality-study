from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status

from publictransit.models import MapBoundary
from publictransit.overpass_api import OverpassClient


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


def boundary_overview(request: HttpRequest) -> HttpResponse:
    """Render the 'boundary_overview.html' template.

    This template is used to add new search boundaries.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered
        'boundary_overview.html' template.
    """
    return render(request, "boundary_overview.html")


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


def list_boundaries(request):
    map_boundaries = MapBoundary.objects.all().values()
    return JsonResponse(list(map_boundaries), safe=False)


@csrf_exempt
def check_boundary(request):
    if request.method == "GET":
        area_standard = request.GET.get("area_standard")
        area_value = request.GET.get("area_value")
        if not area_standard or not area_value:
            return JsonResponse({"error": "Value field is required"})
        elif area_standard == "Ref GSS":
            json_response = process_check_boundary_request(
                area_value, "Ref GSS"
            )
        elif area_standard == "ISO 3166-2":
            json_response = process_check_boundary_request(
                area_value, "ISO 3166-2"
            )
        return json_response


def process_check_boundary_request(area_value, test_area_standard):
    area_standard_map = {"ISO 3166-2": "ISO3166-2", "Ref GSS": "ref:gss"}
    query = (
        '[out:csv(::type,::id,"name")];\n'
        'area[name="England"]->.a;\n'
        f'rel(area.a)["{area_standard_map[test_area_standard]}"="{area_value}"];\n'
        "out;"
    )
    client = OverpassClient()
    response = client.get(query)
    if len(response) > 1:
        data = response[1]
        osm_id = data[1]
        name = data[2]
        success_text = (
            "Found relation: "
            f"<a href='https://www.openstreetmap.org/relation/{osm_id}'>{name}</a>"
        )
        json_response = JsonResponse(
            {"success": (success_text), "osm_id": osm_id}
        )
    else:
        json_response = JsonResponse(
            {
                "error": (
                    f"No boundary with {test_area_standard} value"
                    f" '{area_value}' on OpenStreetMap"
                )
            }
        )
    return json_response


@csrf_exempt
def add_boundary(request):
    if request.method == "POST":
        osm_id = request.POST.get("osm_id")
        if osm_id:
            query = f"[out:json];\nrelation({osm_id});\nout tags;"
            client = OverpassClient()
            response = client.get(query)
            tags = response["elements"][0]["tags"]
            admin_level = tags["admin_level"]
            iso31662 = tags["ISO3166-2"]
            name = tags["name"]
            ref_gss = tags["ref:gss"]
            map_boundary, created = MapBoundary.objects.get_or_create(
                admin_level=admin_level,
                iso31662=iso31662,
                name=name,
                osm_id=osm_id,
                ref_gss=ref_gss,
            )
            return JsonResponse({"status": "success", "name": name})
        else:
            return JsonResponse(
                {"status": "error", "message": "osm_id is missing"}
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Only POST requests are allowed"}
        )


@require_http_methods(["DELETE"])
def delete_boundary(request):
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


def boundary_details(request, boundary_id):
    boundary = get_object_or_404(MapBoundary, pk=boundary_id)
    return render(request, "boundary_details.html", {"boundary": boundary})


def get_osm_url(request):
    if request.method == "GET" and "osm_id" in request.GET:
        osm_id = request.GET["osm_id"]
        boundary = MapBoundary.objects.get(osm_id=osm_id)
        url = boundary.url
        print(url)
        return JsonResponse({"url": url})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


def train_stations(request, boundary_id):
    boundary = get_object_or_404(MapBoundary, pk=boundary_id)
    print(boundary.stations_list_query)
    return render(request, "train_stations.html", {"boundary": boundary})
