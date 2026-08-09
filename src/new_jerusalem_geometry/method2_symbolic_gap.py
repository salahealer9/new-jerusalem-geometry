"""Post-result explanatory audit of the frozen Method 2 gap structure.

The candidate class identities in this module were recognized after Phase 8E.
This module does not present them as preregistered predictions. It checks
whether they follow mechanically from the frozen semantic point construction.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import (
    asdict,
    dataclass,
)
from fractions import Fraction
import json
from math import (
    floor,
    pi,
    sqrt,
    tau,
)
from typing import Any


SPECIFICATION_SHA256 = (
    "d1fe38b9c2cd6cacae504510fa5392630467c11629766bd5cb5f74db9c14c9f8"
)

PHASE8E_COMMIT = "058a934"

PHASE8E_PROPAGATION_JSON_SHA256 = (
    "5af0b893ef9f18f5bb6c04e013f12298d816f426a2a248eccbd9230ab5ad4a43"
)

PHASE8C_LOCAL_COMPARISON_SHA256 = (
    "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f"
)

IDENTITY_TOLERANCE_RADIANS = 1.0e-12

STOPPING_STATUS = (
    "METHOD2_SYMBOLIC_GAP_AUDIT_COMPLETE"
)


@dataclass(frozen=True, slots=True)
class SymbolicGapClass:
    """One mechanically derived exact linear gap signature."""

    class_label: str
    a_pi_over_3: int
    b_alpha: int
    count: int
    exact_expression: str
    delta_residual_coefficient: int
    delta_form: str
    evaluated_gap_radians: float


@dataclass(frozen=True, slots=True)
class SymbolicSetAudit:
    """Exact class structure and derived nonuniformity identities."""

    point_count: int
    regular_gap_radians: float
    cyclic_class_pattern: str
    class_pattern_base: str
    class_pattern_repetitions: int
    signature_classes: tuple[SymbolicGapClass, ...]
    weighted_delta_residual_coefficient_sum: int
    rms_squared_delta_coefficient: int
    rms_delta_coefficient_symbolic: str
    maximum_absolute_delta_coefficient: int
    gap_range_delta_coefficient: int
    predicted_rms_gap_residual_radians: float
    frozen_rms_gap_residual_radians: float
    rms_identity_absolute_error_radians: float
    predicted_maximum_absolute_gap_residual_radians: float
    frozen_maximum_absolute_gap_residual_radians: float
    max_identity_absolute_error_radians: float
    predicted_gap_range_radians: float
    frozen_gap_range_radians: float
    range_identity_absolute_error_radians: float


@dataclass(frozen=True, slots=True)
class CrossRelationAudit:
    """Post-result exact relations between the 21- and 42-point metrics."""

    raw_rms_ratio_symbolic: str
    raw_rms_ratio_predicted: float
    raw_rms_ratio_frozen: float
    raw_rms_ratio_absolute_error: float
    max_abs_ratio_symbolic: str
    max_abs_ratio_predicted: float
    max_abs_ratio_frozen: float
    max_abs_ratio_absolute_error: float
    gap_range_ratio_symbolic: str
    gap_range_ratio_predicted: float
    gap_range_ratio_frozen: float
    gap_range_ratio_absolute_error: float
    normalized_rms_ratio_symbolic: str
    normalized_rms_ratio_predicted: float
    normalized_rms_ratio_frozen: float
    normalized_rms_ratio_absolute_error: float
    seven_step_closure_magnitude_radians: float
    twenty_one_range_vs_closure_absolute_error_radians: float
    forty_two_range_vs_closure_absolute_error_radians: float


@dataclass(frozen=True, slots=True)
class SymbolicAuditDegreesOfFreedom:
    """Explicit zero-fit status of this explanatory audit."""

    continuous_fitted_parameters: int = 0
    scale_parameters: int = 0
    gap_clustering_thresholds: int = 0
    optimized_symbolic_coefficients: int = 0
    candidate_class_selection_after_specification: int = 0


@dataclass(frozen=True, slots=True)
class Method2SymbolicGapAudit:
    """Complete Phase 8F explanatory audit."""

    schema: str
    phase: str
    evidential_status: str
    specification_sha256: str
    phase8e_commit: str
    phase8e_propagation_json_sha256: str
    phase8c_local_comparison_sha256: str
    identity_tolerance_radians: float
    alpha_radians: float
    exact_heptagonal_step_radians: float
    delta_radians: float
    delta_degrees: float
    twenty_one: SymbolicSetAudit
    forty_two: SymbolicSetAudit
    cross_relations: CrossRelationAudit
    degrees_of_freedom: SymbolicAuditDegreesOfFreedom
    stopping_status: str


def _point_q(
    point: dict[str, Any],
    *,
    point_count: int,
) -> int:
    carrier = int(
        point[
            "carrier_index"
        ]
    )

    if point_count == 21:
        return (
            2
            * carrier
        )

    if point_count == 42:
        return carrier

    raise ValueError(
        "Symbolic audit supports only 21- and 42-point sets."
    )


def _winding_number(
    point: dict[str, Any],
    *,
    point_count: int,
    alpha: float,
    gamma_0: float,
) -> tuple[int, float]:
    q = _point_q(
        point,
        point_count=point_count,
    )

    local_k = int(
        point[
            "local_k"
        ]
    )

    raw = (
        gamma_0
        + q
        * (
            pi
            / 3.0
        )
        + local_k
        * alpha
    )

    winding = floor(
        raw
        / tau
    )

    reconstructed = (
        raw
        - winding
        * tau
    )

    frozen_angle = float(
        point[
            "angle_radians"
        ]
    )

    error = abs(
        reconstructed
        - frozen_angle
    )

    if (
        error
        > IDENTITY_TOLERANCE_RADIANS
    ):
        raise AssertionError(
            (
                "Frozen point angle does not match its semantic "
                "unnormalized expression.",
                point[
                    "label"
                ],
                error,
            )
        )

    return (
        winding,
        reconstructed,
    )


def _derive_signatures(
    point_set: dict[str, Any],
    *,
    point_count: int,
    alpha: float,
    gamma_0: float,
) -> tuple[
    tuple[tuple[int, int], ...],
    tuple[float, ...],
]:
    points = list(
        point_set[
            "sorted_points"
        ]
    )

    gaps = list(
        point_set[
            "cyclic_gaps"
        ]
    )

    if (
        len(
            points
        )
        != point_count
        or len(
            gaps
        )
        != point_count
    ):
        raise AssertionError(
            "Frozen point/gap count does not match the requested audit."
        )

    semantic: list[
        tuple[
            int,
            int,
            int,
        ]
    ] = []

    for point in points:
        q = _point_q(
            point,
            point_count=point_count,
        )

        local_k = int(
            point[
                "local_k"
            ]
        )

        winding, _ = _winding_number(
            point,
            point_count=point_count,
            alpha=alpha,
            gamma_0=gamma_0,
        )

        semantic.append(
            (
                q,
                local_k,
                winding,
            )
        )

    signatures: list[
        tuple[
            int,
            int,
        ]
    ] = []

    evaluated: list[
        float
    ] = []

    for index, (
        q,
        local_k,
        winding,
    ) in enumerate(
        semantic
    ):
        next_q, next_k, next_winding = (
            semantic[
                (
                    index
                    + 1
                )
                % point_count
            ]
        )

        wrap = (
            1
            if (
                index
                == point_count
                - 1
            )
            else 0
        )

        a = (
            next_q
            - q
            - 6
            * (
                next_winding
                - winding
            )
            + 6
            * wrap
        )

        b = (
            next_k
            - local_k
        )

        value = (
            a
            * (
                pi
                / 3.0
            )
            + b
            * alpha
        )

        frozen_gap = float(
            gaps[
                index
            ][
                "gap_radians"
            ]
        )

        error = abs(
            value
            - frozen_gap
        )

        if (
            error
            > IDENTITY_TOLERANCE_RADIANS
        ):
            raise AssertionError(
                (
                    "Mechanically derived symbolic signature does "
                    "not reproduce frozen gap.",
                    index,
                    (
                        a,
                        b,
                    ),
                    error,
                )
            )

        signatures.append(
            (
                a,
                b,
            )
        )

        evaluated.append(
            value
        )

    return (
        tuple(
            signatures
        ),
        tuple(
            evaluated
        ),
    )


def _class_label(
    signature: tuple[int, int],
    *,
    expected_large: tuple[int, int],
    expected_small: tuple[int, int],
) -> str:
    if (
        signature
        == expected_large
    ):
        return "L"

    if (
        signature
        == expected_small
    ):
        return "S"

    return "?"


def _audit_set(
    payload: dict[str, Any],
    *,
    point_count: int,
    alpha: float,
    gamma_0: float,
    delta: float,
) -> SymbolicSetAudit:
    if point_count == 21:
        key = "twenty_one"
        expected_large = (
            2,
            -2,
        )
        expected_small = (
            -4,
            5,
        )
        expected_counts = {
            expected_large: 15,
            expected_small: 6,
        }
        base_pattern = "LLLSLLS"
        repetitions = 3
        expected_rms_squared = 10
        expected_max = 5
        expected_range = 7
        regular_fraction = Fraction(
            2,
            21,
        )
    elif point_count == 42:
        key = "forty_two"
        expected_large = (
            1,
            -1,
        )
        expected_small = (
            -5,
            6,
        )
        expected_counts = {
            expected_large: 36,
            expected_small: 6,
        }
        base_pattern = "LLLLLLS"
        repetitions = 6
        expected_rms_squared = 6
        expected_max = 6
        expected_range = 7
        regular_fraction = Fraction(
            1,
            21,
        )
    else:
        raise ValueError(
            point_count
        )

    point_set = payload[
        key
    ]

    signatures, evaluated = (
        _derive_signatures(
            point_set,
            point_count=point_count,
            alpha=alpha,
            gamma_0=gamma_0,
        )
    )

    counts = Counter(
        signatures
    )

    if (
        counts
        != Counter(
            expected_counts
        )
    ):
        raise AssertionError(
            (
                "Post-result candidate signature counts failed.",
                point_count,
                counts,
                expected_counts,
            )
        )

    pattern = "".join(
        _class_label(
            signature,
            expected_large=(
                expected_large
            ),
            expected_small=(
                expected_small
            ),
        )
        for signature in signatures
    )

    expected_pattern = (
        base_pattern
        * repetitions
    )

    if (
        pattern
        != expected_pattern
    ):
        raise AssertionError(
            (
                "Post-result candidate cyclic class pattern failed.",
                point_count,
                pattern,
                expected_pattern,
            )
        )

    class_rows: list[
        SymbolicGapClass
    ] = []

    residual_coefficients: list[
        int
    ] = []

    for label, signature in (
        (
            "L",
            expected_large,
        ),
        (
            "S",
            expected_small,
        ),
    ):
        a, b = signature

        rational_pi = (
            Fraction(
                a,
                3,
            )
            + Fraction(
                2
                * b,
                7,
            )
        )

        if (
            rational_pi
            != regular_fraction
        ):
            raise AssertionError(
                (
                    "Exact rational regular-gap identity failed.",
                    point_count,
                    signature,
                    rational_pi,
                    regular_fraction,
                )
            )

        residual_coefficient = (
            -b
        )

        residual_coefficients.extend(
            [
                residual_coefficient
            ]
            * expected_counts[
                signature
            ]
        )

        exact_expression = (
            f"{a}*(pi/3)"
            + (
                f" + {b}*alpha"
                if b >= 0
                else f" - {abs(b)}*alpha"
            )
        )

        delta_form = (
            f"g_{point_count}"
            + (
                f" + {residual_coefficient}*delta"
                if residual_coefficient >= 0
                else f" - {abs(residual_coefficient)}*delta"
            )
        )

        value = (
            a
            * (
                pi
                / 3.0
            )
            + b
            * alpha
        )

        class_rows.append(
            SymbolicGapClass(
                class_label=label,
                a_pi_over_3=a,
                b_alpha=b,
                count=expected_counts[
                    signature
                ],
                exact_expression=(
                    exact_expression
                ),
                delta_residual_coefficient=(
                    residual_coefficient
                ),
                delta_form=delta_form,
                evaluated_gap_radians=value,
            )
        )

    weighted_sum = sum(
        residual_coefficients
    )

    if weighted_sum != 0:
        raise AssertionError(
            (
                "Weighted residual coefficients do not close.",
                point_count,
                weighted_sum,
            )
        )

    rms_squared = Fraction(
        sum(
            coefficient
            * coefficient
            for coefficient
            in residual_coefficients
        ),
        point_count,
    )

    if (
        rms_squared
        != expected_rms_squared
    ):
        raise AssertionError(
            (
                "RMS coefficient identity failed.",
                point_count,
                rms_squared,
                expected_rms_squared,
            )
        )

    maximum_absolute = max(
        abs(
            coefficient
        )
        for coefficient
        in residual_coefficients
    )

    gap_range_coefficient = (
        max(
            residual_coefficients
        )
        - min(
            residual_coefficients
        )
    )

    if (
        maximum_absolute
        != expected_max
        or gap_range_coefficient
        != expected_range
    ):
        raise AssertionError(
            (
                "Max/range coefficient identity failed.",
                point_count,
                maximum_absolute,
                gap_range_coefficient,
            )
        )

    predicted_rms = (
        sqrt(
            float(
                rms_squared
            )
        )
        * delta
    )

    predicted_max = (
        maximum_absolute
        * delta
    )

    predicted_range = (
        gap_range_coefficient
        * delta
    )

    frozen_rms = float(
        point_set[
            "rms_gap_residual_radians"
        ]
    )

    frozen_max = float(
        point_set[
            "maximum_absolute_gap_residual_radians"
        ]
    )

    frozen_range = float(
        point_set[
            "gap_range_radians"
        ]
    )

    rms_error = abs(
        predicted_rms
        - frozen_rms
    )

    max_error = abs(
        predicted_max
        - frozen_max
    )

    range_error = abs(
        predicted_range
        - frozen_range
    )

    for name, error in (
        (
            "RMS",
            rms_error,
        ),
        (
            "maximum",
            max_error,
        ),
        (
            "range",
            range_error,
        ),
    ):
        if (
            error
            > IDENTITY_TOLERANCE_RADIANS
        ):
            raise AssertionError(
                (
                    "Derived metric does not reproduce frozen metric.",
                    point_count,
                    name,
                    error,
                )
            )

    return SymbolicSetAudit(
        point_count=point_count,
        regular_gap_radians=float(
            point_set[
                "regular_gap_radians"
            ]
        ),
        cyclic_class_pattern=pattern,
        class_pattern_base=(
            base_pattern
        ),
        class_pattern_repetitions=(
            repetitions
        ),
        signature_classes=tuple(
            class_rows
        ),
        weighted_delta_residual_coefficient_sum=(
            weighted_sum
        ),
        rms_squared_delta_coefficient=int(
            rms_squared
        ),
        rms_delta_coefficient_symbolic=(
            f"sqrt({int(rms_squared)})"
        ),
        maximum_absolute_delta_coefficient=(
            maximum_absolute
        ),
        gap_range_delta_coefficient=(
            gap_range_coefficient
        ),
        predicted_rms_gap_residual_radians=(
            predicted_rms
        ),
        frozen_rms_gap_residual_radians=(
            frozen_rms
        ),
        rms_identity_absolute_error_radians=(
            rms_error
        ),
        predicted_maximum_absolute_gap_residual_radians=(
            predicted_max
        ),
        frozen_maximum_absolute_gap_residual_radians=(
            frozen_max
        ),
        max_identity_absolute_error_radians=(
            max_error
        ),
        predicted_gap_range_radians=(
            predicted_range
        ),
        frozen_gap_range_radians=(
            frozen_range
        ),
        range_identity_absolute_error_radians=(
            range_error
        ),
    )


def build_method2_symbolic_gap_audit(
    propagation_payload: dict[str, Any],
    local_comparison_payload: dict[str, Any],
) -> Method2SymbolicGapAudit:
    """Verify the disclosed post-result symbolic gap hypotheses."""

    alpha = float(
        propagation_payload[
            "alpha_2_radians"
        ]
    )

    gamma_0 = float(
        propagation_payload[
            "gamma_0_radians"
        ]
    )

    exact_heptagonal_step = (
        2.0
        * pi
        / 7.0
    )

    delta = (
        exact_heptagonal_step
        - alpha
    )

    if (
        delta
        <= 0.0
    ):
        raise AssertionError(
            "Frozen Phase 8E Method 2 does not have the disclosed positive delta."
        )

    twenty_one = _audit_set(
        propagation_payload,
        point_count=21,
        alpha=alpha,
        gamma_0=gamma_0,
        delta=delta,
    )

    forty_two = _audit_set(
        propagation_payload,
        point_count=42,
        alpha=alpha,
        gamma_0=gamma_0,
        delta=delta,
    )

    frozen_comparison = (
        propagation_payload[
            "comparison"
        ]
    )

    raw_rms_ratio_predicted = sqrt(
        3.0
        / 5.0
    )

    raw_rms_ratio_frozen = float(
        frozen_comparison[
            "rms_ratio_42_over_21"
        ]
    )

    max_ratio_predicted = (
        6.0
        / 5.0
    )

    max_ratio_frozen = float(
        frozen_comparison[
            "max_abs_ratio_42_over_21"
        ]
    )

    range_ratio_predicted = 1.0

    range_ratio_frozen = (
        forty_two
        .frozen_gap_range_radians
        / twenty_one
        .frozen_gap_range_radians
    )

    normalized_ratio_predicted = (
        2.0
        * sqrt(
            3.0
            / 5.0
        )
    )

    normalized_ratio_frozen = (
        float(
            propagation_payload[
                "forty_two"
            ][
                "normalized_rms_gap_residual"
            ]
        )
        / float(
            propagation_payload[
                "twenty_one"
            ][
                "normalized_rms_gap_residual"
            ]
        )
    )

    local_closure = abs(
        float(
            local_comparison_payload[
                "method_2"
            ][
                "seven_step_closure_radians"
            ]
        )
    )

    raw_rms_error = abs(
        raw_rms_ratio_predicted
        - raw_rms_ratio_frozen
    )

    max_ratio_error = abs(
        max_ratio_predicted
        - max_ratio_frozen
    )

    range_ratio_error = abs(
        range_ratio_predicted
        - range_ratio_frozen
    )

    normalized_ratio_error = abs(
        normalized_ratio_predicted
        - normalized_ratio_frozen
    )

    twenty_one_closure_error = abs(
        twenty_one
        .frozen_gap_range_radians
        - local_closure
    )

    forty_two_closure_error = abs(
        forty_two
        .frozen_gap_range_radians
        - local_closure
    )

    for name, error in (
        (
            "raw RMS ratio",
            raw_rms_error,
        ),
        (
            "max ratio",
            max_ratio_error,
        ),
        (
            "range ratio",
            range_ratio_error,
        ),
        (
            "normalized RMS ratio",
            normalized_ratio_error,
        ),
        (
            "21 range/closure",
            twenty_one_closure_error,
        ),
        (
            "42 range/closure",
            forty_two_closure_error,
        ),
    ):
        if (
            error
            > IDENTITY_TOLERANCE_RADIANS
        ):
            raise AssertionError(
                (
                    "Post-result cross-relation failed.",
                    name,
                    error,
                )
            )

    cross = CrossRelationAudit(
        raw_rms_ratio_symbolic="sqrt(3/5)",
        raw_rms_ratio_predicted=(
            raw_rms_ratio_predicted
        ),
        raw_rms_ratio_frozen=(
            raw_rms_ratio_frozen
        ),
        raw_rms_ratio_absolute_error=(
            raw_rms_error
        ),
        max_abs_ratio_symbolic="6/5",
        max_abs_ratio_predicted=(
            max_ratio_predicted
        ),
        max_abs_ratio_frozen=(
            max_ratio_frozen
        ),
        max_abs_ratio_absolute_error=(
            max_ratio_error
        ),
        gap_range_ratio_symbolic="1",
        gap_range_ratio_predicted=(
            range_ratio_predicted
        ),
        gap_range_ratio_frozen=(
            range_ratio_frozen
        ),
        gap_range_ratio_absolute_error=(
            range_ratio_error
        ),
        normalized_rms_ratio_symbolic=(
            "2*sqrt(3/5)"
        ),
        normalized_rms_ratio_predicted=(
            normalized_ratio_predicted
        ),
        normalized_rms_ratio_frozen=(
            normalized_ratio_frozen
        ),
        normalized_rms_ratio_absolute_error=(
            normalized_ratio_error
        ),
        seven_step_closure_magnitude_radians=(
            local_closure
        ),
        twenty_one_range_vs_closure_absolute_error_radians=(
            twenty_one_closure_error
        ),
        forty_two_range_vs_closure_absolute_error_radians=(
            forty_two_closure_error
        ),
    )

    return Method2SymbolicGapAudit(
        schema=(
            "njg_michell_v0_8_method2_symbolic_gap_audit"
        ),
        phase="8F",
        evidential_status=(
            "post-result explanatory derivation"
        ),
        specification_sha256=(
            SPECIFICATION_SHA256
        ),
        phase8e_commit=(
            PHASE8E_COMMIT
        ),
        phase8e_propagation_json_sha256=(
            PHASE8E_PROPAGATION_JSON_SHA256
        ),
        phase8c_local_comparison_sha256=(
            PHASE8C_LOCAL_COMPARISON_SHA256
        ),
        identity_tolerance_radians=(
            IDENTITY_TOLERANCE_RADIANS
        ),
        alpha_radians=alpha,
        exact_heptagonal_step_radians=(
            exact_heptagonal_step
        ),
        delta_radians=delta,
        delta_degrees=(
            delta
            * 180.0
            / pi
        ),
        twenty_one=twenty_one,
        forty_two=forty_two,
        cross_relations=cross,
        degrees_of_freedom=(
            SymbolicAuditDegreesOfFreedom()
        ),
        stopping_status=(
            STOPPING_STATUS
        ),
    )


def method2_symbolic_gap_audit_to_json(
    audit: Method2SymbolicGapAudit,
) -> str:
    """Serialize the explanatory audit deterministically."""

    return (
        json.dumps(
            asdict(
                audit
            ),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def method2_symbolic_gap_audit_to_markdown(
    audit: Method2SymbolicGapAudit,
) -> str:
    """Render the post-result explanatory identities."""

    deg = (
        180.0
        / pi
    )

    twenty_one = (
        audit.twenty_one
    )

    forty_two = (
        audit.forty_two
    )

    cross = (
        audit.cross_relations
    )

    lines = [
        "# v0.8 Method 2 symbolic gap-structure audit",
        "",
        "## Status",
        "",
        f"`{audit.stopping_status}`",
        "",
        "**Evidential status:** post-result explanatory derivation.",
        "",
        "The candidate identities in this audit were recognized after the",
        "Phase 8E numerical result. They are not preregistered predictions.",
        "",
        "The audit asks whether those observed numbers are mechanically derived",
        "symbolic identities of the frozen construction.",
        "",
        "## Local deficit",
        "",
        "Let:",
        "",
        "```text",
        "H = 2*pi/7",
        "alpha = alpha_2",
        "delta = H - alpha",
        "```",
        "",
        "Frozen value:",
        "",
        "```text",
        f"delta_radians = {repr(audit.delta_radians)}",
        f"delta_degrees = {repr(audit.delta_degrees)}",
        "```",
        "",
        "## Twenty-one-point exact gap structure",
        "",
        "Mechanically derived symbolic identity classes:",
        "",
        "```text",
        "15 gaps:  2*(pi/3) - 2*alpha = g_21 + 2*delta",
        " 6 gaps: -4*(pi/3) + 5*alpha = g_21 - 5*delta",
        "",
        f"cyclic pattern = {twenty_one.class_pattern_base} x {twenty_one.class_pattern_repetitions}",
        "```",
        "",
        "The exact residual coefficients close:",
        "",
        "```text",
        "15*(+2) + 6*(-5) = 0",
        "```",
        "",
        "Therefore:",
        "",
        "```text",
        "RMS_21   = sqrt(10)*delta",
        "MAX_21   = 5*delta",
        "RANGE_21 = 7*delta",
        "```",
        "",
        "Frozen numerical identity errors:",
        "",
        "```text",
        (
            "RMS identity error radians = "
            f"{repr(twenty_one.rms_identity_absolute_error_radians)}"
        ),
        (
            "MAX identity error radians = "
            f"{repr(twenty_one.max_identity_absolute_error_radians)}"
        ),
        (
            "RANGE identity error radians = "
            f"{repr(twenty_one.range_identity_absolute_error_radians)}"
        ),
        "```",
        "",
        "## Forty-two-point exact gap structure",
        "",
        "Mechanically derived symbolic identity classes:",
        "",
        "```text",
        "36 gaps:  (pi/3) - alpha = g_42 + delta",
        " 6 gaps: -5*(pi/3) + 6*alpha = g_42 - 6*delta",
        "",
        f"cyclic pattern = {forty_two.class_pattern_base} x {forty_two.class_pattern_repetitions}",
        "```",
        "",
        "The exact residual coefficients close:",
        "",
        "```text",
        "36*(+1) + 6*(-6) = 0",
        "```",
        "",
        "Therefore:",
        "",
        "```text",
        "RMS_42   = sqrt(6)*delta",
        "MAX_42   = 6*delta",
        "RANGE_42 = 7*delta",
        "```",
        "",
        "Frozen numerical identity errors:",
        "",
        "```text",
        (
            "RMS identity error radians = "
            f"{repr(forty_two.rms_identity_absolute_error_radians)}"
        ),
        (
            "MAX identity error radians = "
            f"{repr(forty_two.max_identity_absolute_error_radians)}"
        ),
        (
            "RANGE identity error radians = "
            f"{repr(forty_two.range_identity_absolute_error_radians)}"
        ),
        "```",
        "",
        "## Exact cross-relations",
        "",
        "The Phase 8E comparison is therefore explained algebraically by:",
        "",
        "```text",
        "RMS_42 / RMS_21 = sqrt(3/5)",
        "MAX_42 / MAX_21 = 6/5",
        "RANGE_42 / RANGE_21 = 1",
        "",
        "normalized_RMS_42 / normalized_RMS_21",
        "    = 2*sqrt(3/5)",
        "```",
        "",
        "Numerical verification:",
        "",
        "```text",
        (
            "raw RMS ratio frozen/predicted = "
            f"{repr(cross.raw_rms_ratio_frozen)} / "
            f"{repr(cross.raw_rms_ratio_predicted)}"
        ),
        (
            "max ratio frozen/predicted = "
            f"{repr(cross.max_abs_ratio_frozen)} / "
            f"{repr(cross.max_abs_ratio_predicted)}"
        ),
        (
            "range ratio frozen/predicted = "
            f"{repr(cross.gap_range_ratio_frozen)} / "
            f"{repr(cross.gap_range_ratio_predicted)}"
        ),
        (
            "normalized RMS ratio frozen/predicted = "
            f"{repr(cross.normalized_rms_ratio_frozen)} / "
            f"{repr(cross.normalized_rms_ratio_predicted)}"
        ),
        "```",
        "",
        "The common gap range also equals the magnitude of the frozen local",
        "Method 2 seven-step closure error:",
        "",
        "```text",
        "RANGE_21 = RANGE_42 = 7*delta = abs(7*alpha - 2*pi)",
        (
            "closure magnitude degrees = "
            f"{repr(cross.seven_step_closure_magnitude_radians * deg)}"
        ),
        "```",
        "",
        "## What the reciprocal 42-point stage does",
        "",
        "In raw angular units the RMS gap residual decreases from",
        "`sqrt(10)*delta` to `sqrt(6)*delta`.",
        "",
        "At the same time the worst individual gap residual increases from",
        "`5*delta` to `6*delta`.",
        "",
        "Because the regular reference gap halves from the 21-point to the",
        "42-point construction, normalized RMS nonuniformity increases by the",
        "exact factor `2*sqrt(3/5)`.",
        "",
        "Thus the reciprocal stage does not admit a single unqualified label",
        "such as 'more regular' or 'less regular'; the answer depends on the",
        "registered metric.",
        "",
        "## Evidential boundary",
        "",
        "This is a post-result explanatory derivation.",
        "",
        "It verifies mechanically derived symbolic identity relations in the",
        "frozen project construction. It does not show that Michell stated,",
        "predicted, or intentionally optimized these formulas, and it does not",
        "supply independent historical or empirical evidence.",
        "",
        "## Degrees of freedom",
        "",
        "```text",
        "continuous_fitted_parameters = 0",
        "scale_parameters = 0",
        "gap_clustering_thresholds = 0",
        "optimized_symbolic_coefficients = 0",
        "candidate_class_selection_after_specification = 0",
        "```",
        "",
    ]

    return "\n".join(
        lines
    )
