from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status


def main(request):
    return render(request, "main.html")


def second(request):
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
            "error": "Invalid lat or lng value."
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
            {"error": "Invalid lat or lng value."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    return JsonResponse({"lat": lat, "lng": lng})
