"""Geometric candidates for Michell's Figure 14 heptagram.

Figure 14 places a seven-pointed star within the zodiac circle of the
New Jerusalem diagram.

Michell explicitly states that its extremities accord with:

- the centres of three Moon circles;
- two junctions of the construction circle and Earth square.

The remaining two extremities are inferred from the printed plate as
points in the small gaps between adjacent Moon circles. They are placed
on the construction circle at the angular bisectors of the relevant
Moon-centre pairs.

Three candidate vertex systems are represented:

- an exact regular heptagon with its upper vertex at 90 degrees;
- the seven corresponding points of Michell's approximate 28-point
  scaffold;
- a Figure-14-aligned system built from the stated and inferred anchors.

The promoted near-endpoint source audit supports the heptagram topology {7/2}.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import atan2, cos, pi, sin, sqrt, tau

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import build_oblique_placement
from .primitives import Point2D
from .septenary_geometry import (
    MichellSeptenaryScaffold,
    build_michell_28_point_scaffold,
)
from .wall_geometry import build_ordered_moon_circles


class Figure14AnchorRole(str, Enum):
    """Geometric role of one Figure 14 extremity."""

    MOON_CENTRE = "moon_centre"
    SQUARE_CIRCLE_JUNCTION = "square_circle_junction"
    INTER_MOON_GAP = "inter_moon_gap"


class AnchorEvidence(str, Enum):
    """Evidential status of an endpoint identification."""

    SOURCE_TEXT_AND_PLATE = "source_text_and_plate"
    PLATE_INFERENCE = "plate_inference"


class HeptagramFamily(Enum):
    """The two non-degenerate seven-pointed star families."""

    STEP_2 = 2
    STEP_3 = 3


@dataclass(frozen=True, slots=True)
class Figure14Anchor:
    """One endpoint of the Figure 14 seven-pointed star."""

    index: int
    name: str
    role: Figure14AnchorRole
    evidence: AnchorEvidence
    point: Point2D

    @property
    def radius(self) -> float:
        return sqrt(
            self.point.x * self.point.x
            + self.point.y * self.point.y
        )

    @property
    def angle_radians(self) -> float:
        angle = atan2(self.point.y, self.point.x)

        if angle < 0.0:
            angle += tau

        return angle

    @property
    def angle_degrees(self) -> float:
        return self.angle_radians * 180.0 / pi


@dataclass(frozen=True, slots=True)
class HeptagramGeometry:
    """A seven-vertex system with one heptagram traversal."""

    name: str
    family: HeptagramFamily
    vertices: tuple[Point2D, ...]

    def traversal_indices(self) -> tuple[int, ...]:
        """Return the vertex traversal beginning at index zero."""

        count = len(self.vertices)

        if count != 7:
            raise ValueError(
                "A heptagram must contain exactly seven vertices."
            )

        step = self.family.value
        indices = [0]
        current = 0

        for _ in range(6):
            current = (current + step) % count
            indices.append(current)

        if len(set(indices)) != count:
            raise ValueError(
                "Heptagram traversal does not visit every vertex."
            )

        return tuple(indices)

    def edge_index_pairs(
        self,
    ) -> tuple[tuple[int, int], ...]:
        """Return the seven line segments of the star."""

        traversal = self.traversal_indices()

        return tuple(
            (
                traversal[index],
                traversal[(index + 1) % len(traversal)],
            )
            for index in range(len(traversal))
        )

    def edge_lengths(self) -> tuple[float, ...]:
        """Return the seven heptagram edge lengths."""

        return tuple(
            self.vertices[start].distance_to(
                self.vertices[end]
            )
            for start, end in self.edge_index_pairs()
        )


def _normalise_angle(angle: float) -> float:
    return angle % tau


def _angular_distance(
    first: float,
    second: float,
) -> float:
    return abs(
        (
            first
            - second
            + pi
        )
        % tau
        - pi
    )


def _point_on_circle(
    radius: float,
    angle: float,
) -> Point2D:
    return Point2D(
        radius * cos(angle),
        radius * sin(angle),
    )


def _nearest_moon_centre(
    diagram: CoreDiagram,
    target_angle: float,
) -> Point2D:
    moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    def distance(item: tuple[str, object]) -> float:
        circle = item[1]
        angle = atan2(
            circle.centre.y,
            circle.centre.x,
        )

        return _angular_distance(
            angle,
            target_angle,
        )

    _, moon = min(moons, key=distance)

    return moon.centre


def build_figure14_anchor_set(
    diagram: CoreDiagram,
) -> tuple[Figure14Anchor, ...]:
    """Build the seven stated and inferred Figure 14 anchors.

    The anchors are ordered counter-clockwise beginning with the
    upper cardinal Moon centre.
    """

    radius = diagram.construction_circle.radius
    half_side = diagram.earth_square.half_side

    placement = build_oblique_placement(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    beta = placement.beta_radians

    junction_y = sqrt(
        radius * radius
        - half_side * half_side
    )

    top_moon = _nearest_moon_centre(
        diagram,
        pi / 2.0,
    )

    bottom_left_moon = _nearest_moon_centre(
        diagram,
        3.0 * pi / 2.0 - beta,
    )

    bottom_right_moon = _nearest_moon_centre(
        diagram,
        3.0 * pi / 2.0 + beta,
    )

    lower_left_gap = _point_on_circle(
        radius,
        pi + beta / 2.0,
    )

    lower_right_gap = _point_on_circle(
        radius,
        tau - beta / 2.0,
    )

    return (
        Figure14Anchor(
            index=0,
            name="top_moon_centre",
            role=Figure14AnchorRole.MOON_CENTRE,
            evidence=AnchorEvidence.SOURCE_TEXT_AND_PLATE,
            point=top_moon,
        ),
        Figure14Anchor(
            index=1,
            name="upper_left_square_circle_junction",
            role=(
                Figure14AnchorRole.SQUARE_CIRCLE_JUNCTION
            ),
            evidence=AnchorEvidence.SOURCE_TEXT_AND_PLATE,
            point=Point2D(
                -half_side,
                junction_y,
            ),
        ),
        Figure14Anchor(
            index=2,
            name="lower_left_inter_moon_gap",
            role=Figure14AnchorRole.INTER_MOON_GAP,
            evidence=AnchorEvidence.PLATE_INFERENCE,
            point=lower_left_gap,
        ),
        Figure14Anchor(
            index=3,
            name="bottom_left_moon_centre",
            role=Figure14AnchorRole.MOON_CENTRE,
            evidence=AnchorEvidence.SOURCE_TEXT_AND_PLATE,
            point=bottom_left_moon,
        ),
        Figure14Anchor(
            index=4,
            name="bottom_right_moon_centre",
            role=Figure14AnchorRole.MOON_CENTRE,
            evidence=AnchorEvidence.SOURCE_TEXT_AND_PLATE,
            point=bottom_right_moon,
        ),
        Figure14Anchor(
            index=5,
            name="lower_right_inter_moon_gap",
            role=Figure14AnchorRole.INTER_MOON_GAP,
            evidence=AnchorEvidence.PLATE_INFERENCE,
            point=lower_right_gap,
        ),
        Figure14Anchor(
            index=6,
            name="upper_right_square_circle_junction",
            role=(
                Figure14AnchorRole.SQUARE_CIRCLE_JUNCTION
            ),
            evidence=AnchorEvidence.SOURCE_TEXT_AND_PLATE,
            point=Point2D(
                half_side,
                junction_y,
            ),
        ),
    )


def build_regular_heptagram(
    diagram: CoreDiagram,
    family: HeptagramFamily = HeptagramFamily.STEP_2,
) -> HeptagramGeometry:
    """Build an exact regular heptagram with its first point at the top."""

    radius = diagram.construction_circle.radius

    vertices = tuple(
        _point_on_circle(
            radius,
            pi / 2.0 + index * tau / 7.0,
        )
        for index in range(7)
    )

    return HeptagramGeometry(
        name=f"REGULAR_7_{family.value}",
        family=family,
        vertices=vertices,
    )


def build_scaffold_heptagram(
    diagram: CoreDiagram,
    scaffold: MichellSeptenaryScaffold | None = None,
    family: HeptagramFamily = HeptagramFamily.STEP_2,
) -> HeptagramGeometry:
    """Select the Figure 14-like vertices of the 28-point scaffold."""

    if scaffold is None:
        scaffold = build_michell_28_point_scaffold(
            diagram
        )

    by_index = {
        point.index: point.point
        for point in scaffold.points
    }

    # Ordered from the upper cardinal point and then
    # counter-clockwise around the zodiac circle.
    selected_indices = (
        7,
        11,
        15,
        19,
        23,
        27,
        3,
    )

    vertices = tuple(
        by_index[index]
        for index in selected_indices
    )

    return HeptagramGeometry(
        name=f"MICHELL_28_7_{family.value}",
        family=family,
        vertices=vertices,
    )


def build_figure14_aligned_heptagram(
    diagram: CoreDiagram,
    family: HeptagramFamily = HeptagramFamily.STEP_2,
) -> HeptagramGeometry:
    """Build a heptagram whose vertices are the Figure 14 anchors."""

    anchors = build_figure14_anchor_set(diagram)

    return HeptagramGeometry(
        name=f"FIGURE14_ALIGNED_7_{family.value}",
        family=family,
        vertices=tuple(
            anchor.point
            for anchor in anchors
        ),
    )
