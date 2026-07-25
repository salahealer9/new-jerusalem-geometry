"""Exact normalized core of the New Jerusalem geometry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from .primitives import AxisAlignedSquare, Circle, Point2D


NamedCircle: TypeAlias = tuple[str, Circle]


@dataclass(frozen=True, slots=True)
class CoreDimensions:
    """Scale-free dimensions of the Earth-Moon squared-circle system."""

    unit: float = 1.0

    def __post_init__(self) -> None:
        if self.unit <= 0:
            raise ValueError("The fundamental unit must be positive.")

    @property
    def earth_diameter(self) -> float:
        return 11.0 * self.unit

    @property
    def earth_radius(self) -> float:
        return self.earth_diameter / 2.0

    @property
    def moon_diameter(self) -> float:
        return 3.0 * self.unit

    @property
    def moon_radius(self) -> float:
        return self.moon_diameter / 2.0

    @property
    def construction_radius(self) -> float:
        return 7.0 * self.unit

    @property
    def earth_square_side(self) -> float:
        return 11.0 * self.unit


@dataclass(frozen=True, slots=True)
class CoreDiagram:
    """The common Earth-square-circle system and four cardinal Moons."""

    dimensions: CoreDimensions
    origin: Point2D
    earth_circle: Circle
    construction_circle: Circle
    earth_square: AxisAlignedSquare
    cardinal_moons: tuple[NamedCircle, ...]


def build_core_geometry(unit: float = 1.0) -> CoreDiagram:
    """Construct the exact normalized core geometry.

    The four cardinal Moon circles have radius 3u/2 and centres at
    distance 7u from the origin. Each is externally tangent to the
    Earth circle and tangent to one side-line of the Earth square.
    """

    dimensions = CoreDimensions(unit=unit)
    origin = Point2D(0.0, 0.0)

    earth_circle = Circle(
        centre=origin,
        radius=dimensions.earth_radius,
    )

    construction_circle = Circle(
        centre=origin,
        radius=dimensions.construction_radius,
    )

    earth_square = AxisAlignedSquare(
        centre=origin,
        side=dimensions.earth_square_side,
    )

    r = dimensions.construction_radius
    moon_radius = dimensions.moon_radius

    cardinal_moons: tuple[NamedCircle, ...] = (
        ("east", Circle(Point2D(r, 0.0), moon_radius)),
        ("north", Circle(Point2D(0.0, r), moon_radius)),
        ("west", Circle(Point2D(-r, 0.0), moon_radius)),
        ("south", Circle(Point2D(0.0, -r), moon_radius)),
    )

    return CoreDiagram(
        dimensions=dimensions,
        origin=origin,
        earth_circle=earth_circle,
        construction_circle=construction_circle,
        earth_square=earth_square,
        cardinal_moons=cardinal_moons,
    )
