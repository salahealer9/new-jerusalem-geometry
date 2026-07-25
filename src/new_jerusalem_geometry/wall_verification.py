"""Verification of the inferred New Jerusalem outer wall."""

from __future__ import annotations

from dataclasses import dataclass
from math import hypot

from .core_geometry import CoreDiagram
from .verification import Check
from .wall_geometry import OuterWall


@dataclass(frozen=True, slots=True)
class WallVerificationReport:
    """Constraint checks and geometric diagnostics for an outer wall."""

    checks: tuple[Check, ...]
    side_lengths: tuple[float, ...]
    perimeter: float
    mean_side_length: float
    area: float

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def verify_outer_wall(
    diagram: CoreDiagram,
    wall: OuterWall,
    tolerance: float = 1.0e-12,
) -> WallVerificationReport:
    """Verify tangency, incidence, containment, and convexity."""

    if tolerance <= 0.0:
        raise ValueError("Tolerance must be positive.")

    checks: list[Check] = []

    checks.append(
        Check(
            name="wall_line_count",
            residual=float(len(wall.lines) - 12),
            tolerance=0.0,
        )
    )

    checks.append(
        Check(
            name="wall_vertex_count",
            residual=float(len(wall.vertices) - 12),
            tolerance=0.0,
        )
    )

    moon_lookup = dict(wall.moons)
    expected_offset = (
        diagram.construction_circle.radius
        + diagram.dimensions.moon_radius
    )

    for index, line in enumerate(wall.lines):
        moon = moon_lookup[line.moon_name]

        normal_length = hypot(
            line.normal.x,
            line.normal.y,
        )

        checks.append(
            Check(
                name=f"{line.name}_unit_normal",
                residual=normal_length - 1.0,
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{line.name}_common_support_radius",
                residual=line.offset - expected_offset,
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{line.name}_moon_tangency",
                residual=(
                    line.distance_to(moon.centre)
                    - moon.radius
                ),
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{line.name}_tangency_point_on_line",
                residual=line.evaluate(line.tangency_point),
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{line.name}_tangency_point_on_moon",
                residual=(
                    moon.centre.distance_to(
                        line.tangency_point
                    )
                    - moon.radius
                ),
                tolerance=tolerance,
            )
        )

        start, end = wall.side_endpoints(index)

        checks.append(
            Check(
                name=f"{line.name}_start_vertex_on_line",
                residual=line.evaluate(start),
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{line.name}_end_vertex_on_line",
                residual=line.evaluate(end),
                tolerance=tolerance,
            )
        )

        maximum_containment_violation = max(
            (
                line.normal.x * other.centre.x
                + line.normal.y * other.centre.y
                + other.radius
                - line.offset
            )
            for _, other in wall.moons
        )

        checks.append(
            Check(
                name=f"{line.name}_contains_all_moons",
                residual=max(
                    0.0,
                    maximum_containment_violation,
                ),
                tolerance=tolerance,
            )
        )

    signed_cross_products: list[float] = []

    for index, current in enumerate(wall.vertices):
        following = wall.vertices[
            (index + 1) % len(wall.vertices)
        ]
        after = wall.vertices[
            (index + 2) % len(wall.vertices)
        ]

        first_x = following.x - current.x
        first_y = following.y - current.y
        second_x = after.x - following.x
        second_y = after.y - following.y

        signed_cross_products.append(
            first_x * second_y
            - first_y * second_x
        )

    minimum_cross = min(signed_cross_products)

    checks.append(
        Check(
            name="wall_is_strictly_convex",
            residual=min(0.0, minimum_cross),
            tolerance=tolerance,
        )
    )

    return WallVerificationReport(
        checks=tuple(checks),
        side_lengths=wall.side_lengths,
        perimeter=wall.perimeter,
        mean_side_length=wall.mean_side_length,
        area=wall.area,
    )
