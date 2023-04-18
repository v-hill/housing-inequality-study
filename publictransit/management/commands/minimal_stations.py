import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from scipy.spatial import Voronoi

from publictransit.models import BoundaryPoint, MapBoundary, Station
from publictransit.utilities.boundary_tools import remove_irrelevant_stations
from publictransit.utilities.polygon_tools import generate_circle, to_utm


def snake_case(s):
    return s.lower().replace(" ", "_")


class Command(BaseCommand):
    help = (
        "Plots boundary points, stations, and Voronoi diagram for a given"
        " MapBoundary"
    )

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the MapBoundary")

    def handle(self, *args, **options):
        try:
            boundary = MapBoundary.objects.get(name=options["name"])
        except MapBoundary.DoesNotExist:
            self.stdout.write(
                self.style.ERROR("MapBoundary with given name does not exist")
            )
            return

        bp_vals = self.boundary_points_coords(boundary)
        stations_inside = self.inside_boundary_stations_coords(boundary)
        stations_outside = self.outside_boundary_stations_coords(boundary)
        voronoi_points = stations_inside + stations_outside

        circle_points = generate_circle(stations_outside)

        # Add the circle points to the points list
        voronoi_points = voronoi_points + circle_points

        vor = Voronoi(voronoi_points)
        relevant_stations_outside = remove_irrelevant_stations(
            bp_vals, stations_inside, stations_outside, vor
        )

        x_bp_vals, y_bp_vals = zip(*bp_vals)
        x_in_vals, y_in_vals = zip(*stations_inside)
        x_out_vals, y_out_vals = zip(*stations_outside)
        x_outer_bp_vals, y_outer_bp_vals = zip(*circle_points)
        fig, ax = plt.subplots(figsize=(8, 7))

        # Set the axis to be equal and square
        ax.axis("equal")

        ax.plot(x_bp_vals, y_bp_vals, c="black", label="Boundary")
        ax.scatter(
            x_in_vals, y_in_vals, c="blue", label="Inside boundary stations"
        )
        ax.scatter(
            x_out_vals, y_out_vals, c="red", label="Outside boundary stations"
        )
        # ax.scatter(
        #     x_outer_bp_vals, y_outer_bp_vals, c="orange", label="Outer boundary"
        # )

        # Create a scatter plot of the data
        x_relevant_stations_vals, y_relevant_stations_vals = zip(
            *relevant_stations_outside
        )
        plt.scatter(
            x_relevant_stations_vals,
            y_relevant_stations_vals,
            c="green",
            label="Outside stations to keep",
        )

        for simplex in vor.ridge_vertices:
            if -1 not in simplex:
                x = vor.vertices[simplex, 0]
                y = vor.vertices[simplex, 1]
                ax.plot(x, y, "k-", linewidth=0.5)

        # Set x and y limits to min and max values of station locations
        xmin = min(min(x_in_vals), min(x_out_vals))
        xmax = max(max(x_in_vals), max(x_out_vals))
        ymin = min(min(y_in_vals), min(y_out_vals))
        ymax = max(max(y_in_vals), max(y_out_vals))
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title(
            f"Boundary, stations, and Voronoi diagram for {boundary.name}"
        )
        ax.legend()

        outfile = f'{snake_case(options["name"])}.png'
        plt.show()
        # plt.savefig(outfile, dpi=200, bbox_inches="tight")

    def boundary_points_coords(self, boundary):
        boundary_points = BoundaryPoint.objects.filter(
            boundary=boundary
        ).order_by("order")
        coordinates = [
            [point.location.latitude, point.location.longitude]
            for point in boundary_points
        ]
        utm_coordinates = to_utm(coordinates)
        return utm_coordinates

    def inside_boundary_stations_coords(self, boundary):
        in_boundary_stations = Station.objects.filter(
            boundary=boundary, isin_boundary=True
        ).order_by("name")
        coordinates = [
            [station.location.latitude, station.location.longitude]
            for station in in_boundary_stations
        ]
        utm_coordinates = to_utm(coordinates)
        return utm_coordinates

    def outside_boundary_stations_coords(self, boundary):
        out_boundary_stations = Station.objects.filter(
            boundary=boundary, isin_boundary=False
        ).order_by("name")
        coordinates = [
            [station.location.latitude, station.location.longitude]
            for station in out_boundary_stations
        ]
        utm_coordinates = to_utm(coordinates)
        return utm_coordinates
