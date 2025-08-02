"""
Defines the piecewise curve class
"""

from __future__ import annotations

from typing import Iterable, Tuple, Union

from ..scalar.reals import Real
from ..tools import Is, To
from .box import Box
from .point import Point2D
from .segment import Segment, clean_segment


class PiecewiseCurve:
    """
    Defines a piecewise curve that is the concatenation of several segments.
    """

    def __init__(
        self,
        segments: Iterable[Segment],
        knots: Union[None, Iterable[Real]] = None,
    ):
        segments = tuple(segments)
        if not all(map(Is.segment, segments)):
            raise ValueError("All segments must be instances of Segment")
        if knots is None:
            knots = tuple(map(To.rational, range(len(segments) + 1)))
        else:
            knots = tuple(sorted(map(To.real, knots)))
        self.__segments = segments
        self.__knots = knots

    @property
    def knots(self) -> Tuple[Real]:
        """
        Get the knots of the piecewise curve.
        """
        return self.__knots

    @property
    def length(self) -> Real:
        """
        Gets the length of the curve
        """
        return sum(seg.length for seg in self)

    def __iter__(self):
        yield from self.__segments

    def __getitem__(self, index: int) -> Segment:
        """
        Get the segment at the specified index.
        """
        return self.__segments[index]

    def __len__(self) -> int:
        """
        Get the number of segments in the piecewise curve.
        """
        return len(self.__segments)

    def span(self, node: Real) -> Union[int, None]:
        """
        Finds the index of the node
        """
        if not Is.real(node):
            raise ValueError
        if node < self.knots[0] or self.knots[-1] < node:
            return None
        for i, knot in enumerate(self.knots[1:]):
            if node < knot:
                return i
        return len(self.__segments) - 1

    def box(self) -> Box:
        """The box which encloses the piecewise curve

        :return: The box which encloses the piecewise curve
        :rtype: Box
        """
        box = None
        for bezier in self:
            box |= bezier.box()
        return box

    def __call__(self, node: float) -> Point2D:
        index = self.span(node)
        if index is None:
            raise ValueError(f"Node {node} is out of bounds")
        knota, knotb = self.knots[index], self.knots[index + 1]
        unitparam = (node - knota) / (knotb - knota)
        return self[index](unitparam)

    def __contains__(self, point: Point2D) -> bool:
        """Tells if the point is on the boundary"""
        return any(point in bezier for bezier in self)

    def __and__(
        self, other: PiecewiseCurve
    ) -> Tuple[Tuple[int, int, float, float]]:
        """Computes the intersection of two jordan curves"""
        return self.intersection(other, equal_beziers=False, end_points=False)

    def __intersection(
        self, other: PiecewiseCurve
    ) -> Tuple[Tuple[int, int, float, float]]:
        """Private method of ``intersection``

        Computes the intersection between ``self`` and ``other``
        returning a list of [(a0, b0, u0, v0), ...]
        such self.segments[a0](u0) == other.segments[b0](v0)

        If (ui, vi) == (None, None), it means
        self.segments[a0] == other.segments[b0]

        """
        intersections = set()
        for ai, sbezier in enumerate(self):
            for bj, obezier in enumerate(other):
                inters = sbezier & obezier
                if inters is None:
                    continue
                if len(inters) == 0:  # Equal curves
                    intersections.add((ai, bj, None, None))
                for ui, vj in inters:
                    intersections.add((ai, bj, ui, vj))
        return list(intersections)

    def intersection(
        self,
        other: PiecewiseCurve,
        equal_beziers: bool = True,
        end_points: bool = True,
    ) -> Tuple[Tuple[int, int, float, float]]:
        r"""Computes the intersection between two jordan curves

        Finds the values of (:math:`a^{\star}`, :math:`b^{\star}`,
        :math:`u^{\star}`, :math:`v^{\star}`) such

        .. math::
            S_{a^{\star}}(u^{\star}) == O_{b^{\star}}(v^{\star})

        It computes the intersection between each pair of segments
        from ``self`` and ``other`` and returns the matrix of coefficients

        .. math::

            \begin{bmatrix}
            a_0 & b_0 & u_0 & v_0 \\
            a_1 & b_1 & u_1 & v_1 \\
            \vdots & \vdots & \vdots & \vdots \\
            a_{n} & b_{n} & u_{n} & v_{n}
            \end{bmatrix}

        If two bezier curves are equal, then ``u_i = v_i = None``

        * ``0 <= a_i < len(self.segments)``
        * ``0 <= b_i < len(other.segments)``
        * ``0 <= u_i <= 1`` or ``None``
        * ``0 <= v_i <= 1`` or ``None``

        Parameters
        ----------
        other : JordanCurve
            The jordan curve which intersects ``self``
        equal_beziers : bool, default = True
            Flag to return (or not) when two segments are equal

            If the flag ``equal_beziers`` are inactive,
            then will remove when ``(ui, vi) == (None, None)``.

        end_points : bool, default = True
            Flag to return (or not) when jordans intersect at end points

            If the flag ``end_points`` are inactive,
            then will remove when ``(ui, vi)`` are
            ``(0, 0)``, ``(0, 1)``, ``(1, 0)`` or ``(1, 1)``

        :return: The matrix of coefficients ``[(ai, bi, ui, vi)]``
                 or an empty tuple in case of non-intersection
        :rtype: tuple[(int, int, float, float)]


        Example use
        -----------
        >>> from shapepy import JordanCurve
        >>> vertices_a = [(0, 0), (2, 0), (2, 2), (0, 2)]
        >>> jordan_a = JordanCurve.from_vertices(vertices_a)
        >>> vertices_b = [(1, 1), (3, 1), (3, 3), (1, 3)]
        >>> jordan_b = JordanCurve.from_vertices(vertices_b)
        >>> jordan_a.intersection(jordan_b)
        ((1, 0, 1/2, 1/2), (2, 3, 1/2, 1/2))

        """
        assert Is.piecewise(other)
        intersections = self.__intersection(other)
        # Filter the values
        if not equal_beziers:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None:
                    intersections.remove((ai, bi, ui, vi))
        if not end_points:
            for ai, bi, ui, vi in tuple(intersections):
                if ui is None or (0 < ui < 1) or (0 < vi < 1):
                    continue
                intersections.remove((ai, bi, ui, vi))
        return tuple(sorted(intersections))


def clean_piecewise(piecewise: PiecewiseCurve) -> PiecewiseCurve:
    """
    Cleans the piecewise curve, keeping the current parametrisation
    """
    return PiecewiseCurve(map(clean_segment, piecewise))


def is_piecewise(obj: object) -> bool:
    """
    Checks if the parameter is a Piecewise curve

    Parameters
    ----------
    obj : The object to be tested

    Returns
    -------
    bool
        True if the obj is a PiecewiseCurve, False otherwise
    """
    return Is.instance(obj, PiecewiseCurve)


Is.piecewise = is_piecewise
