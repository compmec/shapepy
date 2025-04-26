"""
This file contains tests functions to test the module polygon.py
"""

import pytest

from shapepy import default
from shapepy.analytic.elementar import piecewise, polynomial


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/analytic/test_polynomial.py::test_all",
    ],
    scope="session",
)
def test_begin():
    pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_begin"])
def test_build():
    polya = polynomial([1, 2])  # p(t) = 1 + 2*t
    polyb = polynomial([5, -2])  # p(t) = 5 - 2*t
    knots = ("-inf", 1, "+inf")
    piecewise([polya, polyb], knots)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_evaluate_natural():
    polya = polynomial([1, 2])  # p(t) = 1 + 2*t
    polyb = polynomial([5, -2])  # p(t) = 5 - 2*t
    knots = ("-inf", 1, "+inf")
    piece = piecewise([polya, polyb], knots)

    for node in range(-5, 1):
        assert piece.eval(node) == polya.eval(node)
    assert piece.eval(1) == polya.eval(1)
    assert piece.eval(1) == polyb.eval(1)
    for node in range(2, 6):
        assert piece.eval(node) == polyb.eval(node)


@pytest.mark.order(4)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_build"])
def test_compare():

    t = polynomial([0, 1])
    knots = ("-inf", 1, "+inf")
    piece1 = piecewise([1 + 2 * t, 5 - 2 * t], knots)
    assert piece1 == piece1

    piece2 = piecewise([1 - 2 * t, 3 + 4 * t], knots)
    assert piece1 != piece2

    assert piece1 != t
    assert piece1 != 5


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_compare"])
def test_derivate():
    polya = polynomial([1, 2])  # p(t) = 1 + 2*t
    polyb = polynomial([5, -2])  # p(t) = 5 - 2*t
    knots = ("-inf", 1, "+inf")
    piece = piecewise([polya, polyb], knots)

    for times in range(1, 3):
        derpolya = polya.derivate(times)
        derpolyb = polyb.derivate(times)
        good = piecewise([derpolya, derpolyb], knots)
        test = piece.derivate(times)
        assert test == good


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_evaluate_natural", "test_derivate"])
def test_evaluate_derivate():
    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = ("-inf", 0, "+inf")
    piece = piecewise([polya, polyb], knots)

    for nder in range(0, 5):
        for node in range(-10, 0):
            assert piece.eval(node, nder) == polya.eval(node, nder)
        # At 0, it's still to be defined
        for node in range(1, 11):
            assert piece.eval(node, nder) == polyb.eval(node, nder)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_compare"])
def test_add():
    t = polynomial([0, 1])
    poly11 = 1 - 2 * t
    poly12 = 1 + 5 * t
    poly21 = -4 + t
    poly22 = 1 + 4 * t
    piece1 = piecewise([poly11, poly12], ("-inf", 0, "+inf"))
    piece2 = piecewise([poly21, poly22], ("-inf", -1, "+inf"))

    good = piecewise(
        [poly11 + poly21, poly11 + poly22, poly12 + poly22],
        ("-inf", -1, 0, "+inf"),
    )
    assert piece1 + piece2 == good

    const = 5
    good = piecewise([const + poly11, const + poly12], ("-inf", 0, "+inf"))
    assert const + piece1 == good


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_compare"])
def test_sub():
    t = polynomial([0, 1])
    poly11 = 1 - 2 * t
    poly12 = 1 + 5 * t
    poly21 = -4 + t
    poly22 = 1 + 4 * t
    piece1 = piecewise([poly11, poly12], ("-inf", 0, "+inf"))
    piece2 = piecewise([poly21, poly22], ("-inf", -1, "+inf"))

    good = piecewise(
        [poly11 - poly21, poly11 - poly22, poly12 - poly22],
        ("-inf", -1, 0, "+inf"),
    )
    assert piece1 - piece2 == good

    const = 5
    good = piecewise([poly11 - const, poly12 - const], ("-inf", 0, "+inf"))
    assert piece1 - const == good


@pytest.mark.order(4)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_mul():
    t = polynomial([0, 1])
    poly11 = 1 - 2 * t
    poly12 = 1 + 5 * t
    poly21 = -4 + t
    poly22 = 1 + 4 * t
    piece1 = piecewise([poly11, poly12], ("-inf", 0, "+inf"))
    piece2 = piecewise([poly21, poly22], ("-inf", -1, "+inf"))

    good = piecewise(
        [poly11 * poly21, poly11 * poly22, poly12 * poly22],
        ("-inf", -1, 0, "+inf"),
    )
    assert piece1 * piece2 == good

    const = 5
    good = piecewise([const * poly11, const * poly12], ("-inf", 0, "+inf"))
    assert const * piece1 == good


@pytest.mark.order(4)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_div():
    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = ("-inf", 0, "+inf")
    piece = piecewise([polya, polyb], knots)

    piece / 10


@pytest.mark.order(4)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_shift():
    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)

    assert piece.shift(1).knots == (0, 1, 2)

    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = ("-inf", 0, 1)
    piece = piecewise([polya, polyb], knots)
    piece.shift(1)


@pytest.mark.order(4)
@pytest.mark.timeout(3)
@pytest.mark.dependency(depends=["test_compare"])
def test_scale():
    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)

    assert piece.scale(2).knots == (-2, 0, 2)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    pass


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_divide_zero():
    polya = polynomial([1, 2, 3, 4])
    polyb = polynomial([5, -2, 7, -9])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)
    with pytest.raises(ZeroDivisionError):
        piece / 0


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_definite_integral():
    polya = polynomial([1, 1])
    polyb = polynomial([1, -1])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)
    assert piece.integrate([-1, 1]) == 1


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_find_roots():
    polya = polynomial([1, 1])
    polyb = polynomial([1, -1])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)
    assert piece.where(0) == {-1, 1}


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_image():
    polya = polynomial([1, 1])
    polyb = polynomial([1, -1])

    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)
    assert piece.image() == [0, 1]

    knots = ("-inf", 0, "+inf")
    piece = piecewise([polya, polyb], knots)
    assert piece.image() == [default.NEGINF, 1]


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    polya = polynomial([1, 1])
    polyb = polynomial([1, -1])
    knots = (-1, 0, 1)
    piece = piecewise([polya, polyb], knots)

    str(piece)
    repr(piece)


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_begin",
        "test_build",
        "test_evaluate_natural",
    ]
)
def test_all():
    pass
