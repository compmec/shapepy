import numpy as np
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
    def test_error_create_regular_polygon(self):
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
            "TestInitial::test_reverse",
            "TestInitial::test_moved_circle",
            "TestInitial::test_elipse",
            "TestInitial::test_rectangle",
        ]
    )
    def test_end(self):
        pass




