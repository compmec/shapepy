import numpy as np
import pytest

from shapepy.scalar.bezier import (
    Bezier,
    bezier2polynomial,
    bezier_caract_matrix,
    clean,
    inverse_caract_matrix,
    polynomial2bezier,
    split,
)
from shapepy.scalar.polynomial import Polynomial


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "tests/scalar/test_polynomial.py::test_all",
    ],
    scope="session",
)
def test_build():
    Bezier([0])  # p(t) = 0
    Bezier([1])  # p(t) = 1
    Bezier([1, 2])  # p(t) = 1 * B_01 + 2 * B_11
    Bezier([1, 2, 3])  # p(t) = 1 * B_02 + 2 * B_12 + 3 * B_22
    Bezier([1.0, 2, -3.0])  # p(t) = 1.0 * B_02 + 2.0 * B_12 - 3.0 * B_22


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_degree():
    bezier = Bezier([0])
    assert bezier.degree == 0
    bezier = Bezier([1])
    assert bezier.degree == 0
    bezier = Bezier([1, 2])
    assert bezier.degree == 1
    bezier = Bezier([1, 2, 3])
    assert bezier.degree == 2


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_coefficients():
    bezier = Bezier([0])
    assert bezier[0] == 0
    bezier = Bezier([1])
    assert bezier[0] == 1
    bezier = Bezier([1, 2])
    assert bezier[0] == 1
    assert bezier[1] == 2
    bezier = Bezier([1, 2, 3])
    assert bezier[0] == 1
    assert bezier[1] == 2
    assert bezier[2] == 3


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree"])
def test_matrices():
    for degree in range(6):
        matrix = bezier_caract_matrix(degree)
        invmat = inverse_caract_matrix(degree)
        test = np.dot(matrix, invmat)
        assert np.all(test == np.eye(degree + 1))
        test = np.dot(invmat, matrix)
        assert np.all(test == np.eye(degree + 1))


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_matrices"])
def test_compare():
    bezier = Bezier([1])
    assert bezier == Polynomial([1])
    assert bezier == 1

    bezier = Bezier([1, 1, 1])
    assert bezier == Polynomial([1])
    assert bezier == 1

    bezier = Bezier([1, 2])
    assert bezier == Polynomial([1, 1])
    bezier = Bezier([1, 2, 3])
    assert bezier == Polynomial([1, 2])

    assert bezier != 1
    assert bezier != "asd"


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_matrices"])
def test_evaluate():
    bezier = Bezier([0])
    assert bezier(0) == 0
    assert bezier(0.5) == 0
    assert bezier(1) == 0
    bezier = Bezier([1])
    assert bezier(0) == 1
    assert bezier(0.5) == 1
    assert bezier(1) == 1
    bezier = Bezier([1, 2])
    assert bezier(0) == 1
    assert bezier(0.5) == 1.5
    assert bezier(1) == 2
    bezier = Bezier([1, 2, 3])
    assert bezier(0) == 1
    assert bezier(0.25) == 1.5
    assert bezier(0.5) == 2
    assert bezier(0.75) == 2.5
    assert bezier(1) == 3

    ntests = 100
    for _ in range(ntests):
        a, b = np.random.randint(-3, 4, 2)
        bezier = Bezier([a, b])
        assert bezier(0) == a
        assert bezier(0.25) == (3 * a + b) / 4
        assert bezier(0.5) == (a + b) / 2
        assert bezier(0.75) == (a + 3 * b) / 4
        assert bezier(1) == b
    for _ in range(ntests):
        a, b, c = np.random.randint(-10, 11, 3)
        bezier = Bezier([a, b, c])
        assert bezier(0) == a
        assert bezier(0.5) == (a + 2 * b + c) / 4
        assert bezier(1) == c


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_evaluate"])
def test_neg():
    beziera = Bezier([1, 2, 3, 4])
    bezierb = Bezier([-1, -2, -3, -4])

    assert -beziera == bezierb


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_evaluate"])
def test_add():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    import numpy as np

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(0, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        beziera = Bezier(coefsa)
        bezierb = Bezier(coefsb)
        bezierc = beziera + bezierb
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa + valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        beziera = Bezier(coefsa)
        bezierb = beziera + const
        bezierc = const + beziera
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa + const, valuesb)
        np.testing.assert_allclose(const + valuesa, valuesc)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_evaluate"])
def test_sub():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    import numpy as np

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(0, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        beziera = Bezier(coefsa)
        bezierb = Bezier(coefsb)
        bezierc = beziera - bezierb
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa - valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        beziera = Bezier(coefsa)
        bezierb = beziera - const
        bezierc = const - beziera
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa - const, valuesb)
        np.testing.assert_allclose(const - valuesa, valuesc)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_degree", "test_evaluate"])
def test_mul():
    """
    BasisFunctions to test if the polynomials coefficients
    are correctly computed
    """
    import numpy as np

    ntests = 100
    maxdeg = 6
    tsample = np.linspace(0, 1, 17)
    for _ in range(ntests):
        dega, degb = np.random.randint(0, maxdeg + 1, 2)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        coefsb = np.random.uniform(-1, 1, degb + 1)
        beziera = Bezier(coefsa)
        bezierb = Bezier(coefsb)
        bezierc = beziera * bezierb
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa * valuesb, valuesc)

    for _ in range(ntests):
        dega = np.random.randint(0, maxdeg + 1)
        coefsa = np.random.uniform(-1, 1, dega + 1)
        const = np.random.uniform(-1, 1)
        beziera = Bezier(coefsa)
        bezierb = beziera * const
        bezierc = const * beziera
        valuesa = beziera(tsample)
        valuesb = bezierb(tsample)
        valuesc = bezierc(tsample)

        np.testing.assert_allclose(valuesa * const, valuesb)
        np.testing.assert_allclose(const * valuesa, valuesc)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build"])
def test_print():
    bezier = Bezier([0])
    assert str(bezier) == "0"
    bezier = Bezier([1])
    assert str(bezier) == "1"
    repr(bezier)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_matrices"])
def test_conversions():
    ntests = 100
    for _ in range(ntests):
        degree = np.random.randint(0, 6)
        ctrlpoints = tuple(np.random.randint(-3, 4, degree + 1))
        bezier = Bezier(ctrlpoints)
        for _ in range(4):
            bezier = bezier2polynomial(bezier)
            bezier = polynomial2bezier(bezier)
            assert bezier == Bezier(ctrlpoints)


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_matrices"])
def test_clean():
    ctrlpoints = [1, 2, 3, 4]
    bezier = Bezier(ctrlpoints)
    assert clean(bezier) == Bezier([1, 4])


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_matrices"])
def test_derivate():
    ctrlpoints = [1, 2, 3, 4]
    bezier = Bezier(ctrlpoints)
    assert clean(bezier) == Bezier([1, 4])


@pytest.mark.order(4)
@pytest.mark.dependency(depends=["test_build", "test_matrices"])
def test_split():
    bezier = Bezier([1, 3, 2, -1])
    bez0, bez1 = tuple(split(bezier, [0.5]))
    assert bez0(0.0) == bezier(0.00)
    assert bez0(0.5) == bezier(0.25)
    assert bez0(1.0) == bezier(0.50)
    assert bez1(0.0) == bezier(0.50)
    assert bez1(0.5) == bezier(0.75)
    assert bez1(1.0) == bezier(1.00)


@pytest.mark.order(4)
@pytest.mark.dependency(
    depends=[
        "test_build",
        "test_coefficients",
        "test_degree",
        "test_matrices",
        "test_evaluate",
        "test_neg",
        "test_add",
        "test_sub",
        "test_mul",
        "test_print",
        "test_conversions",
        "test_clean",
        "test_derivate",
        "test_split",
    ]
)
def test_all():
    pass
