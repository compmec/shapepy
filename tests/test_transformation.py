import pytest

from compmec.shape.primitive import regular_polygon


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
        "tests/test_comparison.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestTransformation:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_move(self):
        square = regular_polygon(4)
        square.move(1, 2)

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_rotate(self):
        square = regular_polygon(4)
        square.rotate_degrees(45)
        square.rotate_radians(45)

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_scale(self):
        square = regular_polygon(4)
        square.scale(2, 3)

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_invert(self):
        square = regular_polygon(4)
        square.invert()

    @pytest.mark.order(3)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestTransformation::test_move",
            "TestTransformation::test_rotate",
            "TestTransformation::test_scale",
            "TestTransformation::test_invert",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_begin", "TestTransformation::test_end"])
def test_end():
    pass
