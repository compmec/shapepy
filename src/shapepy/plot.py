"""
This file is responsible to make it possible to plot the
bidimensional objects, like points, curves and shapes,
using the matplotlib library
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import matplotlib
import numpy as np
from matplotlib import pyplot

from .core import Empty, IObject2D, IShape, Whole
from .curve.abc import IJordanCurve
from .curve.polygon import JordanPolygon
from .shape import ConnectedShape, DisjointShape, SimpleShape

Path = matplotlib.path.Path
PathPatch = matplotlib.patches.PathPatch

DEFAULT_KWARGS = {
    "pos_color": "red",
    "neg_color": "blue",
    "fill_color": "lime",
    "alpha": 0.25,
    "marker": "o",
    "facecolor": "#BFFFBF",
}


def treat_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert into kwargs the pairs (key, value) from the
    DEFAULT_KWARGS if the given key does not exist.
    """
    for key, value in DEFAULT_KWARGS.items():
        if key not in kwargs:
            kwargs[key] = value
    return kwargs


def patch_polygon(jordan: JordanPolygon):
    """
    Create the commands to draw the jordan polygon
    """
    if not isinstance(jordan, JordanPolygon):
        raise TypeError
    pltverts = list(map(tuple, jordan.vertices))
    pltverts.append(pltverts[0])
    commands = [Path.MOVETO]
    commands += (len(pltverts) - 2) * [Path.LINETO]
    commands.append(Path.CLOSEPOLY)
    return pltverts, commands


def patch_jordan(jordan: IJordanCurve):
    """
    Creates the commands to draw an arbitrary jordan polygon
    """
    if isinstance(jordan, JordanPolygon):
        return patch_polygon(jordan)
    raise NotImplementedError


def path_jordan(jordan: IJordanCurve) -> Path:
    """
    Creates a Path, a matplotlib instance, that allows to draw
    on the plane
    """
    vertices, commands = patch_jordan(jordan)
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


def path_simple(simple: SimpleShape) -> Path:
    """
    Creates a Path of a simple shape
    """
    return path_jordan(simple.jordan)


def path_connected(connected: ConnectedShape) -> Path:
    """
    Creates a Path for a connected shape
    """
    vertices = []
    commands = []
    for simple in connected:
        newverts, newcomms = patch_jordan(simple.jordan)
        vertices += newverts
        commands += newcomms
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


class ShapePloter:
    """
    Creates a plotter instance, to behave just like

        matplotlib.pyplot

    So, you can create an instance and plot

    Examples
    --------
    >>> plt = ShapePloter()
    >>> plt.plot([0, 1], [0, 1])  # Draw straight segment
    >>> shape = Primitive.square(side = 4)
    >>> plt.plot(shape, fillcolor="green")
    >>> plt.show()
    """

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
        """
        Gives the actual figure used in the ploter
        """
        return self.__fig

    def gca(self) -> ShapePloter.Axes:
        """
        Gives the actual axis used in the plotter
        """
        return self.__ax

    def __getattr__(self, attr):
        return getattr(matplotlib.pyplot, attr)

    def plot(self, *args, **kwargs):
        """
        Plot the arguments.
        If it's not a package instance, just call the standard plot
        """
        obj = args[0]
        if not isinstance(obj, IObject2D):
            return self.gca().plot(*args, **kwargs)
        kwargs = treat_kwargs(kwargs)
        if isinstance(obj, (Empty, Whole)):
            return None
        if isinstance(obj, IShape):
            return self.plot_shape(obj, kwargs=kwargs)
        if isinstance(obj, IJordanCurve):
            return self.plot_jordan(obj, kwargs=kwargs)
        raise NotImplementedError(f"Received {type(obj)}")

    def plot_jordan(self, jordan: IJordanCurve, **kwargs):
        """
        Plot given jordan curve.

        Parameters
        ----------
        jordan: IJordanCurve
            The jordan curve to be ploted, can be positive or negative
        pos_color: str, default = "red"
            The color of the boundary if jordan curve is positive
        neg_color: str, default = "blue"
            The color of the boundary if jordan curve is negative
        marker: str or None, default = "o"
            The marker of the vertices.
            If it's None, then the marker is removed
        """
        if not isinstance(jordan, IJordanCurve):
            raise TypeError
        kwargs = treat_kwargs(kwargs)
        path = path_jordan(jordan)
        color = kwargs["pos_color"] if jordan.area > 0 else kwargs["neg_color"]
        patch = PathPatch(path, edgecolor=color, facecolor="none", lw=2)
        self.gca().add_patch(patch)
        if kwargs["marker"] is not None:
            vertices = tuple(map(tuple, jordan.vertices))
            xvals, yvals = np.transpose(vertices).astype("float64")
            self.gca().scatter(
                xvals, yvals, color=color, marker=kwargs["marker"]
            )

    def __plot_simple_shape(self, shape: SimpleShape, **kwargs):
        if not isinstance(shape, SimpleShape):
            raise TypeError
        path = path_simple(shape)
        if shape.area > 0:
            patch = PathPatch(
                path, color=kwargs["fill_color"], alpha=kwargs["alpha"]
            )
        else:
            self.gca().set_facecolor(kwargs["facecolor"])
            patch = PathPatch(path, color="white", alpha=1)
        self.gca().add_patch(patch)
        self.plot_jordan(shape.jordan, **kwargs)

    def __plot_connected_shape(self, shape: ConnectedShape, **kwargs):
        if not isinstance(shape, ConnectedShape):
            raise TypeError
        path = path_connected(shape)
        if shape.area > 0:
            patch = PathPatch(
                path, color=kwargs["fill_color"], alpha=kwargs["alpha"]
            )
        else:
            self.gca().set_facecolor(kwargs["facecolor"])
            patch = PathPatch(path, color="white", alpha=1)
        self.gca().add_patch(patch)
        for subshape in shape:
            self.__plot_jordan_curve(subshape.jordan, **kwargs)

    def __plot_disjoint_shape(self, shape: DisjointShape, **kwargs):
        if not isinstance(shape, DisjointShape):
            raise TypeError
        for subshape in shape:
            if isinstance(subshape, SimpleShape):
                self.__plot_simple_shape(subshape, **kwargs)
            elif isinstance(subshape, ConnectedShape):
                self.__plot_connected_shape(subshape, **kwargs)

    def plot_shape(self, obj: IShape, **kwargs):
        """
        Plot the given shape

        Parameters
        ----------
        obj: IShape
            The shape to be plotted
        pos_color: str, default = "red"
            The boundary color of jordan's curve if it's positive
        neg_color: str, default = "blue"
            The boundary color of jordan's curve if it's negative
        alpha: float, default = 0.25
            The transparency of the internal region
        fill_color: str, default = "lime"
            The color of the internal region
        """
        kwargs = treat_kwargs(kwargs)
        if isinstance(obj, SimpleShape):
            return self.__plot_simple_shape(obj, **kwargs)
        if isinstance(obj, ConnectedShape):
            return self.__plot_connected_shape(obj, **kwargs)
        if isinstance(obj, DisjointShape):
            return self.__plot_disjoint_shape(obj, **kwargs)
        raise NotImplementedError(f"Not expected get here {type(obj)}")
