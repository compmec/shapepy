"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest
from matplotlib import pyplot

from compmec.shape import ShapePloter
from compmec.shape.primitive import Primitive


@pytest.mark.order(13)
@pytest.mark.skip()
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
    def test_get_started(self):
        circle = Primitive.circle(radius=1, center=(0, 0))
        square = Primitive.square(side=2, center=(-1, 0))
        left_shape = square + circle  # Unite shapes

        right_shape = left_shape.copy()
        right_shape.rotate(180, degrees=True)
        right_shape.move((0, -1))

        union_shape = left_shape | right_shape
        intersection_shape = left_shape & right_shape

        plt = ShapePloter()
        plt.plot(left_shape, fill_color="cyan")
        plt.plot(right_shape, fill_color="yellow")

        plt = ShapePloter()
        plt.plot(union_shape)

        plt = ShapePloter()
        plt.plot(intersection_shape)

        # plt.show()

    @pytest.mark.order(13)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestPlot::test_begin",
            "TestPlot::test_create",
            "TestPlot::test_get_started",
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
