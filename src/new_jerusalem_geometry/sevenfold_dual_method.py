"""Preregistered v0.8 local comparison of Michell's two Figure 194 methods.

This module implements only the Phase 8B local sevenfold comparison.

It deliberately excludes all downstream 21/28/42-point propagation,
Figure 14 material, plate calibration, fitting, and historical interpretation.
"""

from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
)
import json
from math import (
    acos,
    cos,
    pi,
    sqrt,
)

from .core_geometry import (
    build_core_geometry,
)
from .septenary_geometry import (
    MichellTriangleBase,
    build_michell_sevenfold_division,
)


PROTOCOL_SHA256 = (
    "6e4c4e6a5c87280f3ff67d3e21997c681aec22b5cfbe39be713b5627507d2a99"
)

PHASE8A_COMMIT = "d30a384"

PHASE8A_SOURCE_AUDIT_SHA256 = (
    "48a7892bb7be5ebd1b0cfdc2e66f0de7a4f380b6926d7a1799c6693e7dd441b4"
)

METHOD2_IDENTITY_TOLERANCE_RADIANS = 1.0e-15

STOPPING_STATUS = (
    "DUAL_METHOD_LOCAL_COMPARISON_COMPLETE"
)


@dataclass(frozen=True, slots=True)
class SevenfoldMethodMetrics:
    """Preregistered local angular metrics for one sevenfold method."""

    alpha_radians: float
    signed_residual_radians: float
    absolute_residual_radians: float
    relative_residual: float
    percent_residual: float
    absolute_percent_residual: float
    seven_step_closure_radians: float


@dataclass(frozen=True, slots=True)
class DualMethodRelationships:
    """Registered R1-R4 relationships."""

    bracketing: bool
    opposite_signed_errors: bool
    absolute_accuracy_order: tuple[str, ...] | str
    absolute_error_ratio: float | None


@dataclass(frozen=True, slots=True)
class DualMethodExploratory:
    """Registered R5 exploratory arithmetic-midpoint quantities."""

    arithmetic_midpoint_radians: float
    midpoint_signed_residual_radians: float
    midpoint_absolute_residual_radians: float


@dataclass(frozen=True, slots=True)
class DualMethodDegreesOfFreedom:
    """Preregistered zero-fit degrees of freedom."""

    continuous_fitted_parameters: int = 0
    scale_parameters: int = 0
    target_based_candidate_choices: int = 0
    optimized_combination_weights: int = 0


@dataclass(frozen=True, slots=True)
class DualMethodImplementationChecks:
    """Implementation-identity checks, not evidential thresholds."""

    method_2_identity_radians: float
    method_2_identity_absolute_error_radians: float
    method_2_identity_tolerance_radians: float
    method_2_identity_pass: bool


@dataclass(frozen=True, slots=True)
class DualMethodComparison:
    """Complete preregistered Phase 8C result."""

    schema: str
    phase: str
    protocol_sha256: str
    phase8a_commit: str
    phase8a_source_audit_sha256: str
    method1_source_sha256: str
    alpha_exact_radians: float
    method_1: SevenfoldMethodMetrics
    method_2: SevenfoldMethodMetrics
    relationships: DualMethodRelationships
    exploratory: DualMethodExploratory
    degrees_of_freedom: DualMethodDegreesOfFreedom
    implementation_checks: DualMethodImplementationChecks
    stopping_status: str


def method_2_step_from_source_geometry() -> float:
    """Derive Method 2 from the Figure 194 midpoint-arc chord geometry.

    With circumradius R, an inscribed equilateral triangle has side sqrt(3) R.
    The arc from one triangle vertex through the midpoints of its incident
    sides therefore has chord length sqrt(3) R / 2 to either circle
    intersection.

    Using c^2 = 2 R^2 (1 - cos(alpha)) gives cos(alpha) = 5/8.
    """

    chord_over_radius = (
        sqrt(
            3.0
        )
        / 2.0
    )

    cosine = (
        1.0
        - (
            chord_over_radius
            * chord_over_radius
        )
        / 2.0
    )

    return acos(
        cosine
    )


def _metrics(
    alpha_radians: float,
    alpha_exact_radians: float,
) -> SevenfoldMethodMetrics:
    signed = (
        alpha_radians
        - alpha_exact_radians
    )

    absolute = abs(
        signed
    )

    relative = (
        signed
        / alpha_exact_radians
    )

    percent = (
        100.0
        * relative
    )

    closure = (
        7.0
        * alpha_radians
        - 2.0
        * pi
    )

    return SevenfoldMethodMetrics(
        alpha_radians=alpha_radians,
        signed_residual_radians=signed,
        absolute_residual_radians=absolute,
        relative_residual=relative,
        percent_residual=percent,
        absolute_percent_residual=abs(
            percent
        ),
        seven_step_closure_radians=closure,
    )


def _sign(
    value: float,
) -> int:
    if value > 0.0:
        return 1

    if value < 0.0:
        return -1

    return 0


def _accuracy_order(
    method_1: SevenfoldMethodMetrics,
    method_2: SevenfoldMethodMetrics,
) -> tuple[str, ...] | str:
    first = (
        method_1
        .absolute_residual_radians
    )

    second = (
        method_2
        .absolute_residual_radians
    )

    if first < second:
        return (
            "method_1",
            "method_2",
        )

    if second < first:
        return (
            "method_2",
            "method_1",
        )

    return "TIE"


def build_dual_method_comparison(
    *,
    method1_source_sha256: str,
) -> DualMethodComparison:
    """Execute the frozen Phase 8B local comparison with zero fitted inputs."""

    alpha_exact = (
        2.0
        * pi
        / 7.0
    )

    diagram = build_core_geometry(
        unit=1.0
    )

    method_1_division = (
        build_michell_sevenfold_division(
            diagram,
            MichellTriangleBase.SOUTH,
        )
    )

    alpha_1 = (
        method_1_division
        .step_radians
    )

    alpha_2 = (
        method_2_step_from_source_geometry()
    )

    method_2_identity = acos(
        5.0
        / 8.0
    )

    identity_error = abs(
        alpha_2
        - method_2_identity
    )

    identity_pass = (
        identity_error
        <= METHOD2_IDENTITY_TOLERANCE_RADIANS
    )

    if not identity_pass:
        raise AssertionError(
            "Method 2 source-geometry derivation failed "
            "the preregistered acos(5/8) implementation identity."
        )

    method_1 = _metrics(
        alpha_1,
        alpha_exact,
    )

    method_2 = _metrics(
        alpha_2,
        alpha_exact,
    )

    residual_1 = (
        method_1
        .signed_residual_radians
    )

    residual_2 = (
        method_2
        .signed_residual_radians
    )

    bracketing = (
        alpha_2
        < alpha_exact
        < alpha_1
    )

    opposite_signed_errors = (
        _sign(
            residual_1
        )
        != _sign(
            residual_2
        )
        and _sign(
            residual_1
        )
        != 0
        and _sign(
            residual_2
        )
        != 0
    )

    if (
        method_1
        .absolute_residual_radians
        == 0.0
    ):
        absolute_error_ratio = None
    else:
        absolute_error_ratio = (
            method_2
            .absolute_residual_radians
            / method_1
            .absolute_residual_radians
        )

    midpoint = (
        alpha_1
        + alpha_2
    ) / 2.0

    midpoint_signed = (
        midpoint
        - alpha_exact
    )

    relationships = (
        DualMethodRelationships(
            bracketing=bracketing,
            opposite_signed_errors=(
                opposite_signed_errors
            ),
            absolute_accuracy_order=(
                _accuracy_order(
                    method_1,
                    method_2,
                )
            ),
            absolute_error_ratio=(
                absolute_error_ratio
            ),
        )
    )

    exploratory = (
        DualMethodExploratory(
            arithmetic_midpoint_radians=(
                midpoint
            ),
            midpoint_signed_residual_radians=(
                midpoint_signed
            ),
            midpoint_absolute_residual_radians=(
                abs(
                    midpoint_signed
                )
            ),
        )
    )

    result = DualMethodComparison(
        schema=(
            "njg_michell_v0_8_dual_method_comparison"
        ),
        phase="8C",
        protocol_sha256=PROTOCOL_SHA256,
        phase8a_commit=PHASE8A_COMMIT,
        phase8a_source_audit_sha256=(
            PHASE8A_SOURCE_AUDIT_SHA256
        ),
        method1_source_sha256=(
            method1_source_sha256
        ),
        alpha_exact_radians=(
            alpha_exact
        ),
        method_1=method_1,
        method_2=method_2,
        relationships=relationships,
        exploratory=exploratory,
        degrees_of_freedom=(
            DualMethodDegreesOfFreedom()
        ),
        implementation_checks=(
            DualMethodImplementationChecks(
                method_2_identity_radians=(
                    method_2_identity
                ),
                method_2_identity_absolute_error_radians=(
                    identity_error
                ),
                method_2_identity_tolerance_radians=(
                    METHOD2_IDENTITY_TOLERANCE_RADIANS
                ),
                method_2_identity_pass=(
                    identity_pass
                ),
            )
        ),
        stopping_status=STOPPING_STATUS,
    )

    return result


def dual_method_comparison_to_json(
    result: DualMethodComparison,
) -> str:
    """Serialize the canonical Phase 8C result deterministically."""

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


def dual_method_comparison_to_markdown(
    result: DualMethodComparison,
) -> str:
    """Render the preregistered result without adding new analyses."""

    degrees_per_radian = (
        180.0
        / pi
    )

    method_1 = result.method_1
    method_2 = result.method_2
    relationships = (
        result.relationships
    )
    exploratory = (
        result.exploratory
    )

    order = (
        relationships
        .absolute_accuracy_order
    )

    if isinstance(
        order,
        tuple,
    ):
        order_text = (
            " < ".join(
                order
            )
        )
    else:
        order_text = order

    ratio = (
        relationships
        .absolute_error_ratio
    )

    ratio_text = (
        "undefined"
        if ratio is None
        else repr(
            ratio
        )
    )

    lines = [
        "# v0.8 dual-method local comparison result",
        "",
        "## Status",
        "",
        f"`{result.stopping_status}`",
        "",
        "This is the execution of the preregistered Phase 8B local",
        "Figure 194 comparison. No 21-point or 42-point propagation,",
        "Figure 14 comparison, fitting, or plate calibration is included.",
        "",
        "## Frozen provenance",
        "",
        "```text",
        f"protocol_sha256 = {result.protocol_sha256}",
        f"phase8a_commit = {result.phase8a_commit}",
        (
            "phase8a_source_audit_sha256 = "
            f"{result.phase8a_source_audit_sha256}"
        ),
        (
            "method1_source_sha256 = "
            f"{result.method1_source_sha256}"
        ),
        "```",
        "",
        "## Exact regular reference",
        "",
        "```text",
        f"alpha_exact_radians = {repr(result.alpha_exact_radians)}",
        (
            "alpha_exact_degrees = "
            f"{repr(result.alpha_exact_radians * degrees_per_radian)}"
        ),
        "```",
        "",
        "## Method 1",
        "",
        "```text",
        f"alpha_radians = {repr(method_1.alpha_radians)}",
        (
            "alpha_degrees = "
            f"{repr(method_1.alpha_radians * degrees_per_radian)}"
        ),
        (
            "signed_residual_radians = "
            f"{repr(method_1.signed_residual_radians)}"
        ),
        (
            "signed_residual_degrees = "
            f"{repr(method_1.signed_residual_radians * degrees_per_radian)}"
        ),
        (
            "absolute_residual_radians = "
            f"{repr(method_1.absolute_residual_radians)}"
        ),
        (
            "relative_residual = "
            f"{repr(method_1.relative_residual)}"
        ),
        (
            "percent_residual = "
            f"{repr(method_1.percent_residual)}"
        ),
        (
            "absolute_percent_residual = "
            f"{repr(method_1.absolute_percent_residual)}"
        ),
        (
            "seven_step_closure_radians = "
            f"{repr(method_1.seven_step_closure_radians)}"
        ),
        (
            "seven_step_closure_degrees = "
            f"{repr(method_1.seven_step_closure_radians * degrees_per_radian)}"
        ),
        "```",
        "",
        "## Method 2",
        "",
        "```text",
        f"alpha_radians = {repr(method_2.alpha_radians)}",
        (
            "alpha_degrees = "
            f"{repr(method_2.alpha_radians * degrees_per_radian)}"
        ),
        (
            "signed_residual_radians = "
            f"{repr(method_2.signed_residual_radians)}"
        ),
        (
            "signed_residual_degrees = "
            f"{repr(method_2.signed_residual_radians * degrees_per_radian)}"
        ),
        (
            "absolute_residual_radians = "
            f"{repr(method_2.absolute_residual_radians)}"
        ),
        (
            "relative_residual = "
            f"{repr(method_2.relative_residual)}"
        ),
        (
            "percent_residual = "
            f"{repr(method_2.percent_residual)}"
        ),
        (
            "absolute_percent_residual = "
            f"{repr(method_2.absolute_percent_residual)}"
        ),
        (
            "seven_step_closure_radians = "
            f"{repr(method_2.seven_step_closure_radians)}"
        ),
        (
            "seven_step_closure_degrees = "
            f"{repr(method_2.seven_step_closure_radians * degrees_per_radian)}"
        ),
        "```",
        "",
        "## Registered relationships",
        "",
        "```text",
        (
            "R1 bracketing = "
            f"{relationships.bracketing}"
        ),
        (
            "R2 opposite_signed_errors = "
            f"{relationships.opposite_signed_errors}"
        ),
        (
            "R3 absolute_accuracy_order = "
            f"{order_text}"
        ),
        (
            "R4 absolute_error_ratio_method2_over_method1 = "
            f"{ratio_text}"
        ),
        "```",
        "",
        "## Registered exploratory midpoint",
        "",
        "```text",
        (
            "arithmetic_midpoint_radians = "
            f"{repr(exploratory.arithmetic_midpoint_radians)}"
        ),
        (
            "arithmetic_midpoint_degrees = "
            f"{repr(exploratory.arithmetic_midpoint_radians * degrees_per_radian)}"
        ),
        (
            "midpoint_signed_residual_radians = "
            f"{repr(exploratory.midpoint_signed_residual_radians)}"
        ),
        (
            "midpoint_signed_residual_degrees = "
            f"{repr(exploratory.midpoint_signed_residual_radians * degrees_per_radian)}"
        ),
        (
            "midpoint_absolute_residual_radians = "
            f"{repr(exploratory.midpoint_absolute_residual_radians)}"
        ),
        "```",
        "",
        "The midpoint is an explicitly exploratory arithmetic quantity.",
        "It is not a Michell construction.",
        "It is not a tuned correction.",
        "It is not evidence that the two historical constructions were intended to compensate.",
        "",
        "## Implementation identity",
        "",
        "```text",
        (
            "Method 2 analytic identity = acos(5/8)"
        ),
        (
            "identity_absolute_error_radians = "
            f"{repr(result.implementation_checks.method_2_identity_absolute_error_radians)}"
        ),
        (
            "identity_tolerance_radians = "
            f"{repr(result.implementation_checks.method_2_identity_tolerance_radians)}"
        ),
        (
            "identity_pass = "
            f"{result.implementation_checks.method_2_identity_pass}"
        ),
        "```",
        "",
        "The identity tolerance is an implementation check only, not an",
        "evidential success threshold.",
        "",
        "## Degrees of freedom",
        "",
        "```text",
        "continuous_fitted_parameters = 0",
        "scale_parameters = 0",
        "target_based_candidate_choices = 0",
        "optimized_combination_weights = 0",
        "```",
        "",
        "## Interpretation boundary",
        "",
        "This local comparison reports only the geometry specified by the",
        "Phase 8B protocol. It does not establish historical intention,",
        "physical significance, archaeological validation, or statistical",
        "significance. Downstream 7 -> 21 -> 42 propagation remains deferred.",
        "",
    ]

    return "\n".join(
        lines
    )
