"""Minimal Euclidean primitives used by the New Jerusalem models."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True, slots=True)
class Point2D:
    """A point in the Euclidean plane."""

    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        return hypot(self.x - other.x, self.y - other.y)


@dataclass(frozen=True, slots=True)
class Circle:
    """A Euclidean circle."""

    centre: Point2D
    radius: float

    def __post_init__(self) -> None:
        if self.radius <= 0:
            raise ValueError("Circle radius must be positive.")


@dataclass(frozen=True, slots=True)
class AxisAlignedSquare:
    """A square centred on a point with sides parallel to the axes."""

    centre: Point2D
    side: float

    def __post_init__(self) -> None:
        if self.side <= 0:
            raise ValueError("Square side length must be positive.")

    @property
    def half_side(self) -> float:
        return self.side / 2.0

    @property
    def perimeter(self) -> float:
        return 4.0 * self.side
