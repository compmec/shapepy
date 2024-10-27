from typing import Tuple

from ...core import IObject2D, Scalar
from ...point import GeneralPoint, Point2D


class LinearSegment(IObject2D):

    def __init__(self, vertexa: GeneralPoint, vertexb: GeneralPoint):
        if not isinstance(vertexa, Point2D):
            vertexa = Point2D(vertexa)
        if not isinstance(vertexb, Point2D):
            vertexb = Point2D(vertexb)
        self.vertexa = vertexa
        self.vertexb = vertexb
        self.vector = vertexb - vertexa

    @property
    def ctrlpoints(self) -> Tuple[Point2D, ...]:
        return (self.vertexa, self.vertexb)

    def eval(self, node: Scalar, derivative: int = 0) -> Point2D:
        if node < 0 or 1 < node:
            raise ValueError("Outside interval [0, 1]")
        if derivative > 0:
            return (derivative == 1) * self.vector
        if node == 0:
            return self.vertexa
        if node == 1:
            return self.vertexb
        return self.vertexa + node * self.vector

    def __call__(self, node: Scalar) -> Point2D:
        return self.eval(node, 0)
