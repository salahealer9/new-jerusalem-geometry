"""Verification of Michell's approximate septenary scaffold."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import atan2, pi, sin

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import (
    build_oblique_placement,
    square_intersection_angle,
)
from .septenary_geometry import (
    MichellSeptenaryScaffold,
    ScaffoldRole,
    build_michell_gap_arithmetic,
)
from .primitives import Point2D
from .verification import Check
from .wall_geometry import build_ordered_moon_circles


@dataclass(frozen=True, slots=True)
class SeptenaryVerificationReport:
    """Checks and diagnostics for the approximate 28-point scaffold."""

    checks: tuple[Check, ...]
    moon_centre_count: int
    inter_moon_gap_count: int
    intersection_positioner_count: int
    exact_heptagon_step_radians: float
    relative_heptagon_step_error: float
    scaffold_beta_radians: float
    incidence_beta_radians: float
    centre_displacements: tuple[float, ...]
    angular_displacements_radians: tuple[float, ...]
    scaffold_incidence_residual: float
    gap_arithmetic_total: float

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def maximum_centre_displacement(self) -> float:
        return max(self.centre_displacements)

    @property
    def mean_centre_displacement(self) -> float:
        return (
            sum(self.centre_displacements)
            / len(self.centre_displacements)
        )

    @property
    def maximum_angular_displacement_radians(self) -> float:
        return max(self.angular_displacements_radians)

    @property
    def maximum_angular_displacement_degrees(self) -> float:
        return (
            self.maximum_angular_displacement_radians
            * 180.0
            / pi
        )


def _wrapped_angle_difference(
    first: float,
    second: float,
) -> float:
    """Return the absolute shortest angular separation."""

    difference = (
        first - second + pi
    ) % (2.0 * pi) - pi

    return abs(difference)


def verify_michell_28_point_scaffold(
    diagram: CoreDiagram,
    scaffold: MichellSeptenaryScaffold,
    tolerance: float = 1.0e-12,
) -> SeptenaryVerificationReport:
    """Verify the scaffold and compare it with exact incidence."""

    if tolerance <= 0.0:
        raise ValueError("Tolerance must be positive.")

    checks: list[Check] = []

    role_counts = Counter(
        point.role
        for point in scaffold.points
    )

    moon_count = role_counts[ScaffoldRole.MOON_CENTRE]
    gap_count = role_counts[ScaffoldRole.INTER_MOON_GAP]
    intersection_count = role_counts[
        ScaffoldRole.INTERSECTION_POSITIONER
    ]

    checks.extend(
        [
            Check(
                name="septenary_point_count",
                residual=float(len(scaffold.points) - 28),
                tolerance=0.0,
            ),
            Check(
                name="septenary_moon_centre_count",
                residual=float(moon_count - 12),
                tolerance=0.0,
            ),
            Check(
                name="septenary_inter_moon_gap_count",
                residual=float(gap_count - 8),
                tolerance=0.0,
            ),
            Check(
                name="septenary_intersection_positioner_count",
                residual=float(intersection_count - 8),
                tolerance=0.0,
            ),
        ]
    )

    maximum_radial_residual = max(
        abs(
            point.point.distance_to(
                diagram.construction_circle.centre
            )
            - scaffold.radius
        )
        for point in scaffold.points
    )

    checks.append(
        Check(
            name="all_scaffold_points_on_construction_circle",
            residual=maximum_radial_residual,
            tolerance=tolerance,
        )
    )

    maximum_fourfold_residual = 0.0

    for quadrant in range(4):
        next_quadrant = (quadrant + 1) % 4

        for local_index in range(7):
            current = scaffold.points[
                quadrant * 7 + local_index
            ]

            following = scaffold.points[
                next_quadrant * 7 + local_index
            ]

            rotated_x = -current.point.y
            rotated_y = current.point.x

            maximum_fourfold_residual = max(
                maximum_fourfold_residual,
                following.point.distance_to(
                    Point2D(
                        rotated_x,
                        rotated_y,
                    )
                ),
            )

    checks.append(
        Check(
            name="scaffold_fourfold_rotational_symmetry",
            residual=maximum_fourfold_residual,
            tolerance=tolerance,
        )
    )

    exact_step = 2.0 * pi / 7.0

    relative_step_error = abs(
        scaffold.heptagon_step_radians
        / exact_step
        - 1.0
    )

    checks.append(
        Check(
            name="heptagon_step_better_than_one_in_1000",
            residual=max(
                0.0,
                relative_step_error - 1.0e-3,
            ),
            tolerance=tolerance,
        )
    )

    gap_arithmetic = build_michell_gap_arithmetic()

    checks.append(
        Check(
            name="figure_28_gap_arithmetic_total",
            residual=gap_arithmetic.total - 44.0,
            tolerance=tolerance,
        )
    )

    incidence_placement = build_oblique_placement(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    ordered_incidence_moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    scaffold_moons = scaffold.moon_centre_points

    if len(scaffold_moons) != len(ordered_incidence_moons):
        raise ValueError(
            "Scaffold and incidence Moon counts do not agree."
        )

    centre_displacements: list[float] = []
    angular_displacements: list[float] = []

    for scaffold_point, (_, incidence_moon) in zip(
        scaffold_moons,
        ordered_incidence_moons,
        strict=True,
    ):
        centre_displacements.append(
            scaffold_point.point.distance_to(
                incidence_moon.centre
            )
        )

        incidence_angle = atan2(
            incidence_moon.centre.y,
            incidence_moon.centre.x,
        )

        if incidence_angle < 0.0:
            incidence_angle += 2.0 * pi

        angular_displacements.append(
            _wrapped_angle_difference(
                scaffold_point.angle_radians,
                incidence_angle,
            )
        )

    theta = square_intersection_angle(diagram)

    scaffold_incidence_residual = (
        2.0
        * scaffold.radius
        * sin(
            (
                theta
                - scaffold.beta_radians
            )
            / 2.0
        )
        - diagram.dimensions.moon_radius
    )

    return SeptenaryVerificationReport(
        checks=tuple(checks),
        moon_centre_count=moon_count,
        inter_moon_gap_count=gap_count,
        intersection_positioner_count=intersection_count,
        exact_heptagon_step_radians=exact_step,
        relative_heptagon_step_error=relative_step_error,
        scaffold_beta_radians=scaffold.beta_radians,
        incidence_beta_radians=incidence_placement.beta_radians,
        centre_displacements=tuple(centre_displacements),
        angular_displacements_radians=tuple(
            angular_displacements
        ),
        scaffold_incidence_residual=(
            scaffold_incidence_residual
        ),
        gap_arithmetic_total=gap_arithmetic.total,
    )
