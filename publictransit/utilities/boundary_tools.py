import sys

import matplotlib.pyplot as plt

from publictransit.utilities.polygon_tools import (
    voronoi_cell_intersect_boundary,
)


def get_boundary_coordinates(data):
    """Extract boundary coordinates from OpenStreetMap JSON data.

    Parameters
    ----------
    data : dict
        OpenStreetMap JSON data containing node and way elements.

    Returns
    -------
    dict
        Dictionary of way IDs and their corresponding ordered coordinates
        (lat, lon).
    """
    coordinates = {}

    # Get all way elements from the JSON data
    ways = [
        element for element in data["elements"] if element["type"] == "way"
    ]

    # Create a dictionary with way IDs as keys and their node IDs as values
    way_nodes = {way["id"]: way["nodes"] for way in ways}

    # Get all node elements from the JSON data
    nodes = [
        element for element in data["elements"] if element["type"] == "node"
    ]

    # Create a dictionary with node IDs as keys and their coordinates as values
    node_coordinates = {
        node["id"]: (node["lat"], node["lon"]) for node in nodes
    }

    # Find the relation element
    relation = next(
        (
            element
            for element in data["elements"]
            if element["type"] == "relation"
        ),
        None,
    )

    if not relation:
        print("No relation found.")
        return coordinates

    # Get the outer way members from the relation
    outer_way_members = [
        member
        for member in relation["members"]
        if member["type"] == "way" and member["role"] == "outer"
    ]

    # Get the coordinates from the ordered way IDs
    for way in outer_way_members:
        way_id = way["ref"]
        current_way_nodes = way_nodes[way_id]
        coordinates[way_id] = [
            node_coordinates[node_id] for node_id in current_way_nodes
        ]
    return coordinates


def distance(coord1, coord2):
    """Calculate the squared Euclidean distance between two coordinates.

    Parameters
    ----------
    coord1 : tuple of float
        First coordinate (lat1, lon1).
    coord2 : tuple of float
        Second coordinate (lat2, lon2).

    Returns
    -------
    float
        Squared Euclidean distance between the two coordinates.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    return (lat1 - lat2) ** 2 + (lon1 - lon2) ** 2


def find_best_matching_way(way_coords_dict, last_coord):
    """Find the best matching way based on the distance to the last coordinate.

    Parameters
    ----------
    way_coords_dict : dict
        Dictionary of way IDs and their corresponding ordered coordinates
        (lat, lon).
    last_coord : tuple of float
        Last coordinate (lat, lon) to find the best matching way.

    Returns
    -------
    tuple
        A tuple containing the best matching way ID and a boolean indicating
        if the best match starts with the first coordinate.
    """
    best_match_way_id = None
    best_match_distance = sys.float_info.max
    best_match_start = None

    for way_id, coords in way_coords_dict.items():
        start_distance = distance(last_coord, coords[0])
        end_distance = distance(last_coord, coords[-1])

        if start_distance < best_match_distance:
            best_match_distance = start_distance
            best_match_way_id = way_id
            best_match_start = True

        if end_distance < best_match_distance:
            best_match_distance = end_distance
            best_match_way_id = way_id
            best_match_start = False
    return best_match_way_id, best_match_start


def remove_identical_points(points):
    """Deduplicate a list of points.

    Remove identical points in a list of (latitude, longitude) tuples, keeping
    the start and end points intact.

    Parameters
    ----------
    points : list of tuples
        A list of (latitude, longitude) tuples representing the polygon.

    Returns
    -------
    list of tuples
        The list of (latitude, longitude) tuples with identical points removed.
    """
    if not points:
        return points

    unique_points = [points[0]]

    for i in range(1, len(points) - 1):
        if points[i] != unique_points[-1]:
            unique_points.append(points[i])

    # Append the end point if it's not already the last point
    if unique_points[-1] != points[-1] and points[-1] != points[0]:
        unique_points.append(points[-1])
    return unique_points


def build_polygon(boundary_coordinates):
    """Build a polygon from the given boundary coordinates.

    The build_polygon function constructs a polygon from the given boundary
    coordinates, which are provided as a dictionary of way IDs and their
    corresponding ordered coordinates. It returns a list of ordered latitude
    and longitude coordinates that form the polygon.

    Parameters
    ----------
    boundary_coordinates : dict
        Dictionary of way IDs and their corresponding ordered coordinates
        (lat, lon).

    Returns
    -------
    list of tuple
        List of ordered latitude and longitude coordinates forming a polygon.
    """
    shape_coords = []
    way_coords_dict = boundary_coordinates.copy()

    # Start with the first way
    first_way_id = next(iter(way_coords_dict))
    shape_coords.extend(way_coords_dict[first_way_id])
    del way_coords_dict[first_way_id]

    while way_coords_dict:
        last_coord = shape_coords[-1]
        best_match_way_id, best_match_start = find_best_matching_way(
            way_coords_dict, last_coord
        )

        if best_match_way_id is not None:
            matched_coords = way_coords_dict[best_match_way_id]
            if not best_match_start:
                matched_coords = matched_coords[::-1]
            shape_coords.extend(matched_coords)
            del way_coords_dict[best_match_way_id]
        else:
            break
    shape_coords = remove_identical_points(shape_coords)
    return shape_coords


def plot_boundary_coordinates(coordinates_dict):
    plt.figure(figsize=(10, 10))

    for way_id, coordinates in coordinates_dict.items():
        lats, lons = zip(*coordinates)
        plt.plot(
            lons,
            lats,
            marker="o",
            markersize=2,
            linewidth=1,
            label=f"Way {way_id}",
        )

    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.title("Boundary Coordinates")
    plt.grid(True)
    plt.show()


def remove_irrelevant_stations(
    boundary, stations_inside, stations_outside, vor
):
    relevant_stations_outside = []
    for i, station in enumerate(stations_outside):
        station_index = len(stations_inside) + i
        if voronoi_cell_intersect_boundary(vor, boundary, station_index):
            relevant_stations_outside.append(station)
    return relevant_stations_outside
