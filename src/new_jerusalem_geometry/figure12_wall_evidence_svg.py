"""Deterministic Figure 12 outer-wall evidence comparison.

The calibrated source wall is compared with three complete exact NJG_INC
candidate constructions:

- POLAR_PIVOT_TANGENT
- REGULAR_DIRECTION_TANGENT
- RADIAL_SUPPORT

No candidate parameters are fitted to the source wall.

The source-derived wall and Moon measurements come from the fixed Figure 12
affine calibration. The exact candidates all use the same NJG_INC Moon-circle
placement so that only the wall rule changes.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from html import escape
from math import (
    atan2,
    cos,
    degrees,
    pi,
    sin,
    sqrt,
)
from pathlib import Path
from typing import Sequence

from .core_geometry import (
    CoreDiagram,
    build_core_geometry,
)
from .figure12_source_geometry import (
    Figure12SourceGeometryReport,
    derive_figure12_source_geometry,
)
from .model_variants import ObliqueModel
from .polar_pivot_wall import (
    build_polar_pivot_tangent_wall,
)
from .primitives import Point2D
from .wall_geometry import (
    OuterWall,
    WallLine,
    build_ordered_moon_circles,
    build_radial_support_wall,
)


POLAR_PIVOT_TANGENT = "POLAR_PIVOT_TANGENT"
REGULAR_DIRECTION_TANGENT = "REGULAR_DIRECTION_TANGENT"
RADIAL_SUPPORT = "RADIAL_SUPPORT"


CANDIDATE_ORDER = (
    POLAR_PIVOT_TANGENT,
    REGULAR_DIRECTION_TANGENT,
    RADIAL_SUPPORT,
)


SEMANTIC_WALL_IDS = (
    "wall_east",
    "wall_east_north",
    "wall_north_east",
    "wall_north",
    "wall_north_west",
    "wall_west_north",
    "wall_west",
    "wall_west_south",
    "wall_south_west",
    "wall_south",
    "wall_south_east",
    "wall_east_south",
)


@dataclass(frozen=True, slots=True)
class ExactWallCandidateFit:
    candidate: str
    angle_rms_degrees: float
    angle_maximum_degrees: float
    support_rms_u: float
    support_maximum_u: float


@dataclass(frozen=True, slots=True)
class Figure12WallEvidenceReport:
    source_geometry: Figure12SourceGeometryReport
    fits: tuple[ExactWallCandidateFit, ...]
    candidates: tuple[
        tuple[str, OuterWall],
        ...,
    ]


def _format_number(
    value: float,
) -> str:
    if abs(value) < 5.0e-15:
        value = 0.0

    return format(
        value,
        ".12g",
    )


def _rms(
    values: Sequence[float],
) -> float:
    return sqrt(
        sum(
            value * value
            for value in values
        )
        / len(values)
    )


def _angle_degrees(
    line: WallLine,
) -> float:
    return (
        degrees(
            atan2(
                line.normal.y,
                line.normal.x,
            )
        )
        % 360.0
    )


def _angular_delta(
    observed: float,
    expected: float,
) -> float:
    return (
        (
            observed
            - expected
            + 180.0
        )
        % 360.0
        - 180.0
    )


def _intersection(
    first: WallLine,
    second: WallLine,
) -> Point2D:
    determinant = (
        first.normal.x
        * second.normal.y
        - first.normal.y
        * second.normal.x
    )

    if abs(
        determinant
    ) <= 1.0e-15:
        raise ValueError(
            "Adjacent wall lines are parallel."
        )

    x = (
        first.offset
        * second.normal.y
        - first.normal.y
        * second.offset
    ) / determinant

    y = (
        first.normal.x
        * second.offset
        - first.offset
        * second.normal.x
    ) / determinant

    return Point2D(
        x,
        y,
    )


def build_regular_direction_tangent_wall(
    diagram: CoreDiagram,
) -> OuterWall:
    """Return the exact NJG_INC regular-direction tangent candidate."""

    moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    lines: list[
        WallLine
    ] = []

    for index, (
        moon_name,
        moon,
    ) in enumerate(
        moons
    ):
        angle = (
            index
            * pi
            / 6.0
        )

        normal = Point2D(
            cos(angle),
            sin(angle),
        )

        offset = (
            normal.x
            * moon.centre.x
            + normal.y
            * moon.centre.y
            + moon.radius
        )

        tangency_point = Point2D(
            moon.centre.x
            + moon.radius
            * normal.x,
            moon.centre.y
            + moon.radius
            * normal.y,
        )

        lines.append(
            WallLine(
                name=SEMANTIC_WALL_IDS[
                    index
                ],
                moon_name=moon_name,
                normal=normal,
                offset=offset,
                tangency_point=(
                    tangency_point
                ),
            )
        )

    vertices = tuple(
        _intersection(
            lines[index],
            lines[
                (
                    index
                    + 1
                )
                % len(lines)
            ],
        )
        for index
        in range(
            len(lines)
        )
    )

    return OuterWall(
        model=ObliqueModel.INCIDENCE,
        moons=moons,
        lines=tuple(
            lines
        ),
        vertices=vertices,
    )


def _semantic_candidate_lines(
    candidate: str,
    wall: OuterWall,
) -> dict[str, WallLine]:
    if len(
        wall.lines
    ) != 12:
        raise ValueError(
            f"{candidate} does not contain twelve wall lines."
        )

    if candidate == RADIAL_SUPPORT:
        return {
            wall_id: line
            for wall_id, line
            in zip(
                SEMANTIC_WALL_IDS,
                wall.lines,
                strict=True,
            )
        }

    return {
        line.name: line
        for line
        in wall.lines
    }


def _candidate_fit(
    *,
    candidate: str,
    wall: OuterWall,
    source: Figure12SourceGeometryReport,
) -> ExactWallCandidateFit:
    observed = {
        row.wall_id: row
        for row
        in source.walls
    }

    predicted = (
        _semantic_candidate_lines(
            candidate,
            wall,
        )
    )

    if (
        set(observed)
        != set(
            SEMANTIC_WALL_IDS
        )
    ):
        raise ValueError(
            "Source wall identifiers do not match "
            "the expected twelve-side schema."
        )

    if (
        set(predicted)
        != set(
            SEMANTIC_WALL_IDS
        )
    ):
        raise ValueError(
            f"{candidate} wall identifiers are incomplete."
        )

    angle_residuals = []
    support_residuals = []

    for wall_id in SEMANTIC_WALL_IDS:
        source_row = observed[
            wall_id
        ]

        candidate_line = predicted[
            wall_id
        ]

        angle_residuals.append(
            _angular_delta(
                source_row.normal_angle_degrees,
                _angle_degrees(
                    candidate_line
                ),
            )
        )

        support_residuals.append(
            source_row.support_h_u
            - candidate_line.offset
        )

    return ExactWallCandidateFit(
        candidate=candidate,
        angle_rms_degrees=_rms(
            angle_residuals
        ),
        angle_maximum_degrees=max(
            abs(value)
            for value
            in angle_residuals
        ),
        support_rms_u=_rms(
            support_residuals
        ),
        support_maximum_u=max(
            abs(value)
            for value
            in support_residuals
        ),
    )


def analyze_figure12_wall_evidence(
    pass_paths: Sequence[
        str | Path
    ],
) -> Figure12WallEvidenceReport:
    """Build and compare the three exact wall candidates."""

    source = (
        derive_figure12_source_geometry(
            pass_paths
        )
    )

    diagram = build_core_geometry()

    polar = (
        build_polar_pivot_tangent_wall(
            diagram,
            ObliqueModel.INCIDENCE,
        )
    )

    regular = (
        build_regular_direction_tangent_wall(
            diagram
        )
    )

    radial = (
        build_radial_support_wall(
            diagram,
            ObliqueModel.INCIDENCE,
        )
    )

    candidates = (
        (
            POLAR_PIVOT_TANGENT,
            polar,
        ),
        (
            REGULAR_DIRECTION_TANGENT,
            regular,
        ),
        (
            RADIAL_SUPPORT,
            radial,
        ),
    )

    fits = tuple(
        _candidate_fit(
            candidate=name,
            wall=wall,
            source=source,
        )
        for name, wall
        in candidates
    )

    return Figure12WallEvidenceReport(
        source_geometry=source,
        fits=fits,
        candidates=candidates,
    )


def _source_wall_vertices(
    source: Figure12SourceGeometryReport,
) -> tuple[Point2D, ...]:
    by_id = {
        row.wall_id: row
        for row
        in source.walls
    }

    lines = []

    for wall_id in SEMANTIC_WALL_IDS:
        row = by_id[
            wall_id
        ]

        normal = Point2D(
            row.normal_x,
            row.normal_y,
        )

        tangency_placeholder = Point2D(
            row.support_h_u
            * row.normal_x,
            row.support_h_u
            * row.normal_y,
        )

        lines.append(
            WallLine(
                name=wall_id,
                moon_name="source",
                normal=normal,
                offset=(
                    row.support_h_u
                ),
                tangency_point=(
                    tangency_placeholder
                ),
            )
        )

    return tuple(
        _intersection(
            lines[index],
            lines[
                (
                    index
                    + 1
                )
                % len(lines)
            ],
        )
        for index
        in range(
            len(lines)
        )
    )


def _polygon_points(
    vertices: Sequence[
        Point2D
    ],
) -> str:
    return " ".join(
        (
            f"{_format_number(point.x)},"
            f"{_format_number(point.y)}"
        )
        for point in vertices
    )


def figure12_wall_evidence_to_svg(
    report: Figure12WallEvidenceReport,
    *,
    canvas_width: int = 1800,
    canvas_height: int = 900,
    title: str = (
        "Figure 12 outer-wall evidence comparison"
    ),
) -> str:
    """Return a deterministic three-panel SVG."""

    if canvas_width < 1500:
        raise ValueError(
            "canvas_width must be at least 1500."
        )

    if canvas_height < 800:
        raise ValueError(
            "canvas_height must be at least 800."
        )

    diagram = build_core_geometry()

    source_vertices = (
        _source_wall_vertices(
            report.source_geometry
        )
    )

    source_points = (
        _polygon_points(
            source_vertices
        )
    )

    fit_by_candidate = {
        fit.candidate: fit
        for fit
        in report.fits
    }

    wall_by_candidate = {
        name: wall
        for name, wall
        in report.candidates
    }

    panel_width = (
        canvas_width
        / 3.0
    )

    plot_center_y = 390.0
    scale = 27.0

    lines = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{canvas_width}" '
            f'height="{canvas_height}" '
            f'viewBox="0 0 {canvas_width} {canvas_height}">'
        ),
        f"  <title>{escape(title)}</title>",
        (
            "  <desc>"
            "Affine-calibrated Figure 12 wall compared with three "
            "fixed exact NJG_INC wall constructions. No candidate "
            "parameters are fitted to the source wall."
            "</desc>"
        ),
        "  <metadata>",
        "    Project: New Jerusalem Geometry",
        "    Source: City of Revelation, Figure 12",
        "    Registration: centroid affine",
        "    Moon model: NJG_INC",
        "    Preferred wall reconstruction: POLAR_PIVOT_TANGENT",
        "  </metadata>",
        "  <style>",
        "    text { font-family: sans-serif; fill: #111; }",
        (
            "    .title { font-size: 27px; font-weight: 700; "
            "text-anchor: middle; }"
        ),
        (
            "    .subtitle { font-size: 15px; "
            "text-anchor: middle; fill: #444; }"
        ),
        (
            "    .panel-title { font-size: 17px; "
            "font-weight: 700; text-anchor: middle; }"
        ),
        (
            "    .panel-status { font-size: 13px; "
            "text-anchor: middle; fill: #555; }"
        ),
        (
            "    .metric { font-size: 13px; "
            "text-anchor: middle; fill: #222; }"
        ),
        (
            "    .geometry { fill: none; }"
        ),
        (
            "    .construction-circle { stroke: #c7c7c7; "
            "stroke-width: 0.040741; }"
        ),
        (
            "    .earth-circle { stroke: #aaa; "
            "stroke-width: 0.037037; }"
        ),
        (
            "    .earth-square { stroke: #aaa; "
            "stroke-width: 0.037037; }"
        ),
        (
            "    .moon-circle { stroke: #aaa; "
            "stroke-width: 0.033333; }"
        ),
        (
            "    .source-wall { stroke: #111; "
            "stroke-width: 0.081481; "
            "stroke-dasharray: 0.259259 0.185185; "
            "fill: none; }"
        ),
        (
            "    .candidate-wall { stroke: #3867a8; "
            "stroke-width: 0.111111; fill: none; }"
        ),
        (
            "    .source-moon-centre { fill: #111; "
            "stroke: none; }"
        ),
        (
            "    .panel-rule { stroke: #ddd; "
            "stroke-width: 1; }"
        ),
        (
            "    .legend { font-size: 13px; "
            "fill: #333; }"
        ),
        (
            "    .footnote { font-size: 12px; "
            "fill: #555; text-anchor: middle; }"
        ),
        "  </style>",
        (
            f'  <text class="title" '
            f'x="{canvas_width / 2:.6g}" y="36">'
            f"{escape(title)}</text>"
        ),
        (
            f'  <text class="subtitle" '
            f'x="{canvas_width / 2:.6g}" y="62">'
            "Dashed = affine-calibrated Figure 12 wall; "
            "solid = fixed exact NJG_INC candidate"
            "</text>"
        ),
    ]

    for separator in (
        panel_width,
        2.0 * panel_width,
    ):
        lines.append(
            (
                f'  <line class="panel-rule" '
                f'x1="{separator:.6g}" y1="86" '
                f'x2="{separator:.6g}" y2="785" />'
            )
        )

    panel_status = {
        POLAR_PIVOT_TANGENT: (
            "preferred combined reconstruction"
        ),
        REGULAR_DIRECTION_TANGENT: (
            "intermediate comparison"
        ),
        RADIAL_SUPPORT: (
            "historical project inference"
        ),
    }

    panel_label = {
        POLAR_PIVOT_TANGENT: (
            "Polar-pivot tangent"
        ),
        REGULAR_DIRECTION_TANGENT: (
            "Regular-direction tangent"
        ),
        RADIAL_SUPPORT: (
            "Radial support"
        ),
    }

    source_moons = (
        report.source_geometry.moons
    )

    for panel_index, candidate in enumerate(
        CANDIDATE_ORDER
    ):
        wall = wall_by_candidate[
            candidate
        ]

        fit = fit_by_candidate[
            candidate
        ]

        center_x = (
            panel_width
            * (
                panel_index
                + 0.5
            )
        )

        candidate_points = (
            _polygon_points(
                wall.vertices
            )
        )

        lines.extend(
            [
                (
                    f'  <g id="panel-{panel_index + 1}" '
                    f'data-candidate="{candidate}">'
                ),
                (
                    f'    <text class="panel-title" '
                    f'x="{center_x:.6g}" y="105">'
                    f"{escape(panel_label[candidate])}"
                    "</text>"
                ),
                (
                    f'    <text class="panel-status" '
                    f'x="{center_x:.6g}" y="128">'
                    f"{escape(panel_status[candidate])}"
                    "</text>"
                ),
                (
                    f'    <g id="geometry-{panel_index + 1}" '
                    f'transform="translate('
                    f'{center_x:.12g},{plot_center_y:.12g}) '
                    f'scale({scale:.12g},-{scale:.12g})">'
                ),
                (
                    '      <circle class="geometry construction-circle" '
                    f'cx="{_format_number(diagram.construction_circle.centre.x)}" '
                    f'cy="{_format_number(diagram.construction_circle.centre.y)}" '
                    f'r="{_format_number(diagram.construction_circle.radius)}" />'
                ),
                (
                    '      <circle class="geometry earth-circle" '
                    f'cx="{_format_number(diagram.earth_circle.centre.x)}" '
                    f'cy="{_format_number(diagram.earth_circle.centre.y)}" '
                    f'r="{_format_number(diagram.earth_circle.radius)}" />'
                ),
                (
                    '      <rect class="geometry earth-square" '
                    f'x="{_format_number(-diagram.earth_square.half_side)}" '
                    f'y="{_format_number(-diagram.earth_square.half_side)}" '
                    f'width="{_format_number(2.0 * diagram.earth_square.half_side)}" '
                    f'height="{_format_number(2.0 * diagram.earth_square.half_side)}" />'
                ),
            ]
        )

        for moon_name, moon in wall.moons:
            lines.append(
                (
                    f'      <circle class="geometry moon-circle" '
                    f'data-moon="{escape(moon_name)}" '
                    f'cx="{_format_number(moon.centre.x)}" '
                    f'cy="{_format_number(moon.centre.y)}" '
                    f'r="{_format_number(moon.radius)}" />'
                )
            )

        lines.append(
            (
                '      <polygon class="candidate-wall" '
                f'points="{candidate_points}" />'
            )
        )

        lines.append(
            (
                '      <polygon class="source-wall" '
                f'points="{source_points}" />'
            )
        )

        for moon in source_moons:
            lines.append(
                (
                    '      <circle class="source-moon-centre" '
                    f'cx="{_format_number(moon.centre_x_u)}" '
                    f'cy="{_format_number(moon.centre_y_u)}" '
                    'r="0.055" />'
                )
            )

        lines.extend(
            [
                "    </g>",
                (
                    f'    <text class="metric" '
                    f'x="{center_x:.6g}" y="674">'
                    f"Angle RMS = "
                    f"{fit.angle_rms_degrees:.6f}°"
                    "</text>"
                ),
                (
                    f'    <text class="metric" '
                    f'x="{center_x:.6g}" y="697">'
                    f"Support RMS = "
                    f"{fit.support_rms_u:.6f} u"
                    "</text>"
                ),
                (
                    f'    <text class="metric" '
                    f'x="{center_x:.6g}" y="720">'
                    f"Angle max = "
                    f"{fit.angle_maximum_degrees:.6f}°"
                    "</text>"
                ),
                (
                    f'    <text class="metric" '
                    f'x="{center_x:.6g}" y="743">'
                    f"Support max = "
                    f"{fit.support_maximum_u:.6f} u"
                    "</text>"
                ),
                "  </g>",
            ]
        )

    lines.extend(
        [
            (
                f'  <text class="legend" x="55" y="816">'
                "Dashed polygon: source-plate wall"
                "</text>"
            ),
            (
                f'  <text class="legend" x="355" y="816">'
                "Solid polygon: exact candidate"
                "</text>"
            ),
            (
                f'  <text class="legend" x="650" y="816">'
                "Dots: source-derived Moon centres"
                "</text>"
            ),
            (
                f'  <text class="footnote" '
                f'x="{canvas_width / 2:.6g}" y="851">'
                "No candidate translation, rotation, scale, "
                "wall angle, or support position is fitted."
                "</text>"
            ),
            (
                f'  <text class="footnote" '
                f'x="{canvas_width / 2:.6g}" y="873">'
                "Polar-pivot is preferred by wall-direction and "
                "historical-dimensional evidence; support-distance "
                "evidence is retained separately."
                "</text>"
            ),
            "</svg>",
        ]
    )

    return "\n".join(
        lines
    )


def write_figure12_wall_evidence_svg(
    report: Figure12WallEvidenceReport,
    output_path: str | Path,
    *,
    canvas_width: int = 1800,
    canvas_height: int = 900,
) -> Path:
    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        figure12_wall_evidence_to_svg(
            report,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        ),
        encoding="utf-8",
    )

    return path


def write_figure12_wall_evidence_json(
    report: Figure12WallEvidenceReport,
    output_path: str | Path,
) -> Path:
    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure12-complete-exact-wall-comparison-v1"
        ),
        "moon_model": "NJG_INC",
        "candidate_parameters_fitted": False,
        "preferred_combined_reconstruction": (
            POLAR_PIVOT_TANGENT
        ),
        "fits": [
            asdict(
                fit
            )
            for fit
            in report.fits
        ],
        "interpretation_boundary": (
            "POLAR_PIVOT_TANGENT has the lowest source-wall "
            "angle RMS. RADIAL_SUPPORT has the lowest exact-model "
            "support-distance RMS. Historical dimensional evidence "
            "independently favors POLAR_PIVOT_TANGENT. The preferred "
            "construction remains a source-supported project "
            "reconstruction rather than an explicitly stated "
            "historical algorithm."
        ),
    }

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return path
