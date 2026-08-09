"""Preregistered v0.8 propagation of Michell Figure 194 Method 2.

This module executes the Phase 8D protocol only:

    local 7 -> original-triangle 21 -> original+reciprocal 42

The local Method 2 step is imported from the frozen Phase 8C implementation.
No plate fitting, Method 1 comparison, deduplication, or fitted parameter is
present here.
"""

from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
)
import json
from math import (
    cos,
    pi,
    sin,
    sqrt,
    tau,
)

from .sevenfold_dual_method import (
    method_2_step_from_source_geometry,
)


PROTOCOL_SHA256 = (
    "b87b6c54f6084d549236a7f27b336d396a980b1404337f751862a8e5476217c1"
)

PHASE8D_COMMIT = "11b023e"

PHASE8C_COMMIT = "05e8a89"

PHASE8C_LOCAL_COMPARISON_SHA256 = (
    "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f"
)

METHOD2_SOURCE_SHA256 = (
    "33c5fee3a1d198abc1eb73c1ff114829b1dc5a66f0e355605ed25793b33f5c70"
)

IDENTITY_TOLERANCE_RADIANS = 1.0e-12

GAMMA_0_RADIANS = pi / 2.0

STOPPING_STATUS = (
    "METHOD2_7_21_42_PROPAGATION_COMPLETE"
)


@dataclass(frozen=True, slots=True)
class PropagationPoint:
    """One semantic circumference mark."""

    label: str
    carrier_index: int
    carrier_family: str
    local_k: int
    angle_radians: float
    x: float
    y: float


@dataclass(frozen=True, slots=True)
class RawCyclicGap:
    """One cyclic angular gap without a regularity residual."""

    start_label: str
    end_label: str
    gap_radians: float


@dataclass(frozen=True, slots=True)
class ResidualCyclicGap:
    """One cyclic gap with its preregistered regular-gap residual."""

    start_label: str
    end_label: str
    gap_radians: float
    signed_gap_residual_radians: float
    absolute_gap_residual_radians: float


@dataclass(frozen=True, slots=True)
class LocalSevenResult:
    """Registered local seven-mark operational completion."""

    semantic_count: int
    sorted_points: tuple[PropagationPoint, ...]
    cyclic_gaps: tuple[RawCyclicGap, ...]


@dataclass(frozen=True, slots=True)
class PropagationSetResult:
    """Registered 21- or 42-point result and nonuniformity metrics."""

    semantic_count: int
    numerical_distinct_count: int
    sorted_points: tuple[PropagationPoint, ...]
    cyclic_gaps: tuple[ResidualCyclicGap, ...]
    regular_gap_radians: float
    minimum_gap_radians: float
    maximum_gap_radians: float
    mean_gap_radians: float
    gap_range_radians: float
    rms_gap_residual_radians: float
    maximum_absolute_gap_residual_radians: float
    normalized_rms_gap_residual: float
    numerically_regular_at_identity_tolerance: bool


@dataclass(frozen=True, slots=True)
class TwentyOneStructuralChecks:
    """Registered S1-S2 checks for the original 21-point set."""

    all_semantic_marks_numerically_distinct: bool
    rotational_identity_2pi_over_3: bool


@dataclass(frozen=True, slots=True)
class ReciprocalTwentyOneResult:
    """Registered reciprocal-triangle 21-point subset and S3."""

    semantic_count: int
    numerical_distinct_count: int
    sorted_points: tuple[PropagationPoint, ...]
    all_semantic_marks_numerically_distinct: bool
    rotated_original_identity_pi_over_3: bool


@dataclass(frozen=True, slots=True)
class FortyTwoStructuralChecks:
    """Registered S1, S4, and S5 checks for the 42-point set."""

    all_semantic_marks_numerically_distinct: bool
    union_identity: bool
    rotational_identity_pi_over_3: bool


@dataclass(frozen=True, slots=True)
class PropagationComparison:
    """Registered descriptive comparison of 21- and 42-point nonuniformity."""

    rms_ratio_42_over_21: float | None
    max_abs_ratio_42_over_21: float | None
    rms_order: tuple[str, ...] | str
    maximum_absolute_residual_order: tuple[str, ...] | str


@dataclass(frozen=True, slots=True)
class PropagationDegreesOfFreedom:
    """Preregistered zero-fit degrees of freedom."""

    continuous_fitted_parameters: int = 0
    scale_parameters: int = 0
    target_based_candidate_choices: int = 0
    optimized_phase_parameters: int = 0
    fitted_deduplication_thresholds: int = 0


@dataclass(frozen=True, slots=True)
class Method2PropagationResult:
    """Complete Phase 8E propagation result."""

    schema: str
    phase: str
    protocol_sha256: str
    phase8d_commit: str
    phase8c_commit: str
    phase8c_local_comparison_sha256: str
    method2_source_sha256: str
    identity_tolerance_radians: float
    alpha_2_radians: float
    gamma_0_radians: float
    local_seven: LocalSevenResult
    twenty_one: PropagationSetResult
    twenty_one_structural_checks: TwentyOneStructuralChecks
    reciprocal_twenty_one: ReciprocalTwentyOneResult
    forty_two: PropagationSetResult
    forty_two_structural_checks: FortyTwoStructuralChecks
    comparison: PropagationComparison
    degrees_of_freedom: PropagationDegreesOfFreedom
    stopping_status: str


def _normalise_angle(
    angle: float,
) -> float:
    return angle % tau


def _circular_distance(
    first: float,
    second: float,
) -> float:
    raw = abs(
        _normalise_angle(
            first
        )
        - _normalise_angle(
            second
        )
    )

    return min(
        raw,
        tau - raw,
    )


def _point(
    *,
    label: str,
    carrier_index: int,
    carrier_family: str,
    local_k: int,
    angle_radians: float,
) -> PropagationPoint:
    angle = _normalise_angle(
        angle_radians
    )

    return PropagationPoint(
        label=label,
        carrier_index=carrier_index,
        carrier_family=carrier_family,
        local_k=local_k,
        angle_radians=angle,
        x=cos(
            angle
        ),
        y=sin(
            angle
        ),
    )


def _generate_carrier_marks(
    *,
    carrier_index: int,
    carrier_family: str,
    carrier_angle_radians: float,
    alpha_2_radians: float,
    label_prefix: str,
) -> tuple[PropagationPoint, ...]:
    return tuple(
        _point(
            label=(
                f"{label_prefix}:"
                f"c{carrier_index}:"
                f"k{local_k:+d}"
            ),
            carrier_index=carrier_index,
            carrier_family=carrier_family,
            local_k=local_k,
            angle_radians=(
                carrier_angle_radians
                + local_k
                * alpha_2_radians
            ),
        )
        for local_k in range(
            -3,
            4,
        )
    )


def _sorted_points(
    points: tuple[PropagationPoint, ...],
) -> tuple[PropagationPoint, ...]:
    return tuple(
        sorted(
            points,
            key=lambda point: (
                point.angle_radians,
                point.label,
            ),
        )
    )


def _raw_cyclic_gaps(
    points: tuple[PropagationPoint, ...],
) -> tuple[RawCyclicGap, ...]:
    ordered = _sorted_points(
        points
    )

    gaps: list[RawCyclicGap] = []

    for index, start in enumerate(
        ordered
    ):
        end = ordered[
            (
                index
                + 1
            )
            % len(
                ordered
            )
        ]

        if (
            index
            + 1
            < len(
                ordered
            )
        ):
            gap = (
                end.angle_radians
                - start.angle_radians
            )
        else:
            gap = (
                end.angle_radians
                + tau
                - start.angle_radians
            )

        gaps.append(
            RawCyclicGap(
                start_label=start.label,
                end_label=end.label,
                gap_radians=gap,
            )
        )

    return tuple(
        gaps
    )


def _residual_cyclic_gaps(
    points: tuple[PropagationPoint, ...],
) -> tuple[
    tuple[ResidualCyclicGap, ...],
    float,
]:
    ordered = _sorted_points(
        points
    )

    regular_gap = (
        tau
        / len(
            ordered
        )
    )

    raw = _raw_cyclic_gaps(
        points
    )

    gaps = tuple(
        ResidualCyclicGap(
            start_label=gap.start_label,
            end_label=gap.end_label,
            gap_radians=gap.gap_radians,
            signed_gap_residual_radians=(
                gap.gap_radians
                - regular_gap
            ),
            absolute_gap_residual_radians=abs(
                gap.gap_radians
                - regular_gap
            ),
        )
        for gap in raw
    )

    return (
        gaps,
        regular_gap,
    )


def _numerical_distinct_count(
    points: tuple[PropagationPoint, ...],
) -> int:
    """Count circular angle clusters without changing the semantic point set."""

    size = len(
        points
    )

    parent = list(
        range(
            size
        )
    )

    def find(
        index: int,
    ) -> int:
        while (
            parent[
                index
            ]
            != index
        ):
            parent[
                index
            ] = parent[
                parent[
                    index
                ]
            ]

            index = parent[
                index
            ]

        return index

    def union(
        left: int,
        right: int,
    ) -> None:
        root_left = find(
            left
        )

        root_right = find(
            right
        )

        if (
            root_left
            != root_right
        ):
            parent[
                root_right
            ] = root_left

    for left in range(
        size
    ):
        for right in range(
            left + 1,
            size,
        ):
            if (
                _circular_distance(
                    points[
                        left
                    ].angle_radians,
                    points[
                        right
                    ].angle_radians,
                )
                <= IDENTITY_TOLERANCE_RADIANS
            ):
                union(
                    left,
                    right,
                )

    return len(
        {
            find(
                index
            )
            for index in range(
                size
            )
        }
    )


def _angle_multiset_matches(
    source: tuple[PropagationPoint, ...],
    target: tuple[PropagationPoint, ...],
    *,
    rotation_radians: float = 0.0,
) -> bool:
    """Compare two semantic angle multisets under a fixed registered rotation."""

    if (
        len(
            source
        )
        != len(
            target
        )
    ):
        return False

    used: set[int] = set()

    for source_point in source:
        rotated = _normalise_angle(
            source_point.angle_radians
            + rotation_radians
        )

        candidates = [
            index
            for index, target_point
            in enumerate(
                target
            )
            if (
                index
                not in used
                and _circular_distance(
                    rotated,
                    target_point.angle_radians,
                )
                <= IDENTITY_TOLERANCE_RADIANS
            )
        ]

        if len(
            candidates
        ) != 1:
            return False

        used.add(
            candidates[
                0
            ]
        )

    return (
        len(
            used
        )
        == len(
            target
        )
    )


def _set_result(
    points: tuple[PropagationPoint, ...],
) -> PropagationSetResult:
    ordered = _sorted_points(
        points
    )

    gaps, regular_gap = (
        _residual_cyclic_gaps(
            points
        )
    )

    raw_gaps = tuple(
        gap.gap_radians
        for gap in gaps
    )

    signed = tuple(
        gap.signed_gap_residual_radians
        for gap in gaps
    )

    absolute = tuple(
        gap.absolute_gap_residual_radians
        for gap in gaps
    )

    minimum = min(
        raw_gaps
    )

    maximum = max(
        raw_gaps
    )

    mean = (
        sum(
            raw_gaps
        )
        / len(
            raw_gaps
        )
    )

    rms = sqrt(
        sum(
            value
            * value
            for value in signed
        )
        / len(
            signed
        )
    )

    maximum_absolute = max(
        absolute
    )

    if (
        abs(
            sum(
                raw_gaps
            )
            - tau
        )
        > IDENTITY_TOLERANCE_RADIANS
    ):
        raise AssertionError(
            "Cyclic gaps do not close to 2*pi at the "
            "registered implementation tolerance."
        )

    if (
        abs(
            mean
            - regular_gap
        )
        > IDENTITY_TOLERANCE_RADIANS
    ):
        raise AssertionError(
            "Mean cyclic gap does not equal 2*pi/N at the "
            "registered implementation tolerance."
        )

    return PropagationSetResult(
        semantic_count=len(
            points
        ),
        numerical_distinct_count=(
            _numerical_distinct_count(
                points
            )
        ),
        sorted_points=ordered,
        cyclic_gaps=gaps,
        regular_gap_radians=regular_gap,
        minimum_gap_radians=minimum,
        maximum_gap_radians=maximum,
        mean_gap_radians=mean,
        gap_range_radians=(
            maximum
            - minimum
        ),
        rms_gap_residual_radians=rms,
        maximum_absolute_gap_residual_radians=(
            maximum_absolute
        ),
        normalized_rms_gap_residual=(
            rms
            / regular_gap
        ),
        numerically_regular_at_identity_tolerance=(
            maximum_absolute
            <= IDENTITY_TOLERANCE_RADIANS
        ),
    )


def _ordering(
    *,
    twenty_one_value: float,
    forty_two_value: float,
) -> tuple[str, ...] | str:
    if (
        twenty_one_value
        < forty_two_value
    ):
        return (
            "twenty_one",
            "forty_two",
        )

    if (
        forty_two_value
        < twenty_one_value
    ):
        return (
            "forty_two",
            "twenty_one",
        )

    return "TIE"


def build_method2_propagation() -> Method2PropagationResult:
    """Execute the complete preregistered Method 2 propagation."""

    alpha_2 = (
        method_2_step_from_source_geometry()
    )

    local_points = (
        _generate_carrier_marks(
            carrier_index=0,
            carrier_family="local",
            carrier_angle_radians=(
                GAMMA_0_RADIANS
            ),
            alpha_2_radians=(
                alpha_2
            ),
            label_prefix="local7",
        )
    )

    local_seven = LocalSevenResult(
        semantic_count=len(
            local_points
        ),
        sorted_points=_sorted_points(
            local_points
        ),
        cyclic_gaps=_raw_cyclic_gaps(
            local_points
        ),
    )

    original_parts: list[
        PropagationPoint
    ] = []

    for j in range(
        3
    ):
        carrier_angle = (
            GAMMA_0_RADIANS
            + j
            * (
                2.0
                * pi
                / 3.0
            )
        )

        original_parts.extend(
            _generate_carrier_marks(
                carrier_index=j,
                carrier_family="original",
                carrier_angle_radians=(
                    carrier_angle
                ),
                alpha_2_radians=(
                    alpha_2
                ),
                label_prefix="original21",
            )
        )

    original_points = tuple(
        original_parts
    )

    twenty_one = _set_result(
        original_points
    )

    reciprocal_parts: list[
        PropagationPoint
    ] = []

    forty_two_parts: list[
        PropagationPoint
    ] = []

    for n in range(
        6
    ):
        family = (
            "original"
            if (
                n
                % 2
                == 0
            )
            else "reciprocal"
        )

        carrier_angle = (
            GAMMA_0_RADIANS
            + n
            * (
                pi
                / 3.0
            )
        )

        carrier_points = (
            _generate_carrier_marks(
                carrier_index=n,
                carrier_family=family,
                carrier_angle_radians=(
                    carrier_angle
                ),
                alpha_2_radians=(
                    alpha_2
                ),
                label_prefix="hex42",
            )
        )

        forty_two_parts.extend(
            carrier_points
        )

        if (
            family
            == "reciprocal"
        ):
            reciprocal_parts.extend(
                carrier_points
            )

    reciprocal_points = tuple(
        reciprocal_parts
    )

    forty_two_points = tuple(
        forty_two_parts
    )

    reciprocal_twenty_one = (
        ReciprocalTwentyOneResult(
            semantic_count=len(
                reciprocal_points
            ),
            numerical_distinct_count=(
                _numerical_distinct_count(
                    reciprocal_points
                )
            ),
            sorted_points=_sorted_points(
                reciprocal_points
            ),
            all_semantic_marks_numerically_distinct=(
                _numerical_distinct_count(
                    reciprocal_points
                )
                == len(
                    reciprocal_points
                )
            ),
            rotated_original_identity_pi_over_3=(
                _angle_multiset_matches(
                    original_points,
                    reciprocal_points,
                    rotation_radians=(
                        pi
                        / 3.0
                    ),
                )
            ),
        )
    )

    forty_two = _set_result(
        forty_two_points
    )

    twenty_one_structural_checks = (
        TwentyOneStructuralChecks(
            all_semantic_marks_numerically_distinct=(
                twenty_one.numerical_distinct_count
                == twenty_one.semantic_count
            ),
            rotational_identity_2pi_over_3=(
                _angle_multiset_matches(
                    original_points,
                    original_points,
                    rotation_radians=(
                        2.0
                        * pi
                        / 3.0
                    ),
                )
            ),
        )
    )

    combined_subset_points = (
        original_points
        + reciprocal_points
    )

    forty_two_structural_checks = (
        FortyTwoStructuralChecks(
            all_semantic_marks_numerically_distinct=(
                forty_two.numerical_distinct_count
                == forty_two.semantic_count
            ),
            union_identity=(
                _angle_multiset_matches(
                    combined_subset_points,
                    forty_two_points,
                )
            ),
            rotational_identity_pi_over_3=(
                _angle_multiset_matches(
                    forty_two_points,
                    forty_two_points,
                    rotation_radians=(
                        pi
                        / 3.0
                    ),
                )
            ),
        )
    )

    if (
        twenty_one.rms_gap_residual_radians
        == 0.0
    ):
        rms_ratio = None
    else:
        rms_ratio = (
            forty_two.rms_gap_residual_radians
            / twenty_one.rms_gap_residual_radians
        )

    if (
        twenty_one
        .maximum_absolute_gap_residual_radians
        == 0.0
    ):
        max_ratio = None
    else:
        max_ratio = (
            forty_two
            .maximum_absolute_gap_residual_radians
            / twenty_one
            .maximum_absolute_gap_residual_radians
        )

    comparison = PropagationComparison(
        rms_ratio_42_over_21=(
            rms_ratio
        ),
        max_abs_ratio_42_over_21=(
            max_ratio
        ),
        rms_order=_ordering(
            twenty_one_value=(
                twenty_one
                .rms_gap_residual_radians
            ),
            forty_two_value=(
                forty_two
                .rms_gap_residual_radians
            ),
        ),
        maximum_absolute_residual_order=(
            _ordering(
                twenty_one_value=(
                    twenty_one
                    .maximum_absolute_gap_residual_radians
                ),
                forty_two_value=(
                    forty_two
                    .maximum_absolute_gap_residual_radians
                ),
            )
        ),
    )

    return Method2PropagationResult(
        schema=(
            "njg_michell_v0_8_method2_propagation"
        ),
        phase="8E",
        protocol_sha256=PROTOCOL_SHA256,
        phase8d_commit=PHASE8D_COMMIT,
        phase8c_commit=PHASE8C_COMMIT,
        phase8c_local_comparison_sha256=(
            PHASE8C_LOCAL_COMPARISON_SHA256
        ),
        method2_source_sha256=(
            METHOD2_SOURCE_SHA256
        ),
        identity_tolerance_radians=(
            IDENTITY_TOLERANCE_RADIANS
        ),
        alpha_2_radians=alpha_2,
        gamma_0_radians=(
            GAMMA_0_RADIANS
        ),
        local_seven=local_seven,
        twenty_one=twenty_one,
        twenty_one_structural_checks=(
            twenty_one_structural_checks
        ),
        reciprocal_twenty_one=(
            reciprocal_twenty_one
        ),
        forty_two=forty_two,
        forty_two_structural_checks=(
            forty_two_structural_checks
        ),
        comparison=comparison,
        degrees_of_freedom=(
            PropagationDegreesOfFreedom()
        ),
        stopping_status=STOPPING_STATUS,
    )


def method2_propagation_to_json(
    result: Method2PropagationResult,
) -> str:
    """Serialize the canonical Phase 8E result deterministically."""

    return (
        json.dumps(
            asdict(
                result
            ),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _order_text(
    value: tuple[str, ...] | str,
) -> str:
    if isinstance(
        value,
        tuple,
    ):
        return " < ".join(
            value
        )

    return value


def method2_propagation_to_markdown(
    result: Method2PropagationResult,
) -> str:
    """Render only the preregistered Phase 8E quantities."""

    deg = (
        180.0
        / pi
    )

    twenty_one = (
        result.twenty_one
    )

    forty_two = (
        result.forty_two
    )

    comparison = (
        result.comparison
    )

    lines = [
        "# v0.8 Method 2 propagation result",
        "",
        "## Status",
        "",
        f"`{result.stopping_status}`",
        "",
        "This is the execution of the preregistered Phase 8D",
        "Figure 194 Method 2 propagation audit.",
        "",
        "No Method 1 28-point comparison, Figure 14 comparison,",
        "plate fitting, phase optimization, or deduplication is included.",
        "",
        "## Frozen provenance",
        "",
        "```text",
        f"protocol_sha256 = {result.protocol_sha256}",
        f"phase8d_commit = {result.phase8d_commit}",
        f"phase8c_commit = {result.phase8c_commit}",
        (
            "phase8c_local_comparison_sha256 = "
            f"{result.phase8c_local_comparison_sha256}"
        ),
        (
            "method2_source_sha256 = "
            f"{result.method2_source_sha256}"
        ),
        "```",
        "",
        "## Frozen construction",
        "",
        "```text",
        (
            "alpha_2_radians = "
            f"{repr(result.alpha_2_radians)}"
        ),
        (
            "alpha_2_degrees = "
            f"{repr(result.alpha_2_radians * deg)}"
        ),
        (
            "gamma_0_radians = "
            f"{repr(result.gamma_0_radians)}"
        ),
        (
            "gamma_0_degrees = "
            f"{repr(result.gamma_0_radians * deg)}"
        ),
        (
            "identity_tolerance_radians = "
            f"{repr(result.identity_tolerance_radians)}"
        ),
        "```",
        "",
        "The local seven-mark completion uses the preregistered",
        "`k = -3, ..., +3` operational rule.",
        "",
        "## Structural identities",
        "",
        "```text",
        (
            "local seven semantic count = "
            f"{result.local_seven.semantic_count}"
        ),
        (
            "21 semantic count = "
            f"{twenty_one.semantic_count}"
        ),
        (
            "21 numerical distinct count = "
            f"{twenty_one.numerical_distinct_count}"
        ),
        (
            "S1 21 all distinct = "
            f"{result.twenty_one_structural_checks.all_semantic_marks_numerically_distinct}"
        ),
        (
            "S2 21 rotation 2*pi/3 identity = "
            f"{result.twenty_one_structural_checks.rotational_identity_2pi_over_3}"
        ),
        (
            "reciprocal 21 semantic count = "
            f"{result.reciprocal_twenty_one.semantic_count}"
        ),
        (
            "S3 reciprocal = original rotated pi/3 = "
            f"{result.reciprocal_twenty_one.rotated_original_identity_pi_over_3}"
        ),
        (
            "42 semantic count = "
            f"{forty_two.semantic_count}"
        ),
        (
            "42 numerical distinct count = "
            f"{forty_two.numerical_distinct_count}"
        ),
        (
            "S1 42 all distinct = "
            f"{result.forty_two_structural_checks.all_semantic_marks_numerically_distinct}"
        ),
        (
            "S4 42 union identity = "
            f"{result.forty_two_structural_checks.union_identity}"
        ),
        (
            "S5 42 rotation pi/3 identity = "
            f"{result.forty_two_structural_checks.rotational_identity_pi_over_3}"
        ),
        "```",
        "",
        "S1-S5 are construction/implementation identities, not empirical",
        "validation tests.",
        "",
        "## Twenty-one-point nonuniformity",
        "",
        "```text",
        (
            "regular_gap_degrees = "
            f"{repr(twenty_one.regular_gap_radians * deg)}"
        ),
        (
            "minimum_gap_degrees = "
            f"{repr(twenty_one.minimum_gap_radians * deg)}"
        ),
        (
            "maximum_gap_degrees = "
            f"{repr(twenty_one.maximum_gap_radians * deg)}"
        ),
        (
            "mean_gap_degrees = "
            f"{repr(twenty_one.mean_gap_radians * deg)}"
        ),
        (
            "gap_range_degrees = "
            f"{repr(twenty_one.gap_range_radians * deg)}"
        ),
        (
            "rms_gap_residual_degrees = "
            f"{repr(twenty_one.rms_gap_residual_radians * deg)}"
        ),
        (
            "maximum_absolute_gap_residual_degrees = "
            f"{repr(twenty_one.maximum_absolute_gap_residual_radians * deg)}"
        ),
        (
            "normalized_rms_gap_residual = "
            f"{repr(twenty_one.normalized_rms_gap_residual)}"
        ),
        (
            "numerically_regular_at_identity_tolerance = "
            f"{twenty_one.numerically_regular_at_identity_tolerance}"
        ),
        "```",
        "",
        "## Forty-two-point nonuniformity",
        "",
        "```text",
        (
            "regular_gap_degrees = "
            f"{repr(forty_two.regular_gap_radians * deg)}"
        ),
        (
            "minimum_gap_degrees = "
            f"{repr(forty_two.minimum_gap_radians * deg)}"
        ),
        (
            "maximum_gap_degrees = "
            f"{repr(forty_two.maximum_gap_radians * deg)}"
        ),
        (
            "mean_gap_degrees = "
            f"{repr(forty_two.mean_gap_radians * deg)}"
        ),
        (
            "gap_range_degrees = "
            f"{repr(forty_two.gap_range_radians * deg)}"
        ),
        (
            "rms_gap_residual_degrees = "
            f"{repr(forty_two.rms_gap_residual_radians * deg)}"
        ),
        (
            "maximum_absolute_gap_residual_degrees = "
            f"{repr(forty_two.maximum_absolute_gap_residual_radians * deg)}"
        ),
        (
            "normalized_rms_gap_residual = "
            f"{repr(forty_two.normalized_rms_gap_residual)}"
        ),
        (
            "numerically_regular_at_identity_tolerance = "
            f"{forty_two.numerically_regular_at_identity_tolerance}"
        ),
        "```",
        "",
        "Every individual cyclic gap and its residual is retained in the",
        "canonical JSON artifact.",
        "",
        "## Registered 21-versus-42 comparison",
        "",
        "```text",
        (
            "rms_ratio_42_over_21 = "
            f"{repr(comparison.rms_ratio_42_over_21)}"
        ),
        (
            "max_abs_ratio_42_over_21 = "
            f"{repr(comparison.max_abs_ratio_42_over_21)}"
        ),
        (
            "rms_order = "
            f"{_order_text(comparison.rms_order)}"
        ),
        (
            "maximum_absolute_residual_order = "
            f"{_order_text(comparison.maximum_absolute_residual_order)}"
        ),
        "```",
        "",
        "These comparisons are descriptive only. No direction of improvement",
        "was preregistered as a success criterion.",
        "",
        "## Degrees of freedom",
        "",
        "```text",
        "continuous_fitted_parameters = 0",
        "scale_parameters = 0",
        "target_based_candidate_choices = 0",
        "optimized_phase_parameters = 0",
        "fitted_deduplication_thresholds = 0",
        "```",
        "",
        "## Interpretation boundary",
        "",
        "The result describes the deterministic geometry of the preregistered",
        "Method 2 operationalization. It does not establish historical intent,",
        "physical significance, archaeological validation, or statistical",
        "significance. Comparison with the Method 1 28-point geometry remains",
        "explicitly deferred.",
        "",
    ]

    return "\n".join(
        lines
    )
