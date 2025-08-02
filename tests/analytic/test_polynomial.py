import numpy as np
import pytest

from shapepy.analytic.polynomial import Polynomial, scale, shift


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_reals.py::test_all",
        "tests/scalar/test_angle.py::test_all",
    ],
    scope="session",
)
def test_build():
    Polynomial([0])  # p(t) = 0
    Polynomial([1])  # p(t) = 1
    Polynomial([1, 2])  # p(t) = 1 + 2 * t
    Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    Polynomial([1.0, 2, -3.0])  # p(t) = 1.0 + 2 * t - 3.0 * t^2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_degree():
    poly = Polynomial([0])  # p(t) = 0
    assert poly.degree == 0
    poly = Polynomial([1])  # p(t) = 1
    assert poly.degree == 0
    poly = Polynomial([1, 2])  # p(t) = 1 + 2 * t
    assert poly.degree == 1
    poly = Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    assert poly.degree == 2


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_coefficients():
    bezier = Polynomial([0])
    assert bezier[0] == 0
    bezier = Polynomial([1])
    assert bezier[0] == 1
    bezier = Polynomial([1, 2])
    assert bezier[0] == 1
    assert bezier[1] == 2
    bezier = Polynomial([1, 2, 3])
    assert bezier[0] == 1
    assert bezier[1] == 2
    assert bezier[2] == 3


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build", "test_degree"])
def test_compare():
    poly = Polynomial([0])
    assert poly == 0
    assert poly != 1
    assert poly != "asd"

    polya = Polynomial([3, 2])
    polyb = Polynomial([3.0, 2.0])
    assert polya == polyb


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build", "test_degree"])
def test_evaluate():
    poly = Polynomial([0])  # p(t) = 0
    assert poly(0) == 0
    assert poly(-1) == 0
    assert poly(2) == 0
    poly = Polynomial([1])  # p(t) = 1
    assert poly(0) == 1
    assert poly(-1) == 1
    assert poly(2) == 1
    poly = Polynomial([1, 2])  # p(t) = 1 + 2 * t
    assert poly(0) == 1
    assert poly(-1) == 1 + 2 * (-1)
    assert poly(2) == 1 + 2 * (+2)
    poly = Polynomial([1, 2, 3])  # p(t) = 1 + 2 * t + 3 * t^2
    assert poly(0) == 1
    assert poly(-1) == 1 + 2 * (-1) + 3 * (-1) * (-1)
    assert poly(2) == 1 + 2 * (+2) + 3 * (+2) * (+2)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_neg():
    polya = Polynomial([1, 2, 3, 4])
    polyb = Polynomial([-1, -2, -3, -4])

    assert -polya == polyb


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_add():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    np.random.seed(0)

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(-1, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        polya = Polynomial(coefsa)
        polyb = Polynomial(coefsb)
        polyc = polya + polyb
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa + valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        polya = Polynomial(coefsa)
        polyb = polya + const
        polyc = const + polya
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa + const, valuesb)
        np.testing.assert_allclose(const + valuesa, valuesc)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_sub():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    np.random.seed(0)

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(-1, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        polya = Polynomial(coefsa)
        polyb = Polynomial(coefsb)
        polyc = polya - polyb
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa - valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        polya = Polynomial(coefsa)
        polyb = polya - const
        polyc = const - polya
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa - const, valuesb)
        np.testing.assert_allclose(const - valuesa, valuesc)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=["test_build", "test_degree", "test_evaluate", "test_compare"]
)
def test_mul():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    np.random.seed(0)

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(-1, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        polya = Polynomial(coefsa)
        polyb = Polynomial(coefsb)
        polyc = polya * polyb
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa * valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        polya = Polynomial(coefsa)
        polyb = polya * const
        polyc = const * polya
        valuesa = polya(tsample)
        valuesb = polyb(tsample)
        valuesc = polyc(tsample)

        np.testing.assert_allclose(valuesa * const, valuesb)
        np.testing.assert_allclose(const * valuesa, valuesc)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_compare",
        "test_mul",
    ]
)
def test_pow():
    poly = Polynomial([-1, 1])
    assert poly**0 == 1
    assert poly**1 == poly
    assert poly**2 == poly * poly
    assert poly**3 == poly * poly * poly


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_add",
        "test_mul",
    ]
)
def test_shift():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    np.random.seed(0)

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(-1, 1, 17)
    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        polya = Polynomial(coefsa)
        polyb = shift(polya, 1)
        valuesa = polya(tsample)
        valuese = polyb(1 + tsample)

        np.testing.assert_allclose(valuese, valuesa)


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_add",
        "test_mul",
    ]
)
def test_scale():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    np.random.seed(0)

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(-1, 1, 17)
    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        polya = Polynomial(coefsa)
        polyb = scale(polya, 2)
        valuesa = polya(2 * tsample)
        valuesb = polyb(tsample)

        np.testing.assert_allclose(valuesb, valuesa)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    poly = Polynomial([0])
    assert str(poly) == "0"
    poly = Polynomial([1])
    assert str(poly) == "1"
    poly = Polynomial([0, 1])
    assert str(poly) == "t"
    repr(poly)

    poly = Polynomial([1, 2, 3])
    assert str(poly) == "1 + 2 * t + 3 * t^2"
    repr(poly)


@pytest.mark.order(3)
@pytest.mark.dependency(depends=["test_build"])
def test_numpy_array():
    degree = 3
    coefs = np.zeros((degree + 1, 3), dtype="int64")
    poly = Polynomial(coefs)
    assert poly.degree == 0
    assert tuple(poly[0]) == (0, 0, 0)
    str(poly)
    repr(poly)

    coefs = ((3, 2), (-4, 1), (1, -3))
    coefs = np.array(coefs, dtype="int64")
    poly = Polynomial(coefs)
    str(poly)
    repr(poly)

    square = poly @ poly
    assert square.degree == 4
    assert square == Polynomial([13, -20, 11, -14, 10])
    point = np.array([2, 1], dtype="int64")
    assert poly @ point == Polynomial([8, -7, -1])


@pytest.mark.order(3)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_degree",
        "test_evaluate",
        "test_neg",
        "test_add",
        "test_sub",
        "test_mul",
        "test_pow",
        "test_shift",
        "test_scale",
    ]
)
def test_all():
    pass
