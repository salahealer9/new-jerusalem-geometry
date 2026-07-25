"""Verification of the alternative oblique Moon placements."""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, pi

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import ObliquePlacement
from .verification import Check


@dataclass(frozen=True, slots=True)
class ObliqueVerificationReport:
    """Verification results for one oblique model."""

    model: ObliqueModel
    checks: tuple[Check, ...]
    incidence_residuals: tuple[float, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def max_abs_incidence_residual(self) -> float:
        return max(abs(value) for value in self.incidence_residuals)


def verify_oblique_placement(
    diagram: CoreDiagram,
    placement: ObliquePlacement,
    tolerance: float = 1.0e-12,
) -> ObliqueVerificationReport:
    """Verify universal and model-defining constraints."""

    if tolerance <= 0:
        raise ValueError("Tolerance must be positive.")

    checks: list[Check] = []

    construction_radius = diagram.construction_circle.radius
    earth_radius = diagram.earth_circle.radius
    moon_radius = diagram.dimensions.moon_radius

    for moon in placement.moons:
        centre_distance = diagram.origin.distance_to(
            moon.circle.centre
        )

        checks.append(
            Check(
                name=f"{moon.name}_centre_on_construction_circle",
                residual=centre_distance - construction_radius,
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{moon.name}_earth_external_tangency",
                residual=(
                    centre_distance
                    - earth_radius
                    - moon.circle.radius
                ),
                tolerance=tolerance,
            )
        )

    if placement.model is ObliqueModel.INCIDENCE:
        for moon in placement.moons:
            checks.append(
                Check(
                    name=f"{moon.name}_exact_target_incidence",
                    residual=moon.incidence_residual,
                    tolerance=tolerance,
                )
            )

    elif placement.model is ObliqueModel.DIVISION_28:
        checks.append(
            Check(
                name="exact_28_fold_beta",
                residual=placement.beta_radians - pi / 7.0,
                tolerance=tolerance,
            )
        )

    elif placement.model is ObliqueModel.WIKIMEDIA_SVG:
        expected_beta = (
            placement.intersection_angle_radians
            - asin(moon_radius / construction_radius)
        )

        checks.append(
            Check(
                name="wikimedia_svg_beta_formula",
                residual=placement.beta_radians - expected_beta,
                tolerance=tolerance,
            )
        )

    return ObliqueVerificationReport(
        model=placement.model,
        checks=tuple(checks),
        incidence_residuals=placement.incidence_residuals,
    )
