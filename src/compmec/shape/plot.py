from __future__ import annotations

from typing import Optional

import matplotlib
import numpy as np
from matplotlib import pyplot

from compmec.shape.shape import (
    BaseShape,
    ConnectedShape,
    DisjointShape,
    EmptyShape,
    SimpleShape,
    WholeShape,
)

Path = matplotlib.path.Path
PathPatch = matplotlib.patches.PathPatch


def patchify(polys, color, alpha):
    """
    https://stackoverflow.com/questions/8919719/how-to-plot-a-complex-polygon
    """

    def reorder(poly, cw=True):
        """Reorders the polygon to run clockwise or counter-clockwise
        according to the value of cw. It calculates whether a polygon is
        cw or ccw by summing (x2-x1)*(y2+y1) for all edges of the polygon,
        see https://stackoverflow.com/a/1165943/898213.
        """
        # Close polygon if not closed
        if not np.allclose(poly[:, 0], poly[:, -1]):
            poly = np.c_[poly, poly[:, 0]]
        direction = (
            (poly[0] - np.roll(poly[0], 1)) * (poly[1] + np.roll(poly[1], 1))
        ).sum() < 0
        if direction == cw:
            return poly
        else:
            return poly[::-1]

    def ring_coding(n):
        """Returns a list of len(n) of this format:
        [MOVETO, LINETO, LINETO, ..., LINETO, LINETO CLOSEPOLY]
        """
        codes = [Path.LINETO] * n
        codes[0] = Path.MOVETO
        codes[-1] = Path.CLOSEPOLY
        return codes

    ccw = [True] + ([False] * (len(polys) - 1))
    polys = [reorder(poly, c) for poly, c in zip(polys, ccw)]
    codes = np.concatenate([ring_coding(p.shape[1]) for p in polys])
    vertices = np.concatenate(polys, axis=1)
    return PathPatch(Path(vertices.T, codes), color=color, alpha=alpha)


class ShapePloter:
    Figure = matplotlib.figure.Figure
    Axes = matplotlib.axes._axes.Axes

    def __init__(
        self,
        *,
        fig: Optional[ShapePloter.Figure] = None,
        ax: Optional[ShapePloter.Axes] = None,
    ):
        if fig is None and ax is None:
            fig, ax = pyplot.subplots()
        elif fig is None:
            fig = ax.get_figure()
        elif ax is None:
            ax = fig.axes
            if isinstance(ax, list) and len(ax) == 0:
                ax = pyplot.gca()
        else:
            if not isinstance(fig, ShapePloter.Figure):
                raise TypeError
            if not isinstance(ax, ShapePloter.Axes):
                raise TypeError
        self.__fig = fig
        self.__ax = ax

    def gcf(self) -> ShapePloter.Figure:
        return self.__fig

    def gca(self) -> ShapePloter.Axes:
        return self.__ax

    def __getattr__(self, attr):
        return getattr(matplotlib.pyplot, attr)

    def plot(self, *args, **kwargs):
        if isinstance(args[0], BaseShape):
            self.plot_shape(args[0], kwargs=kwargs)
        else:
            return self.gca().plot(*args, **kwargs)

    def plot_shape(self, shape: BaseShape, *, kwargs={}):
        assert isinstance(shape, BaseShape)
        if isinstance(shape, EmptyShape):
            return
        attrs = ["pos_color", "neg_color", "fill_color", "alpha", "marker"]
        defas = ["red", "blue", "lime", 0.3, "o"]
        for key, default in zip(attrs, defas):
            kwargs[key] = default if key not in kwargs else kwargs[key]
        pos_color = kwargs.pop("pos_color")
        neg_color = kwargs.pop("neg_color")
        fill_color = kwargs.pop("fill_color")
        alpha = kwargs.pop("alpha")
        marker = kwargs.pop("marker")
        connecteds = shape.subshapes if isinstance(shape, DisjointShape) else [shape]
        for connected in connecteds:
            pos_points = []
            neg_points = []
            for jordan in connected.jordans:
                points = np.array(jordan.points(), dtype="float64").T
                if float(jordan) > 0:
                    pos_points.append(points)
                else:
                    neg_points.append(points)
            patch = patchify(pos_points + neg_points, fill_color, alpha)
            self.gca().add_patch(patch)
            for xvals, yvals in pos_points:
                self.plot(xvals, yvals, color=pos_color, **kwargs)
            for xvals, yvals in neg_points:
                self.plot(xvals, yvals, color=neg_color, **kwargs)
            for jordan in connected.jordans:
                xvals, yvals = np.array(jordan.points(0), dtype="float64").T
                color = pos_color if float(jordan) > 0 else neg_color
                self.scatter(xvals, yvals, color=color, marker=marker, **kwargs)
