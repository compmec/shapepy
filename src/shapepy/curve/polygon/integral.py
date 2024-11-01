import math
from functools import lru_cache
from typing import Tuple

import numpy as np

from ...core import Scalar


@lru_cache
def binom(n: int, i: int) -> int:
    return math.comb(n, i)


def polybidim(
    vertices: Tuple[Tuple[Scalar, Scalar], ...], expx: int, expy: int
) -> Scalar:
    xvalues = tuple(vertex[0] for vertex in vertices)
    yvalues = tuple(vertex[1] for vertex in vertices)
    xvalues = np.array(xvalues, dtype="object")
    yvalues = np.array(yvalues, dtype="object")
    shixvls = np.roll(xvalues, shift=-1, axis=0)
    shiyvls = np.roll(yvalues, shift=-1, axis=0)

    matrix = [[0] * (expy + 1) for _ in range(expx + 1)]
    for i in range(expx + 1):
        for j in range(expy + 1):
            matrix[i][j] = binom(i + j, i) * binom(
                expx + expy - i - j, expy - j
            )
    cross = xvalues * shiyvls - yvalues * shixvls
    xvand0 = np.vander(xvalues, expx + 1)
    xvand1 = np.vander(shixvls, expx + 1, True)
    yvand0 = np.vander(yvalues, expy + 1)
    yvand1 = np.vander(shiyvls, expy + 1, True)
    soma = np.einsum(
        "k,ki,ki,ij,kj,kj", cross, xvand0, xvand1, matrix, yvand0, yvand1
    )
    denom = (expx + expy + 2) * (expx + expy + 1) * binom(expx + expy, expx)
    return soma / denom
