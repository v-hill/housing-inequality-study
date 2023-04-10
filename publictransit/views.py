import json

from django.http import HttpRequest, HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import status

from publictransit import models
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
    map_boundaries = models.MapBoundary.objects.all().values()
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


def get_boundary_check_query(area_value, test_area_standard):
    area_dict = {"ISO 3166-2": "ISO3166-2", "Ref GSS": "ref:gss"}
    query = (
        '[out:csv(::type,::id,"name")];\n'
        'area[name="England"]->.a;\n'
        f'rel(area.a)["{area_dict[test_area_standard]}"="{area_value}"];\n'
        "out;"
    )
    return query


def process_check_boundary_request(area_value, test_area_standard):
    query = get_boundary_check_query(area_value, test_area_standard)
    client = OverpassClient()
    response = client.get(query)
    if len(response) > 1:
        data = response[1]
        osm_id = data[1]
        name = data[2]
        success_text = (
            "Found relation: <a"
            f" href='https://www.openstreetmap.org/relation/{osm_id}'"
            f" target='_blank'>{name}</a>"
        )
        json_response = JsonResponse(
            {"success": (success_text), "osm_id": osm_id}
        )
    else:
        no_boundary_response = {
            "error": (
                f"No boundary with {test_area_standard} value"
                f" '{area_value}' on OpenStreetMap"
            )
        }
        json_response = JsonResponse(no_boundary_response)
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
            map_boundary, created = models.MapBoundary.objects.get_or_create(
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
            boundary = models.MapBoundary.objects.get(id=boundary_id)
            boundary.delete()
        except:
            pass
        print("deleting")
    return JsonResponse({}, safe=False)


def boundary_details(request, boundary_id):
    boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
    return render(request, "boundary_details.html", {"boundary": boundary})


def get_osm_url(request):
    if request.method == "GET" and "osm_id" in request.GET:
        osm_id = request.GET["osm_id"]
        boundary = models.MapBoundary.objects.get(osm_id=osm_id)
        url = boundary.url
        print(url)
        return JsonResponse({"url": url})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


@csrf_exempt
def get_station_data(request, boundary_id):
    """Get info for train stations inside of a boundary.

    This Django view retrieves data about train stations within a specified
    boundary using the OpenStreetMap Overpass API. The data is fetched via POST
    request and returned as a JSON response with a sorted list of train
    stations by name.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request containing method type (POST).
    boundary_id : int
        The primary key (ID) of the MapBoundary instance to fetch train
        stations data for.

    Returns
    -------
    JsonResponse
        A JsonResponse object containing either the list of train stations
        sorted by name or an error message if the request method is invalid or
        a required parameter is missing.
    """
    if request.method == "POST":
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        client = OverpassClient()
        response = client.get(boundary.stations_list_query)

        # Sort each list (excluding header) by name in ascending order
        sorted_stations = sorted(response[1:], key=lambda x: x[0])
        return JsonResponse({"stations": sorted_stations})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


def fetch_and_save_stations(request, boundary_id):
    """Download station data if needed, else return stations from database.

    Call the get_station_data method to get the stations data from the API and
    save the records into the Station model.

    Parameters
    ----------
    request : HttpRequest
        The incoming HTTP request containing method type (POST).
    boundary_id : int
        The primary key (ID) of the MapBoundary instance to fetch train
        stations data for.

    Returns
    -------
    JsonResponse
        A JsonResponse object containing either the list of train stations
        saved in the Station model or an error message if the request method is
        invalid or a required parameter is missing.
    """
    if request.method == "POST":
        # Get stations data from API
        station_response = get_station_data(request, boundary_id)
        stations_data = json.loads(station_response.content).get(
            "stations", []
        )
        # Save stations data in Station model
        for station in stations_data:
            name, osm_id, lat, lon = station
            location = models.Location.objects.create(
                latitude=float(lat), longitude=float(lon)
            )
            boundary = models.MapBoundary.objects.get(pk=boundary_id)
            models.Station.objects.create(
                boundary=boundary,
                location=location,
                name=name,
                osm_id=int(osm_id),
            )
        stations_data = serialise_stations_data(boundary_id)
        return JsonResponse({"stations": stations_data})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


def serialise_stations_data(boundary_id):
    stations = models.Station.objects.filter(boundary_id=boundary_id)
    stations_data = [
        {
            "name": station.name,
            "osm_id": station.osm_id,
            "location": {
                "latitude": station.location.latitude,
                "longitude": station.location.longitude,
            },
        }
        for station in stations
    ]
    return stations_data


@csrf_exempt
def remove_stations(request, boundary_id):
    if request.method == "POST":
        models.Station.objects.filter(boundary_id=boundary_id).delete()
        stations_data = serialise_stations_data(boundary_id)
        return JsonResponse({"stations": stations_data})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


@csrf_exempt
def download_stations_data(request, boundary_id):
    return fetch_and_save_stations(request, boundary_id)


@csrf_exempt
def stations_in_db(request, boundary_id):
    if request.method == "GET":
        stations_data = serialise_stations_data(boundary_id)
        return JsonResponse({"stations": stations_data})
    else:
        return JsonResponse(
            {"error": "Invalid request method or missing parameter."}
        )


def stations_map(request):
    return render(request, "stations_map.html")
