"""
Defines functions that allows plotting the figures made,
like shapes, curves, points, doing projections and so on
"""

from __future__ import annotations

from typing import Optional

import matplotlib
import numpy as np
from matplotlib import pyplot

from shapepy.curve import PlanarCurve
from shapepy.jordancurve import JordanCurve
from shapepy.shape import (
    BaseShape,
    ConnectedShape,
    DisjointShape,
    EmptyShape,
    WholeShape,
)

Path = matplotlib.path.Path
PathPatch = matplotlib.patches.PathPatch


def patch_segment(segment: PlanarCurve):
    """
    Creates the commands for matplotlib to plot the segment
    """
    vertices = []
    commands = []
    if segment.degree == 1:
        vertices.append(segment.ctrlpoints[1])
        commands.append(Path.LINETO)
    elif segment.degree == 2:
        vertices += list(segment.ctrlpoints[1:])
        commands += [Path.CURVE3] * 2
    return vertices, commands


def path_shape(connected: ConnectedShape) -> Path:
    """
    Creates the commands for matplotlib to plot the shape
    """
    vertices = []
    commands = []
    for jordan in connected.jordans:
        vertices.append(jordan.segments[0].ctrlpoints[0])
        commands.append(Path.MOVETO)
        for segment in jordan.segments:
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
    vertices = [jordan.segments[0].ctrlpoints[0]]
    commands = [Path.MOVETO]
    for segment in jordan.segments:
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
            if isinstance(ax, list) and len(ax) == 0:
                ax = pyplot.gca()
        else:
            if not isinstance(fig, matplotlib.figure.Figure):
                raise TypeError
            if not isinstance(ax, type(matplotlib.pyplot.gca())):
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
        if isinstance(args[0], BaseShape):
            return self.plot_shape(args[0], kwargs=kwargs)
        return self.gca().plot(*args, **kwargs)

    # pylint: disable=too-many-locals
    def plot_shape(self, shape: BaseShape, *, kwargs):
        """
        Plots a BaseShape, which can be Empty, Whole, Simple, etc
        """
        assert isinstance(shape, BaseShape)
        if isinstance(shape, EmptyShape):
            return
        if isinstance(shape, WholeShape):
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
        connecteds = (
            shape.subshapes if isinstance(shape, DisjointShape) else [shape]
        )
        for connected in connecteds:
            path = path_shape(connected)
            if float(connected) > 0:
                patch = PathPatch(path, color=fill_color, alpha=alpha)
            else:
                self.gca().set_facecolor("#BFFFBF")
                patch = PathPatch(path, color="white", alpha=1)
            self.gca().add_patch(patch)
            for jordan in connected.jordans:
                path = path_jordan(jordan)
                color = pos_color if float(jordan) > 0 else neg_color
                patch = PathPatch(
                    path, edgecolor=color, facecolor="none", lw=2
                )
                self.gca().add_patch(patch)
                xvals, yvals = np.array(jordan.points(0), dtype="float64").T
                self.gca().scatter(xvals, yvals, color=color, marker=marker)
