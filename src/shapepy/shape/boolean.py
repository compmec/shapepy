"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple, Union

import numpy as np

from ..boolean import BoolOr
from ..core import Empty, IBoolean2D, ICurve, IShape, Whole
from ..curve.abc import IJordanCurve
from ..curve.concatenate import concatenate, transform_to_jordan
from ..curve.intersect import curve_and_curve
from ..point import Point2D
from ..utils import sorter
from .simple import ConnectedShape, DisjointShape, SimpleShape


def close_shape(shape: IShape) -> IShape:
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, SimpleShape):
        return SimpleShape(shape.jordan, True)
    subshapes = tuple(map(close_shape, shape.subshapes))
    return shape.__class__(subshapes)


def open_shape(shape: IShape) -> IShape:
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, SimpleShape):
        return SimpleShape(shape.jordan, False)
    subshapes = tuple(map(open_shape, shape.subshapes))
    return shape.__class__(subshapes)


def flatten2simples(shape: IShape) -> Tuple[SimpleShape, ...]:
    if not isinstance(shape, IShape):
        raise TypeError
    if isinstance(shape, SimpleShape):
        return (shape,)
    if isinstance(shape, ConnectedShape):
        return shape.subshapes
    if isinstance(shape, DisjointShape):
        subshapes = []
        for subshape in shape.subshapes:
            subshapes += list(flatten2simples(subshape))
    raise NotImplementedError


def unite_shapes(*shapes: IShape) -> IBoolean2D:
    for shape in shapes:
        if not isinstance(shape, IShape):
            raise TypeError(f"Invalid type: {type(shape)}: {shape}")
    orisimples = []  # Original simple shapes
    for shape in shapes:
        orisimples += flatten2simples(shape)
    params_inters = tuple(FollowPath.curves_intersection(shapes))
    allpairs = set()
    for triplea, tripleb in params_inters:
        allpairs.add(triplea)
        allpairs.add(tripleb)
    positions = FollowPath.position_midpoints(shapes, allpairs, True)
    newsimples = []
    folsimples = {}
    for i, (posi, simpli) in enumerate(zip(positions, orisimples)):
        if not any(posi):
            continue
        elif all(posi):
            newsimples.append(simpli)
        else:
            folsimples[i] = simpli
    if folsimples:
        newsimples += FollowPath.follow(orisimples, positions, params_inters)
    if len(newsimples) == 0:
        return Whole()
    return identify_shape(newsimples)


def intersect_shapes(*shapes: IShape) -> IBoolean2D:
    for shape in shapes:
        if not isinstance(shape, IShape):
            raise TypeError(f"Invalid type: {type(shape)}: {shape}")
    orisimples = []  # Original simple shapes
    for shape in shapes:
        orisimples += flatten2simples(shape)
    params_inters = tuple(FollowPath.curves_intersection(shapes))
    allpairs = set()
    for paira, pairb in params_inters:
        allpairs.add(paira)
        allpairs.add(pairb)
    positions = FollowPath.position_midpoints(shapes, allpairs, False)
    newsimples = []
    folsimples = {}
    for i, (posi, simpli) in enumerate(zip(positions, orisimples)):
        if not any(posi):
            continue
        elif all(posi):
            newsimples.append(simpli)
        else:
            folsimples[i] = simpli
    if folsimples:
        newsimples += FollowPath.follow(orisimples, positions, params_inters)
    if len(newsimples) == 0:
        return Empty()
    return identify_shape(newsimples)


def identify_shape(
    simples: Iterable[SimpleShape],
) -> Union[SimpleShape, ConnectedShape, DisjointShape]:
    """
    Identify the final shape (Simple, Connected, Disjoint) from the
    given simple shapes
    """
    simples = tuple(simples)
    for simple in simples:
        if not isinstance(simple, SimpleShape):
            raise TypeError
    areas = tuple(simple.area for simple in simples)
    simples = [simples[i] for i in sorter(areas)]
    disshapes = []
    while simples:
        connsimples = [simples.pop(len(simples) - 1)]
        index = 0
        while index < len(simples):
            simple = simples[index]
            for simplj in connsimples:
                if simple.jordan not in simplj:
                    break
                if simplj.jordan not in simple:
                    break
            else:
                connsimples.append(simples.pop(index))
                index -= 1
            index += 1
        if len(connsimples) == 1:
            shape = connsimples[0]
        else:
            shape = ConnectedShape(connsimples)
        disshapes.append(shape)
    if len(disshapes) == 1:
        return disshapes[0]
    return DisjointShape(disshapes)


class FollowPath:
    """
    Specific static class with functions to compute the
    union and intersection of shapes
    """

    @staticmethod
    def two_curve_inter(
        curvea: IJordanCurve, curveb: IJordanCurve
    ) -> Iterable[Tuple[float, float]]:
        """
        Computes the intersection of two parameted curves P(t) and Q(u)
        returning the pairs (ti, ui) such P(ti) = Q(ui)
        """
        if not isinstance(curvea, IJordanCurve):
            raise TypeError
        if not isinstance(curveb, IJordanCurve):
            raise TypeError
        objs = curve_and_curve(curvea, curveb)
        curvea = curvea.param_curve
        curveb = curveb.param_curve
        if isinstance(objs, Empty):
            return
        if isinstance(objs, BoolOr):
            objs = tuple(objs)
        else:
            objs = (objs,)
        points = []
        for obj in objs:
            if isinstance(obj, Point2D):
                points.append(obj)
            elif isinstance(obj, ICurve):
                points += list(obj.vertices)
            else:
                raise NotImplementedError
        setpts = []
        for point in points:
            for setpt in setpts:
                if point == setpt:
                    break
            else:
                setpts.append(point)
        for point in setpts:
            parama = curvea.projection(point)[0]
            paramb = curveb.projection(point)[0]
            yield (parama, paramb)

    @staticmethod
    def two_shape_inter(shapea: IShape, shapeb: IShape):
        """
        Computes the intersection of all the curves from two shapes.
        Meaning, shapea has some jordan curves and shapeb have also some
        jordan curves. By construction, jordan curves of shapea doesn't
        intersect with each other, then we need only check the intersection
        of the jordans from shapea with the jordans from shapeb.

        This function gives an iterable of (i, a), (j, b)
        Which jordansa[i](a) == jordansb[j](b)
        """
        for i, jordani in enumerate(shapea.jordans):
            for j, jordanj in enumerate(shapeb.jordans):
                pairs = FollowPath.two_curve_inter(jordani, jordanj)
                for ti, tj in pairs:
                    yield (i, ti), (j, tj)

    @staticmethod
    def curves_intersection(
        shapes: Tuple[IShape, ...],
    ) -> Iterable[Tuple[int, float]]:
        """
        Computes the parameters of the intersection of the curves for every
        pair of shapes

        Parameters
        ----------
        shapes: Tuple[IShape]
            The shapes that we must compute the intersection points
        return: Tuple[Tuple[(int, float), (int, float)]]
            The intersection values.
            Each line is a pair of (int, float)
            The int means the index of the jordan curve
            based from all shapes
            the float means the node such has the
        """
        for shape in shapes:
            if not isinstance(shape, IShape):
                raise TypeError(f"Invalid type: {type(shape)}: {shape}")
        lenghts = tuple(len(shape.jordans) for shape in shapes)
        cumlens = [0] + list(np.cumsum(lenghts))
        for i, shapei in enumerate(shapes):
            for j, shapej in enumerate(shapes):
                if j <= i:
                    continue
                temp_inters = FollowPath.two_shape_inter(shapei, shapej)
                for (a, ta), (b, tb) in temp_inters:
                    x = cumlens[i] + a
                    y = cumlens[j] + b
                    yield (x, ta), (y, tb)

    @staticmethod
    def position_midpoints(
        shapes: Tuple[IShape],
        pairs: Tuple[Tuple[int, float], Tuple[int, float]],
        union: bool,
    ) -> Dict[Tuple[int, int], bool]:
        """
        Receives the
        """
        alljordans = []
        for shape in shapes:
            alljordans += list(shape.jordans)
        allknots = [None] * len(alljordans)
        for i, jordan in enumerate(alljordans):
            allknots[i] = set(jordan.param_curve.knots)
        for k, node in pairs:
            allknots[k].add(node)
        allpositions = [None] * len(alljordans)
        index = 0
        for i, shape in enumerate(shapes):
            for jordan in shape.jordans:
                knots = tuple(sorted(allknots[index]))
                curve = jordan.param_curve
                positions = []
                for ta, tb in zip(knots, knots[1:]):
                    midpoint = curve.eval((ta + tb) / 2)
                    for k, shapek in enumerate(shapes):
                        if k == i:
                            continue
                        if union and 0 < shapek.winding(midpoint):
                            positions.append(False)
                            break
                        if not union and not shapek.winding(midpoint):
                            positions.append(False)
                            break
                    else:
                        positions.append(True)
                allpositions[index] = tuple(positions)
                index += 1
        return allpositions

    @staticmethod
    def follow(
        simples: Tuple[SimpleShape],
        allpositions: Tuple[Tuple[bool]],
        intersparams: Tuple,
    ) -> Tuple[IJordanCurve, ...]:
        """
        This function receives the jordan curves,
        that can intersect the other jordan curves,
        and follows the paths using these curves.

        This is an intermediate function and should not be
        called without taking care of the arguments.
        I'm not proud of this function cause it became too
        complex, but better working than perfect.

        Parameters
        ----------
        jordans: Tuple[IJordanCurve]
            The jordan curves that are on the plane
        allpositions: Tuple[Tuple[bool]]
            The midpoint positions, to start following the path
        intersparams: Tuple[Tuple[int, float]]
            A list of two pairs like [[[i0, ai0], [j0, bj0]], ...]
            Which tells the intersection parameters.
            Example: jordans[i0].eval(ai0) == jordans[j0].eval(bj0)
        return: Tuple[IJordanCurve]
            The wanted jordan curves that don't intersect each others
        """
        all_curves = tuple(simple.jordan.param_curve for simple in simples)
        intersparams = tuple(intersparams)
        allpositions = list(map(list, allpositions))

        newjordans: list[IJordanCurve] = []
        for i, positions in enumerate(allpositions):
            if all(positions) or not any(positions):
                raise ValueError
        if not intersparams:
            return tuple(newjordans)

        connections = {}
        for pairi, pairj in intersparams:
            connections[pairi] = pairj
            connections[pairj] = pairi
        all_knots = [curve.knots for curve in all_curves]
        for i, knots in enumerate(all_knots):
            connections[(i, knots[0])] = i, knots[-1]
            connections[(i, knots[-1])] = i, knots[0]

        all_knots = tuple(map(set, all_knots))
        for i, a in connections.keys():
            all_knots[i].add(a)
        all_knots = tuple(map(sorted, all_knots))

        for index, positions in enumerate(allpositions):
            while any(positions):
                triplets = []
                i = index
                trues = tuple(k for k, p in enumerate(positions) if p)
                nodea = all_knots[i][trues[0]]
                while True:
                    start = all_knots[i].index(nodea)
                    ending = start
                    while ending in trues:
                        ending += 1
                    for k in range(start, ending):
                        allpositions[i][k] = False
                    nodeb = all_knots[i][ending]
                    triplets.append((i, nodea, nodeb))
                    i, nodea = connections.pop((i, nodeb))
                    if i == triplets[0][0] and nodea == triplets[0][1]:
                        break
                    trues = tuple(
                        k for k, p in enumerate(allpositions[i]) if p
                    )
                new_segments = []
                for j, nodea, nodeb in triplets:
                    segment = all_curves[j].section(nodea, nodeb)
                    new_segments.append(segment)
                new_curve = concatenate(*new_segments)
                new_jordan = transform_to_jordan(new_curve)
                newjordans.append(new_jordan)
        boundaries = [False for _ in newjordans]
        return tuple(
            SimpleShape(jordan, boundary)
            for jordan, boundary in zip(newjordans, boundaries)
        )
