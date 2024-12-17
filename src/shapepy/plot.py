from __future__ import annotations

from typing import Optional

import matplotlib
import numpy as np
from matplotlib import pyplot

from .core import Empty, IObject2D, IShape, Whole
from .curve.abc import IJordanCurve
from .curve.polygon import JordanPolygon
from .shape import ConnectedShape, DisjointShape, SimpleShape

Path = matplotlib.path.Path
PathPatch = matplotlib.patches.PathPatch


def patch_polygon(jordan: JordanPolygon):
    if not isinstance(jordan, JordanPolygon):
        raise TypeError
    pltverts = list(map(tuple, jordan.vertices))
    pltverts.append(pltverts[0])
    commands = [Path.MOVETO]
    commands += (len(pltverts) - 2) * [Path.LINETO]
    commands.append(Path.CLOSEPOLY)
    return pltverts, commands


def patch_jordan(jordan: IJordanCurve):
    if isinstance(jordan, JordanPolygon):
        return patch_polygon(jordan)
    raise NotImplementedError


def path_jordan(jordan: IJordanCurve) -> Path:
    vertices, commands = patch_jordan(jordan)
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


def path_simple(simple: SimpleShape) -> Path:
    vertices, commands = patch_jordan(simple.jordan)
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


def path_connected(connected: ConnectedShape) -> Path:
    vertices = []
    commands = []
    for simple in connected:
        newverts, newcomms = patch_jordan(simple.jordan)
        vertices += newverts
        commands += newcomms
    vertices = tuple(tuple(map(float, point)) for point in vertices)
    return Path(vertices, commands)


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
        if isinstance(args[0], IShape):
            self.plot_shape(args[0], kwargs=kwargs)
        else:
            return self.gca().plot(*args, **kwargs)

    def __plot_jordan_curve(self, jordan: IJordanCurve, **kwargs):
        if not isinstance(jordan, IJordanCurve):
            raise TypeError
        path = path_jordan(jordan)
        color = kwargs["pos_color"] if jordan.area > 0 else kwargs["neg_color"]
        patch = PathPatch(path, edgecolor=color, facecolor="none", lw=2)
        self.gca().add_patch(patch)
        vertices = tuple(map(tuple, jordan.vertices))
        xvals, yvals = np.array(vertices, dtype="float64").T
        self.gca().scatter(xvals, yvals, color=color, marker=kwargs["marker"])

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
        self.__plot_jordan_curve(shape.jordan, **kwargs)

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

    def plot_shape(self, object: IObject2D, **kwargs):
        if isinstance(object, Empty):
            return
        if "pos_color" not in kwargs:
            kwargs["pos_color"] = "red"
        if "neg_color" not in kwargs:
            kwargs["neg_color"] = "blue"
        if "fill_color" not in kwargs:
            kwargs["fill_color"] = "lime"
        if "alpha" not in kwargs:
            kwargs["alpha"] = 0.25
        if "marker" not in kwargs:
            kwargs["marker"] = "o"
        if "facecolor" not in kwargs:
            kwargs["facecolor"] = "#BFFFBF"
        if isinstance(object, Whole):
            self.gca().set_facecolor(kwargs["facecolor"])
            return
        if isinstance(object, IJordanCurve):
            return self.__plot_jordan_curve(object, **kwargs)
        if isinstance(object, SimpleShape):
            return self.__plot_simple_shape(object, **kwargs)
        if isinstance(object, ConnectedShape):
            return self.__plot_connected_shape(object, **kwargs)
        if isinstance(object, DisjointShape):
            return self.__plot_disjoint_shape(object, **kwargs)
