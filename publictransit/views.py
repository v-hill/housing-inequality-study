from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from publictransit import models
from publictransit.overpass_api import OverpassClient, get_boundary_check_query
from publictransit.utilities.boundary_tools import (
    build_polygon,
    get_boundary_coordinates

)
from publictransit.utilities.polygon_tools import (
    simplify_points,
    to_latlon,
    to_utm,
)

from .serializers import (
    BoundaryPointSerializer,
    CheckBoundarySerializer,
    MapBoundarySerializer,
    StationSerializer,
)


class MapBoundaryViewSet(viewsets.ModelViewSet):
    queryset = models.MapBoundary.objects.all()
    serializer_class = MapBoundarySerializer

    @action(detail=True, methods=["delete"])
    def delete_boundary(self, request, pk=None):
        try:
            boundary = self.get_object()
            boundary.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.MapBoundary.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"])
    def add_boundary(self, request):
        osm_id = request.data.get("osm_id")
        if osm_id:
            name = self.get_or_create_boundary(osm_id)
            return Response({"status": "success", "name": name})
        else:
            return Response(
                {"status": "error", "message": "osm_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def get_or_create_boundary(osm_id):
        query = f"[out:json];\nrelation({osm_id});\nout tags;"
        client = OverpassClient()
        response = client.get(query)
        tags = response["elements"][0]["tags"]
        admin_level = tags["admin_level"]
        iso31662 = tags["ISO3166-2"]
        name = tags["name"]
        ref_gss = tags["ref:gss"]
        map_boundary, _ = models.MapBoundary.objects.get_or_create(
            admin_level=admin_level,
            iso31662=iso31662,
            name=name,
            osm_id=osm_id,
            ref_gss=ref_gss,
        )
        return name


class StationViewSet(viewsets.ModelViewSet):
    queryset = models.Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self):
        boundary_id = self.request.query_params.get("boundary_id", None)
        if boundary_id is not None:
            queryset = models.Station.objects.filter(
                boundary_id=boundary_id
            ).order_by("name")
        else:
            # Return an empty queryset if no boundary_id is provided
            queryset = models.Station.objects.none()
        return queryset

    @action(detail=False, methods=["post"])
    def download_data(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            self.fetch_and_save_stations(boundary_id)
            self.fetch_and_save_nearby_stations(boundary_id)
            queryset = self.get_queryset().filter(boundary_id=boundary_id)
            serializer = self.get_serializer(queryset, many=True)
            return Response({"stations": serializer.data})
        else:
            return Response(
                {"error": "boundary_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def remove_data(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            queryset = self.get_queryset().filter(boundary_id=boundary_id)
            queryset.delete()
            serializer = self.get_serializer(queryset, many=True)
            return Response({"stations": serializer.data})
        else:
            return Response(
                {"error": "boundary_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def remove_irrelevant_stations(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            pass

    @staticmethod
    def fetch_and_save_stations(boundary_id):
        """Download station data from API and save it to the database."""
        # Get stations data from API
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        client = OverpassClient()
        response = client.get(boundary.stations_list_query)

        # Save stations data in Station model
        for station in response[1:]:
            name, osm_id, lat, lon = station
            location, _ = models.Location.objects.get_or_create(
                latitude=float(lat), longitude=float(lon)
            )
            boundary = models.MapBoundary.objects.get(pk=boundary_id)
            qs = models.Station.objects.filter(
                boundary=boundary, osm_id=int(osm_id)
            )
            if not qs.exists():
                models.Station.objects.create(
                    boundary=boundary,
                    location=location,
                    name=name,
                    osm_id=int(osm_id),
                    isin_boundary=True,
                )

    @staticmethod
    def fetch_and_save_nearby_stations(boundary_id):
        """Download station data from API and save it to the database."""
        # Get stations data from API
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        client = OverpassClient()
        response = client.get(boundary.stations_list_query_outside_boundary)

        # Save stations data in Station model
        for station in response[1:]:
            name, osm_id, lat, lon = station
            location, _ = models.Location.objects.get_or_create(
                latitude=float(lat), longitude=float(lon)
            )
            boundary = models.MapBoundary.objects.get(pk=boundary_id)
            qs = models.Station.objects.filter(
                boundary=boundary, osm_id=int(osm_id)
            )
            if not qs.exists():
                models.Station.objects.create(
                    boundary=boundary,
                    location=location,
                    name=name,
                    osm_id=int(osm_id),
                    isin_boundary=False,
                )


class CheckBoundaryView(APIView):
    def get(self, request):
        serializer = CheckBoundarySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        area_standard = serializer.validated_data["area_standard"]
        area_value = serializer.validated_data["area_value"]
        response = self.process_check_boundary_request(
            area_value, area_standard
        )
        json_response = JsonResponse(response)
        return json_response

    @staticmethod
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
            response = {"success": (success_text), "osm_id": osm_id}
        else:
            response = {
                "error": (
                    f"No boundary with {test_area_standard} value"
                    f" '{area_value}' on OpenStreetMap"
                )
            }
        return response


class BoundaryOverviewView(APIView):
    def get(self, request):
        return render(request, "boundary_overview.html")


class BoundaryDetailsView(APIView):
    def get(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        return render(request, "boundary_details.html", {"boundary": boundary})


class StationsMapView(APIView):
    def get(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        return render(request, "stations_map.html", {"boundary": boundary})


class BoundaryPointViewSet(viewsets.ModelViewSet):
    queryset = models.BoundaryPoint.objects.all()
    serializer_class = BoundaryPointSerializer

    def get_queryset(self):
        boundary_id = self.request.query_params.get("boundary_id", None)
        if boundary_id is not None:
            queryset = models.BoundaryPoint.objects.filter(
                boundary_id=boundary_id
            ).order_by("order")
        else:
            # Return an empty queryset if no boundary_id is provided
            queryset = models.BoundaryPoint.objects.none()
        return queryset

    @action(detail=False, methods=["get"])
    def count(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            num_nodes = (
                self.get_queryset().filter(boundary_id=boundary_id).count()
            )
            return Response({"num_nodes": num_nodes})
        else:
            return Response(
                {"error": "boundary_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["post"])
    def download_data(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            self.fetch_and_save_polygon(boundary_id)
            num_nodes = (
                self.get_queryset().filter(boundary_id=boundary_id).count()
            )
            return Response({"num_nodes": num_nodes})
        else:
            return Response(
                {"error": "boundary_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @staticmethod
    def fetch_and_save_polygon(boundary_id):
        """Download polygon data from API and save it to the database."""
        # Get stations data from API
        boundary = get_object_or_404(models.MapBoundary, pk=boundary_id)
        client = OverpassClient()
        response = client.get(boundary.polygon_query)

        # Convert response coordinates into a continuous polygon
        boundary_coordinates = get_boundary_coordinates(response)
        polygon = build_polygon(boundary_coordinates)
        print(f"Num coordinates: {len(polygon)}")

        # Convert the geographic coordinates to UTM coordinates
        utm_points = to_utm(polygon)

        simplified_polygon = simplify_points(utm_points, epsilon=1)

        # Convert the simplified UTM coordinates back to geographic coordinates
        simplified_points = to_latlon(simplified_polygon)
        print(f"Num simplified coordinates: {len(simplified_points)}")

        # Remove all existing points for the given boundary
        existing_qs = models.BoundaryPoint.objects.filter(boundary=boundary)
        existing_qs.delete()
        for i, (lat, lon) in enumerate(simplified_points):
            # Create a new Location object and save it
            location, _ = models.Location.objects.get_or_create(
                latitude=lat, longitude=lon
            )
            location.save()

            # Create a new BoundaryPoint object and save it
            boundary_point = models.BoundaryPoint(
                boundary=boundary, location=location, order=i
            )
            boundary_point.save()

    @action(detail=False, methods=["post"])
    def remove_data(self, request):
        boundary_id = request.query_params.get("boundary_id", None)
        if boundary_id:
            queryset = self.get_queryset().filter(boundary_id=boundary_id)
            queryset.delete()
            num_nodes = (
                self.get_queryset().filter(boundary_id=boundary_id).count()
            )
            return Response({"num_nodes": num_nodes})
        else:
            return Response(
                {"error": "boundary_id is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )
