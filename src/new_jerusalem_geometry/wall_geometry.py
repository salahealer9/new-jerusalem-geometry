"""Candidate outer-wall geometry for Michell's New Jerusalem.

The construction implemented here is a project inference from Michell's
Figure 12 and accompanying description:

- each of the twelve Moon circles has one outward support tangent;
- the tangent is perpendicular to the radius through the Moon centre;
- consecutive tangent lines intersect to form the wall vertices.

This model must remain labelled as an inferred construction until the
primary sources are shown to specify it uniquely.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, hypot, pi

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import build_oblique_placement
from .primitives import Circle, Point2D


NamedCircle = tuple[str, Circle]


@dataclass(frozen=True, slots=True)
class WallLine:
    """One wall side-line in unit-normal form.

    The line equation is

        normal.x * x + normal.y * y = offset.
    """

    name: str
    moon_name: str
    normal: Point2D
    offset: float
    tangency_point: Point2D

    def evaluate(self, point: Point2D) -> float:
        """Return the signed line-equation residual."""

        return (
            self.normal.x * point.x
            + self.normal.y * point.y
            - self.offset
        )

    def distance_to(self, point: Point2D) -> float:
        """Return distance to the line, assuming a unit normal."""

        return abs(self.evaluate(point))


@dataclass(frozen=True, slots=True)
class OuterWall:
    """A convex twelve-sided wall surrounding the Moon circles.

    Vertex ``i`` is the intersection of wall lines ``i`` and ``i + 1``.
    Wall side ``i`` lies on line ``i`` and runs from vertex ``i - 1``
    to vertex ``i``.
    """

    model: ObliqueModel
    moons: tuple[NamedCircle, ...]
    lines: tuple[WallLine, ...]
    vertices: tuple[Point2D, ...]

    def side_endpoints(
        self,
        index: int,
    ) -> tuple[Point2D, Point2D]:
        count = len(self.vertices)

        if not 0 <= index < count:
            raise IndexError("Wall-side index out of range.")

        return (
            self.vertices[(index - 1) % count],
            self.vertices[index],
        )

    @property
    def side_lengths(self) -> tuple[float, ...]:
        return tuple(
            start.distance_to(end)
            for start, end in (
                self.side_endpoints(index)
                for index in range(len(self.lines))
            )
        )

    @property
    def perimeter(self) -> float:
        return sum(self.side_lengths)

    @property
    def mean_side_length(self) -> float:
        return self.perimeter / len(self.lines)

    @property
    def area(self) -> float:
        """Return polygon area from the shoelace formula."""

        total = 0.0
        count = len(self.vertices)

        for index, current in enumerate(self.vertices):
            following = self.vertices[(index + 1) % count]
            total += (
                current.x * following.y
                - current.y * following.x
            )

        return abs(total) / 2.0


def _positive_angle(point: Point2D) -> float:
    angle = atan2(point.y, point.x)
    return angle if angle >= 0.0 else angle + 2.0 * pi


def _intersection(
    first: WallLine,
    second: WallLine,
) -> Point2D:
    """Return the unique intersection of two nonparallel lines."""

    a = first.normal.x
    b = first.normal.y
    c = second.normal.x
    d = second.normal.y

    determinant = a * d - b * c

    if abs(determinant) <= 1.0e-15:
        raise ValueError("Adjacent wall lines are parallel.")

    x = (
        first.offset * d
        - b * second.offset
    ) / determinant

    y = (
        a * second.offset
        - first.offset * c
    ) / determinant

    return Point2D(x, y)


def build_ordered_moon_circles(
    diagram: CoreDiagram,
    model: ObliqueModel = ObliqueModel.INCIDENCE,
) -> tuple[NamedCircle, ...]:
    """Return all twelve Moon circles in counterclockwise order."""

    if not isinstance(model, ObliqueModel):
        model = ObliqueModel(model)

    placement = build_oblique_placement(
        diagram,
        model,
    )

    moons: list[NamedCircle] = [
        (f"moon-{direction}", circle)
        for direction, circle in diagram.cardinal_moons
    ]

    moons.extend(
        (moon.name, moon.circle)
        for moon in placement.moons
    )

    moons.sort(
        key=lambda item: _positive_angle(item[1].centre)
    )

    if len(moons) != 12:
        raise ValueError(
            f"Expected twelve Moon circles; received {len(moons)}."
        )

    return tuple(moons)


def build_radial_support_wall(
    diagram: CoreDiagram,
    model: ObliqueModel = ObliqueModel.INCIDENCE,
) -> OuterWall:
    """Construct the inferred one-support-line-per-Moon outer wall."""

    if not isinstance(model, ObliqueModel):
        model = ObliqueModel(model)

    moons = build_ordered_moon_circles(
        diagram,
        model,
    )

    lines: list[WallLine] = []

    for index, (moon_name, moon) in enumerate(moons):
        centre_distance = hypot(
            moon.centre.x,
            moon.centre.y,
        )

        if centre_distance <= 0.0:
            raise ValueError(
                f"Moon centre {moon_name!r} cannot be the origin."
            )

        normal = Point2D(
            moon.centre.x / centre_distance,
            moon.centre.y / centre_distance,
        )

        offset = centre_distance + moon.radius

        tangency_point = Point2D(
            moon.centre.x + moon.radius * normal.x,
            moon.centre.y + moon.radius * normal.y,
        )

        lines.append(
            WallLine(
                name=f"wall-line-{index:02d}",
                moon_name=moon_name,
                normal=normal,
                offset=offset,
                tangency_point=tangency_point,
            )
        )

    vertices = tuple(
        _intersection(
            lines[index],
            lines[(index + 1) % len(lines)],
        )
        for index in range(len(lines))
    )

    return OuterWall(
        model=model,
        moons=moons,
        lines=tuple(lines),
        vertices=vertices,
    )
