from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import status


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
