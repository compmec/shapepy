"""
Defines functions that allows plotting the figures made,
like shapes, curves, points, doing projections and so on
"""

from __future__ import annotations

from typing import Iterator, Optional, Union

import matplotlib
from matplotlib import pyplot

from shapepy.bool2d.base import EmptyShape, WholeShape
from shapepy.bool2d.shape import (
    ConnectedShape,
    DisjointShape,
    SimpleShape,
    SubSetR2,
)
from shapepy.geometry.jordancurve import JordanCurve
from shapepy.geometry.segment import Segment

from ..analytic import Bezier
from ..tools import Is

Path = matplotlib.path.Path
PathPatch = matplotlib.patches.PathPatch


def patch_segment(segment: Segment):
    """
    Creates the commands for matplotlib to plot the segment
    """
    assert Is.instance(segment, Segment)
    vertices = []
    commands = []
    xfunc, yfunc = segment.xfunc, segment.yfunc
    if xfunc.degree <= 1 and yfunc.degree <= 1:
        vertices.append(segment(segment.knots[-1]))
        commands.append(Path.LINETO)
    elif xfunc.degree == 2 and yfunc.degree == 2:
        xfunc: Bezier = segment.xfunc
        yfunc: Bezier = segment.yfunc
        ctrlpoints = tuple(zip(xfunc, yfunc))
        vertices += list(ctrlpoints[1:])
        commands += [Path.CURVE3] * 2
    return vertices, commands


def path_shape(simples: Iterator[SimpleShape]) -> Path:
    """
    Creates the commands for matplotlib to plot the shape
    """
    vertices = []
    commands = []
    for simple in simples:
        if not Is.instance(simple, SimpleShape):
            raise TypeError(f"Invalid type: {type(simple)}")
        segments = tuple(simple.jordan.parametrize())
        vertices.append(segments[0](segments[0].knots[0]))
        commands.append(Path.MOVETO)
        for segment in segments:
            verts, comms = patch_segment(segment)
            vertices += verts
            commands += comms
        vertices.append(vertices[0])
        commands.append(Path.CLOSEPOLY)
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


def path_jordan(jordan: JordanCurve) -> Path:
    """
    Creates the commands for matplotlib to plot the jordan curve
    """
    segments = tuple(useg.parametrize() for useg in jordan)
    vertices = [segments[0](segments[0].knots[0])]
    commands = [Path.MOVETO]
    for segment in segments:
        verts, comms = patch_segment(segment)
        vertices += verts
        commands += comms
    vertices.append(vertices[0])
    commands.append(Path.CLOSEPOLY)
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    vertices = tuple(
        tuple(1e-6 * round(1e6 * val) for val in point) for point in vertices
    )
    return Path(vertices, commands)


def shape2union_intersections(
    shape: Union[SimpleShape, ConnectedShape, DisjointShape],
) -> Iterator[Iterator[SimpleShape]]:
    """Function used to transform any shape as a union
    of intersection of simple shapes"""
    if Is.instance(shape, SimpleShape):
        return [[shape]]
    if Is.instance(shape, ConnectedShape):
        return [list(shape)]
    result = []
    for sub in shape:
        result.append([sub] if Is.instance(sub, SimpleShape) else tuple(sub))
    return result


class ShapePloter:
    """
    Class which is a wrapper of the matplotlib.pyplot.plt

    You can create the instance of this class and call the same way as plt

    Example
    -------
    >>> plt = ShapePloter()
    >>> plot.plot([0, 1], [3, -2])
    >>> plt.show()
    """

    Figure = matplotlib.pyplot.gcf()
    Axes = matplotlib.pyplot.gca()

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
            if Is.instance(ax, list) and len(ax) == 0:
                ax = pyplot.gca()
        else:
            if not Is.instance(fig, matplotlib.figure.Figure):
                raise TypeError
            if not Is.instance(ax, type(matplotlib.pyplot.gca())):
                raise TypeError
        self.__fig = fig
        self.__ax = ax

    def gcf(self) -> ShapePloter.Figure:
        """
        Gets the current figure
        """
        return self.__fig

    def gca(self) -> ShapePloter.Axes:
        """
        Gets the current axis
        """
        return self.__ax

    def __getattr__(self, attr):
        return getattr(matplotlib.pyplot, attr)

    def plot(self, *args, **kwargs):
        """
        A wrapper of the matplotlib.pyplot.plt.plot
        """
        if Is.instance(args[0], SubSetR2):
            return self.plot_subset(args[0], kwargs=kwargs)
        return self.gca().plot(*args, **kwargs)

    # pylint: disable=too-many-locals
    def plot_subset(self, shape: SubSetR2, *, kwargs):
        """
        Plots a SubSetR2, which can be EmptyShape, WholeShape, Simple, etc
        """
        assert Is.instance(shape, SubSetR2)
        shape = shape.clean()
        if Is.instance(shape, EmptyShape):
            return
        if Is.instance(shape, WholeShape):
            self.gca().set_facecolor("#BFFFBF")
            return
        attrs = ["pos_color", "neg_color", "fill_color", "alpha", "marker"]
        defas = ["red", "blue", "lime", 0.25, "o"]
        for key, default in zip(attrs, defas):
            kwargs[key] = default if key not in kwargs else kwargs[key]
        pos_color = kwargs.pop("pos_color")
        neg_color = kwargs.pop("neg_color")
        fill_color = kwargs.pop("fill_color")
        alpha = kwargs.pop("alpha")
        marker = kwargs.pop("marker")
        connecteds = tuple(map(tuple, shape2union_intersections(shape)))
        for connected in connecteds:
            path = path_shape(connected)
            if sum(s.area for s in connected) > 0:
                patch = PathPatch(path, color=fill_color, alpha=alpha)
            else:
                self.gca().set_facecolor("#BFFFBF")
                patch = PathPatch(path, color="white", alpha=1)
            self.gca().add_patch(patch)
            for simple in connected:
                path = path_jordan(simple.jordan)
                color = pos_color if simple.jordan.area > 0 else neg_color
                patch = PathPatch(
                    path, edgecolor=color, facecolor="none", lw=2
                )
                self.gca().add_patch(patch)
                xvals, yvals = zip(*simple.jordan.vertices())
                self.gca().scatter(xvals, yvals, color=color, marker=marker)
