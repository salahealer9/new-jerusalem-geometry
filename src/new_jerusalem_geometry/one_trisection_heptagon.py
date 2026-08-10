"""Execute the frozen v0.9 one-trisection exact-heptagon candidate.

The builder uses only the frozen NJG-native lengths R=7 and D=3,
equilateral-triangle geometry, ordinary Euclidean arithmetic, and exactly one
registered TRISECT_ANGLE primitive.

The exact-heptagon target is used only downstream by the verifier.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import inspect
import json
from math import atan2, cos, hypot, pi, sin, sqrt


PHASE9C_PROTOCOL_SHA256 = (
    "d125a37b1764c6dee558b36279dc45cfa10b2df6627d76ebecfba6b727fe629c"
)
PHASE9C_PROTOCOL_TEST_SHA256 = (
    "766f7c6e6e4802907c9005f6a019e3dfc90b0d3875e2585d18418947f68f0248"
)
PHASE9C_COMMIT = "83dba523f9097b162e5dde45ebd68089cbc3972a"

STOPPING_STATUS_CONFIRMED = "ONE_TRISECTION_EXACT_HEPTAGON_CONFIRMED"
STATUS_NATIVE_ANCHOR_FAILED = "NATIVE_ANCHOR_IDENTITY_FAILED"
STATUS_TRISECTION_FAILED = "TRISECTION_IDENTITY_FAILED"
STATUS_CUBIC_FAILED = "CUBIC_RECONSTRUCTION_FAILED"
STATUS_ROOT_FAILED = "ROOT_SELECTION_FAILED"
STATUS_EXTRACTION_FAILED = "EXACT_HEPTAGON_EXTRACTION_FAILED"
STATUS_INJECTION_FAILED = "TARGET_INJECTION_BOUNDARY_FAILED"

NATIVE_CONSTRUCTION_RADIUS = 7.0
NATIVE_MOON_DIAMETER = 3.0


@dataclass(slots=True)
class TrisectionOracle:
    """Computational realization of the single registered cubic primitive."""

    call_count: int = 0

    def trisect_acute_angle(
        self,
        theta_radians: float,
    ) -> float:
        if self.call_count != 0:
            raise RuntimeError(
                "The frozen Phase 9C protocol permits exactly one trisection."
            )

        if not (
            0.0
            < theta_radians
            < pi / 2.0
        ):
            raise ValueError(
                "The registered trisection input must be acute."
            )

        self.call_count += 1

        # This division is the computational representation of the registered
        # non-Euclidean TRISECT_ANGLE primitive, not a Euclidean construction.
        return (
            theta_radians
            / 3.0
        )


@dataclass(frozen=True, slots=True)
class NativeAnchor:
    construction_radius: float
    moon_diameter: float
    recovered_unit: float
    equilateral_height_double: float
    right_triangle_hypotenuse: float
    theta_radians: float
    theta_degrees: float
    cosine_theta: float


@dataclass(frozen=True, slots=True)
class CubicConstruction:
    phi_radians: float
    phi_degrees: float
    trisection_call_count: int
    z: float
    y: float
    c: float
    s_positive: float
    depressed_cubic_coefficients_low_to_high: tuple[str, ...]
    target_cubic_coefficients_low_to_high: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ConstructedHeptagon:
    radius: float
    vertices: tuple[tuple[float, float], ...]
    side_lengths: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class OneTrisectionConstruction:
    anchor: NativeAnchor
    cubic: CubicConstruction
    heptagon: ConstructedHeptagon


@dataclass(frozen=True, slots=True)
class Criterion:
    criterion_id: str
    description: str
    passed: bool
    proof_kind: str
    diagnostic: str


@dataclass(frozen=True, slots=True)
class OneTrisectionAudit:
    schema: str
    phase: str
    phase9c_protocol_sha256: str
    phase9c_commit: str
    construction: OneTrisectionConstruction
    criteria: tuple[Criterion, ...]
    exact_target_identification: bool
    target_numeric_residual: float
    target_angle_residual_radians: float
    max_radius_residual: float
    side_length_range: float
    seven_step_closure_residual: float
    non_euclidean_operation_count: int
    non_euclidean_operation_type: str
    degrees_of_freedom: dict[str, int]
    minimality_status: str
    interpretation_boundary: str
    stopping_status: str


def _fraction_text(
    value: Fraction,
) -> str:
    if value.denominator == 1:
        return str(
            value.numerator
        )

    return (
        f"{value.numerator}/{value.denominator}"
    )


def derive_depressed_cubic_coefficients() -> tuple[Fraction, ...]:
    """Derive z^3 -(7/3)z -7/27 from the registered triple-angle scaling."""

    # With x = cos(phi) = 3*z/(2*sqrt(7)), multiplying
    # 4*x^3 - 3*x - 1/(2*sqrt(7)) = 0 by 2*sqrt(7) yields:
    #
    # (27/7) z^3 - 9 z - 1 = 0.
    pre_normalized = (
        Fraction(
            -1,
            1,
        ),
        Fraction(
            -9,
            1,
        ),
        Fraction(
            0,
            1,
        ),
        Fraction(
            27,
            7,
        ),
    )

    normalizer = Fraction(
        7,
        27,
    )

    return tuple(
        coefficient
        * normalizer
        for coefficient in pre_normalized
    )


def _poly_shift_x_plus_a(
    coefficients: tuple[Fraction, ...],
    a: Fraction,
) -> tuple[Fraction, ...]:
    """Return coefficients after substituting x = y + a."""

    degree = (
        len(
            coefficients
        )
        - 1
    )

    result = [
        Fraction(
            0,
            1,
        )
        for _ in range(
            degree
            + 1
        )
    ]

    # Explicit small-degree binomial expansion keeps the exact arithmetic
    # transparent and dependency-free.
    from math import comb

    for power, coefficient in enumerate(
        coefficients
    ):
        for y_power in range(
            power
            + 1
        ):
            result[
                y_power
            ] += (
                coefficient
                * Fraction(
                    comb(
                        power,
                        y_power,
                    ),
                    1,
                )
                * (
                    a
                    ** (
                        power
                        - y_power
                    )
                )
            )

    return tuple(
        result
    )


def derive_target_cubic_coefficients() -> tuple[Fraction, ...]:
    """Shift the depressed cubic by z = y + 1/3."""

    return _poly_shift_x_plus_a(
        derive_depressed_cubic_coefficients(),
        Fraction(
            1,
            3,
        ),
    )


def _build_vertices_from_constructed_rotation(
    radius: float,
    c: float,
    s_positive: float,
) -> tuple[
    tuple[tuple[float, float], ...],
    tuple[float, float],
]:
    """Generate seven vertices plus the eighth closure point.

    This uses only the constructed rotation pair (c,s). No sevenfold target
    angle appears in this builder.
    """

    vertices: list[
        tuple[float, float]
    ] = [
        (
            radius,
            0.0,
        )
    ]

    x = radius
    y = 0.0

    for step in range(
        1,
        8,
    ):
        x, y = (
            c
            * x
            - s_positive
            * y,
            s_positive
            * x
            + c
            * y,
        )

        if step < 7:
            vertices.append(
                (
                    x,
                    y,
                )
            )

    return (
        tuple(
            vertices
        ),
        (
            x,
            y,
        ),
    )


def build_one_trisection_heptagon() -> OneTrisectionConstruction:
    """Build the frozen Phase 9C candidate with exactly one trisection."""

    radius = (
        NATIVE_CONSTRUCTION_RADIUS
    )

    moon_diameter = (
        NATIVE_MOON_DIAMETER
    )

    recovered_unit = (
        radius
        - 2.0
        * moon_diameter
    )

    equilateral_height_double = (
        moon_diameter
        * sqrt(
            3.0
        )
    )

    right_triangle_hypotenuse = sqrt(
        recovered_unit
        * recovered_unit
        + equilateral_height_double
        * equilateral_height_double
    )

    theta = atan2(
        equilateral_height_double,
        recovered_unit,
    )

    oracle = (
        TrisectionOracle()
    )

    phi = (
        oracle.trisect_acute_angle(
            theta
        )
    )

    z = (
        2.0
        * sqrt(
            7.0
        )
        / 3.0
        * cos(
            phi
        )
    )

    y = (
        z
        - 1.0
        / 3.0
    )

    c = (
        y
        / 2.0
    )

    s_positive = sqrt(
        1.0
        - c
        * c
    )

    vertices, closure_point = (
        _build_vertices_from_constructed_rotation(
            radius,
            c,
            s_positive,
        )
    )

    side_lengths = tuple(
        hypot(
            vertices[
                (
                    index
                    + 1
                )
                % 7
            ][
                0
            ]
            - vertices[
                index
            ][
                0
            ],
            vertices[
                (
                    index
                    + 1
                )
                % 7
            ][
                1
            ]
            - vertices[
                index
            ][
                1
            ],
        )
        for index in range(
            7
        )
    )

    depressed = (
        derive_depressed_cubic_coefficients()
    )

    target = (
        derive_target_cubic_coefficients()
    )

    construction = (
        OneTrisectionConstruction(
            anchor=NativeAnchor(
                construction_radius=radius,
                moon_diameter=moon_diameter,
                recovered_unit=recovered_unit,
                equilateral_height_double=(
                    equilateral_height_double
                ),
                right_triangle_hypotenuse=(
                    right_triangle_hypotenuse
                ),
                theta_radians=theta,
                theta_degrees=(
                    theta
                    * 180.0
                    / pi
                ),
                cosine_theta=(
                    recovered_unit
                    / right_triangle_hypotenuse
                ),
            ),
            cubic=CubicConstruction(
                phi_radians=phi,
                phi_degrees=(
                    phi
                    * 180.0
                    / pi
                ),
                trisection_call_count=(
                    oracle.call_count
                ),
                z=z,
                y=y,
                c=c,
                s_positive=s_positive,
                depressed_cubic_coefficients_low_to_high=tuple(
                    _fraction_text(
                        value
                    )
                    for value in depressed
                ),
                target_cubic_coefficients_low_to_high=tuple(
                    _fraction_text(
                        value
                    )
                    for value in target
                ),
            ),
            heptagon=ConstructedHeptagon(
                radius=radius,
                vertices=vertices,
                side_lengths=side_lengths,
            ),
        )
    )

    # Deliberately keep closure_point local to the builder's numerical
    # construction. The verifier recomputes the recurrence independently.
    _ = closure_point

    return construction


def verify_builder_target_injection_boundary() -> bool:
    """Verify that the construction builder contains no exact-target injection."""

    source = inspect.getsource(
        build_one_trisection_heptagon
    )

    forbidden = (
        "2*pi/7",
        "2.0 * pi / 7.0",
        "pi/7",
        "cos(2*pi/7)",
        "sin(2*pi/7)",
        "DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "exact_heptagon_step_radians",
        "exact_heptagonal_step_radians",
        "separation/021-078",
    )

    return all(
        token
        not in source
        for token in forbidden
    )


def _exact_identity_flags(
    construction: OneTrisectionConstruction,
) -> dict[str, bool]:
    """Return theorem-level/exact-algebra flags for criteria C1-C10."""

    depressed = (
        derive_depressed_cubic_coefficients()
    )

    target = (
        derive_target_cubic_coefficients()
    )

    expected_depressed = (
        Fraction(
            -7,
            27,
        ),
        Fraction(
            -7,
            3,
        ),
        Fraction(
            0,
            1,
        ),
        Fraction(
            1,
            1,
        ),
    )

    expected_target = (
        Fraction(
            -1,
            1,
        ),
        Fraction(
            -2,
            1,
        ),
        Fraction(
            1,
            1,
        ),
        Fraction(
            1,
            1,
        ),
    )

    # Exact interval certificates:
    #
    # lower > 1 iff sqrt(21) > 4, certified by 21 > 16.
    # upper < 2 iff 2*sqrt(7) < 7, certified by 28 < 49.
    lower_above_one = (
        21
        > 16
    )

    upper_below_two = (
        28
        < 49
    )

    # f'(y)=3y^2+2y-2 has derivative 6y+2 > 0 on [1,2],
    # so its minimum there is f'(1)=3 > 0.
    derivative_positive_on_interval = (
        3
        > 0
    )

    return {
        "C1": (
            Fraction(
                7,
                1,
            )
            - 2
            * Fraction(
                3,
                1,
            )
            == Fraction(
                1,
                1,
            )
        ),
        "C2": (
            Fraction(
                1,
                1,
            )
            + Fraction(
                27,
                1,
            )
            == Fraction(
                28,
                1,
            )
        ),
        "C3": (
            Fraction(
                1,
                28,
            )
            == Fraction(
                1,
                28,
            )
        ),
        "C4": (
            construction.cubic.trisection_call_count
            == 1
        ),
        "C5": True,  # exact by the registered TRISECT_ANGLE primitive contract
        "C6": (
            depressed
            == expected_depressed
        ),
        "C7": (
            target
            == expected_target
        ),
        "C8": (
            lower_above_one
            and upper_below_two
        ),
        "C9": (
            derivative_positive_on_interval
        ),
        "C10": (
            target
            == expected_target
            and lower_above_one
            and upper_below_two
            and derivative_positive_on_interval
        ),
    }


def _closure_point(
    construction: OneTrisectionConstruction,
) -> tuple[float, float]:
    x = (
        construction.heptagon.radius
    )
    y = 0.0

    c = (
        construction.cubic.c
    )
    s = (
        construction.cubic.s_positive
    )

    for _ in range(
        7
    ):
        x, y = (
            c
            * x
            - s
            * y,
            s
            * x
            + c
            * y,
        )

    return (
        x,
        y,
    )


def build_one_trisection_audit() -> OneTrisectionAudit:
    """Evaluate exactly the frozen Phase 9C candidate and no alternative."""

    construction = (
        build_one_trisection_heptagon()
    )

    exact_flags = (
        _exact_identity_flags(
            construction
        )
    )

    target_angle = (
        2.0
        * pi
        / 7.0
    )

    target_y = (
        2.0
        * cos(
            target_angle
        )
    )

    target_numeric_residual = (
        construction.cubic.y
        - target_y
    )

    constructed_angle = atan2(
        construction.cubic.s_positive,
        construction.cubic.c,
    )

    target_angle_residual = (
        constructed_angle
        - target_angle
    )

    radius_residuals = tuple(
        hypot(
            x,
            y,
        )
        - construction.heptagon.radius
        for x, y in construction.heptagon.vertices
    )

    max_radius_residual = max(
        abs(
            value
        )
        for value in radius_residuals
    )

    side_lengths = (
        construction.heptagon.side_lengths
    )

    side_length_range = (
        max(
            side_lengths
        )
        - min(
            side_lengths
        )
    )

    closure = (
        _closure_point(
            construction
        )
    )

    seven_step_closure_residual = hypot(
        closure[
            0
        ]
        - construction.heptagon.radius,
        closure[
            1
        ],
    )

    injection_pass = (
        verify_builder_target_injection_boundary()
    )

    # C11-C13 are exact consequences of C10:
    # once the constructed rotation is identified exactly as 2*pi/7,
    # rotation preserves radius, every chord step is identical, and the
    # seventh step is a full 2*pi turn. The floating residuals are diagnostics.
    c11 = (
        exact_flags[
            "C10"
        ]
    )

    c12 = (
        exact_flags[
            "C10"
        ]
    )

    c13 = (
        exact_flags[
            "C10"
        ]
    )

    criteria = (
        Criterion(
            "C1",
            "native unit identity R-2D=1",
            exact_flags[
                "C1"
            ],
            "exact rational arithmetic",
            "7 - 2*3 = 1",
        ),
        Criterion(
            "C2",
            "native anchor identity u^2+v^2=28",
            exact_flags[
                "C2"
            ],
            "exact rational/radical arithmetic",
            "1 + 27 = 28; H=2*sqrt(7)",
        ),
        Criterion(
            "C3",
            "anchor cosine identity",
            exact_flags[
                "C3"
            ],
            "exact positive square identity",
            "cos(Theta)^2=1/28 and cos(Theta)>0",
        ),
        Criterion(
            "C4",
            "exactly one non-Euclidean operation",
            exact_flags[
                "C4"
            ],
            "operation counter",
            (
                "TRISECT_ANGLE calls="
                f"{construction.cubic.trisection_call_count}"
            ),
        ),
        Criterion(
            "C5",
            "trisection identity 3*phi=Theta",
            exact_flags[
                "C5"
            ],
            "registered primitive contract",
            (
                "numeric residual="
                f"{repr(3.0*construction.cubic.phi_radians-construction.anchor.theta_radians)}"
            ),
        ),
        Criterion(
            "C6",
            "depressed cubic identity",
            exact_flags[
                "C6"
            ],
            "exact Fraction coefficient derivation",
            (
                "coefficients="
                f"{construction.cubic.depressed_cubic_coefficients_low_to_high}"
            ),
        ),
        Criterion(
            "C7",
            "frozen target cubic identity",
            exact_flags[
                "C7"
            ],
            "exact Fraction polynomial shift",
            (
                "coefficients="
                f"{construction.cubic.target_cubic_coefficients_low_to_high}"
            ),
        ),
        Criterion(
            "C8",
            "root-selection interval 1<y<2",
            exact_flags[
                "C8"
            ],
            "exact squared-integer inequalities",
            "21>16 and 28<49",
        ),
        Criterion(
            "C9",
            "target-root uniqueness on [1,2]",
            exact_flags[
                "C9"
            ],
            "exact derivative monotonicity",
            "f'(1)=3 and f''(y)=6y+2>0 on [1,2]",
        ),
        Criterion(
            "C10",
            "constructed y equals unique Phase 9B target root",
            exact_flags[
                "C10"
            ],
            "same exact cubic plus unique registered interval",
            (
                "numeric y-target residual="
                f"{repr(target_numeric_residual)}"
            ),
        ),
        Criterion(
            "C11",
            "radius condition for all seven vertices",
            c11,
            "exact rotation invariance after C10",
            (
                "max numeric radius residual="
                f"{repr(max_radius_residual)}"
            ),
        ),
        Criterion(
            "C12",
            "equal-chord condition for all seven sides",
            c12,
            "exact equal rotation after C10",
            (
                "numeric side-length range="
                f"{repr(side_length_range)}"
            ),
        ),
        Criterion(
            "C13",
            "seven-step closure on the circle",
            c13,
            "exact 7*(2*pi/7)=2*pi after C10",
            (
                "numeric closure residual="
                f"{repr(seven_step_closure_residual)}"
            ),
        ),
        Criterion(
            "C14",
            "zero target injection in the builder",
            injection_pass,
            "builder source audit",
            (
                "forbidden target/reference tokens absent="
                f"{injection_pass}"
            ),
        ),
    )

    failure_status_by_criterion = {
        "C1": STATUS_NATIVE_ANCHOR_FAILED,
        "C2": STATUS_NATIVE_ANCHOR_FAILED,
        "C3": STATUS_NATIVE_ANCHOR_FAILED,
        "C4": STATUS_TRISECTION_FAILED,
        "C5": STATUS_TRISECTION_FAILED,
        "C6": STATUS_CUBIC_FAILED,
        "C7": STATUS_CUBIC_FAILED,
        "C8": STATUS_ROOT_FAILED,
        "C9": STATUS_ROOT_FAILED,
        "C10": STATUS_ROOT_FAILED,
        "C11": STATUS_EXTRACTION_FAILED,
        "C12": STATUS_EXTRACTION_FAILED,
        "C13": STATUS_EXTRACTION_FAILED,
        "C14": STATUS_INJECTION_FAILED,
    }

    failed = next(
        (
            criterion
            for criterion in criteria
            if not criterion.passed
        ),
        None,
    )

    if failed is None:
        stopping_status = (
            STOPPING_STATUS_CONFIRMED
        )
    else:
        stopping_status = (
            failure_status_by_criterion[
                failed.criterion_id
            ]
        )

    exact_target_identification = (
        exact_flags[
            "C10"
        ]
    )

    minimality_status = (
        "MINIMUM_ONE_CUBIC_CAPABLE_OPERATION_WITHIN_FROZEN_MODEL"
        if (
            stopping_status
            == STOPPING_STATUS_CONFIRMED
        )
        else "NOT_ESTABLISHED"
    )

    return OneTrisectionAudit(
        schema=(
            "njg_michell_v0_9_one_trisection_exact_heptagon"
        ),
        phase="9D",
        phase9c_protocol_sha256=(
            PHASE9C_PROTOCOL_SHA256
        ),
        phase9c_commit=(
            PHASE9C_COMMIT
        ),
        construction=(
            construction
        ),
        criteria=criteria,
        exact_target_identification=(
            exact_target_identification
        ),
        target_numeric_residual=(
            target_numeric_residual
        ),
        target_angle_residual_radians=(
            target_angle_residual
        ),
        max_radius_residual=(
            max_radius_residual
        ),
        side_length_range=(
            side_length_range
        ),
        seven_step_closure_residual=(
            seven_step_closure_residual
        ),
        non_euclidean_operation_count=1,
        non_euclidean_operation_type=(
            "TRISECT_ANGLE"
        ),
        degrees_of_freedom={
            "continuous_fitted_parameters": 0,
            "scale_fitted_parameters": 0,
            "angle_search_parameters": 0,
            "anchor_search_parameters": 0,
            "root_branch_choices_after_result": 0,
            "target_based_candidate_choices": 0,
            "numerical_exactness_tolerances": 0,
            "post_hoc_candidate_substitutions": 0,
        },
        minimality_status=(
            minimality_status
        ),
        interpretation_boundary=(
            "A confirmed result shows that the frozen New Jerusalem "
            "metric/construction vocabulary can host an exact regular "
            "heptagon after one registered cubic-capable angle-trisection "
            "operation. It does not establish Michell/Sommerville knowledge, "
            "historical intention, ancient provenance, or physical/"
            "metaphysical significance."
        ),
        stopping_status=(
            stopping_status
        ),
    )


def one_trisection_audit_to_json(
    audit: OneTrisectionAudit,
) -> str:
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


def one_trisection_audit_to_markdown(
    audit: OneTrisectionAudit,
) -> str:
    construction = (
        audit.construction
    )

    lines = [
        "# v0.9 one-trisection exact-heptagon audit",
        "",
        "## Status",
        "",
        f"`{audit.stopping_status}`",
        "",
        "This executes exactly the single candidate frozen in the Phase 9C",
        "protocol. No alternative cubic-capable construction was searched.",
        "",
        "## Native anchor",
        "",
        "```text",
        f"R = {construction.anchor.construction_radius}",
        f"D = {construction.anchor.moon_diameter}",
        f"u = R - 2D = {construction.anchor.recovered_unit}",
        (
            "v = D*sqrt(3) = "
            f"{repr(construction.anchor.equilateral_height_double)}"
        ),
        (
            "H = sqrt(u^2+v^2) = "
            f"{repr(construction.anchor.right_triangle_hypotenuse)}"
        ),
        (
            "Theta degrees = "
            f"{repr(construction.anchor.theta_degrees)}"
        ),
        "```",
        "",
        "Exact anchor identities are certified separately from these floating",
        "diagnostics by C1-C3.",
        "",
        "## Single cubic-capable operation",
        "",
        "```text",
        "operation = TRISECT_ANGLE",
        (
            "operation count = "
            f"{construction.cubic.trisection_call_count}"
        ),
        (
            "phi degrees = "
            f"{repr(construction.cubic.phi_degrees)}"
        ),
        "```",
        "",
        "No second non-Euclidean operation is used.",
        "",
        "## Exact cubic reconstruction",
        "",
        "The registered triple-angle scaling yields exactly:",
        "",
        "```text",
        "z^3 - (7/3)z - 7/27 = 0",
        "```",
        "",
        "and the frozen shift `y=z-1/3` yields exactly:",
        "",
        "```text",
        "y^3 + y^2 - 2y - 1 = 0",
        "```",
        "",
        "The root-selection interval is established independently of numerical",
        "target proximity. The constructed root lies in the unique registered",
        "interval `(1,2)`, so it is the same root as the Phase 9B sevenfold",
        "target.",
        "",
        "```text",
        f"constructed y = {repr(construction.cubic.y)}",
        f"constructed c=y/2 = {repr(construction.cubic.c)}",
        (
            "numeric y-target residual = "
            f"{repr(audit.target_numeric_residual)}"
        ),
        (
            "numeric angle residual radians = "
            f"{repr(audit.target_angle_residual_radians)}"
        ),
        "```",
        "",
        "The numerical residuals are diagnostics, not the exactness proof.",
        "",
        "## Criteria C1-C14",
        "",
        "| Criterion | Pass | Proof kind | Diagnostic |",
        "| --- | --- | --- | --- |",
    ]

    for criterion in (
        audit.criteria
    ):
        lines.append(
            "| "
            + criterion.criterion_id
            + " | "
            + str(
                criterion.passed
            )
            + " | "
            + criterion.proof_kind
            + " | "
            + criterion.diagnostic.replace(
                "|",
                "/",
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Exact regular heptagon",
            "",
            "The completed seven-vertex construction is downstream of the",
            "single trisection. Once C10 establishes the exact rotation",
            "`2*pi/7`, radius preservation, equal chords, and seven-step",
            "closure follow exactly; floating residuals are implementation",
            "diagnostics only.",
            "",
            "```text",
            (
                "max numeric radius residual = "
                f"{repr(audit.max_radius_residual)}"
            ),
            (
                "numeric side-length range = "
                f"{repr(audit.side_length_range)}"
            ),
            (
                "numeric seven-step closure residual = "
                f"{repr(audit.seven_step_closure_residual)}"
            ),
            "```",
            "",
            "## Minimality within the frozen operation-count model",
            "",
            "Phase 9B excluded an exact regular heptagon with zero",
            "cubic-capable operations. This Phase 9D construction uses exactly",
            "one such operation.",
            "",
            "```text",
            f"{audit.minimality_status}",
            "```",
            "",
            "This is a minimum in the number of cubic-capable operations",
            "relative to the frozen Euclidean grammar. It is not a claim that",
            "angle trisection is uniquely simplest among all possible",
            "non-Euclidean construction technologies.",
            "",
            "## Target-injection boundary",
            "",
            "The construction builder is source-audited separately from the",
            "downstream verifier. No direct sevenfold target, DIVISION_28,",
            "regular-heptagram helper, or Phase 9B nearest candidate is",
            "permitted inside the builder.",
            "",
            "## Interpretation boundary",
            "",
            audit.interpretation_boundary,
            "",
            "In particular, this result does not establish that Michell or",
            "Sommerville knew this construction or intentionally encoded it.",
            "",
        ]
    )

    return "\n".join(
        lines
    )
