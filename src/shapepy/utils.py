from typing import Any, Iterable, Tuple


def sorter(items: Iterable[Any], /, *, reverse: bool = False) -> Iterable[int]:
    items = tuple(items)
    values = sorted(zip(items, range(len(items))), reverse=reverse)
    return (vs[-1] for vs in values)


def permutations(*numbers: int) -> Iterable[Tuple[int, ...]]:
    """
    Permutes the numbers

    Example:
    permutations(4) -> [0, 1, 2, 3]
    permutations(4, 2) -> [(0, 0), (0, 1), (1, 0), ..., (3, 0), (3, 0)]
    permutations(2, 4, 1) -> [(0, 0, 0), ..., (1, 3, 1), (1, 3, 2)]
    """
    if len(numbers) == 1:
        for j in range(numbers[0]):
            yield j
        return
    for j in range(numbers[0]):
        for perm in permutations(*numbers[1:]):
            if isinstance(perm, int):
                yield (j, perm)
            else:
                yield (j,) + perm
