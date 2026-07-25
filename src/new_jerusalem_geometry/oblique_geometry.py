"""Geometry of the eight non-cardinal Moon-circle placements."""

from __future__ import annotations

from dataclasses import dataclass
from math import acos, asin, cos, degrees, pi, sin

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .primitives import Circle, Point2D


@dataclass(frozen=True, slots=True)
class ConstructionIntersection:
    """One intersection of the Earth square and construction circle."""

    name: str
    angle_radians: float
    point: Point2D


@dataclass(frozen=True, slots=True)
class ObliqueMoon:
    """One non-cardinal Moon circle and its associated target point."""

    name: str
    centre_angle_radians: float
    circle: Circle
    target_intersection: ConstructionIntersection

    @property
    def incidence_residual(self) -> float:
        """Distance-to-target residual relative to the Moon radius."""

        return (
            self.circle.centre.distance_to(
                self.target_intersection.point
            )
            - self.circle.radius
        )


@dataclass(frozen=True, slots=True)
class ObliquePlacement:
    """The eight non-cardinal Moon circles for one model."""

    model: ObliqueModel
    beta_radians: float
    intersection_angle_radians: float
    moons: tuple[ObliqueMoon, ...]

    @property
    def beta_degrees(self) -> float:
        return degrees(self.beta_radians)

    @property
    def incidence_residuals(self) -> tuple[float, ...]:
        return tuple(moon.incidence_residual for moon in self.moons)

    @property
    def max_abs_incidence_residual(self) -> float:
        return max(abs(value) for value in self.incidence_residuals)


def polar_point(radius: float, angle_radians: float) -> Point2D:
    """Construct a point from polar coordinates."""

    return Point2D(
        radius * cos(angle_radians),
        radius * sin(angle_radians),
    )


def square_intersection_angle(
    diagram: CoreDiagram,
) -> float:
    """Return the first-quadrant square-circle intersection angle.

    The relevant intersection has coordinates

        (square_half_side, sqrt(R² - square_half_side²)).

    Therefore

        theta = arccos(square_half_side / R).
    """

    square_half_side = diagram.earth_square.half_side
    construction_radius = diagram.construction_circle.radius

    ratio = square_half_side / construction_radius

    if not 0.0 < ratio < 1.0:
        raise ValueError(
            "The square and construction circle do not have "
            "the expected eight-intersection configuration."
        )

    return acos(ratio)


def build_square_construction_intersections(
    diagram: CoreDiagram,
) -> tuple[ConstructionIntersection, ...]:
    """Construct the eight square–construction-circle intersections."""

    radius = diagram.construction_circle.radius
    theta = square_intersection_angle(diagram)

    intersections: list[ConstructionIntersection] = []

    for quadrant_index in range(4):
        quadrant = quadrant_index + 1
        base_angle = quadrant_index * pi / 2.0

        angle_a = base_angle + theta
        angle_b = base_angle + pi / 2.0 - theta

        intersections.extend(
            [
                ConstructionIntersection(
                    name=f"q{quadrant}-a",
                    angle_radians=angle_a,
                    point=polar_point(radius, angle_a),
                ),
                ConstructionIntersection(
                    name=f"q{quadrant}-b",
                    angle_radians=angle_b,
                    point=polar_point(radius, angle_b),
                ),
            ]
        )

    return tuple(intersections)


def model_beta_radians(
    diagram: CoreDiagram,
    model: ObliqueModel,
) -> float:
    """Return the characteristic oblique-centre angle for a model."""

    theta = square_intersection_angle(diagram)
    construction_radius = diagram.construction_circle.radius
    moon_radius = diagram.dimensions.moon_radius

    if model is ObliqueModel.INCIDENCE:
        # The centre and target point both lie on the radius-R
        # construction circle. Their chord distance must equal the
        # Moon radius:
        #
        #     2R sin(delta / 2) = r.
        #
        angular_separation = 2.0 * asin(
            moon_radius / (2.0 * construction_radius)
        )
        return theta - angular_separation

    if model is ObliqueModel.DIVISION_28:
        # Two steps of a 28-fold angular division:
        #
        #     2 × 360° / 28 = 360° / 14 = pi / 7.
        #
        return pi / 7.0

    if model is ObliqueModel.WIKIMEDIA_SVG:
        # Formula encoded by the Wikimedia reconstruction.
        return theta - asin(
            moon_radius / construction_radius
        )

    raise ValueError(f"Unsupported oblique model: {model}")


def build_oblique_placement(
    diagram: CoreDiagram,
    model: ObliqueModel,
) -> ObliquePlacement:
    """Build the eight oblique Moon circles for one model."""

    if not isinstance(model, ObliqueModel):
        model = ObliqueModel(model)

    radius = diagram.construction_circle.radius
    moon_radius = diagram.dimensions.moon_radius
    theta = square_intersection_angle(diagram)
    beta = model_beta_radians(diagram, model)

    intersections = {
        intersection.name: intersection
        for intersection in build_square_construction_intersections(
            diagram
        )
    }

    moons: list[ObliqueMoon] = []

    for quadrant_index in range(4):
        quadrant = quadrant_index + 1
        base_angle = quadrant_index * pi / 2.0

        centre_angle_a = base_angle + beta
        centre_angle_b = base_angle + pi / 2.0 - beta

        target_a = intersections[f"q{quadrant}-a"]
        target_b = intersections[f"q{quadrant}-b"]

        moons.extend(
            [
                ObliqueMoon(
                    name=f"moon-q{quadrant}-a",
                    centre_angle_radians=centre_angle_a,
                    circle=Circle(
                        centre=polar_point(
                            radius,
                            centre_angle_a,
                        ),
                        radius=moon_radius,
                    ),
                    target_intersection=target_a,
                ),
                ObliqueMoon(
                    name=f"moon-q{quadrant}-b",
                    centre_angle_radians=centre_angle_b,
                    circle=Circle(
                        centre=polar_point(
                            radius,
                            centre_angle_b,
                        ),
                        radius=moon_radius,
                    ),
                    target_intersection=target_b,
                ),
            ]
        )

    return ObliquePlacement(
        model=model,
        beta_radians=beta,
        intersection_angle_radians=theta,
        moons=tuple(moons),
    )
