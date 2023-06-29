import pytest

from compmec.shape.primitive import regular_polygon


@pytest.mark.order(2)
@pytest.mark.dependency()
def test_begin():
    pass


class TestInitial:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_create_regular(self):
        regular_polygon(3)
        regular_polygon(4)
        regular_polygon(5)
        regular_polygon(101)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_error_create_regular(self):
        with pytest.raises(TypeError):
            regular_polygon("asd")
        with pytest.raises(ValueError):
            regular_polygon(2)
        with pytest.raises(ValueError):
            regular_polygon(-1)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestInitial::test_begin",
            "TestInitial::test_create_regular",
            "TestInitial::test_error_create_regular",
        ]
    )
    def test_end(self):
        pass


class TestTransformation:
    @pytest.mark.order(2)
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_move(self):
        square = regular_polygon(4)
        square.move(1, 2)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_rotate(self):
        square = regular_polygon(4)
        square.rotate_degrees(45)
        square.rotate_radians(45)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_scale(self):
        square = regular_polygon(4)
        square.scale(2, 3)

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["TestTransformation::test_begin"])
    def test_invert(self):
        square = regular_polygon(4)
        square.invert()

    @pytest.mark.order(2)
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


class TestOperations:
    @pytest.mark.order(2)
    @pytest.mark.skip(reason="Needs implementation")
    @pytest.mark.dependency(depends=["TestInitial::test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_sum_regular(self):
        triangle = regular_polygon(3)
        square = regular_polygon(4)
        triangle + square
        triangle | square
        triangle or square

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_sub_regular(self):
        triangle = regular_polygon(3)
        square = regular_polygon(4)
        triangle - square
        square - triangle

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_mul_regular(self):
        triangle = regular_polygon(3)
        square = regular_polygon(4)
        triangle * square
        triangle & square
        square and triangle

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(depends=["TestOperations::test_begin"])
    def test_xor_regular(self):
        triangle = regular_polygon(3)
        square = regular_polygon(4)
        triangle ^ square

    @pytest.mark.order(2)
    @pytest.mark.timeout(1)
    @pytest.mark.dependency(
        depends=[
            "TestOperations::test_sum_regular",
            "TestOperations::test_sub_regular",
            "TestOperations::test_mul_regular",
            "TestOperations::test_xor_regular",
        ]
    )
    def test_end(self):
        pass
