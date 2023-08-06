from __future__ import annotations

import fractions
import math
from copy import deepcopy
from typing import Tuple, Union

import numpy as np


def pytha_triples(mmax: int):
    """
    Returns pythagorean triplets using integers
    """
    assert isinstance(mmax, int)
    assert mmax > 0
    triplets = [(1, 0, 1), (0, 1, 1), (-1, 0, 1), (0, -1, 1)]
    for m in range(1, mmax + 1):
        for n in range(1, m):
            a = m**2 - n**2
            b = 2 * m * n
            c = m**2 + n**2
            gcd = abs(math.gcd(a, b, c))
            a, b, c = a // gcd, b // gcd, c // gcd
            if (a, b, c) in triplets:
                continue
            triplets.append((a, b, c))
            triplets.append((b, a, c))
            triplets.append((-a, b, c))
            triplets.append((-b, a, c))
            triplets.append((a, -b, c))
            triplets.append((b, -a, c))
            triplets.append((-a, -b, c))
            triplets.append((-b, -a, c))
    return tuple(triplets)


class Point2D:
    def __init__(self, x: float, y: float = None):
        if y is None:
            x, y = x
        if isinstance(x, str) or isinstance(y, str):
            raise TypeError
        float(x)  # entry validation
        float(y)  # entry validation
        self._x = x
        self._y = y
        if isinstance(x, (int, fractions.Fraction)):
            self._x = fractions.Fraction(x).limit_denominator(1e9)
            self._y = fractions.Fraction(y).limit_denominator(1e9)

    def inner(self, other: Point2D) -> float:
        """
        Inner product between two points
        """
        assert isinstance(other, self.__class__)
        return self[0] * other[0] + self[1] * other[1]

    def cross(self, other: Point2D) -> float:
        """
        Cross product between two points
        """
        assert isinstance(other, self.__class__)
        return self[0] * other[1] - self[1] * other[0]

    def norm_square(self) -> float:
        return self.inner(self)

    def __abs__(self) -> float:
        """
        The euclidean distance to origin
        """
        norm2 = self.norm_square()
        if not isinstance(norm2, fractions.Fraction):
            sqrt = math.sqrt(norm2)
            return int(sqrt) if int(sqrt) == sqrt else sqrt
        num, den = norm2.numerator, norm2.denominator
        sqrtnum = math.sqrt(num)
        sqrtnum = int(sqrtnum) if int(sqrtnum) == sqrtnum else sqrtnum
        sqrtden = math.sqrt(den)
        sqrtden = int(sqrtden) if int(sqrtden) == sqrtden else sqrtden
        return sqrtnum / sqrtden

    def copy(self) -> Point2D:
        return deepcopy(self)

    def __iter__(self):
        yield self._x
        yield self._y

    def __getitem__(self, index: int):
        assert isinstance(index, int)
        assert index == 0 or index == 1
        return self._x if index == 0 else self._y

    def __str__(self) -> str:
        if isinstance(self._x, fractions.Fraction):
            xmsg = str(self._x.numerator)
            xmsg += (
                "" if (self._x.denominator == 1) else ("/" + str(self._x.denominator))
            )
        else:
            xmsg = str(self._x)
        if isinstance(self._y, fractions.Fraction):
            ymsg = str(self._y.numerator)
            ymsg += (
                "" if (self._y.denominator == 1) else ("/" + str(self._y.denominator))
            )
        else:
            ymsg = str(self._y)
        return "(%s, %s)" % (xmsg, ymsg)

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Point2D) -> bool:
        if not isinstance(other, Point2D):
            other = Point2D(other)
        if self._x != other._x:
            return False
        if self._y != other._y:
            return False
        return True

    def __neg__(self) -> Point2D:
        return self.__class__(-self[0], -self[1])

    def __iadd__(self, other: Point2D) -> Point2D:
        assert isinstance(other, self.__class__)
        self._x += other[0]
        self._y += other[1]
        return self

    def __isub__(self, other: Point2D) -> Point2D:
        assert isinstance(other, self.__class__)
        self._x -= other[0]
        self._y -= other[1]
        return self

    def __imul__(self, other: float) -> Point2D:
        if isinstance(other, self.__class__):
            return self.inner(other)
        self._x *= other
        self._y *= other
        return self

    def __add__(self, other: Point2D) -> Point2D:
        new = self.copy()
        new += other
        return new

    def __sub__(self, other: Point2D) -> Point2D:
        new = self.copy()
        new -= other
        return new

    def __mul__(self, other: float) -> Point2D:
        new = self.copy()
        new *= other
        return new

    def __rmul__(self, other: float) -> Point2D:
        return self.__mul__(other)

    def __or__(self, other: Point2D) -> float:
        return self.inner(other)

    def __xor__(self, other: Point2D) -> float:
        return self.cross(other)


class Segment:
    def __init__(self, point0: Point2D, point1: Point2D) -> Tuple:
        point0 = Point2D(point0)
        point1 = Point2D(point1)
        assert point0 != point1
        self._point0 = point0
        self._point1 = point1
        self._vector = point1 - point0

    def __str__(self) -> str:
        msg = "Segment %s -> %s"
        msg %= str(self._point0), str(self._point1)
        return msg

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: Point2D) -> str:
        return (self[0] == other[0]) and (self[1] == other[1])

    @property
    def vector(self) -> Point2D:
        return self._vector

    def __call__(self, other: float) -> Point2D:
        float(other)
        return self._point0 + other * self.vector

    def __getitem__(self, index: int):
        assert isinstance(index, int)
        assert index == 0 or index == 1
        return self._point0 if index == 0 else self._point1

    def __contains__(self, other: Union[Point2D, Segment]):
        if isinstance(other, Point2D):
            param = self.projection(other)
            if param < 0 or 1 < param:
                return False
            projectpt = self(param)
            vector = projectpt - other
            return vector.norm_square() < 1e-9
        if isinstance(other, Segment):
            return (other[0] in self) and (other[1] in self)
        return Point2D(other) in self

    def __and__(self, other: Segment) -> Union[None, Tuple[float], Segment]:
        """
        Returns the intersection of a segment and another segment
        """
        assert isinstance(other, self.__class__)
        vector0 = self.vector
        vector1 = other.vector
        diff0 = other[0] - self[0]
        denom = vector0.cross(vector1)
        if denom != 0:  # Lines are not parallel
            param0 = diff0.cross(vector1) / denom
            param1 = diff0.cross(vector0) / denom
            if param0 < 0 or 1 < param0:
                return None
            if param1 < 0 or 1 < param1:
                return None
            return param0, param1
        # Lines are parallel
        if vector0.cross(diff0):
            return None  # Parallel, but not colinear
        param0 = self.projection(other[0])
        param1 = self.projection(other[1])
        assert param0 != param1
        if (param0 < 0 or 1 < param0) and (param1 < 0 or 1 < param1):
            return None  # Colinear, but no intersect

        left = max(0, min(param0, param1))
        righ = min(1, max(param0, param1))
        if 0 <= param0 and param0 <= 1 and 0 <= param1 and param1 <= 1:
            return Segment(self(left), self(righ))
        if left == 0 and righ == 0:
            if param0 == 0:
                return (0, 0)
            if param1 == 0:
                return (0, 1)
        if left == 1 and righ == 1:
            if param0 == 1:
                return (1, 0)
            if param1 == 1:
                return (1, 1)
        return Segment(self(left), self(righ))

    def projection(self, point: Point2D):
        """
        Given a point P, it returns the parameter t* such
        minimizes the distance square
            dist2(t*) = min_t dist2(t) = min_t |P - V(t)|^2
        """
        point = Point2D(point)
        vector = self.vector
        return vector.inner(point - self[0]) / vector.inner(vector)


class HelperPolygon:
    """
    Defines all functions related to a polygon:
    - Is a point inside a polygon?
    - obtain the minimum convex polygon outside a polygon
    - Compute area
    """

    @staticmethod
    def valid_entry(vertices: Tuple[Point2D]) -> bool:
        if not isinstance(vertices, (list, tuple)):
            return False
        vertices = list(vertices)
        for i, vertex in enumerate(vertices):
            vertices[i] = Point2D(vertex)
        # Test if there's no equal vertex
        nverts = len(vertices)
        for i, vertex0 in enumerate(vertices):
            for j in range(i + 1, nverts):
                vertex1 = vertices[j]
                if vertex0 == vertex1:
                    return False

        # Create segments to test self intersection
        segments = []
        for i in range(nverts):
            vertex0 = vertices[i]
            vertex1 = vertices[(i + 1) % nverts]
            newsegment = Segment(vertex0, vertex1)
            segments.append(newsegment)

        # Check self intersection
        for i, seg0 in enumerate(segments):
            for j, seg1 in enumerate(segments):
                distance = min((i - j) % nverts, (j - i) % nverts)
                if distance < 2:
                    continue
                if seg0 & seg1 is not None:
                    return False
        return True

    @staticmethod
    def is_convex(vertices: Tuple[Point2D]) -> bool:
        """ """
        assert isinstance(vertices, (tuple, list))
        nvertices = len(vertices)
        assert nvertices > 2
        for vertex in vertices:
            assert isinstance(vertex, Point2D)
        diff_vertices = []
        for i, vertex0 in enumerate(vertices):
            vertex1 = vertices[(i + 1) % nvertices]
            diff_vertices.append(vertex1 - vertex0)
        crosses = []
        for i, diff0 in enumerate(diff_vertices):
            diff1 = diff_vertices[(i + 1) % nvertices]
            crosses.append(diff0.cross(diff1))
        for i in range(nvertices - 1):
            if crosses[i] * crosses[i + 1] < 0:
                return False
        return True

    @staticmethod
    def origin_in_polygon(vertices: Tuple[Point2D]) -> bool:
        """
        Given a closed polygon, this function tells if the origin
        is inside this polygon.
        It uses ray-casting algorithm
            points[0] != points[-1]
        """
        frac = fractions.Fraction
        origin = Point2D(frac(0), frac(0))
        diameter_sq = 1
        npts = len(vertices)
        for i in range(npts):
            for j in range(i + 1, npts):
                vector = vertices[i] - vertices[j]
                norm_sq = vector.norm_square()
                diameter_sq = max(diameter_sq, norm_sq)
        diameter_sq = math.ceil(diameter_sq)
        polygon_segments = []
        for i in range(npts):
            new_segment = Segment(vertices[i], vertices[(i + 1) % npts])
            polygon_segments.append(new_segment)

        times = 0
        directions = list(pytha_triples(2 + math.ceil(np.sqrt(len(vertices)) / 2)))
        for direction in directions:
            vector = Point2D(frac(direction[0]), frac(direction[1]))
            ray_segment = Segment(origin, vector)
            counter = frac(0)
            for poly_seg in polygon_segments:
                inters = poly_seg & ray_segment
                if inters is None:
                    continue
                if isinstance(inters, Segment):
                    counter += 1
                    continue
                counter += frac(1, 2)
                if inters[0] != 0 and inters[0] != 1:
                    counter += frac(1, 2)
            times += int(counter) % 2
        return 2 * times > len(directions)

    @staticmethod
    def convex_hull(points: Tuple[Point2D]) -> Tuple[int]:
        """
        Receives a list of points of a simple polygon.
        returns the minimum convex polygon which
        is a convex hull.
        The polygon must have minimum 3 points
            points[0] != points[-1]
        Returns the index of the convex hull points

        The result convex hull is positive (counter-clockwise)
        """
        assert isinstance(points, (list, tuple))
        assert len(points) > 2
        # Still need to verify if all the points are not colinear

        # First we select the point with max x
        # Since can exist more than one, we get
        # the one with highest y
        xvals = [point[0] for point in points]
        yvals = [point[1] for point in points]
        xmax = max(xvals)
        indexs_xmax = []
        for i, xval in enumerate(xvals):
            if xval == xmax:
                indexs_xmax.append(i)
        index_xmax_ymax = indexs_xmax[0]
        for ind in indexs_xmax:
            if yvals[ind] > yvals[index_xmax_ymax]:
                index_xmax_ymax = ind

        next_index = index_xmax_ymax
        cnvhull_indexs = [next_index]
        point0 = points[next_index]
        vector0 = point0.__class__(0, 1)
        norm2_vec0 = vector0.norm_square()

        coss2 = [-1] * len(points)  # Store the cossinus square
        norms2 = [0] * len(points)  # Store the norm of the vectors
        while True:  # Loop to get all other points
            for i, point in enumerate(points):
                if i == next_index:
                    coss2[i] = -1
                    norms2[i] = 0
                    continue
                vector = point - point0
                norm2_vector = vector.norm_square()
                norms2[i] = norm2_vector
                inner = vector0.inner(vector)
                newcos2 = (inner**2) / (norm2_vec0 * norm2_vector)
                newcos2 *= 1 if inner > 0 else -1
                coss2[i] = newcos2
            maxcos2 = max(coss2)
            indexs_maxcos2 = []
            for i, cos2 in enumerate(coss2):
                if cos2 == maxcos2:
                    indexs_maxcos2.append(i)
            next_index = indexs_maxcos2[0]
            for ind in indexs_maxcos2:
                if norms2[ind] > norms2[next_index]:
                    next_index = ind
            if next_index == cnvhull_indexs[0]:
                break
            cnvhull_indexs.append(next_index)
            vector0 = points[next_index] - point0
            point0 = points[next_index]
            norm2_vec0 = norms2[next_index]

        minindex = min(cnvhull_indexs)
        indminindex = cnvhull_indexs.index(minindex)
        return tuple(cnvhull_indexs[indminindex:] + cnvhull_indexs[:indminindex])


class BasePolygon(object):
    def __init__(self, vertices: Tuple[Point2D]):
        assert HelperPolygon.valid_entry(vertices)
        self.__vertices = tuple(vertices)

    def __str__(self) -> str:
        return str(self.vertices)

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def nvertices(self) -> int:
        return len(self.__vertices)

    @property
    def vertices(self) -> Tuple[Point2D]:
        return tuple([vertex for vertex in self.__vertices])

    @property
    def segments(self) -> Tuple[Segment]:
        vertices = self.vertices
        segments = []
        for i in range(self.nvertices - 1):
            segments.append(Segment(vertices[i], vertices[i + 1]))
        segments.append(Segment(vertices[-1], vertices[0]))
        return tuple(segments)

    def clean(self):
        """
        Removes the aligned vertices
        """
        vertices = self.vertices
        nvertices = len(vertices)
        vectors = [None] * nvertices
        for i, vertex0 in enumerate(vertices):
            vertex1 = vertices[(i + 1) % nvertices]
            vectors[i] = vertex1 - vertex0
        coss2 = [None] * nvertices
        for i, vector0 in enumerate(vectors):
            vector1 = vectors[(i + 1) % nvertices]
            normsq0 = vector0.norm_square()
            normsq1 = vector1.norm_square()
            inner = vector0.inner(vector1)
            coss2[i] = (inner**2) / (normsq0 * normsq1)
        vector0 = vectors[-1]
        vector1 = vectors[0]
        normsq0 = vector0.norm_square()
        normsq1 = vector1.norm_square()
        inner = vector0.inner(vector1)
        coss2[i] = (inner**2) / (normsq0 * normsq1)
        clean_indexs = []
        for i, cos2 in enumerate(coss2):
            if cos2 != 1:
                clean_indexs.append((i + 1) % nvertices)
        clean_indexs = sorted(clean_indexs)
        self.__vertices = tuple([vertices[i] for i in clean_indexs])
        return self


class SimplePolygon(BasePolygon):
    def __init__(self, vertices: Tuple[Point2D]):
        super().__init__(vertices)

    def copy(self) -> SimplePolygon:
        return deepcopy(self)

    def __eq__(self, other: SimplePolygon) -> bool:
        """
        Tells if a polygon is equal to another one base on
        the points. Allows permutations

        """
        assert isinstance(other, SimplePolygon)
        selfcopy = self.copy()
        selfcopy.clean()
        othecopy = other.copy()
        othecopy.clean()
        selfvertices = selfcopy.vertices
        othevertices = othecopy.vertices
        if len(selfvertices) != len(othevertices):
            return False
        for shift, vertex in enumerate(othevertices):
            if vertex == selfvertices[0]:
                break
        else:
            return False
        nvertices = len(selfvertices)
        for i, vertex in enumerate(selfvertices):
            if othevertices[(i + shift) % nvertices] != vertex:
                return False
        return True

    def __ne__(self, other: SimplePolygon) -> bool:
        return not self.__eq__(other)

    def __point_on_boundary(self, other: Point2D) -> bool:
        """
        Tells if the point is on the boundary.
        Basicly it computes the projection of P on each
        segment V(t) = (1-t) * V0 + t * V1
        """
        assert isinstance(other, Point2D)
        for segment in self.segments:
            if other in segment:
                return True
        return False

    def __point_is_internal(self, other: Point2D) -> bool:
        """
        Tells if the point is inside the openset created
        by the polygon. Excludes the boundary
        """
        vertices = list(self.vertices)
        for i, vertex in enumerate(vertices):
            vertices[i] = vertex - other
        return HelperPolygon.origin_in_polygon(vertices)

    def __contains_point(self, other: Point2D) -> bool:
        assert isinstance(other, Point2D)
        if self.__point_on_boundary(other):
            return True
        return self.__point_is_internal(other)

    def __contains_polygon(self, other: SimplePolygon) -> bool:
        assert isinstance(other, SimplePolygon)
        othvertices = other.vertices
        for vertex in othvertices:
            if vertex not in self:
                return False
        if isinstance(self, ConvexPolygon):
            return True
        selvertices = self.vertices
        nptsself = len(selvertices)
        nptsothe = len(othvertices)
        selfsegs = [None] * nptsself
        othesegs = [None] * nptsothe
        for i in range(nptsself):
            selfsegs[i] = Segment(selvertices[i], selvertices[(i + 1) % nptsself])
        for i in range(nptsothe):
            othesegs[i] = Segment(othvertices[i], othvertices[(i + 1) % nptsothe])
        for i, otheseg in enumerate(othesegs):
            intersections = [0, 1]
            for selfseg in selfsegs:
                inters = otheseg & selfseg
                if inters is None:
                    continue
                if not isinstance(inters, Segment):
                    intersections.append(inters[0])
                    continue
                param0 = otheseg.projection(inters[0])
                param1 = otheseg.projection(inters[1])
                intersections.append(param0)
                intersections.append(param1)
            intersections = tuple(sorted(set(intersections)))
            midparams = [
                (a + b) / 2 for a, b in zip(intersections[:-1], intersections[1:])
            ]
            points = [otheseg(midparam) for midparam in midparams]
            for point in points:
                if point not in self:
                    return False
        return True

    def __contains__(self, other: Union[Point2D, SimplePolygon]) -> bool:
        if isinstance(other, Point2D):
            return self.__contains_point(other)
        if isinstance(other, SimplePolygon):
            return self.__contains_polygon(other)
        return Point2D(other) in self


class ConvexPolygon(SimplePolygon):
    """
    Class to store a convex polygon
    """

    def __init__(self, vertices: Tuple[Point2D]):
        assert HelperPolygon.is_convex(vertices)
        super().__init__(vertices)


def ConvexHull(polygon: SimplePolygon) -> ConvexPolygon:
    assert isinstance(polygon, SimplePolygon)
    if isinstance(polygon, ConvexPolygon):
        newpolygon = polygon.copy()
        newpolygon.clean()
        return newpolygon
    vertices = polygon.vertices
    indexs_convexhull = HelperPolygon.convex_hull(vertices)
    new_vertices = []
    for index in indexs_convexhull:
        new_vertices.append(vertices[index])
    return ConvexPolygon(new_vertices)


def Polygon(vertices: Tuple[Point2D]) -> Union[SimplePolygon, ConvexPolygon]:
    if not HelperPolygon.valid_entry(vertices):
        raise ValueError
    vertices = list(vertices)
    for i, vertex in enumerate(vertices):
        vertices[i] = Point2D(vertex)
    vertices = tuple(vertices)
    if HelperPolygon.is_convex(vertices):
        return ConvexPolygon(vertices)
    return SimplePolygon(vertices)
