import pytest

from compmec.shape import primitive


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/test_buildup.py::test_end",
        "tests/test_comparison.py::test_end",
        "tests/test_transformation.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestOperation:
    @pytest.mark.order(4)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_sum_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle + square
        triangle | square
        triangle or square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_sub_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle - square
        square - triangle

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_mul_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle * square
        triangle & square
        square and triangle

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperation::test_begin"])
    def test_xor_regular(self):
        triangle = primitive.regular_polygon(3)
        square = primitive.regular_polygon(4)
        triangle ^ square

    @pytest.mark.order(4)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestOperation::test_sum_regular",
            "TestOperation::test_sub_regular",
            "TestOperation::test_mul_regular",
            "TestOperation::test_xor_regular",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin", "TestOperation::test_end"])
def test_end():
    pass
