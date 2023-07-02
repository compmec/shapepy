"""
This modules contains a powerful class called JordanCurve which
is in fact, stores a list of spline-curves.
"""

from typing import Tuple

import numpy as np
from compmec.nurbs import GeneratorKnotVector, SplineCurve


class JordanCurve:
    """
    Jordan Curve is an arbitrary closed curve which doesn't intersect itself.
    It stores a list of 'segments': Each 'segment' is a lambda function.
    The standard is to receive a list of points
    """

    @staticmethod
    def init_from_points(vertices: np.ndarray):
        """
        Given a list of points, this function creates a polygon which
        vertices are `vertices`.
        Each segment is straight.
        """
        segments = []
        knotvector = GeneratorKnotVector.bezier(1)
        for ctrlpoints in zip(vertices[:-1], vertices[1:]):
            splinecurve = SplineCurve(knotvector, ctrlpoints)
            segments.append(splinecurve)
        return JordanCurve(segments)

    def __init__(self, segments: Tuple[SplineCurve]):
        self.segments = segments

    def __eq__(self, other):
        if len(self.segments) != len(other.segments):
            return False
        nsegmentsother = len(other.segments)
        for i in range(nsegmentsother):
            if other.segments[0] == self.segments[0]:
                break
            other.roll()
        else:
            return False
        for seg1, seg2 in zip(self, other):
            if seg1 != seg2:
                return False
        return True

    def __ne__(self, other):
        return not self == other

    def __neg__(self):
        raise NotImplementedError

    def __iter__(self):
        for segment in self.segments:
            yield segment

    def roll(self, times: int = 1):
        """
        Rolls the list of segments:
        times = 1: [A, B, C, D] -> [B, C, D, E]
        """
        self.segments = self.segments[times:] + self.segments[:times]

    def move(self, horizontal: float = 0, vertical: float = 0):
        """
        Move all the curve by an amount of (x, y)
        Example: move(1, 2)
            (0, 0) becomes (1, 2)
            (1, 2) becomes (2, 4)
            (1, 0) becomes (2, 2)
        """
        for segment in self:
            segment.ctrlpoints[:, 0] += horizontal
            segment.ctrlpoints[:, 1] += vertical
        return self

    def rotate_radians(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in radians
        Example: rotate(pi/2)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        cossinus, sinus = np.cos(angle), np.sin(angle)
        rotation_matrix = cossinus * np.eye(2)
        rotation_matrix[0, 1] = -sinus
        rotation_matrix[1, 0] = sinus
        for segment in self:
            for i, point in enumerate(segment.ctrlpoints):
                segment.ctrlpoints[i] = rotation_matrix @ point
        return self

    def rotate_degrees(self, angle: float):
        """
        Rotates counter-clockwise by an amount of 'angle' in degrees
        Example: rotate(90)
            (1, 0) becomes (0, 1)
            (2, 3) becomes (-3, 2)
        """
        return self.rotate_radians(np.pi * angle / 180)

    def scale(self, horizontal: float = 1, vertical: float = 1):
        """
        Scales the current curve by 'x' in x-direction and 'y' in y-direction
        Example: scale(1, 2)
            (1, 0) becomes (1, 0)
            (1, 3) becomes (1, 6)
        """
        for segment in self:
            segment.ctrlpoints[:, 0] *= horizontal
            segment.ctrlpoints[:, 1] *= vertical
        return self

    def invert(self):
        """
        Inverts the orientation of the jordan curve
        """
        self.segments = self.segments[::-1]
        for segment in self:
            segment.ctrlpoints = segment.ctrlpoints[::-1]
        return self

    def deepcopy(self):
        """
        Creates a deep copy of all internal objects
        """
        newsegments = []
        for segment in self:
            ctrlpoints = np.copy(segment.ctrlpoints)
            knotvector = np.copy(segment.knotvector)
            ctrlpoints = np.array(ctrlpoints, dtype="float64")
            newsegment = SplineCurve(knotvector, ctrlpoints)
            newsegments.append(newsegment)
        return self.__class__(newsegments)

    def polygon_points(self, ndiv: int = 1):
        """
        Discretize each segment of the curve and transform it into a polygon
        Result shape is ndiv * len(curve.segments) + 1
        The last point is equal to the first one
        """
        points = np.zeros((ndiv * len(self.segments) + 1, 2))
        tsample = np.linspace(0, 1, ndiv, endpoint=False)
        for i, segment in enumerate(self):
            lower = i * ndiv
            upper = (i + 1) * ndiv
            points[lower:upper] = segment(tsample)
        points[-1] = points[0]
        return points

    def contains_point(self, point: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve contains the specified point
        This function displaces all the points, turning each desired point
        in the origin, and then verifies if the polygon contains the origin
        """
        point = np.array(point)
        displaced_vertices = self.polygon_points()
        displaced_vertices[:, 0] -= point[0]
        displaced_vertices[:, 1] -= point[1]
        if is_origin_in_boundary(displaced_vertices):
            return False
        return is_origin_inside_polygon(displaced_vertices)

    def contains_points(self, points: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve contains all the points
        """
        displaced_vertices = self.polygon_points()
        for point in points:
            displaced_vertices[:, 0] -= point[0]
            displaced_vertices[:, 1] -= point[1]
            if is_origin_in_boundary(displaced_vertices):
                return False
            if not is_origin_inside_polygon(displaced_vertices):
                return False
            displaced_vertices[:, 0] += point[0]
            displaced_vertices[:, 1] += point[1]
        return True

    def omits_point(self, point: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve contains the specified point
        This function displaces all the points, turning each desired point
        in the origin, and then verifies if the polygon contains the origin
        """
        point = np.array(point)
        displaced_vertices = self.polygon_points()
        displaced_vertices[:, 0] -= point[0]
        displaced_vertices[:, 1] -= point[1]
        if is_origin_in_boundary(displaced_vertices):
            return False
        return not is_origin_inside_polygon(displaced_vertices)

    def omits_points(self, points: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve omits all the points
        """
        displaced_vertices = self.polygon_points()
        for point in points:
            displaced_vertices[:, 0] -= point[0]
            displaced_vertices[:, 1] -= point[1]
            if is_origin_in_boundary(displaced_vertices):
                return False
            if is_origin_inside_polygon(displaced_vertices):
                return False
            displaced_vertices[:, 0] += point[0]
            displaced_vertices[:, 1] += point[1]
        return True

    def intersects_point(self, point: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve omits all the points
        """
        point = np.array(point)
        displaced_vertices = self.polygon_points()
        displaced_vertices[:, 0] -= point[0]
        displaced_vertices[:, 1] -= point[1]
        return is_origin_in_boundary(displaced_vertices)

    def intersects_points(self, points: np.ndarray) -> bool:
        """
        Verifies if the current jordan curve omits all the points
        """
        displaced_vertices = self.polygon_points()
        for point in points:
            displaced_vertices[:, 0] -= point[0]
            displaced_vertices[:, 1] -= point[1]
            if is_origin_in_boundary(displaced_vertices):
                return True
            displaced_vertices[:, 0] += point[0]
            displaced_vertices[:, 1] += point[1]
        return False

    def contains(self, other) -> bool:
        """
        Verifies if the current jordan curve contains the object
        The object can be
            * a point
            * a set of points
            * another jordan curve
        If the jordan curve is negative, it switches the interior
        and exterior part of a positive jordan curve
        """
        if isinstance(other, JordanCurve):
            other = other.polygon_points()
        other = np.array(other)
        if other.ndim == 1:
            return self.contains_point(other)
        return self.contains_points(other)

    def omits(self, other) -> bool:
        """
        Verifies if the object is outside the current jordan curve
        The object can be
            * a point
            * a set of points
            * another jordan curve
        If the jordan curve is negative, it switches the interior
        and exterior part of a positive jordan curve
        """
        if isinstance(other, JordanCurve):
            other = other.polygon_points()
        other = np.array(other)
        if other.ndim == 1:
            return self.omits_point(other)
        return self.omits_points(other)

    def intersects(self, other) -> bool:
        """
        Verifies if the object  intersects the current jordan curve
        The object can be
            * a point
            * a set of points
            * another jordan curve
        """
        if isinstance(other, JordanCurve):
            other = other.polygon_points()
        other = np.array(other)
        if other.ndim == 1:
            return self.intersects_point(other)
        return self.intersects_points(other)


def find_line_equation(point0: Tuple, point1: Tuple) -> Tuple:
    """
    Given two points, like A = (xA, yA) and B = (xB, yB)
    This functions finds the coefficients (a, b, c) such
        a * xA + b * yA + c = 0
        a * xB + b * yB + c = 0
    """
    coefa = point1[1] - point0[1]
    coefb = point0[0] - point1[0]
    coefc = point0[1] * point1[0] - point0[0] * point1[1]
    return coefa, coefb, coefc


def get_angle_ray(vertices: np.ndarray) -> Tuple[float]:
    """
    Given a polygon, it computes the good angle for ray-tracing.
    The ray-tracing is used to decide if a point is inside a polygon.
    This function computes the forbiden angles, and sets the ray's
    angle such stays away for all these angles.
    Forbiden means: The ray does't intersect any vertex
    """
    forbid_angles = [0, np.pi]
    for vertex in vertices:
        # Loop to be sure the ray doesn't pass thought a vertices
        angle = np.arctan2(vertex[1], vertex[0]) % np.pi
        forbid_angles.append(angle)

    # Find a good angle for ray tracing
    forbid_angles = np.array(forbid_angles)
    forbid_angles.sort()
    diffangles = forbid_angles[1:] - forbid_angles[:-1]
    index = np.where(diffangles == np.max(diffangles))[0]
    index = index[np.random.randint(len(index))]
    rayangle = 0.5 * (forbid_angles[index] + forbid_angles[index + 1])
    return rayangle


def ray_pass_through_segment(angle: float, vert0: Tuple, vert1: Tuple) -> bool:
    """
    Given two vertex, called vertex0 = (x0, y0) and vertex1 = (x1, y1)
    This function returns if the ray that starts at (0, 0) and goes to
    infinity touches the segment (x0, y0) -> (x1, y1)
    The ray's equation is:
        r(u) = (u*cos(angle), u*sin(angle))
    The line's equation is:
        l(t) = ((x0+x1)/2 + t*(x1-x0)/2,
                (y0+y1)/2 + t*(y1+y0)/2)
    There's an intersection point only if:
        * Line l(t) is not parallel to the ray r(u)
        * Parameter u is positive (ray can't go other direction)
        * Parameter t is between (-1, 1)
    """
    cosray, sinray = np.cos(angle), np.sin(angle)
    meanx = vert1[0] + vert0[0]
    meany = vert1[1] + vert0[1]
    deltax = vert1[0] - vert0[0]
    deltay = vert1[1] - vert0[1]
    denomin = deltay * cosray - deltax * sinray
    if denomin == 0:  # Parallel line
        return False
    tparam = (meanx * sinray - meany * cosray) / denomin
    uparam = meany + deltay * tparam
    if np.abs(tparam) < 1 and uparam > 0:
        return True
    return False


def is_origin_in_boundary(vertices: np.ndarray) -> bool:
    """
    Verify if at least one pass through the origin.
    First, it verifies if at least one vertice is at (0, 0)
    Second, it verifies if the point (0, 0) is in at least one edge
    """
    for vertex in vertices:
        if np.linalg.norm(vertex) < 1e-9:
            return True
    for vertex0, vertex1 in zip(vertices[:-1], vertices[1:]):
        coefa, coefb, coefc = find_line_equation(vertex0, vertex1)
        if np.abs(coefc / np.sqrt(coefa**2 + coefb**2)) < 1e-9:  # tolerance
            modvertex0 = np.linalg.norm(vertex0)
            modvertex1 = np.linalg.norm(vertex1)
            moddiffver = np.linalg.norm(vertex1 - vertex0)
            tparameter = (modvertex1**2 - modvertex0**2) / (moddiffver**2)
            if np.abs(tparameter) <= 1:
                return True
    return False


def is_origin_inside_polygon(vertices: np.ndarray) -> bool:
    """
    Given a point like (xp, yp), verifies if this point is inside the polygon
    made by the points ``vertices``.
    Algorithm used: ray-casting
    Frist: It translate all the points, such (xp, yp) becomes origin
    Second: For each vertex (xi, pi), find the forbid angle
        to be sure the ray don't pass through a vertex
    Third: For each segment, find the line's parameter (a, b, c)
        if 'c' is zero, then we must test if the origin is on the boundary
    """
    rayangle = get_angle_ray(vertices)
    counter = 0
    for vertex0, vertex1 in zip(vertices[:-1], vertices[1:]):
        if ray_pass_through_segment(rayangle, vertex0, vertex1):
            counter += 1
    return bool(counter % 2)
