"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest
from matplotlib import pyplot

from shapepy import ShapePloter
from shapepy.primitive import Primitive


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "tests/test_shape.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestPlot:
    @pytest.mark.order(13)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestPlot::test_begin"])
    def test_create(self):
        ShapePloter()
        fig = pyplot.figure()
        ShapePloter(fig=fig)
        ax = pyplot.gca()
        ShapePloter(ax=ax)
        ShapePloter(fig=fig, ax=ax)

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlot::test_begin",
            "TestPlot::test_create",
        ]
    )
    def test_simple(self):
        circle = Primitive.circle(radius=1, center=(0, 0))
        square = Primitive.square(side=1, center=(0, 0))

        plt = ShapePloter()
        plt.plot(circle, fill_color="cyan")
        plt.plot(square, fill_color="yellow")

        circle.invert()
        fig, ax = pyplot.subplots()
        plt = ShapePloter(fig=fig, ax=ax)
        plt.plot(circle)

        # plt.show()

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlot::test_begin",
            "TestPlot::test_create",
            "TestPlot::test_simple",
        ]
    )
    def test_connected(self):
        circle = Primitive.circle(radius=1, center=(0, 0))
        square = Primitive.square(side=0.3, center=(0, 0))
        hollow = circle - square

        plt = ShapePloter()
        plt.plot(hollow, fill_color="cyan")

        left = ~Primitive.circle(radius=1, center=(-2, 0))
        right = ~Primitive.square(side=1, center=(2, 0))
        shape = left & right

        plt = ShapePloter()
        plt.plot(shape)

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlot::test_begin",
            "TestPlot::test_create",
            "TestPlot::test_simple",
            "TestPlot::test_connected",
        ]
    )
    def test_disjoint(self):
        left = Primitive.circle(radius=1, center=(-1, 0))
        right = Primitive.square(side=2, center=(4, 0))
        shape = left + right  # Unite shapes

        plt = ShapePloter()
        plt.plot(shape, fill_color="cyan")

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlot::test_begin",
            "TestPlot::test_create",
            "TestPlot::test_simple",
            "TestPlot::test_connected",
            "TestPlot::test_disjoint",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(13)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestPlot::test_end",
    ]
)
def test_end():
    pass
