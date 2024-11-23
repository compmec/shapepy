"""
This modules contains all the geometry need to make any kind of shape.
You can use directly the function ```regular_polygon``` and the transformations
like ```move```, ```rotate``` and ```scale``` to model your desired curve.

You can assemble JordanCurves to create shapes with holes,
or even unconnected shapes.
"""

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import numpy as np

from ..core import Empty, IBoolean2D, IShape, Whole
from ..curve.abc import IJordanCurve, IParameterCurve
from ..point import Point2D
from .condisj import ConnectedShape, DisjointShape, identify_shape
from .simple import SimpleShape


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


def intersection(curvea: IParameterCurve, curveb: IParameterCurve):
    return tuple()  # No intersection implemented yet


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
        raise NotImplementedError
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
    for triplea, tripleb in params_inters:
        allpairs.add(triplea)
        allpairs.add(tripleb)
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
        raise NotImplementedError
    if len(newsimples) == 0:
        return Empty()
    return identify_shape(newsimples)


class FollowPath:
    """
    Specific static class with functions to compute the
    union and intersection of shapes
    """

    @staticmethod
    def two_curve_inter(
        curvea: IParameterCurve, curveb: IParameterCurve
    ) -> Iterable[Tuple[float]]:
        """
        Computes the intersection of two parameted curves P(t) and Q(u)
        returning the pairs (ti, ui) such P(ti) = Q(ui)
        """
        if not isinstance(curvea, IParameterCurve):
            raise TypeError
        if not isinstance(curveb, IParameterCurve):
            raise TypeError
        for item in intersection(curvea, curveb):
            if not isinstance(item, Point2D):
                raise NotImplementedError
            parama = curvea.projection(item)[0]
            paramb = curveb.projection(item)[0]
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
            curvei = jordani.param_curve
            for j, jordanj in enumerate(shapeb.jordans):
                curvej = jordanj.param_curve
                for ti, tj in FollowPath.two_curve_inter(curvei, curvej):
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
                        if union and midpoint in shapek:
                            positions.append(False)
                            break
                        if not union and midpoint not in shapek:
                            positions.append(False)
                            break
                    else:
                        positions.append(True)
                allpositions[index] = tuple(positions)
                index += 1
        return allpositions

    @staticmethod
    def follow(
        jordans: Tuple[IJordanCurve],
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
        all_curves = tuple(jordan.param_curve for jordan in jordans)
        intersparams = tuple(intersparams)
        allpositions = list(map(list, allpositions))

        newjordans: list[IJordanCurve] = []
        for i, positions in enumerate(allpositions):
            if all(positions):
                allpositions[i] = [False] * len(positions)
                newjordans.append(jordans[i])
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
                new_jordan = None
                newjordans.append(new_jordan)

        return tuple(newjordans)
