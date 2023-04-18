import json

from django.core.management.base import BaseCommand

from publictransit.utilities.boundary_tools import (
    build_polygon,
    get_boundary_coordinates,
    plot_boundary_coordinates,
)
from publictransit.utilities.polygon_tools import simplify_points


class Command(BaseCommand):
    help = "Test out algorithms for building boundary polygon"

    def handle(self, *args, **options):
        # Load GeoJSON file with explicit encoding
        with open("response.json", encoding="utf-8") as f:
            data = json.load(f)
        boundary_coordinates = get_boundary_coordinates(data)
        polygon = build_polygon(boundary_coordinates)
        simplified_polygon = simplify_points(polygon, epsilon=1)
        print(f"Num coordinates: {len(polygon)}")
        print(f"Num simplified coordinates: {len(simplified_polygon)}")
        plot_boundary_coordinates(
            {
                "Shape": polygon,
                "Shape New": simplified_polygon,
            }
        )
