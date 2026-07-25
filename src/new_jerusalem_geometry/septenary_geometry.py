"""Michell's approximate twenty-eight-point septenary scaffold.

The construction follows Method 1 of Figure 194 in John Michell and
Allan Brown, How the World Is Made:

1. enclose a circle in a square;
2. erect an equilateral triangle on one side of the square;
3. use the relevant triangle-circle intersection to obtain an
   approximate heptagonal step;
4. repeat the construction on all four sides of the square.

The resulting twenty-eight points provide the approximate framework
described by Michell for positioning the twelve lunar circles.

The analytic formula for the heptagonal step is a project derivation
from Michell's geometric instructions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import acos, cos, pi, sin, sqrt

from .core_geometry import CoreDiagram
from .primitives import Point2D


class ScaffoldRole(str, Enum):
    """Source-described role of a point in the 28-point scaffold."""

    MOON_CENTRE = "moon_centre"
    INTER_MOON_GAP = "inter_moon_gap"
    INTERSECTION_POSITIONER = "intersection_positioner"


@dataclass(frozen=True, slots=True)
class SeptenaryPoint:
    """One point in Michell's approximate 28-point scaffold."""

    index: int
    quadrant: int
    local_index: int
    role: ScaffoldRole
    angle_radians: float
    point: Point2D

    @property
    def angle_degrees(self) -> float:
        return self.angle_radians * 180.0 / pi


@dataclass(frozen=True, slots=True)
class MichellSeptenaryScaffold:
    """The complete approximate 28-point framework."""

    radius: float
    heptagon_step_radians: float
    points: tuple[SeptenaryPoint, ...]

    @property
    def heptagon_step_degrees(self) -> float:
        return self.heptagon_step_radians * 180.0 / pi

    @property
    def beta_radians(self) -> float:
        """Return the first oblique Moon-centre angle."""

        return pi - 3.0 * self.heptagon_step_radians

    @property
    def beta_degrees(self) -> float:
        return self.beta_radians * 180.0 / pi

    @property
    def moon_centre_points(self) -> tuple[SeptenaryPoint, ...]:
        return tuple(
            point
            for point in self.points
            if point.role is ScaffoldRole.MOON_CENTRE
        )

    @property
    def inter_moon_gap_points(
        self,
    ) -> tuple[SeptenaryPoint, ...]:
        return tuple(
            point
            for point in self.points
            if point.role is ScaffoldRole.INTER_MOON_GAP
        )

    @property
    def intersection_positioner_points(
        self,
    ) -> tuple[SeptenaryPoint, ...]:
        return tuple(
            point
            for point in self.points
            if point.role
            is ScaffoldRole.INTERSECTION_POSITIONER
        )


@dataclass(frozen=True, slots=True)
class MichellGapArithmetic:
    """Normalized circumference bookkeeping from Michell's Figure 28."""

    moon_diameter: float
    moon_count: int
    large_gap: float
    large_gap_count: int
    small_gap: float
    small_gap_count: int

    @property
    def moon_total(self) -> float:
        return self.moon_diameter * self.moon_count

    @property
    def large_gap_total(self) -> float:
        return self.large_gap * self.large_gap_count

    @property
    def small_gap_total(self) -> float:
        return self.small_gap * self.small_gap_count

    @property
    def total(self) -> float:
        return (
            self.moon_total
            + self.large_gap_total
            + self.small_gap_total
        )


def michell_heptagon_step_angle() -> float:
    """Return the central angle of Michell's first approximation.

    Work in a unit circle enclosed by the square [-1, 1]^2.

    An equilateral triangle erected on the lower side of the square has
    a lower-right circle intersection whose angular separation from the
    bottom point of the circle is alpha.

    Solving the triangle-side and unit-circle equations gives

        cos(alpha)
            = (1 - sqrt(3) + sqrt(6 sqrt(3))) / 4.
    """

    cosine = (
        1.0
        - sqrt(3.0)
        + sqrt(6.0 * sqrt(3.0))
    ) / 4.0

    return acos(cosine)


def michell_scaffold_local_offsets() -> tuple[float, ...]:
    """Return the seven unique offsets inside one quadrant."""

    alpha = michell_heptagon_step_angle()

    offsets = (
        0.0,
        2.0 * alpha - pi / 2.0,
        pi - 3.0 * alpha,
        pi / 2.0 - alpha,
        alpha,
        3.0 * alpha - pi / 2.0,
        pi - 2.0 * alpha,
    )

    if not all(
        offsets[index] < offsets[index + 1]
        for index in range(len(offsets) - 1)
    ):
        raise ValueError(
            "Derived septenary offsets are not strictly increasing."
        )

    if offsets[0] < 0.0 or offsets[-1] >= pi / 2.0:
        raise ValueError(
            "Derived offsets must lie in one half-open quadrant."
        )

    return offsets


def build_michell_28_point_scaffold(
    diagram: CoreDiagram,
) -> MichellSeptenaryScaffold:
    """Construct Michell's approximate 28-point framework."""

    radius = diagram.construction_circle.radius
    alpha = michell_heptagon_step_angle()
    offsets = michell_scaffold_local_offsets()

    roles = (
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTER_MOON_GAP,
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTERSECTION_POSITIONER,
        ScaffoldRole.INTERSECTION_POSITIONER,
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTER_MOON_GAP,
    )

    points: list[SeptenaryPoint] = []

    for quadrant in range(4):
        quadrant_start = quadrant * pi / 2.0

        for local_index, (offset, role) in enumerate(
            zip(offsets, roles, strict=True)
        ):
            angle = quadrant_start + offset

            points.append(
                SeptenaryPoint(
                    index=quadrant * 7 + local_index,
                    quadrant=quadrant,
                    local_index=local_index,
                    role=role,
                    angle_radians=angle,
                    point=Point2D(
                        radius * cos(angle),
                        radius * sin(angle),
                    ),
                )
            )

    return MichellSeptenaryScaffold(
        radius=radius,
        heptagon_step_radians=alpha,
        points=tuple(points),
    )


def build_michell_gap_arithmetic() -> MichellGapArithmetic:
    """Return Figure 28's circumference accounting in normalized units.

    Michell gives:

    - twelve Moon diameters of 2160;
    - four large gaps of 1200;
    - eight small gaps of 120;
    - total circumference 31680.

    Division by 720 gives:

    - Moon diameter 3;
    - large gap 5/3;
    - small gap 1/6;
    - total 44.
    """

    return MichellGapArithmetic(
        moon_diameter=3.0,
        moon_count=12,
        large_gap=5.0 / 3.0,
        large_gap_count=4,
        small_gap=1.0 / 6.0,
        small_gap_count=8,
    )
