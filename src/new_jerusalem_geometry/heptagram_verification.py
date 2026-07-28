"""Verification and candidate fitting for Michell's Figure 14."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from math import atan2, pi, sqrt, tau

from .core_geometry import CoreDiagram
from .heptagram_geometry import (
    AnchorEvidence,
    Figure14Anchor,
    Figure14AnchorRole,
    HeptagramFamily,
    HeptagramGeometry,
)
from .verification import Check


def _root_mean_square(
    values: tuple[float, ...],
) -> float:
    if not values:
        return 0.0

    return sqrt(
        sum(value * value for value in values)
        / len(values)
    )


def _wrapped_angle_difference(
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


@dataclass(frozen=True, slots=True)
class HeptagramFit:
    """Residuals between one candidate and the Figure 14 anchors."""

    candidate_name: str
    point_residuals: tuple[float, ...]
    angular_residuals_radians: tuple[float, ...]
    stated_point_residuals: tuple[float, ...]
    inferred_point_residuals: tuple[float, ...]

    @property
    def maximum_point_residual(self) -> float:
        return max(self.point_residuals)

    @property
    def rms_point_residual(self) -> float:
        return _root_mean_square(
            self.point_residuals
        )

    @property
    def maximum_stated_point_residual(self) -> float:
        return max(self.stated_point_residuals)

    @property
    def rms_stated_point_residual(self) -> float:
        return _root_mean_square(
            self.stated_point_residuals
        )

    @property
    def maximum_angular_residual_degrees(self) -> float:
        return (
            max(self.angular_residuals_radians)
            * 180.0
            / pi
        )

    @property
    def rms_angular_residual_degrees(self) -> float:
        return (
            _root_mean_square(
                self.angular_residuals_radians
            )
            * 180.0
            / pi
        )


@dataclass(frozen=True, slots=True)
class Figure14VerificationReport:
    """Full verification of the Figure 14 candidate systems."""

    checks: tuple[Check, ...]
    moon_centre_count: int
    junction_count: int
    gap_count: int
    stated_anchor_count: int
    inferred_anchor_count: int
    regular_fit: HeptagramFit
    scaffold_fit: HeptagramFit
    aligned_fit: HeptagramFit
    anchor_step_angles_radians: tuple[float, ...]
    regular_edge_lengths: tuple[float, ...]
    scaffold_edge_lengths: tuple[float, ...]
    aligned_edge_lengths: tuple[float, ...]

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks)


def compare_heptagram_to_anchors(
    candidate: HeptagramGeometry,
    anchors: tuple[Figure14Anchor, ...],
) -> HeptagramFit:
    """Compare one seven-vertex candidate with the anchor system."""

    if len(candidate.vertices) != len(anchors):
        raise ValueError(
            "Candidate and anchor counts must agree."
        )

    point_residuals: list[float] = []
    angular_residuals: list[float] = []
    stated_residuals: list[float] = []
    inferred_residuals: list[float] = []

    for vertex, anchor in zip(
        candidate.vertices,
        anchors,
        strict=True,
    ):
        point_residual = vertex.distance_to(
            anchor.point
        )

        vertex_angle = atan2(
            vertex.y,
            vertex.x,
        )

        anchor_angle = atan2(
            anchor.point.y,
            anchor.point.x,
        )

        angular_residual = _wrapped_angle_difference(
            vertex_angle,
            anchor_angle,
        )

        point_residuals.append(point_residual)
        angular_residuals.append(angular_residual)

        if (
            anchor.evidence
            is AnchorEvidence.SOURCE_TEXT_AND_PLATE
        ):
            stated_residuals.append(
                point_residual
            )
        else:
            inferred_residuals.append(
                point_residual
            )

    return HeptagramFit(
        candidate_name=candidate.name,
        point_residuals=tuple(point_residuals),
        angular_residuals_radians=tuple(
            angular_residuals
        ),
        stated_point_residuals=tuple(
            stated_residuals
        ),
        inferred_point_residuals=tuple(
            inferred_residuals
        ),
    )


def verify_figure14_heptagrams(
    diagram: CoreDiagram,
    anchors: tuple[Figure14Anchor, ...],
    regular: HeptagramGeometry,
    scaffold: HeptagramGeometry,
    aligned: HeptagramGeometry,
    tolerance: float = 1.0e-12,
) -> Figure14VerificationReport:
    """Verify Figure 14 anchors and all three candidate systems."""

    if tolerance <= 0.0:
        raise ValueError("Tolerance must be positive.")

    checks: list[Check] = []

    role_counts = Counter(
        anchor.role
        for anchor in anchors
    )

    evidence_counts = Counter(
        anchor.evidence
        for anchor in anchors
    )

    moon_count = role_counts[
        Figure14AnchorRole.MOON_CENTRE
    ]

    junction_count = role_counts[
        Figure14AnchorRole.SQUARE_CIRCLE_JUNCTION
    ]

    gap_count = role_counts[
        Figure14AnchorRole.INTER_MOON_GAP
    ]

    stated_count = evidence_counts[
        AnchorEvidence.SOURCE_TEXT_AND_PLATE
    ]

    inferred_count = evidence_counts[
        AnchorEvidence.PLATE_INFERENCE
    ]

    checks.extend(
        [
            Check(
                name="figure14_anchor_count",
                residual=float(len(anchors) - 7),
                tolerance=0.0,
            ),
            Check(
                name="figure14_moon_centre_count",
                residual=float(moon_count - 3),
                tolerance=0.0,
            ),
            Check(
                name="figure14_junction_count",
                residual=float(junction_count - 2),
                tolerance=0.0,
            ),
            Check(
                name="figure14_gap_count",
                residual=float(gap_count - 2),
                tolerance=0.0,
            ),
            Check(
                name="figure14_stated_anchor_count",
                residual=float(stated_count - 5),
                tolerance=0.0,
            ),
            Check(
                name="figure14_inferred_anchor_count",
                residual=float(inferred_count - 2),
                tolerance=0.0,
            ),
        ]
    )

    radius = diagram.construction_circle.radius

    maximum_radial_residual = max(
        abs(anchor.radius - radius)
        for anchor in anchors
    )

    checks.append(
        Check(
            name="figure14_anchors_on_zodiac_circle",
            residual=maximum_radial_residual,
            tolerance=tolerance,
        )
    )

    reflected_pairs = (
        (1, 6),
        (2, 5),
        (3, 4),
    )

    maximum_reflection_residual = 0.0

    for left_index, right_index in reflected_pairs:
        left = anchors[left_index].point
        right = anchors[right_index].point

        maximum_reflection_residual = max(
            maximum_reflection_residual,
            abs(left.x + right.x),
            abs(left.y - right.y),
        )

    maximum_reflection_residual = max(
        maximum_reflection_residual,
        abs(anchors[0].point.x),
    )

    checks.append(
        Check(
            name="figure14_vertical_reflection_symmetry",
            residual=maximum_reflection_residual,
            tolerance=tolerance,
        )
    )

    for candidate in (
        regular,
        scaffold,
        aligned,
    ):
        checks.extend(
            [
                Check(
                    name=f"{candidate.name}_vertex_count",
                    residual=float(
                        len(candidate.vertices) - 7
                    ),
                    tolerance=0.0,
                ),
                Check(
                    name=f"{candidate.name}_family",
                    residual=float(
                        candidate.family.value
                        - HeptagramFamily.STEP_2.value
                    ),
                    tolerance=0.0,
                ),
            ]
        )

    expected_traversal = (
        0,
        2,
        4,
        6,
        1,
        3,
        5,
    )

    checks.append(
        Check(
            name="figure14_step2_traversal",
            residual=float(
                regular.traversal_indices()
                != expected_traversal
            ),
            tolerance=0.0,
        )
    )

    regular_fit = compare_heptagram_to_anchors(
        regular,
        anchors,
    )

    scaffold_fit = compare_heptagram_to_anchors(
        scaffold,
        anchors,
    )

    aligned_fit = compare_heptagram_to_anchors(
        aligned,
        anchors,
    )

    checks.extend(
        [
            Check(
                name="regular_candidate_within_0_05_u",
                residual=max(
                    0.0,
                    regular_fit.maximum_point_residual
                    - 0.05,
                ),
                tolerance=tolerance,
            ),
            Check(
                name="scaffold_candidate_within_0_05_u",
                residual=max(
                    0.0,
                    scaffold_fit.maximum_point_residual
                    - 0.05,
                ),
                tolerance=tolerance,
            ),
            Check(
                name="aligned_candidate_exact",
                residual=(
                    aligned_fit.maximum_point_residual
                ),
                tolerance=tolerance,
            ),
        ]
    )

    anchor_angles = tuple(
        anchor.angle_radians
        for anchor in anchors
    )

    anchor_steps = tuple(
        (
            anchor_angles[(index + 1) % len(anchor_angles)]
            - anchor_angles[index]
        )
        % tau
        for index in range(len(anchor_angles))
    )

    checks.append(
        Check(
            name="figure14_steps_sum_to_full_circle",
            residual=sum(anchor_steps) - tau,
            tolerance=tolerance,
        )
    )

    return Figure14VerificationReport(
        checks=tuple(checks),
        moon_centre_count=moon_count,
        junction_count=junction_count,
        gap_count=gap_count,
        stated_anchor_count=stated_count,
        inferred_anchor_count=inferred_count,
        regular_fit=regular_fit,
        scaffold_fit=scaffold_fit,
        aligned_fit=aligned_fit,
        anchor_step_angles_radians=anchor_steps,
        regular_edge_lengths=regular.edge_lengths(),
        scaffold_edge_lengths=scaffold.edge_lengths(),
        aligned_edge_lengths=aligned.edge_lengths(),
    )
