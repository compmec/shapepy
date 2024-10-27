"""
Tests related to shape module, more specifically about the class SimpleShape
Which are in fact positive shapes defined only by one jordan curve 
"""

import pytest

from shapepy.bounding import BoundCircle, BoundRectangle


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/test_point.py::test_end",
    ],
    scope="session",
)
def test_begin():
    pass


class TestRectangle:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestRectangle::test_begin"])
    def test_create(self):
        BoundRectangle((0, 0), (1, 1))

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
        ]
    )
    def test_winding(self):
        rect = BoundRectangle((0, 0), (2, 2))

        # Outside
        points = [(-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3)]
        points += [(0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1)]
        points += [(3, 0), (3, -1), (2, -1), (1, -1), (0, -1), (-1, -1)]
        for point in points:
            assert rect.winding(point) == 0

        # Boundary
        points = [(0, 0), (2, 0), (2, 2), (0, 2)]
        for point in points:
            assert rect.winding(point) == 0.25
        points = [(1, 0), (2, 1), (1, 2), (0, 1)]
        for point in points:
            assert rect.winding(point) == 0.5

        # Inside
        for xval in (0.5, 1, 1.5):
            for yval in (0.5, 1, 1.5):
                assert rect.winding((xval, yval)) == 1

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
        ]
    )
    def test_contains(self):
        rect = BoundRectangle((0, 0), (2, 2))

        # Outside
        points = [(-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3)]
        points += [(0, 3), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1)]
        points += [(3, 0), (3, -1), (2, -1), (1, -1), (0, -1), (-1, -1)]
        for point in points:
            assert point not in rect

        # Boundary
        points = [(0, 0), (2, 0), (2, 2), (0, 2)]
        points += [(1, 0), (2, 1), (1, 2), (0, 1)]
        for point in points:
            assert point in rect

        # Inside
        for xval in (0.5, 1, 1.5):
            for yval in (0.5, 1, 1.5):
                point = (xval, yval)
                assert point in rect

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
        ]
    )
    def test_compare(self):
        recta = BoundRectangle((0, 0), (2, 2))
        rectb = BoundRectangle((0, 0), (2, 2))
        rectc = BoundRectangle((-1, -1), (2, 2))
        assert recta == rectb
        assert recta != rectc

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
            "TestRectangle::test_compare",
        ]
    )
    def test_union(self):
        recta = BoundRectangle((0, 0), (2, 2))
        rectb = BoundRectangle((-1, -1), (1, 1))
        rectc = BoundRectangle((-1, -1), (2, 2))
        assert recta | rectb == rectc

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
            "TestRectangle::test_compare",
        ]
    )
    def test_intersect(self):
        recta = BoundRectangle((0, 0), (2, 2))
        rectb = BoundRectangle((-1, -1), (1, 1))
        rectc = BoundRectangle((0, 0), (1, 1))
        assert recta & rectb == rectc

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
            "TestRectangle::test_contains",
            "TestRectangle::test_compare",
            "TestRectangle::test_union",
            "TestRectangle::test_intersect",
        ]
    )
    def test_end(self):
        pass


class TestCircle:
    @pytest.mark.order(3)
    @pytest.mark.dependency(depends=["test_begin"])
    def test_begin(self):
        pass

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(depends=["TestCircle::test_begin"])
    def test_create(self):
        BoundCircle((0, 0), 1)

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_create",
        ]
    )
    def test_winding(self):
        radius = 5
        circle = BoundCircle((0, 0), radius)

        assert circle.winding((2 * radius, 2 * radius)) == 0
        assert circle.winding((0, 0)) == 1
        assert circle.winding((radius, 0)) == 0.5
        assert circle.winding((0, radius)) == 0.5

        for xval in range(-2 * radius, 2 * radius + 1):
            for yval in range(-2 * radius, 2 * radius + 1):
                diff = xval**2 + yval**2 - radius**2
                wind = 0 if diff > 0 else 1 if diff < 0 else 0.5
                assert circle.winding((xval, yval)) == wind

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_create",
            "TestCircle::test_winding",
        ]
    )
    def test_contains(self):
        radius = 5
        circle = BoundCircle((0, 0), radius)

        for xval in range(-10, 11):
            for yval in range(-10, 11):
                inside = xval**2 + yval**2 <= radius**2
                if inside:
                    assert (xval, yval) in circle
                else:
                    assert (xval, yval) not in circle

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
        ]
    )
    def test_compare(self):
        circa = BoundCircle((0, 0), 2)
        circb = BoundCircle((0, 0), 2)
        circc = BoundCircle((-1, -1), 2)
        circd = BoundCircle((0, 0), 3)
        assert circa == circb
        assert circa != circc
        assert circa != circd
        assert circc != circd

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
        ]
    )
    def test_union(self):
        circa = BoundCircle((0, 0), 2)
        circb = BoundCircle((0, 0), 4)
        assert circa | circb == circb

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestRectangle::test_begin",
            "TestRectangle::test_create",
            "TestRectangle::test_winding",
        ]
    )
    def test_intersect(self):
        circa = BoundCircle((0, 0), 2)
        circb = BoundCircle((0, 0), 4)
        assert circa & circb == circa

    @pytest.mark.order(3)
    @pytest.mark.timeout(10)
    @pytest.mark.dependency(
        depends=[
            "TestCircle::test_begin",
            "TestCircle::test_create",
            "TestCircle::test_winding",
            "TestCircle::test_contains",
            "TestCircle::test_compare",
            "TestCircle::test_union",
            "TestCircle::test_intersect",
        ]
    )
    def test_end(self):
        pass


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "TestRectangle::test_end",
        "TestCircle::test_end",
    ]
)
def test_end():
    pass
