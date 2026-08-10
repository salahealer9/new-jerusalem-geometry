"""Phase 9E visual/numerical synthesis of the frozen exact sevenfold result.

This module performs no model fitting and no new geometric search.

The exact heptagon comes from the frozen Phase 9D one-trisection construction,
rotated by a fixed +90 degrees solely to place vertex 0 at north for comparison
with the already-frozen Figure 14 / scaffold ordering.

The comparison orientation is fixed:
    phase = 90 degrees
    order = counter-clockwise
    rotational fitting = forbidden

Figure 14 plate endpoints are source-calibrated observations loaded from the
frozen affine-calibration derived CSV. They are compared by their existing
semantic sequence index, with no permutation or phase optimization.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import hashlib
import json
from math import atan2, cos, degrees, hypot, pi, radians, sin, sqrt
from pathlib import Path
from typing import Sequence

from .core_geometry import build_core_geometry
from .heptagram_geometry import (
    HeptagramFamily,
    build_scaffold_heptagram,
)
from .michell_composite import build_michell_composite
from .model_variants import ObliqueModel
from .one_trisection_heptagon import (
    build_one_trisection_heptagon,
)
from .septenary_geometry import michell_heptagon_step_angle
from .sevenfold_dual_method import method_2_step_from_source_geometry
from .wall_geometry import build_ordered_moon_circles


PHASE9E_PROTOCOL_SHA256 = "8d256b7cf8eeab7903fc88386b8f16333a938993937d07f990dd98dddbc6d8b1"
PHASE9D_COMMIT = "fb111056291a478884fb2e2b340fa4bb8930a98b"

STOPPING_STATUS = "EXACT_HEPTAGON_SYNTHESIS_COMPLETE"

MODEL_FEET_PER_UNIT = 720.0
FIXED_PHASE_DEGREES = 90.0
EXACT_VERTEX_COUNT = 7

PLATE_ENDPOINT_PATH = Path(
    "data/calibration/figure14/derived/star_endpoint_geometry.csv"
)

EXPECTED_PLATE_ENDPOINT_IDS = tuple(
    f"star_endpoint_{index:02d}_{name}"
    for index, name in enumerate(
        (
            "top",
            "upper_left",
            "lower_left",
            "bottom_left",
            "bottom_right",
            "lower_right",
            "upper_right",
        )
    )
)


@dataclass(frozen=True, slots=True)
class StepComparison:
    method_id: str
    step_degrees: float
    signed_residual_degrees: float
    absolute_residual_degrees: float
    relative_residual: float
    seven_step_closure_degrees: float
    evidential_status: str


@dataclass(frozen=True, slots=True)
class VertexComparison:
    source_id: str
    vertex_index: int
    endpoint_id: str
    exact_x: float
    exact_y: float
    exact_angle_degrees: float
    observed_x: float
    observed_y: float
    observed_radius: float
    observed_angle_degrees: float
    signed_angular_residual_degrees: float
    absolute_angular_residual_degrees: float
    radial_residual_u: float
    arc_displacement_u: float
    chord_displacement_u: float
    euclidean_displacement_u: float
    chord_displacement_model_feet: float
    euclidean_displacement_model_feet: float


@dataclass(frozen=True, slots=True)
class AggregateComparison:
    source_id: str
    vertex_count: int
    angular_rms_degrees: float
    angular_maximum_degrees: float
    radial_rms_u: float
    radial_maximum_u: float
    chord_rms_u: float
    chord_maximum_u: float
    euclidean_rms_u: float
    euclidean_maximum_u: float
    euclidean_rms_model_feet: float
    euclidean_maximum_model_feet: float
    interpretation: str


@dataclass(frozen=True, slots=True)
class ContextSummary:
    wall_vertex_count: int
    wall_radius_min_u: float
    wall_radius_max_u: float
    incidence_moon_count: int
    square_circle_junction_count: int
    wall_comparison_performed: bool
    note: str


@dataclass(frozen=True, slots=True)
class SynthesisDegreesOfFreedom:
    rotational_fit_parameters: int = 0
    phase_optimization_parameters: int = 0
    endpoint_permutation_searches: int = 0
    wall_nearest_neighbor_searches: int = 0
    fitted_parameters_total: int = 0


@dataclass(frozen=True, slots=True)
class ExactHeptagonSynthesis:
    schema: str
    phase: str
    phase9e_protocol_sha256: str
    phase9d_commit: str
    stopping_status: str
    fixed_orientation_degrees: float
    orientation_fit_applied: bool
    exact_vertex_angles_degrees: tuple[float, ...]
    exact_vertices: tuple[tuple[float, float], ...]
    step_comparisons: tuple[StepComparison, ...]
    scaffold_vertex_comparisons: tuple[VertexComparison, ...]
    figure14_plate_comparisons: tuple[VertexComparison, ...]
    scaffold_aggregate: AggregateComparison
    figure14_plate_aggregate: AggregateComparison
    context: ContextSummary
    figure14_plate_input_sha256: str
    degrees_of_freedom: SynthesisDegreesOfFreedom
    interpretation_status: str


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(
        Path(path).read_bytes()
    ).hexdigest()


def _normalize_degrees(angle_degrees: float) -> float:
    value = angle_degrees % 360.0

    if value < 0.0:
        value += 360.0

    return value


def _signed_angle_residual_degrees(
    observed_degrees: float,
    exact_degrees: float,
) -> float:
    return (
        (
            observed_degrees
            - exact_degrees
            + 180.0
        )
        % 360.0
        - 180.0
    )


def _rms(values: Sequence[float]) -> float:
    if not values:
        raise ValueError(
            "RMS requires at least one value."
        )

    return sqrt(
        sum(
            value * value
            for value in values
        )
        / len(
            values
        )
    )


def _exact_north_vertices() -> tuple[
    tuple[float, float],
    ...,
]:
    """Rotate the frozen Phase 9D constructed vertices by fixed +90 degrees."""

    construction = (
        build_one_trisection_heptagon()
    )

    vertices = construction.heptagon.vertices

    if len(
        vertices
    ) != EXACT_VERTEX_COUNT:
        raise AssertionError(
            "Phase 9D construction does not contain seven vertices."
        )

    # Fixed +90-degree rotation: (x,y) -> (-y,x).
    return tuple(
        (
            -y,
            x,
        )
        for x, y in vertices
    )


def _angles_from_vertices(
    vertices: Sequence[
        tuple[float, float]
    ],
) -> tuple[float, ...]:
    return tuple(
        _normalize_degrees(
            degrees(
                atan2(
                    y,
                    x,
                )
            )
        )
        for x, y in vertices
    )


def _load_plate_endpoints(
    root: Path,
) -> tuple[
    tuple[str, float, float],
    ...,
]:
    path = (
        root
        / PLATE_ENDPOINT_PATH
    )

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    endpoint_rows = [
        row
        for row in rows
        if row[
            "landmark_id"
        ].startswith(
            "star_endpoint_"
        )
    ]

    endpoint_rows.sort(
        key=lambda row: int(
            row[
                "sequence_index"
            ]
        )
    )

    ids = tuple(
        row[
            "landmark_id"
        ]
        for row in endpoint_rows
    )

    if ids != EXPECTED_PLATE_ENDPOINT_IDS:
        raise AssertionError(
            (
                "Figure 14 source endpoint order does not match "
                "the frozen semantic sequence.",
                ids,
            )
        )

    return tuple(
        (
            row[
                "landmark_id"
            ],
            float(
                row[
                    "observed_x"
                ]
            ),
            float(
                row[
                    "observed_y"
                ]
            ),
        )
        for row in endpoint_rows
    )


def _scaffold_vertices() -> tuple[
    tuple[float, float],
    ...,
]:
    diagram = (
        build_core_geometry(
            unit=1.0
        )
    )

    scaffold = (
        build_scaffold_heptagram(
            diagram,
            family=HeptagramFamily.STEP_2,
        )
    )

    if len(
        scaffold.vertices
    ) != EXACT_VERTEX_COUNT:
        raise AssertionError(
            "Scaffold comparison does not contain seven vertices."
        )

    return tuple(
        (
            vertex.x,
            vertex.y,
        )
        for vertex in scaffold.vertices
    )


def _comparison_rows(
    *,
    source_id: str,
    exact_vertices: Sequence[
        tuple[float, float]
    ],
    observed_vertices: Sequence[
        tuple[str, float, float]
    ],
) -> tuple[
    VertexComparison,
    ...,
]:
    if (
        len(
            exact_vertices
        )
        != len(
            observed_vertices
        )
    ):
        raise AssertionError(
            "Exact and observed vertex counts differ."
        )

    if not exact_vertices:
        raise AssertionError(
            "Vertex comparison requires at least one vertex."
        )

    rows: list[
        VertexComparison
    ] = []

    radius = 7.0

    for index, (
        exact_vertex,
        observed,
    ) in enumerate(
        zip(
            exact_vertices,
            observed_vertices,
            strict=True,
        )
    ):
        endpoint_id, observed_x, observed_y = (
            observed
        )

        exact_x, exact_y = (
            exact_vertex
        )

        exact_angle = (
            _normalize_degrees(
                degrees(
                    atan2(
                        exact_y,
                        exact_x,
                    )
                )
            )
        )

        observed_angle = (
            _normalize_degrees(
                degrees(
                    atan2(
                        observed_y,
                        observed_x,
                    )
                )
            )
        )

        signed_angle = (
            _signed_angle_residual_degrees(
                observed_angle,
                exact_angle,
            )
        )

        absolute_angle = abs(
            signed_angle
        )

        observed_radius = hypot(
            observed_x,
            observed_y,
        )

        radial_residual = (
            observed_radius
            - radius
        )

        angular_radians = radians(
            absolute_angle
        )

        arc_displacement = (
            radius
            * angular_radians
        )

        chord_displacement = (
            2.0
            * radius
            * sin(
                angular_radians
                / 2.0
            )
        )

        euclidean_displacement = hypot(
            observed_x
            - exact_x,
            observed_y
            - exact_y,
        )

        rows.append(
            VertexComparison(
                source_id=source_id,
                vertex_index=index,
                endpoint_id=endpoint_id,
                exact_x=exact_x,
                exact_y=exact_y,
                exact_angle_degrees=(
                    exact_angle
                ),
                observed_x=(
                    observed_x
                ),
                observed_y=(
                    observed_y
                ),
                observed_radius=(
                    observed_radius
                ),
                observed_angle_degrees=(
                    observed_angle
                ),
                signed_angular_residual_degrees=(
                    signed_angle
                ),
                absolute_angular_residual_degrees=(
                    absolute_angle
                ),
                radial_residual_u=(
                    radial_residual
                ),
                arc_displacement_u=(
                    arc_displacement
                ),
                chord_displacement_u=(
                    chord_displacement
                ),
                euclidean_displacement_u=(
                    euclidean_displacement
                ),
                chord_displacement_model_feet=(
                    chord_displacement
                    * MODEL_FEET_PER_UNIT
                ),
                euclidean_displacement_model_feet=(
                    euclidean_displacement
                    * MODEL_FEET_PER_UNIT
                ),
            )
        )

    return tuple(
        rows
    )


def _aggregate(
    *,
    source_id: str,
    rows: Sequence[
        VertexComparison
    ],
    interpretation: str,
) -> AggregateComparison:
    angular = [
        row.absolute_angular_residual_degrees
        for row in rows
    ]

    radial = [
        row.radial_residual_u
        for row in rows
    ]

    chord = [
        row.chord_displacement_u
        for row in rows
    ]

    euclidean = [
        row.euclidean_displacement_u
        for row in rows
    ]

    return AggregateComparison(
        source_id=source_id,
        vertex_count=len(
            rows
        ),
        angular_rms_degrees=(
            _rms(
                angular
            )
        ),
        angular_maximum_degrees=max(
            angular
        ),
        radial_rms_u=(
            _rms(
                radial
            )
        ),
        radial_maximum_u=max(
            abs(
                value
            )
            for value in radial
        ),
        chord_rms_u=(
            _rms(
                chord
            )
        ),
        chord_maximum_u=max(
            chord
        ),
        euclidean_rms_u=(
            _rms(
                euclidean
            )
        ),
        euclidean_maximum_u=max(
            euclidean
        ),
        euclidean_rms_model_feet=(
            _rms(
                euclidean
            )
            * MODEL_FEET_PER_UNIT
        ),
        euclidean_maximum_model_feet=(
            max(
                euclidean
            )
            * MODEL_FEET_PER_UNIT
        ),
        interpretation=(
            interpretation
        ),
    )


def _step_comparisons() -> tuple[
    StepComparison,
    ...,
]:
    exact = (
        360.0
        / 7.0
    )

    method1 = degrees(
        michell_heptagon_step_angle()
    )

    method2 = degrees(
        method_2_step_from_source_geometry()
    )

    rows: list[
        StepComparison
    ] = []

    for method_id, value, status in (
        (
            "EXACT_ONE_TRISECTION",
            exact,
            "Phase 9D exact construction; reference step.",
        ),
        (
            "MICHELL_METHOD_1",
            method1,
            "Frozen v0.8 approximate Figure 194 Method 1.",
        ),
        (
            "MICHELL_METHOD_2",
            method2,
            "Frozen v0.8 approximate Figure 194 Method 2.",
        ),
    ):
        signed = (
            value
            - exact
        )

        rows.append(
            StepComparison(
                method_id=method_id,
                step_degrees=value,
                signed_residual_degrees=signed,
                absolute_residual_degrees=abs(
                    signed
                ),
                relative_residual=(
                    signed
                    / exact
                ),
                seven_step_closure_degrees=(
                    7.0
                    * value
                    - 360.0
                ),
                evidential_status=status,
            )
        )

    return tuple(
        rows
    )


def _context_summary() -> ContextSummary:
    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    wall_vertices = (
        composite
        .wall_reconstruction
        .vertices
    )

    wall_radii = tuple(
        hypot(
            vertex.x,
            vertex.y,
        )
        for vertex in wall_vertices
    )

    diagram = (
        composite.core
    )

    moons = (
        build_ordered_moon_circles(
            diagram,
            ObliqueModel.INCIDENCE,
        )
    )

    return ContextSummary(
        wall_vertex_count=len(
            wall_vertices
        ),
        wall_radius_min_u=min(
            wall_radii
        ),
        wall_radius_max_u=max(
            wall_radii
        ),
        incidence_moon_count=len(
            moons
        ),
        square_circle_junction_count=8,
        wall_comparison_performed=False,
        note=(
            "Wall vertices, incidence Moon centres, and square-circle "
            "junctions are rendered only as architectural context. "
            "No nearest-neighbour or sevenfold wall fit is performed."
        ),
    )


def build_exact_heptagon_synthesis(
    *,
    root: str | Path = ".",
) -> ExactHeptagonSynthesis:
    root_path = Path(
        root
    )

    exact_vertices = (
        _exact_north_vertices()
    )

    exact_angles = (
        _angles_from_vertices(
            exact_vertices
        )
    )

    expected_angles = tuple(
        _normalize_degrees(
            FIXED_PHASE_DEGREES
            + index
            * (
                360.0
                / 7.0
            )
        )
        for index in range(
            EXACT_VERTEX_COUNT
        )
    )

    for actual, expected in zip(
        exact_angles,
        expected_angles,
        strict=True,
    ):
        if abs(
            _signed_angle_residual_degrees(
                actual,
                expected,
            )
        ) > 1.0e-12:
            raise AssertionError(
                "Fixed north rotation of the Phase 9D heptagon failed."
            )

    scaffold_vertices = (
        _scaffold_vertices()
    )

    scaffold_observed = tuple(
        (
            f"scaffold_vertex_{index}",
            x,
            y,
        )
        for index, (
            x,
            y,
        ) in enumerate(
            scaffold_vertices
        )
    )

    plate_observed = (
        _load_plate_endpoints(
            root_path
        )
    )

    scaffold_rows = (
        _comparison_rows(
            source_id="MICHELL_SCAFFOLD_7_2",
            exact_vertices=(
                exact_vertices
            ),
            observed_vertices=(
                scaffold_observed
            ),
        )
    )

    plate_rows = (
        _comparison_rows(
            source_id="FIGURE14_AFFINE_PLATE_ENDPOINTS",
            exact_vertices=(
                exact_vertices
            ),
            observed_vertices=(
                plate_observed
            ),
        )
    )

    return ExactHeptagonSynthesis(
        schema=(
            "njg_michell_v0_9_exact_heptagon_synthesis"
        ),
        phase="9E",
        phase9e_protocol_sha256=(
            PHASE9E_PROTOCOL_SHA256
        ),
        phase9d_commit=(
            PHASE9D_COMMIT
        ),
        stopping_status=(
            STOPPING_STATUS
        ),
        fixed_orientation_degrees=(
            FIXED_PHASE_DEGREES
        ),
        orientation_fit_applied=False,
        exact_vertex_angles_degrees=(
            exact_angles
        ),
        exact_vertices=(
            exact_vertices
        ),
        step_comparisons=(
            _step_comparisons()
        ),
        scaffold_vertex_comparisons=(
            scaffold_rows
        ),
        figure14_plate_comparisons=(
            plate_rows
        ),
        scaffold_aggregate=(
            _aggregate(
                source_id=(
                    "MICHELL_SCAFFOLD_7_2"
                ),
                rows=(
                    scaffold_rows
                ),
                interpretation=(
                    "Frozen Method-1 scaffold source-consistency comparison; "
                    "no phase fitting and not independent validation."
                ),
            )
        ),
        figure14_plate_aggregate=(
            _aggregate(
                source_id=(
                    "FIGURE14_AFFINE_PLATE_ENDPOINTS"
                ),
                rows=(
                    plate_rows
                ),
                interpretation=(
                    "Frozen source-plate consistency comparison against "
                    "the north-anchored exact sevenfold set. Figure 14 "
                    "calibration/topology informed earlier project work, "
                    "so this is not independent validation."
                ),
            )
        ),
        context=(
            _context_summary()
        ),
        figure14_plate_input_sha256=(
            sha256_file(
                root_path
                / PLATE_ENDPOINT_PATH
            )
        ),
        degrees_of_freedom=(
            SynthesisDegreesOfFreedom()
        ),
        interpretation_status=(
            "SOURCE_CONSISTENCY_SYNTHESIS_NO_REFIT"
        ),
    )


def synthesis_to_json(
    synthesis: ExactHeptagonSynthesis,
) -> str:
    return (
        json.dumps(
            asdict(
                synthesis
            ),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    )


def _format_step_table(
    synthesis: ExactHeptagonSynthesis,
) -> list[str]:
    lines = [
        (
            "| Construction | Step (deg) | Signed error (deg) | "
            "|error| (deg) | 7-step closure (deg) |"
        ),
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for row in (
        synthesis.step_comparisons
    ):
        lines.append(
            "| "
            + row.method_id
            + " | "
            + f"{row.step_degrees:.12f}"
            + " | "
            + f"{row.signed_residual_degrees:+.12f}"
            + " | "
            + f"{row.absolute_residual_degrees:.12f}"
            + " | "
            + f"{row.seven_step_closure_degrees:+.12f}"
            + " |"
        )

    return lines


def _format_vertex_table(
    rows: Sequence[
        VertexComparison
    ],
) -> list[str]:
    lines = [
        (
            "| i | Endpoint | Exact angle (deg) | Observed angle (deg) | "
            "dtheta (deg) | dr (u) | chord d (u) | Euclidean d (u) |"
        ),
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for row in rows:
        lines.append(
            "| "
            + str(
                row.vertex_index
            )
            + " | "
            + row.endpoint_id
            + " | "
            + f"{row.exact_angle_degrees:.9f}"
            + " | "
            + f"{row.observed_angle_degrees:.9f}"
            + " | "
            + f"{row.signed_angular_residual_degrees:+.9f}"
            + " | "
            + f"{row.radial_residual_u:+.9f}"
            + " | "
            + f"{row.chord_displacement_u:.9f}"
            + " | "
            + f"{row.euclidean_displacement_u:.9f}"
            + " |"
        )

    return lines


def synthesis_to_markdown(
    synthesis: ExactHeptagonSynthesis,
) -> str:
    scaffold = (
        synthesis.scaffold_aggregate
    )

    plate = (
        synthesis.figure14_plate_aggregate
    )

    exact_angles = ", ".join(
        f"{angle:.6f}"
        for angle in (
            synthesis.exact_vertex_angles_degrees
        )
    )

    lines = [
        "# v0.9 exact-heptagon comparison and visual synthesis",
        "",
        "## Status",
        "",
        f"`{synthesis.stopping_status}`",
        "",
        "This phase adds no new construction search and performs no refitting.",
        "The exact Phase 9D heptagon is rotated by a fixed +90 degrees so that",
        "vertex 0 is north, matching the frozen Figure 14/scaffold sequence.",
        "",
        "```text",
        "orientation = 90 degrees",
        "rotation fitting = none",
        "endpoint permutation search = none",
        "wall nearest-neighbour search = none",
        "```",
        "",
        "## Exact north-anchored sevenfold set",
        "",
        "The seven exact polar angles, counter-clockwise from north, are:",
        "",
        "```text",
        exact_angles,
        "```",
        "",
        "All seven vertices remain on the construction circle `R = 7 u`",
        "(`5040 model ft`).",
        "",
        "## Exact step versus Michell's two approximations",
        "",
        *_format_step_table(
            synthesis
        ),
        "",
        "Method 1 and Method 2 are the already-frozen v0.8 Figure 194",
        "approximations. The exact row is the frozen Phase 9D result.",
        "",
        "## Exact sevenfold versus frozen Method-1 scaffold star",
        "",
        *_format_vertex_table(
            synthesis.scaffold_vertex_comparisons
        ),
        "",
        "Aggregate:",
        "",
        "```text",
        (
            "angular RMS (deg)       = "
            f"{scaffold.angular_rms_degrees:.12f}"
        ),
        (
            "angular maximum (deg)   = "
            f"{scaffold.angular_maximum_degrees:.12f}"
        ),
        (
            "Euclidean RMS (u)       = "
            f"{scaffold.euclidean_rms_u:.12f}"
        ),
        (
            "Euclidean maximum (u)   = "
            f"{scaffold.euclidean_maximum_u:.12f}"
        ),
        (
            "Euclidean RMS (ft)      = "
            f"{scaffold.euclidean_rms_model_feet:.6f}"
        ),
        "```",
        "",
        "This is a source-consistency comparison of a frozen project candidate.",
        "No phase is fitted to improve agreement.",
        "",
        "## Exact sevenfold versus affine-calibrated Figure 14 plate endpoints",
        "",
        *_format_vertex_table(
            synthesis.figure14_plate_comparisons
        ),
        "",
        "Aggregate:",
        "",
        "```text",
        (
            "angular RMS (deg)       = "
            f"{plate.angular_rms_degrees:.12f}"
        ),
        (
            "angular maximum (deg)   = "
            f"{plate.angular_maximum_degrees:.12f}"
        ),
        (
            "radial RMS (u)          = "
            f"{plate.radial_rms_u:.12f}"
        ),
        (
            "radial maximum (u)      = "
            f"{plate.radial_maximum_u:.12f}"
        ),
        (
            "Euclidean RMS (u)       = "
            f"{plate.euclidean_rms_u:.12f}"
        ),
        (
            "Euclidean maximum (u)   = "
            f"{plate.euclidean_maximum_u:.12f}"
        ),
        (
            "Euclidean RMS (ft)      = "
            f"{plate.euclidean_rms_model_feet:.6f}"
        ),
        "```",
        "",
        "The plate endpoints are frozen affine-registered source observations.",
        "Their existing semantic order is used directly. There is no rotational",
        "fit and no endpoint reassignment in Phase 9E.",
        "",
        "This is not statistically independent validation: Figure 14 source",
        "calibration and topology already informed earlier project development.",
        "",
        "## Outer wall and twelvefold architecture",
        "",
        "The wall, Moon centres, and square-circle junctions are retained only",
        "as architectural context in the synthesis SVG.",
        "",
        "```text",
        (
            "wall vertices = "
            f"{synthesis.context.wall_vertex_count}"
        ),
        (
            "wall radius range (u) = "
            f"{synthesis.context.wall_radius_min_u:.12f}"
            " .. "
            f"{synthesis.context.wall_radius_max_u:.12f}"
        ),
        (
            "incidence Moon centres = "
            f"{synthesis.context.incidence_moon_count}"
        ),
        (
            "square-circle junctions = "
            f"{synthesis.context.square_circle_junction_count}"
        ),
        "wall sevenfold comparison = none",
        "```",
        "",
        "The wall is on a different radial layer and is not treated as a",
        "sevenfold approximation. No nearest wall vertex to an exact heptagon",
        "vertex is searched or reported.",
        "",
        "## Displacement conventions",
        "",
        "For an angular discrepancy `dtheta` on the radius-7 construction",
        "circle, Phase 9E reports:",
        "",
        "```text",
        "arc displacement   = 7*|dtheta|",
        "chord displacement = 14*sin(|dtheta|/2)",
        "```",
        "",
        "with `dtheta` in radians. For the source plate, the direct Euclidean",
        "endpoint displacement is also reported so radial and angular departure",
        "are not conflated.",
        "",
        "## Interpretation boundary",
        "",
        "Phase 9E is a numerical and visual synthesis of already-frozen results.",
        "It does not establish a new exact construction, a new statistical",
        "significance result, or an independent validation of Figure 14.",
        "",
        "The Phase 9D conclusion remains unchanged: the frozen New Jerusalem",
        "metric/construction vocabulary can host an exact regular heptagon after",
        "one registered cubic-capable angle trisection, while Phase 9B excludes",
        "the exact heptagon from the ordinary Euclidean closure.",
        "",
        "No historical knowledge or intention by Michell or Sommerville follows",
        "from these comparisons.",
        "",
    ]

    return "\n".join(
        lines
    )


def _svg_point(
    x: float,
    y: float,
    *,
    cx: float,
    cy: float,
    scale: float,
) -> tuple[float, float]:
    return (
        cx
        + scale
        * x,
        cy
        - scale
        * y,
    )


def _svg_polyline_points(
    vertices: Sequence[
        tuple[float, float]
    ],
    indices: Sequence[int],
    *,
    cx: float,
    cy: float,
    scale: float,
) -> str:
    points = []

    for index in indices:
        sx, sy = _svg_point(
            *vertices[
                index
            ],
            cx=cx,
            cy=cy,
            scale=scale,
        )

        points.append(
            f"{sx:.6f},{sy:.6f}"
        )

    return " ".join(
        points
    )


def synthesis_to_svg(
    synthesis: ExactHeptagonSynthesis,
) -> str:
    diagram = (
        build_core_geometry(
            unit=1.0
        )
    )

    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    moons = (
        build_ordered_moon_circles(
            diagram,
            ObliqueModel.INCIDENCE,
        )
    )

    exact_vertices = tuple(
        synthesis.exact_vertices
    )

    scaffold_vertices = tuple(
        (
            row.observed_x,
            row.observed_y,
        )
        for row in (
            synthesis.scaffold_vertex_comparisons
        )
    )

    plate_vertices = tuple(
        (
            row.observed_x,
            row.observed_y,
        )
        for row in (
            synthesis.figure14_plate_comparisons
        )
    )

    wall_vertices = tuple(
        (
            vertex.x,
            vertex.y,
        )
        for vertex in (
            composite
            .wall_reconstruction
            .vertices
        )
    )

    traversal = (
        0,
        2,
        4,
        6,
        1,
        3,
        5,
        0,
    )

    width = 1480
    height = 820

    left_cx = 420.0
    left_cy = 420.0
    left_scale = 37.0

    right_origin_x = 1000.0
    right_origin_y = 555.0
    anchor_scale = 62.0

    u = 1.0
    v = 3.0 * sqrt(
        3.0
    )

    theta = atan2(
        v,
        u,
    )

    phi = (
        theta
        / 3.0
    )

    anchor_a = (
        right_origin_x,
        right_origin_y,
    )

    anchor_b = (
        right_origin_x
        + anchor_scale
        * u,
        right_origin_y,
    )

    anchor_c = (
        right_origin_x
        + anchor_scale
        * u,
        right_origin_y
        - anchor_scale
        * v,
    )

    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
        ),
        "<title>v0.9 exact-heptagon synthesis</title>",
        (
            "<desc>Fixed-orientation comparison of the Phase 9D exact "
            "heptagon with the frozen Method-1 scaffold and affine-calibrated "
            "Figure 14 endpoints, with the one-trisection anchor geometry.</desc>"
        ),
        "<style>",
        "text { font-family: sans-serif; fill: #111; }",
        ".title { font-size: 24px; font-weight: 700; }",
        ".subtitle { font-size: 15px; font-weight: 600; }",
        ".label { font-size: 12px; }",
        ".small { font-size: 10px; }",
        ".legend-exact { fill: #111111; font-weight: 600; }",
        ".legend-scaffold { fill: #0072B2; font-weight: 600; }",
        ".legend-plate { fill: #D55E00; font-weight: 600; }",
        ".context { fill: none; stroke: #999; stroke-width: 1.1; }",
        ".wall { fill: none; stroke: #aaa; stroke-width: 1.4; }",
        ".exact { fill: none; stroke: #111111; stroke-width: 1.35; }",
        ".scaffold { fill: none; stroke: #0072B2; stroke-width: 2.2; stroke-dasharray: 12 7; }",
        ".plate { fill: none; stroke: #D55E00; stroke-width: 2.4; stroke-dasharray: 1 6; stroke-linecap: round; }",
        ".exact-point { fill: #fff; stroke: #111111; stroke-width: 1.8; }",
        ".scaffold-point { fill: #0072B2; stroke: #fff; stroke-width: 0.8; }",
        ".plate-point { fill: #fff; stroke: #D55E00; stroke-width: 1.8; }",
        ".moon-centre { fill: #999; stroke: none; }",
        ".junction { fill: #fff; stroke: #999; stroke-width: 1.2; }",
        ".anchor { fill: none; stroke: #111; stroke-width: 2; }",
        ".ray { fill: none; stroke: #666; stroke-width: 1.3; stroke-dasharray: 5 4; }",
        "</style>",
        '<text class="title" x="40" y="42">v0.9 exact-heptagon comparison and one-trisection synthesis</text>',
        '<text class="subtitle" x="40" y="70">Fixed north orientation; no rotational fitting or endpoint reassignment</text>',
        '<text class="subtitle" x="420" y="88" text-anchor="middle">Exact sevenfold within the New Jerusalem architecture</text>',
    ]

    wall_points = (
        _svg_polyline_points(
            wall_vertices,
            tuple(
                range(
                    len(
                        wall_vertices
                    )
                )
            )
            + (
                0,
            ),
            cx=left_cx,
            cy=left_cy,
            scale=left_scale,
        )
    )

    lines.append(
        f'<polyline class="wall" points="{wall_points}" />'
    )

    radius_px = (
        diagram.construction_circle.radius
        * left_scale
    )

    lines.append(
        (
            f'<circle class="context" cx="{left_cx:.6f}" cy="{left_cy:.6f}" '
            f'r="{radius_px:.6f}" />'
        )
    )

    half_side = (
        diagram.earth_square.half_side
    )

    sq_x, sq_y = (
        _svg_point(
            -half_side,
            half_side,
            cx=left_cx,
            cy=left_cy,
            scale=left_scale,
        )
    )

    lines.append(
        (
            f'<rect class="context" x="{sq_x:.6f}" y="{sq_y:.6f}" '
            f'width="{2.0 * half_side * left_scale:.6f}" '
            f'height="{2.0 * half_side * left_scale:.6f}" />'
        )
    )

    for _, moon in moons:
        mx, my = (
            _svg_point(
                moon.centre.x,
                moon.centre.y,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        lines.append(
            (
                f'<circle class="moon-centre" cx="{mx:.6f}" cy="{my:.6f}" '
                'r="2.7" />'
            )
        )

    junction_other = (
        5.0
        * sqrt(
            3.0
        )
        / 2.0
    )

    junction_half = (
        11.0
        / 2.0
    )

    junctions = (
        (
            junction_half,
            junction_other,
        ),
        (
            junction_other,
            junction_half,
        ),
        (
            -junction_other,
            junction_half,
        ),
        (
            -junction_half,
            junction_other,
        ),
        (
            -junction_half,
            -junction_other,
        ),
        (
            -junction_other,
            -junction_half,
        ),
        (
            junction_other,
            -junction_half,
        ),
        (
            junction_half,
            -junction_other,
        ),
    )

    for x, y in junctions:
        sx, sy = (
            _svg_point(
                x,
                y,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        lines.append(
            (
                f'<rect class="junction" x="{sx - 3.0:.6f}" '
                f'y="{sy - 3.0:.6f}" width="6" height="6" />'
            )
        )

    # Draw the exact path first, then the two comparison layers.
    # The three paths are near-coincident, so the dashed and dotted
    # approximations must be painted above the thin exact line.
    for css_class, vertices in (
        (
            "exact",
            exact_vertices,
        ),
        (
            "scaffold",
            scaffold_vertices,
        ),
        (
            "plate",
            plate_vertices,
        ),
    ):
        points = (
            _svg_polyline_points(
                vertices,
                traversal,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        lines.append(
            f'<polyline class="{css_class}" points="{points}" />'
        )

    for index, (
        exact,
        scaffold,
        plate,
    ) in enumerate(
        zip(
            exact_vertices,
            scaffold_vertices,
            plate_vertices,
            strict=True,
        )
    ):
        ex, ey = (
            _svg_point(
                *exact,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        sx, sy = (
            _svg_point(
                *scaffold,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        px, py = (
            _svg_point(
                *plate,
                cx=left_cx,
                cy=left_cy,
                scale=left_scale,
            )
        )

        lines.extend(
            [
                (
                    f'<circle class="exact-point" cx="{ex:.6f}" cy="{ey:.6f}" '
                    'r="5" />'
                ),
                (
                    f'<circle class="scaffold-point" cx="{sx:.6f}" cy="{sy:.6f}" '
                    'r="3.2" />'
                ),
                (
                    f'<circle class="plate-point" cx="{px:.6f}" cy="{py:.6f}" '
                    'r="3.8" />'
                ),
                (
                    f'<text class="small" x="{ex + 7.0:.6f}" '
                    f'y="{ey - 7.0:.6f}">{index}</text>'
                ),
            ]
        )

    lines.extend(
        [
            '<text class="small legend-exact" x="105" y="748">solid: exact {7/2}</text>',
            '<text class="small legend-scaffold" x="275" y="748">dashed: Method-1 scaffold {7/2}</text>',
            '<text class="small legend-plate" x="510" y="748">dotted: affine Figure 14 plate endpoints</text>',
            '<text class="small" x="105" y="766">outer wall / Moon centres / square-circle junctions: context only</text>',
            '<text class="subtitle" x="900" y="105">Native anchor and the single cubic-capable operation</text>',
        ]
    )

    lines.extend(
        [
            (
                f'<line class="anchor" x1="{anchor_a[0]:.6f}" y1="{anchor_a[1]:.6f}" '
                f'x2="{anchor_b[0]:.6f}" y2="{anchor_b[1]:.6f}" />'
            ),
            (
                f'<line class="anchor" x1="{anchor_b[0]:.6f}" y1="{anchor_b[1]:.6f}" '
                f'x2="{anchor_c[0]:.6f}" y2="{anchor_c[1]:.6f}" />'
            ),
            (
                f'<line class="anchor" x1="{anchor_a[0]:.6f}" y1="{anchor_a[1]:.6f}" '
                f'x2="{anchor_c[0]:.6f}" y2="{anchor_c[1]:.6f}" />'
            ),
            (
                f'<text class="label" x="{(anchor_a[0] + anchor_b[0]) / 2:.6f}" '
                f'y="{anchor_a[1] + 22:.6f}">u = 7 - 2×3 = 1</text>'
            ),
            (
                f'<text class="label" x="{anchor_b[0] + 10:.6f}" '
                f'y="{(anchor_b[1] + anchor_c[1]) / 2:.6f}">v = 3√3</text>'
            ),
            (
                f'<text class="label" x="{(anchor_a[0] + anchor_c[0]) / 2 - 95:.6f}" '
                f'y="{(anchor_a[1] + anchor_c[1]) / 2 - 8:.6f}">H = 2√7</text>'
            ),
        ]
    )

    ray_length = (
        155.0
    )

    for multiplier, label in (
        (
            1,
            "φ",
        ),
        (
            2,
            "2φ",
        ),
        (
            3,
            "Θ=3φ",
        ),
    ):
        angle = (
            multiplier
            * phi
        )

        rx = (
            anchor_a[
                0
            ]
            + ray_length
            * cos(
                angle
            )
        )

        ry = (
            anchor_a[
                1
            ]
            - ray_length
            * sin(
                angle
            )
        )

        css_class = (
            "anchor"
            if multiplier == 3
            else "ray"
        )

        lines.append(
            (
                f'<line class="{css_class}" x1="{anchor_a[0]:.6f}" '
                f'y1="{anchor_a[1]:.6f}" x2="{rx:.6f}" y2="{ry:.6f}" />'
            )
        )

        lines.append(
            (
                f'<text class="small" x="{rx + 5.0:.6f}" '
                f'y="{ry:.6f}">{label}</text>'
            )
        )

    lines.extend(
        [
            '<text class="label" x="900" y="615">Exactly one operation: TRISECT_ANGLE(Θ) → φ</text>',
            (
                '<text class="label" x="900" y="640">'
                'z = (2√7/3) cos φ;   y = z − 1/3'
                '</text>'
            ),
            (
                '<text class="label" x="900" y="663">'
                'y³ + y² − 2y − 1 = 0'
                '</text>'
            ),
            (
                '<text class="label" x="900" y="686">'
                'unique root 1&lt;y&lt;2 → y = 2 cos(2π/7)'
                '</text>'
            ),
            (
                '<text class="small" x="900" y="725">'
                f'Method-1 angular RMS vs exact: '
                f'{synthesis.scaffold_aggregate.angular_rms_degrees:.6f}°'
                '</text>'
            ),
            (
                '<text class="small" x="900" y="744">'
                f'Figure 14 plate angular RMS vs exact: '
                f'{synthesis.figure14_plate_aggregate.angular_rms_degrees:.6f}°'
                '</text>'
            ),
            (
                '<text class="small" x="900" y="763">'
                'Source consistency only; no refit and not independent validation.'
                '</text>'
            ),
            "</svg>",
            "",
        ]
    )

    return "\n".join(
        lines
    )
