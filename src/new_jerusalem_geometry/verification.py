"""Numerical verification of the exact core geometry."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Any

from .core_geometry import CoreDiagram


@dataclass(frozen=True, slots=True)
class Check:
    """One numerical constraint check."""

    name: str
    residual: float
    tolerance: float

    @property
    def passed(self) -> bool:
        return abs(self.residual) <= self.tolerance


@dataclass(frozen=True, slots=True)
class VerificationReport:
    """Verification results and squared-circle perimeter diagnostics."""

    checks: tuple[Check, ...]
    square_perimeter: float
    construction_circumference: float

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def perimeter_discrepancy(self) -> float:
        return self.square_perimeter - self.construction_circumference

    @property
    def relative_perimeter_discrepancy(self) -> float:
        return self.perimeter_discrepancy / self.square_perimeter

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "checks": [
                {
                    "name": check.name,
                    "residual": check.residual,
                    "tolerance": check.tolerance,
                    "passed": check.passed,
                }
                for check in self.checks
            ],
            "metrics": {
                "square_perimeter": self.square_perimeter,
                "construction_circumference": self.construction_circumference,
                "perimeter_discrepancy": self.perimeter_discrepancy,
                "relative_perimeter_discrepancy": (
                    self.relative_perimeter_discrepancy
                ),
                "relative_perimeter_discrepancy_percent": (
                    100.0 * self.relative_perimeter_discrepancy
                ),
            },
        }


def verify_core_geometry(
    diagram: CoreDiagram,
    tolerance: float = 1.0e-12,
) -> VerificationReport:
    """Verify the defining constraints of the cardinal core."""

    if tolerance <= 0:
        raise ValueError("Tolerance must be positive.")

    dimensions = diagram.dimensions
    checks: list[Check] = []

    # Fundamental exact radius identity:
    # 7u = 11u/2 + 3u/2.
    checks.append(
        Check(
            name="fundamental_radius_identity",
            residual=(
                dimensions.construction_radius
                - dimensions.earth_radius
                - dimensions.moon_radius
            ),
            tolerance=tolerance,
        )
    )

    for direction, moon in diagram.cardinal_moons:
        centre_distance = diagram.origin.distance_to(moon.centre)

        checks.append(
            Check(
                name=f"{direction}_centre_on_construction_circle",
                residual=(
                    centre_distance
                    - diagram.construction_circle.radius
                ),
                tolerance=tolerance,
            )
        )

        checks.append(
            Check(
                name=f"{direction}_earth_moon_external_tangency",
                residual=(
                    centre_distance
                    - diagram.earth_circle.radius
                    - moon.radius
                ),
                tolerance=tolerance,
            )
        )

        if direction in {"east", "west"}:
            side_tangency_residual = (
                abs(moon.centre.x)
                - moon.radius
                - diagram.earth_square.half_side
            )
        else:
            side_tangency_residual = (
                abs(moon.centre.y)
                - moon.radius
                - diagram.earth_square.half_side
            )

        checks.append(
            Check(
                name=f"{direction}_moon_square_side_tangency",
                residual=side_tangency_residual,
                tolerance=tolerance,
            )
        )

    square_perimeter = diagram.earth_square.perimeter
    construction_circumference = (
        2.0 * pi * diagram.construction_circle.radius
    )

    return VerificationReport(
        checks=tuple(checks),
        square_perimeter=square_perimeter,
        construction_circumference=construction_circumference,
    )
