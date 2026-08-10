"""v0.9 exact-sevenfold Euclidean-boundary and native-incidence audit.

This module executes Questions A and B of the frozen Phase 9A protocol.
It does not search for neusis, marked-ruler, origami, conic, or any other
non-Euclidean construction.

Exact exclusion of the regular-heptagon target is theorem-based. Floating
point angles are used only for the preregistered descriptive nearest-native
diagnostic.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
import json
from math import acos, atan2, cos, pi, sin, sqrt, tau


PROTOCOL_SHA256 = (
    "ac50f47c4a57000a831958b4e47381533768ed8cebe1d40d309e5c66e3aa2d22"
)
PHASE9A_COMMIT = "d986a18a3985bf55b620a41678380231e71c7c38"
REGISTRY_SPEC_SHA256 = "e26b1725d44ce2454324b97d4b63d11ee8e371cfabef64c1f2da3bb7835cfc35"

STOPPING_STATUS = "EXACT_SEVENFOLD_BOUNDARY_AUDIT_COMPLETE"

EUCLIDEAN_EXCLUDED = "EUCLIDEAN_EXACT_SEVENFOLD_EXCLUDED"
EUCLIDEAN_LINEAGE_FAILED = "EUCLIDEAN_SEED_LINEAGE_NOT_ESTABLISHED"
TARGET_DEGREE_FAILED = "TARGET_DEGREE_CHECK_FAILED"

NO_NATIVE_EXACT = "NO_NATIVE_EXACT_SEVENFOLD"
NATIVE_REQUIRES_AUDIT = "NATIVE_EXACT_SEVENFOLD_REQUIRES_PROVENANCE_AUDIT"


@dataclass(frozen=True, slots=True)
class PolynomialAudit:
    target_variable: str
    target_definition: str
    cyclotomic_identity: str
    polynomial_coefficients_low_to_high: tuple[int, ...]
    polynomial_text: str
    cosine_polynomial_coefficients_low_to_high: tuple[int, ...]
    cosine_polynomial_text: str
    rational_root_candidates: tuple[int, ...]
    rational_root_values: tuple[int, ...]
    irreducible_over_q: bool
    algebraic_degree: int
    degree_is_power_of_two: bool
    numeric_target_radians: float
    numeric_target_degrees: float
    numeric_polynomial_residual: float


@dataclass(frozen=True, slots=True)
class LineageRecord:
    node_id: str
    tier: str
    role: str
    exact_lineage: str
    euclidean_operation_class: str
    verified_constructible: bool
    census_enabled: bool


@dataclass(frozen=True, slots=True)
class TargetInjectionExclusion:
    exclusion_id: str
    object_name: str
    reason: str


@dataclass(frozen=True, slots=True)
class NativePointDirection:
    point_id: str
    source_node: str
    construction_lineage: str
    exact_definition: str
    angle_radians: float


@dataclass(frozen=True, slots=True)
class NativeCandidate:
    candidate_id: str
    source_node: str
    construction_lineage: str
    feature_type: str
    exact_definition: str
    symmetry_class: str
    angle_radians: float
    constructible_lineage: bool
    target_injected: bool


@dataclass(frozen=True, slots=True)
class CensusSummary:
    census_tiers: tuple[str, ...]
    radial_direction_count: int
    pairwise_separation_count: int
    native_line_count: int
    candidate_count_semantic: int
    symmetry_reduction_mode: str
    candidate_count_symmetry_reduced: int
    target_injected_candidate_count_excluded: int
    exact_classification_method: str
    exact_candidate_count: int
    closest_descriptive_candidate_id: str
    closest_descriptive_feature_type: str
    closest_descriptive_angle_radians: float
    closest_descriptive_angle_degrees: float
    closest_descriptive_residual_radians: float
    closest_descriptive_residual_degrees: float
    native_incidence_status: str


@dataclass(frozen=True, slots=True)
class AuditDegreesOfFreedom:
    continuous_fitted_parameters: int = 0
    scale_fitted_parameters: int = 0
    phase_optimized_parameters: int = 0
    target_based_candidate_choices: int = 0
    numerical_acceptance_tolerances: int = 0
    post_hoc_seed_additions: int = 0
    non_euclidean_operations: int = 0


@dataclass(frozen=True, slots=True)
class ExactSevenfoldBoundaryAudit:
    schema: str
    phase: str
    protocol_sha256: str
    phase9a_commit: str
    registry_spec_sha256: str
    polynomial_audit: PolynomialAudit
    euclidean_quadratic_tower_criterion: str
    n0_seed_lineage_checks: tuple[LineageRecord, ...]
    n1_seed_lineage_checks: tuple[LineageRecord, ...]
    euclidean_closure_status: str
    target_injection_exclusions: tuple[TargetInjectionExclusion, ...]
    native_candidates: tuple[NativeCandidate, ...]
    census: CensusSummary
    degrees_of_freedom: AuditDegreesOfFreedom
    question_c_status: str
    stopping_status: str


def _poly_trim(poly: tuple[int, ...]) -> tuple[int, ...]:
    values = list(poly)
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def _poly_add(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...]:
    size = max(len(left), len(right))
    result = [0] * size

    for index in range(size):
        result[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )

    return _poly_trim(
        tuple(result)
    )


def _poly_sub(
    left: tuple[int, ...],
    right: tuple[int, ...],
) -> tuple[int, ...]:
    size = max(len(left), len(right))
    result = [0] * size

    for index in range(size):
        result[index] = (
            (left[index] if index < len(left) else 0)
            - (right[index] if index < len(right) else 0)
        )

    return _poly_trim(
        tuple(result)
    )


def _poly_mul_y(poly: tuple[int, ...]) -> tuple[int, ...]:
    return (0,) + poly


def _poly_eval_int(
    poly: tuple[int, ...],
    value: int,
) -> int:
    total = 0
    power = 1

    for coefficient in poly:
        total += coefficient * power
        power *= value

    return total


def _poly_eval_float(
    poly: tuple[int, ...],
    value: float,
) -> float:
    total = 0.0
    power = 1.0

    for coefficient in poly:
        total += float(coefficient) * power
        power *= value

    return total


def build_target_polynomial_audit() -> PolynomialAudit:
    """Verify the exact cubic arising from the seventh cyclotomic identity."""

    # S_n = z^n + z^(-n), with y = z + z^(-1).
    # S_0 = 2; S_1 = y; S_n = y*S_(n-1) - S_(n-2).
    s0 = (2,)
    s1 = (0, 1)
    s2 = _poly_sub(
        _poly_mul_y(s1),
        s0,
    )
    s3 = _poly_sub(
        _poly_mul_y(s2),
        s1,
    )

    # For primitive seventh root z:
    # z^-3 * (1 + z + ... + z^6) = S3 + S2 + S1 + 1 = 0.
    derived = _poly_add(
        _poly_add(
            _poly_add(
                s3,
                s2,
            ),
            s1,
        ),
        (1,),
    )

    expected = (
        -1,
        -2,
        1,
        1,
    )

    if derived != expected:
        raise AssertionError(
            (
                "Seventh-cyclotomic recurrence did not produce "
                "y^3 + y^2 - 2y - 1.",
                derived,
            )
        )

    roots = (
        -1,
        1,
    )

    root_values = tuple(
        _poly_eval_int(
            derived,
            root,
        )
        for root in roots
    )

    irreducible = all(
        value != 0
        for value in root_values
    )

    degree = (
        3
        if irreducible
        else 0
    )

    cosine_poly = tuple(
        coefficient
        * (
            2 ** index
        )
        for index, coefficient in enumerate(
            derived
        )
    )

    expected_cosine = (
        -1,
        -4,
        4,
        8,
    )

    if cosine_poly != expected_cosine:
        raise AssertionError(
            (
                "Substitution y = 2c did not produce the registered "
                "cosine cubic.",
                cosine_poly,
            )
        )

    target = (
        2.0
        * pi
        / 7.0
    )

    y_numeric = (
        2.0
        * cos(
            target
        )
    )

    return PolynomialAudit(
        target_variable="y_7",
        target_definition="y_7 = 2*cos(2*pi/7)",
        cyclotomic_identity=(
            "S3(y) + S2(y) + S1(y) + 1 = 0 "
            "from z^-3*(1+z+...+z^6)=0"
        ),
        polynomial_coefficients_low_to_high=(
            derived
        ),
        polynomial_text=(
            "y^3 + y^2 - 2*y - 1"
        ),
        cosine_polynomial_coefficients_low_to_high=(
            cosine_poly
        ),
        cosine_polynomial_text=(
            "8*c^3 + 4*c^2 - 4*c - 1"
        ),
        rational_root_candidates=roots,
        rational_root_values=root_values,
        irreducible_over_q=irreducible,
        algebraic_degree=degree,
        degree_is_power_of_two=(
            degree > 0
            and (
                degree
                & (
                    degree
                    - 1
                )
            )
            == 0
        ),
        numeric_target_radians=target,
        numeric_target_degrees=(
            target
            * 180.0
            / pi
        ),
        numeric_polynomial_residual=(
            _poly_eval_float(
                derived,
                y_numeric,
            )
        ),
    )


def build_lineage_audit() -> tuple[
    tuple[LineageRecord, ...],
    tuple[LineageRecord, ...],
]:
    """Record Euclidean lineage for the frozen native construction tiers."""

    n0 = (
        LineageRecord(
            "CORE_DIMENSIONS",
            "N0",
            "rational normalized seed lengths",
            "11, 3, 7 and rational halves are rational seed data.",
            "rational seed field",
            True,
            True,
        ),
        LineageRecord(
            "EARTH_CIRCLE",
            "N0",
            "Earth circle",
            "Rational centre and rational radius 11/2.",
            "circle from constructible centre and radius",
            True,
            True,
        ),
        LineageRecord(
            "EARTH_SQUARE",
            "N0",
            "Earth square",
            "Axis-aligned square with rational half-side 11/2.",
            "lines through constructible points",
            True,
            True,
        ),
        LineageRecord(
            "CONSTRUCTION_CIRCLE",
            "N0",
            "construction circle",
            "Rational centre and rational radius 7.",
            "circle from constructible centre and radius",
            True,
            True,
        ),
        LineageRecord(
            "CARDINAL_MOONS",
            "N0",
            "four cardinal Moon circles",
            "Centres (±7,0),(0,±7) and radius 3/2 are rational.",
            "circles from constructible centres and radius",
            True,
            True,
        ),
        LineageRecord(
            "SQUARE_CIRCLE_INTERSECTIONS",
            "N0",
            "eight square/construction-circle intersections",
            (
                "For x=±11/2 or y=±11/2 on x^2+y^2=49, "
                "the remaining coordinate satisfies u^2=75/4, "
                "hence u=±5*sqrt(3)/2."
            ),
            "line/circle intersection; one quadratic extraction",
            True,
            True,
        ),
        LineageRecord(
            "NJG_INC_MOONS",
            "N0",
            "twelve exact-incidence Moon circles",
            (
                "Oblique centres are intersections of the construction "
                "circle with radius-3/2 circles about constructible "
                "square-circle junctions."
            ),
            "circle/circle intersection; quadratic extraction",
            True,
            True,
        ),
        LineageRecord(
            "MOON_GROUPS_4X3",
            "N0",
            "semantic four-by-three grouping",
            "Grouping adds no coordinate or new geometric operation.",
            "semantic only",
            True,
            False,
        ),
        LineageRecord(
            "SEPTENARY_METHOD_1",
            "N0",
            "Michell Figure 194 Method 1",
            (
                "Square, equilateral triangle and line/circle intersection; "
                "cos(alpha_1)=(1-sqrt(3)+sqrt(6*sqrt(3)))/4."
            ),
            "finite tower of quadratic extensions",
            True,
            True,
        ),
        LineageRecord(
            "RECIPROCAL_TRIANGLE_14",
            "N0",
            "Method 1 reciprocal triangle",
            (
                "Opposite-side repetition and reflection/rotation of the "
                "constructible Method 1 triangle."
            ),
            "constructible reflection/rotation",
            True,
            True,
        ),
        LineageRecord(
            "SCAFFOLD_28",
            "N0",
            "Method 1 twenty-eight-point scaffold",
            (
                "Four square-side repetitions of the constructible Method 1 "
                "step; coordinates follow constructible rotations."
            ),
            "finite constructible rotations and line/circle incidences",
            True,
            True,
        ),
        LineageRecord(
            "SEPTENARY_METHOD_2",
            "N0",
            "Michell Figure 194 Method 2",
            (
                "Equilateral triangle, side midpoint and vertex-centred arc; "
                "cos(alpha_2)=5/8 and sin(alpha_2)=sqrt(39)/8."
            ),
            "midpoint plus circle/circle intersection; quadratic extraction",
            True,
            True,
        ),
        LineageRecord(
            "METHOD2_21",
            "N0",
            "Method 2 twenty-one-point propagation",
            (
                "Three constructible equilateral carrier phases with the "
                "constructible Method 2 local step."
            ),
            "constructible rotations by 2*pi/3",
            True,
            True,
        ),
        LineageRecord(
            "METHOD2_42",
            "N0",
            "Method 2 forty-two-point propagation",
            (
                "Adds the reciprocal equilateral triangle, a constructible "
                "pi/3 rotation of the original carrier system."
            ),
            "constructible rotation by pi/3",
            True,
            True,
        ),
    )

    n1 = (
        LineageRecord(
            "REGULAR_DODECAGON_BASELINE",
            "N1",
            "regular dodecagon auxiliary baseline",
            (
                "Apothem 17/2 with 30-degree normal increments generated "
                "from equilateral and right-angle constructions."
            ),
            "rational length plus constructible 30-degree rotations",
            True,
            False,
        ),
        LineageRecord(
            "POLAR_PIVOT_WALL",
            "N1",
            "preferred polar-pivot tangent wall",
            (
                "Each nonpolar side is the selected tangent from a "
                "constructible pivot point to a constructible Moon circle; "
                "tangent points and adjacent-line intersections are ordinary "
                "Euclidean constructions."
            ),
            "point-to-circle tangent plus line/line intersection",
            True,
            False,
        ),
    )

    return (
        n0,
        n1,
    )


def build_target_injection_exclusions() -> tuple[
    TargetInjectionExclusion,
    ...,
]:
    """Return frozen reference classes that must never enter the census."""

    return (
        TargetInjectionExclusion(
            "X01",
            "ObliqueModel.DIVISION_28",
            "Its definition already injects the exact pi/7 comparator.",
        ),
        TargetInjectionExclusion(
            "X02",
            "NJG_28",
            "When generated from DIVISION_28 it inherits the exact target.",
        ),
        TargetInjectionExclusion(
            "X03",
            "build_regular_heptagram",
            "Exact regular-heptagram helper is reference geometry.",
        ),
        TargetInjectionExclusion(
            "X04",
            "free regular seven-vertex fits",
            "Fitted regular-seven geometry assumes the target family.",
        ),
        TargetInjectionExclusion(
            "X05",
            "exact_heptagon_step_radians",
            "Direct exact-target reference quantity.",
        ),
        TargetInjectionExclusion(
            "X06",
            "exact_heptagonal_step_radians",
            "Direct exact-target reference quantity.",
        ),
        TargetInjectionExclusion(
            "X07",
            "direct 2*pi/7 reference objects",
            "Any object defined from the exact target is circular evidence.",
        ),
    )


def _normalise_angle(
    angle: float,
) -> float:
    return angle % tau


def _circular_separation(
    first: float,
    second: float,
) -> float:
    delta = abs(
        _normalise_angle(
            first
        )
        - _normalise_angle(
            second
        )
    )

    return min(
        delta,
        tau
        - delta,
    )


def _canonical_line_angle(
    angle: float,
) -> float:
    value = angle % pi

    return min(
        value,
        pi
        - value,
    )


def _method1_alpha_native() -> float:
    cosine = (
        1.0
        - sqrt(
            3.0
        )
        + sqrt(
            6.0
            * sqrt(
                3.0
            )
        )
    ) / 4.0

    return acos(
        cosine
    )


def _method2_alpha_native() -> float:
    return acos(
        5.0
        / 8.0
    )


def _native_radial_points() -> tuple[NativePointDirection, ...]:
    """Build frozen N0 radial points without using a sevenfold target."""

    points: list[
        NativePointDirection
    ] = []

    cardinal_names = (
        "east",
        "north",
        "west",
        "south",
    )

    for index, name in enumerate(
        cardinal_names
    ):
        angle = (
            index
            * pi
            / 2.0
        )

        points.append(
            NativePointDirection(
                point_id=(
                    f"cardinal-moon/{name}"
                ),
                source_node="CARDINAL_MOONS",
                construction_lineage=(
                    "rational cardinal centre on construction circle"
                ),
                exact_definition=(
                    f"gamma={index}*pi/2"
                ),
                angle_radians=angle,
            )
        )

    square_vertices = (
        (
            "north-east",
            pi / 4.0,
        ),
        (
            "north-west",
            3.0 * pi / 4.0,
        ),
        (
            "south-west",
            5.0 * pi / 4.0,
        ),
        (
            "south-east",
            7.0 * pi / 4.0,
        ),
    )

    for name, angle in square_vertices:
        points.append(
            NativePointDirection(
                point_id=(
                    f"earth-square-vertex/{name}"
                ),
                source_node="EARTH_SQUARE",
                construction_lineage=(
                    "intersection of two rational square side-lines"
                ),
                exact_definition=(
                    "radial direction to (±11/2,±11/2)"
                ),
                angle_radians=angle,
            )
        )

    h = (
        11.0
        / 2.0
    )

    other = (
        5.0
        * sqrt(
            3.0
        )
        / 2.0
    )

    square_circle_points = (
        (
            "east-upper",
            h,
            other,
        ),
        (
            "north-right",
            other,
            h,
        ),
        (
            "north-left",
            -other,
            h,
        ),
        (
            "west-upper",
            -h,
            other,
        ),
        (
            "west-lower",
            -h,
            -other,
        ),
        (
            "south-left",
            -other,
            -h,
        ),
        (
            "south-right",
            other,
            -h,
        ),
        (
            "east-lower",
            h,
            -other,
        ),
    )

    for name, x, y in square_circle_points:
        points.append(
            NativePointDirection(
                point_id=(
                    f"square-circle/{name}"
                ),
                source_node=(
                    "SQUARE_CIRCLE_INTERSECTIONS"
                ),
                construction_lineage=(
                    "exact line/circle intersection"
                ),
                exact_definition=(
                    "coordinates are a sign/permutation of "
                    "(11/2,5*sqrt(3)/2)"
                ),
                angle_radians=_normalise_angle(
                    atan2(
                        y,
                        x,
                    )
                ),
            )
        )

    square_intersection_angle = acos(
        11.0
        / 14.0
    )

    incidence_chord_angle = acos(
        383.0
        / 392.0
    )

    beta_incidence = (
        square_intersection_angle
        - incidence_chord_angle
    )

    for quadrant, name in enumerate(
        cardinal_names
    ):
        gamma = (
            quadrant
            * pi
            / 2.0
        )

        for offset_name, offset in (
            (
                "clockwise-oblique",
                -beta_incidence,
            ),
            (
                "cardinal",
                0.0,
            ),
            (
                "counterclockwise-oblique",
                beta_incidence,
            ),
        ):
            points.append(
                NativePointDirection(
                    point_id=(
                        f"njg-inc-moon/{name}/{offset_name}"
                    ),
                    source_node="NJG_INC_MOONS",
                    construction_lineage=(
                        "circle/circle incidence centre on construction circle"
                    ),
                    exact_definition=(
                        "beta = acos(11/14)-acos(383/392); "
                        f"gamma={quadrant}*pi/2 plus signed beta"
                    ),
                    angle_radians=_normalise_angle(
                        gamma
                        + offset
                    ),
                )
            )

    alpha_1 = (
        _method1_alpha_native()
    )

    offsets = (
        (
            "moon-0",
            0.0,
        ),
        (
            "gap-1",
            2.0
            * alpha_1
            - pi
            / 2.0,
        ),
        (
            "moon-2",
            pi
            - 3.0
            * alpha_1,
        ),
        (
            "intersection-3",
            pi
            / 2.0
            - alpha_1,
        ),
        (
            "intersection-4",
            alpha_1,
        ),
        (
            "moon-5",
            3.0
            * alpha_1
            - pi
            / 2.0,
        ),
        (
            "gap-6",
            pi
            - 2.0
            * alpha_1,
        ),
    )

    for quadrant in range(
        4
    ):
        quadrant_start = (
            quadrant
            * pi
            / 2.0
        )

        for local_index, (
            role,
            offset,
        ) in enumerate(
            offsets
        ):
            points.append(
                NativePointDirection(
                    point_id=(
                        f"method1-scaffold/q{quadrant}/"
                        f"i{local_index}-{role}"
                    ),
                    source_node="SCAFFOLD_28",
                    construction_lineage=(
                        "Figure 194 Method 1 constructible scaffold"
                    ),
                    exact_definition=(
                        "quadrant*pi/2 plus registered Method 1 "
                        "linear combination of alpha_1 and pi/2"
                    ),
                    angle_radians=_normalise_angle(
                        quadrant_start
                        + offset
                    ),
                )
            )

    alpha_2 = (
        _method2_alpha_native()
    )

    gamma_0 = (
        pi
        / 2.0
    )

    for carrier_index in range(
        6
    ):
        carrier_angle = (
            gamma_0
            + carrier_index
            * pi
            / 3.0
        )

        family = (
            "original"
            if carrier_index % 2 == 0
            else "reciprocal"
        )

        source_node = (
            "METHOD2_21"
            if family == "original"
            else "METHOD2_42"
        )

        for local_k in range(
            -3,
            4,
        ):
            points.append(
                NativePointDirection(
                    point_id=(
                        f"method2/{family}/"
                        f"carrier{carrier_index}/"
                        f"k{local_k:+d}"
                    ),
                    source_node=source_node,
                    construction_lineage=(
                        "Figure 194 Method 2 constructible carrier/arc geometry"
                    ),
                    exact_definition=(
                        "gamma_0 + carrier*pi/3 + k*alpha_2; "
                        "cos(alpha_2)=5/8"
                    ),
                    angle_radians=_normalise_angle(
                        carrier_angle
                        + local_k
                        * alpha_2
                    ),
                )
            )

    ids = [
        point.point_id
        for point in points
    ]

    if len(
        ids
    ) != len(
        set(
            ids
        )
    ):
        raise AssertionError(
            "Native radial point identifiers are not unique."
        )

    return tuple(
        points
    )


def _line_direction_from_points(
    first: float,
    second: float,
) -> float:
    x1 = cos(
        first
    )
    y1 = sin(
        first
    )
    x2 = cos(
        second
    )
    y2 = sin(
        second
    )

    return _canonical_line_angle(
        atan2(
            y2
            - y1,
            x2
            - x1,
        )
    )


def _native_line_candidates() -> tuple[NativeCandidate, ...]:
    """Build the registered semantic native-line inventory."""

    rows: list[
        NativeCandidate
    ] = []

    square_sides = (
        (
            "east",
            pi
            / 2.0,
        ),
        (
            "north",
            0.0,
        ),
        (
            "west",
            pi
            / 2.0,
        ),
        (
            "south",
            0.0,
        ),
    )

    for side, direction in square_sides:
        rows.append(
            NativeCandidate(
                candidate_id=(
                    f"line/earth-square/{side}"
                ),
                source_node="EARTH_SQUARE",
                construction_lineage=(
                    "native rational square side-line"
                ),
                feature_type="native_line_direction",
                exact_definition=(
                    f"Earth-square {side} side direction"
                ),
                symmetry_class=(
                    f"line/earth-square/{side}"
                ),
                angle_radians=_canonical_line_angle(
                    direction
                ),
                constructible_lineage=True,
                target_injected=False,
            )
        )

    for quadrant in range(
        4
    ):
        centre_angle = (
            quadrant
            * pi
            / 2.0
        )

        base_direction = (
            centre_angle
            + pi
            / 2.0
        )

        for line_name, direction in (
            (
                "base",
                base_direction,
            ),
            (
                "leg-plus",
                base_direction
                + pi
                / 3.0,
            ),
            (
                "leg-minus",
                base_direction
                - pi
                / 3.0,
            ),
        ):
            rows.append(
                NativeCandidate(
                    candidate_id=(
                        f"line/method1/q{quadrant}/{line_name}"
                    ),
                    source_node="SEPTENARY_METHOD_1",
                    construction_lineage=(
                        "source-described equilateral triangle on square side"
                    ),
                    feature_type="native_line_direction",
                    exact_definition=(
                        "square-side direction plus 0 or ±pi/3"
                    ),
                    symmetry_class=(
                        f"line/method1/q{quadrant}/{line_name}"
                    ),
                    angle_radians=_canonical_line_angle(
                        direction
                    ),
                    constructible_lineage=True,
                    target_injected=False,
                )
            )

    gamma_0 = (
        pi
        / 2.0
    )

    for family, phase in (
        (
            "original",
            0.0,
        ),
        (
            "reciprocal",
            pi
            / 3.0,
        ),
    ):
        carrier_angles = tuple(
            gamma_0
            + phase
            + index
            * 2.0
            * pi
            / 3.0
            for index in range(
                3
            )
        )

        for side_index in range(
            3
        ):
            direction = (
                _line_direction_from_points(
                    carrier_angles[
                        side_index
                    ],
                    carrier_angles[
                        (
                            side_index
                            + 1
                        )
                        % 3
                    ],
                )
            )

            rows.append(
                NativeCandidate(
                    candidate_id=(
                        f"line/method2/{family}/side{side_index}"
                    ),
                    source_node=(
                        "METHOD2_21"
                        if family == "original"
                        else "METHOD2_42"
                    ),
                    construction_lineage=(
                        "source-described equilateral carrier triangle"
                    ),
                    feature_type="native_line_direction",
                    exact_definition=(
                        "line through adjacent equilateral carrier vertices"
                    ),
                    symmetry_class=(
                        f"line/method2/{family}/side{side_index}"
                    ),
                    angle_radians=direction,
                    constructible_lineage=True,
                    target_injected=False,
                )
            )

    return tuple(
        rows
    )


def build_native_candidate_registry() -> tuple[
    NativeCandidate,
    ...,
]:
    """Build the complete frozen N0 census without using the sevenfold target."""

    points = (
        _native_radial_points()
    )

    candidates: list[
        NativeCandidate
    ] = []

    for point in points:
        candidates.append(
            NativeCandidate(
                candidate_id=(
                    f"radial/{point.point_id}"
                ),
                source_node=(
                    point.source_node
                ),
                construction_lineage=(
                    point.construction_lineage
                ),
                feature_type="radial_direction",
                exact_definition=(
                    point.exact_definition
                ),
                symmetry_class=(
                    f"radial/{point.point_id}"
                ),
                angle_radians=(
                    point.angle_radians
                ),
                constructible_lineage=True,
                target_injected=False,
            )
        )

    for (
        first_index,
        first,
    ), (
        second_index,
        second,
    ) in combinations(
        enumerate(
            points
        ),
        2,
    ):
        separation = (
            _circular_separation(
                first.angle_radians,
                second.angle_radians,
            )
        )

        candidates.append(
            NativeCandidate(
                candidate_id=(
                    "separation/"
                    f"{first_index:03d}-{second_index:03d}"
                ),
                source_node=(
                    f"{first.source_node}|{second.source_node}"
                ),
                construction_lineage=(
                    "angular separation of two constructible native radial "
                    "directions; dot/cross arithmetic remains in the "
                    "constructible closure"
                ),
                feature_type="pairwise_radial_separation",
                exact_definition=(
                    f"separation({first.point_id},{second.point_id})"
                ),
                symmetry_class=(
                    "separation/"
                    f"{first_index:03d}-{second_index:03d}"
                ),
                angle_radians=separation,
                constructible_lineage=True,
                target_injected=False,
            )
        )

    candidates.extend(
        _native_line_candidates()
    )

    ids = [
        candidate.candidate_id
        for candidate in candidates
    ]

    if len(
        ids
    ) != len(
        set(
            ids
        )
    ):
        raise AssertionError(
            "Native census candidate identifiers are not unique."
        )

    return tuple(
        candidates
    )


def _candidate_residual(
    candidate: NativeCandidate,
    target: float,
) -> float:
    if (
        candidate.feature_type
        == "radial_direction"
    ):
        return min(
            _circular_separation(
                candidate.angle_radians,
                target,
            ),
            _circular_separation(
                candidate.angle_radians,
                -target,
            ),
        )

    if (
        candidate.feature_type
        == "pairwise_radial_separation"
    ):
        return abs(
            candidate.angle_radians
            - target
        )

    if (
        candidate.feature_type
        == "native_line_direction"
    ):
        return abs(
            candidate.angle_radians
            - target
        )

    raise ValueError(
        candidate.feature_type
    )


def build_exact_sevenfold_boundary_audit() -> ExactSevenfoldBoundaryAudit:
    """Execute the preregistered A/B exact-sevenfold boundary audit."""

    polynomial = (
        build_target_polynomial_audit()
    )

    n0, n1 = (
        build_lineage_audit()
    )

    if (
        not polynomial.irreducible_over_q
        or polynomial.algebraic_degree
        != 3
    ):
        euclidean_status = (
            TARGET_DEGREE_FAILED
        )
    elif not all(
        record.verified_constructible
        for record in (
            n0
            + n1
        )
    ):
        euclidean_status = (
            EUCLIDEAN_LINEAGE_FAILED
        )
    else:
        euclidean_status = (
            EUCLIDEAN_EXCLUDED
        )

    exclusions = (
        build_target_injection_exclusions()
    )

    candidates = (
        build_native_candidate_registry()
    )

    if any(
        candidate.target_injected
        for candidate in candidates
    ):
        raise AssertionError(
            "Target-injected candidate entered the native registry."
        )

    if not all(
        candidate.constructible_lineage
        for candidate in candidates
    ):
        raise AssertionError(
            "Native candidate without verified constructible lineage."
        )

    exact_candidate_count = (
        0
        if (
            euclidean_status
            == EUCLIDEAN_EXCLUDED
        )
        else -1
    )

    target = (
        polynomial.numeric_target_radians
    )

    ranked = sorted(
        (
            (
                _candidate_residual(
                    candidate,
                    target,
                ),
                candidate.candidate_id,
                candidate,
            )
            for candidate in candidates
        ),
        key=lambda row: (
            row[
                0
            ],
            row[
                1
            ],
        ),
    )

    closest_residual, _, closest = (
        ranked[
            0
        ]
    )

    radial_count = sum(
        candidate.feature_type
        == "radial_direction"
        for candidate in candidates
    )

    separation_count = sum(
        candidate.feature_type
        == "pairwise_radial_separation"
        for candidate in candidates
    )

    line_count = sum(
        candidate.feature_type
        == "native_line_direction"
        for candidate in candidates
    )

    native_status = (
        NO_NATIVE_EXACT
        if exact_candidate_count == 0
        else NATIVE_REQUIRES_AUDIT
    )

    census = CensusSummary(
        census_tiers=(
            "N0",
        ),
        radial_direction_count=(
            radial_count
        ),
        pairwise_separation_count=(
            separation_count
        ),
        native_line_count=(
            line_count
        ),
        candidate_count_semantic=len(
            candidates
        ),
        symmetry_reduction_mode=(
            "none; semantic provenance retained and no numerical "
            "symmetry clustering performed"
        ),
        candidate_count_symmetry_reduced=len(
            {
                candidate.symmetry_class
                for candidate in candidates
            }
        ),
        target_injected_candidate_count_excluded=len(
            exclusions
        ),
        exact_classification_method=(
            "constructibility_degree_obstruction; no numerical tolerance"
        ),
        exact_candidate_count=(
            exact_candidate_count
        ),
        closest_descriptive_candidate_id=(
            closest.candidate_id
        ),
        closest_descriptive_feature_type=(
            closest.feature_type
        ),
        closest_descriptive_angle_radians=(
            closest.angle_radians
        ),
        closest_descriptive_angle_degrees=(
            closest.angle_radians
            * 180.0
            / pi
        ),
        closest_descriptive_residual_radians=(
            closest_residual
        ),
        closest_descriptive_residual_degrees=(
            closest_residual
            * 180.0
            / pi
        ),
        native_incidence_status=(
            native_status
        ),
    )

    return ExactSevenfoldBoundaryAudit(
        schema=(
            "njg_michell_v0_9_exact_sevenfold_boundary"
        ),
        phase="9B",
        protocol_sha256=(
            PROTOCOL_SHA256
        ),
        phase9a_commit=(
            PHASE9A_COMMIT
        ),
        registry_spec_sha256=(
            REGISTRY_SPEC_SHA256
        ),
        polynomial_audit=(
            polynomial
        ),
        euclidean_quadratic_tower_criterion=(
            "A finite ordinary straightedge-and-compass construction from "
            "rational seeds lies in a tower of degree-at-most-two field "
            "extensions; every algebraic element therefore has degree over "
            "Q equal to a power of two."
        ),
        n0_seed_lineage_checks=n0,
        n1_seed_lineage_checks=n1,
        euclidean_closure_status=(
            euclidean_status
        ),
        target_injection_exclusions=(
            exclusions
        ),
        native_candidates=(
            candidates
        ),
        census=census,
        degrees_of_freedom=(
            AuditDegreesOfFreedom()
        ),
        question_c_status=(
            "DEFERRED_UNTIL_PHASE_9B_FREEZE"
        ),
        stopping_status=(
            STOPPING_STATUS
        ),
    )


def exact_sevenfold_boundary_to_json(
    audit: ExactSevenfoldBoundaryAudit,
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


def exact_sevenfold_boundary_to_markdown(
    audit: ExactSevenfoldBoundaryAudit,
) -> str:
    p = (
        audit.polynomial_audit
    )

    c = (
        audit.census
    )

    n0_lines = [
        "| Node | Euclidean lineage | Constructible | Census |",
        "| --- | --- | --- | --- |",
    ]

    for record in (
        audit.n0_seed_lineage_checks
    ):
        n0_lines.append(
            "| "
            + record.node_id
            + " | "
            + record.euclidean_operation_class
            + " | "
            + str(
                record.verified_constructible
            )
            + " | "
            + str(
                record.census_enabled
            )
            + " |"
        )

    n1_lines = [
        "| Node | Euclidean lineage | Constructible | Phase 9B census |",
        "| --- | --- | --- | --- |",
    ]

    for record in (
        audit.n1_seed_lineage_checks
    ):
        n1_lines.append(
            "| "
            + record.node_id
            + " | "
            + record.euclidean_operation_class
            + " | "
            + str(
                record.verified_constructible
            )
            + " | "
            + str(
                record.census_enabled
            )
            + " |"
        )

    exclusion_lines = [
        (
            f"- `{row.object_name}` — {row.reason}"
        )
        for row in (
            audit.target_injection_exclusions
        )
    ]

    lines = [
        "# v0.9 exact-sevenfold boundary audit",
        "",
        "## Status",
        "",
        f"`{audit.stopping_status}`",
        "",
        "This is the execution of Questions A and B of the frozen Phase 9A",
        "constructibility protocol. Question C remains deferred.",
        "",
        "## Exact target cubic",
        "",
        "Define:",
        "",
        "```text",
        "theta_7 = 2*pi/7",
        "y_7 = 2*cos(theta_7)",
        "```",
        "",
        "The seventh-cyclotomic recurrence gives exactly:",
        "",
        "```text",
        f"{p.polynomial_text} = 0",
        "```",
        "",
        "Equivalent cosine form:",
        "",
        "```text",
        f"{p.cosine_polynomial_text} = 0",
        "```",
        "",
        "The rational-root candidates are `-1` and `+1`; neither is a root.",
        "Therefore the cubic is irreducible over `Q` and:",
        "",
        "```text",
        f"target algebraic degree = {p.algebraic_degree}",
        "```",
        "",
        "The floating-point polynomial residual is retained only as an",
        "implementation diagnostic:",
        "",
        "```text",
        f"numeric polynomial residual = {repr(p.numeric_polynomial_residual)}",
        "```",
        "",
        "It is not the proof of exactness or irreducibility.",
        "",
        "## Question A — Euclidean closure",
        "",
        "Registered Euclidean criterion:",
        "",
        audit.euclidean_quadratic_tower_criterion,
        "",
        "All admitted N0 construction nodes have verified ordinary Euclidean",
        "lineage:",
        "",
        *n0_lines,
        "",
        "The secondary N1 wall lineage is also Euclidean, but its finite",
        "features were not enabled in the Phase 9B native-incidence census:",
        "",
        *n1_lines,
        "",
        "Result:",
        "",
        "```text",
        f"euclidean_closure_status = {audit.euclidean_closure_status}",
        "```",
        "",
        "Because the exact target has degree 3 while every algebraic coordinate",
        "in the admitted Euclidean closure has power-of-two degree over `Q`,",
        "the exact regular-heptagon target is excluded from that closure.",
        "",
        "This is a theorem-level constructibility result, not a finite-search",
        "failure.",
        "",
        "## Target-injected references excluded",
        "",
        *exclusion_lines,
        "",
        "These objects remain valid comparison/reference geometries elsewhere",
        "in the repository, but they cannot count as native v0.9 discoveries.",
        "",
        "## Question B — native-incidence census",
        "",
        "The finite Phase 9B census was frozen before result generation as:",
        "",
        "```text",
        f"radial directions           = {c.radial_direction_count}",
        f"pairwise radial separations = {c.pairwise_separation_count}",
        f"native straight lines       = {c.native_line_count}",
        f"semantic candidates         = {c.candidate_count_semantic}",
        f"symmetry-reduced candidates = {c.candidate_count_symmetry_reduced}",
        "```",
        "",
        "No numerical symmetry clustering was performed; semantic provenance",
        "was retained for every candidate.",
        "",
        "Exact classification uses:",
        "",
        "```text",
        f"{c.exact_classification_method}",
        "```",
        "",
        "Result:",
        "",
        "```text",
        f"exact_candidate_count = {c.exact_candidate_count}",
        f"native_incidence_status = {c.native_incidence_status}",
        "```",
        "",
        "Thus no already-existing N0 canonical feature can be the exact",
        "sevenfold target under the frozen admissibility rules.",
        "",
        "## Closest descriptive native feature",
        "",
        "For descriptive geometry only, after exact classification was fixed,",
        "the nearest numerical candidate was:",
        "",
        "```text",
        f"candidate_id = {c.closest_descriptive_candidate_id}",
        f"feature_type = {c.closest_descriptive_feature_type}",
        (
            "candidate_angle_degrees = "
            f"{repr(c.closest_descriptive_angle_degrees)}"
        ),
        (
            "absolute_residual_degrees = "
            f"{repr(c.closest_descriptive_residual_degrees)}"
        ),
        "```",
        "",
        "This nearest value is not promoted to an exact construction, does not",
        "alter the theorem-level result, and was not used to select or modify",
        "the census registry.",
        "",
        "## Question C",
        "",
        "```text",
        f"{audit.question_c_status}",
        "```",
        "",
        "No neusis, marked-ruler, origami, or conic extension was searched in",
        "Phase 9B.",
        "",
        "## Degrees of freedom",
        "",
        "```text",
        "continuous_fitted_parameters = 0",
        "scale_fitted_parameters = 0",
        "phase_optimized_parameters = 0",
        "target_based_candidate_choices = 0",
        "numerical_acceptance_tolerances = 0",
        "post_hoc_seed_additions = 0",
        "non_euclidean_operations = 0",
        "```",
        "",
        "## Interpretation boundary",
        "",
        "The Euclidean no-go result establishes a constructibility boundary for",
        "the admitted New Jerusalem generative geometry. It does not establish",
        "that Michell or Sommerville attempted every possible construction.",
        "",
        "The finite native-incidence null result concerns the preregistered N0",
        "canonical registry. N1 wall features were lineage-audited but not",
        "included in the finite Phase 9B census.",
        "",
        "No historical intention, physical significance, archaeological",
        "significance, or metaphysical significance follows from this result.",
        "",
    ]

    return "\n".join(
        lines
    )
