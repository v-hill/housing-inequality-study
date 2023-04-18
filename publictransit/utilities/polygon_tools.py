import math
from typing import List, Tuple

import numpy as np
from pyproj import Transformer


def to_utm(points):
    """Convert a list of (latitude, longitude) tuples to UTM coordinates.

    Parameters
    ----------
    points : list of tuples
        A list of (latitude, longitude) tuples.

    Returns
    -------
    list of tuples
        A list of (Easting, Northing) tuples.
    """
    # Create a pyproj transformer object to convert between WGS84 (lat/lon)
    # and UTM coordinates
    transformer = Transformer.from_crs(
        "EPSG:4326", "EPSG:32630"
    )  # WGS84 to UTM Zone 30N

    # Convert the latitude and longitude to UTM coordinates
    return [transformer.transform(point[0], point[1]) for point in points]


def to_latlon(utm_points):
    """
    Convert a list of UTM coordinates to (latitude, longitude) tuples.

    Parameters
    ----------
    utm_points : list of tuples
        A list of (Easting, Northing) tuples.

    Returns
    -------
    list of tuples
        A list of (latitude, longitude) tuples.
    """
    # Create a pyproj transformer object to convert between UTM coordinates and
    #  WGS84 (lat/lon)
    transformer = Transformer.from_crs(
        "EPSG:32630", "EPSG:4326"
    )  # UTM Zone 30N to WGS84

    # Convert the UTM coordinates to latitude and longitude
    return [transformer.transform(point[0], point[1]) for point in utm_points]


def point_line_distance(
    point: Tuple[float, float],
    line_start: Tuple[float, float],
    line_end: Tuple[float, float],
) -> float:
    """Calculate the perpendicular distance from a point to a line segment.

    Parameters
    ----------
    point : tuple of float
        Latitude and longitude coordinates of the point (lat, lon).
    line_start : tuple of float
        Latitude and longitude coordinates of the line start point (lat, lon).
    line_end : tuple of float
        Latitude and longitude coordinates of the line end point (lat, lon).

    Returns
    -------
    float
        Perpendicular distance from the point to the line segment.
    """
    num = abs(
        (line_end[1] - line_start[1]) * point[0]
        - (line_end[0] - line_start[0]) * point[1]
        + line_end[0] * line_start[1]
        - line_end[1] * line_start[0]
    )
    den = math.sqrt(
        (line_end[1] - line_start[1]) ** 2 + (line_end[0] - line_start[0]) ** 2
    )
    distance = num / den
    return distance


def ramer_douglas_peucker(
    points: List[Tuple[float, float]], epsilon: float
) -> List[Tuple[float, float]]:
    """Simplify a list of points using the Ramer-Douglas-Peucker algorithm.

    Parameters
    ----------
    points : list of tuple
        List of tuples containing latitude and longitude coordinates
        (lat, lon).
    epsilon : float
        Tolerance value that determines the minimum distance a point must be
        from a line segment to be retained.

    Returns
    -------
    list of tuple
        Simplified list of latitude and longitude points.
    """
    if len(points) < 3:
        return points

    max_distance = 0.0
    index = 0

    for i in range(1, len(points) - 1):
        distance = point_line_distance(points[i], points[0], points[-1])
        if distance > max_distance:
            max_distance = distance
            index = i

    if max_distance > epsilon:
        left_points = ramer_douglas_peucker(points[: index + 1], epsilon)
        right_points = ramer_douglas_peucker(points[index:], epsilon)

        return left_points[:-1] + right_points
    else:
        return [points[0], points[-1]]


def simplify_points(points, epsilon):
    """
    Simplify a list of points using the Ramer-Douglas-Peucker algorithm.

    The function takes a list of latitude and longitude points and simplifies
    them by retaining only the significant points that contribute to the
    overall shape of the polygon. The level of simplification is controlled by
    the distance threshold parameter 'epsilon'.

    Parameters
    ----------
    points : list of tuple
        List of tuples containing latitude and longitude coordinates
        (lat, lon).
    epsilon : float
        The distance threshold for removing points.

    Returns
    -------
    list of tuple
        Simplified list of latitude and longitude points.

    Notes
    -----
    The distance_threshold is converted to tolerance (in degrees) for use
    within the Ramer-Douglas-Peucker algorithm. The conversion factor is
    approximately 111.32 * 1000.
    """

    if not points:
        return points

    simplified_points = ramer_douglas_peucker(points, epsilon)

    # Ensure the polygon is closed
    if simplified_points[0] != simplified_points[-1]:
        simplified_points.append(simplified_points[0])

    return simplified_points


def generate_circle(points, num_points=64, radius_multiplier=1.5):
    # Convert the input list of points to a numpy array
    points = np.array(points)

    # Calculate the center of the circle
    max_x, max_y = np.max(points, axis=0)
    min_x, min_y = np.min(points, axis=0)
    center = np.array([(max_x + min_x) / 2, (max_y + min_y) / 2])

    # Calculate the radius of the circle
    radius = np.max(np.sqrt(np.sum((points - center) ** 2, axis=1)))

    radius *= radius_multiplier

    # Generate 64 points around the circumference of the circle
    angles = np.linspace(0, 2 * np.pi, num_points)
    circle_points = np.zeros((num_points, 2))
    circle_points[:, 0] = center[0] + radius * np.cos(angles)
    circle_points[:, 1] = center[1] + radius * np.sin(angles)

    # Convert the generated points back to a list and return the result
    return circle_points.tolist()


def ccw(A, B, C):
    return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])


def edge_intersection(A, B, C, D):
    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)


def voronoi_cell_intersect_boundary(voronoi, boundary, index):
    cell_region = voronoi.regions[voronoi.point_region[index]]
    if -1 in cell_region:
        return True
    cell_points = [
        voronoi.vertices[vertex_index] for vertex_index in cell_region
    ]

    cell_edges = [
        (cell_points[i], cell_points[(i + 1) % len(cell_points)])
        for i in range(len(cell_points))
    ]
    boundary_edges = [
        (boundary[i], boundary[(i + 1) % len(boundary)])
        for i in range(len(boundary))
    ]

    for cell_edge in cell_edges:
        for boundary_edge in boundary_edges:
            if edge_intersection(
                cell_edge[0], cell_edge[1], boundary_edge[0], boundary_edge[1]
            ):
                return True
    return False
