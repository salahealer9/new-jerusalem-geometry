"""Deterministic SVG visualisation of the inferred Michell outer wall.

The wall itself is a project inference:

- one outward radial support tangent is assigned to each Moon circle;
- consecutive support tangents intersect to form twelve vertices.

The source-supported geometry is the exact-incidence placement of the
twelve Moon circles described by Michell.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import build_oblique_placement
from .wall_geometry import OuterWall, build_radial_support_wall
from .wall_verification import verify_outer_wall


SVG_NAMESPACE = "http://www.w3.org/2000/svg"

MICHELL_MEAN_SIDE_FEET = 3264.0
MICHELL_PERIMETER_MY = 14400.0
MICHELL_AREA_SQUARE_FEET = 120_000_000.0
FEET_PER_MY = 2.72


def _format_number(value: float) -> str:
    """Return a compact deterministic decimal representation."""

    if abs(value) < 1.0e-15:
        return "0"

    return format(value, ".12g")


def _screen_point(
    x: float,
    y: float,
    *,
    centre_x: float,
    centre_y: float,
    scale: float,
) -> tuple[float, float]:
    """Convert mathematical coordinates to SVG screen coordinates."""

    return (
        centre_x + scale * x,
        centre_y - scale * y,
    )


def _side_class(
    length: float,
    *,
    short_length: float,
    long_length: float,
) -> str:
    """Classify one wall side as short or long."""

    if abs(length - short_length) <= abs(length - long_length):
        return "short"

    return "long"


def michell_outer_wall_to_svg(
    diagram: CoreDiagram,
    wall: OuterWall | None = None,
    *,
    canvas_width: int = 1200,
    canvas_height: int = 900,
    unit_feet: float = 720.0,
    title: str = "Inferred Michell outer wall",
) -> str:
    """Return a deterministic source-comparison SVG."""

    if canvas_width < 1000:
        raise ValueError("Wall SVG width must be at least 1000 px.")

    if canvas_height < 700:
        raise ValueError("Wall SVG height must be at least 700 px.")

    if unit_feet <= 0.0:
        raise ValueError("unit_feet must be positive.")

    if wall is None:
        wall = build_radial_support_wall(
            diagram,
            ObliqueModel.INCIDENCE,
        )

    report = verify_outer_wall(diagram, wall)

    if not report.passed:
        raise ValueError(
            "Cannot render an outer wall that fails verification."
        )

    placement = build_oblique_placement(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    plot_left = 30.0
    plot_width = 790.0
    information_left = 850.0
    information_width = canvas_width - information_left - 30.0

    centre_x = plot_left + plot_width / 2.0
    centre_y = canvas_height / 2.0 + 10.0

    maximum_coordinate = max(
        max(abs(vertex.x), abs(vertex.y))
        for vertex in wall.vertices
    )

    geometry_extent = maximum_coordinate + 0.8

    scale = min(
        (plot_width - 80.0) / (2.0 * geometry_extent),
        (canvas_height - 110.0) / (2.0 * geometry_extent),
    )

    side_lengths = report.side_lengths
    short_length = min(side_lengths)
    long_length = max(side_lengths)

    short_count = sum(
        _side_class(
            length,
            short_length=short_length,
            long_length=long_length,
        )
        == "short"
        for length in side_lengths
    )

    long_count = len(side_lengths) - short_count

    mean_side_feet = report.mean_side_length * unit_feet
    perimeter_feet = report.perimeter * unit_feet
    perimeter_my = perimeter_feet / FEET_PER_MY
    area_square_feet = report.area * unit_feet**2

    mean_difference_percent = (
        100.0
        * (mean_side_feet - MICHELL_MEAN_SIDE_FEET)
        / MICHELL_MEAN_SIDE_FEET
    )

    perimeter_difference_percent = (
        100.0
        * (perimeter_my - MICHELL_PERIMETER_MY)
        / MICHELL_PERIMETER_MY
    )

    area_difference_percent = (
        100.0
        * (
            area_square_feet
            - MICHELL_AREA_SQUARE_FEET
        )
        / MICHELL_AREA_SQUARE_FEET
    )

    square_half_side = diagram.earth_square.half_side

    wall_points = " ".join(
        (
            f"{_format_number(vertex.x)},"
            f"{_format_number(vertex.y)}"
        )
        for vertex in wall.vertices
    )

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="{SVG_NAMESPACE}" '
            f'width="{canvas_width}" '
            f'height="{canvas_height}" '
            f'viewBox="0 0 {canvas_width} {canvas_height}" '
            'preserveAspectRatio="xMidYMid meet" '
            'role="img" '
            'shape-rendering="geometricPrecision">'
        ),
        f"  <title>{escape(title)}</title>",
        (
            "  <desc>"
            "Source-supported exact-incidence Moon placement with the "
            "project's inferred radial-support outer wall, compared with "
            "the approximate dimensions reported by John Michell."
            "</desc>"
        ),
        "  <metadata>",
        "    Project: New Jerusalem Geometry",
        "    Geometry model: NJG_INC",
        "    Wall model: inferred radial support tangents",
        "    Source figure: City of Revelation, Figure 12",
        "  </metadata>",
        "  <style>",
        "    text {",
        "      font-family: system-ui, sans-serif;",
        "      fill: #171717;",
        "    }",
        "    .title {",
        "      font-size: 25px;",
        "      font-weight: 600;",
        "      text-anchor: middle;",
        "    }",
        "    .subtitle {",
        "      font-size: 14px;",
        "      text-anchor: middle;",
        "      fill: #555555;",
        "    }",
        "    .geometry {",
        "      fill: none;",
        "      vector-effect: non-scaling-stroke;",
        "      stroke-linecap: round;",
        "      stroke-linejoin: round;",
        "    }",
        "    .wall-fill {",
        "      fill: #eef3f8;",
        "      fill-opacity: 0.55;",
        "      stroke: none;",
        "    }",
        "    .wall-outline {",
        "      stroke: #0d3658;",
        "      stroke-width: 2.3;",
        "    }",
        "    .construction-circle {",
        "      stroke: #8b8b8b;",
        "      stroke-width: 1.2;",
        "      stroke-dasharray: 6 5;",
        "    }",
        "    .earth-square {",
        "      stroke: #333333;",
        "      stroke-width: 1.4;",
        "    }",
        "    .earth-circle {",
        "      stroke: #111111;",
        "      stroke-width: 1.8;",
        "    }",
        "    .moon-circle {",
        "      stroke: #555555;",
        "      stroke-width: 1.3;",
        "      fill: #ffffff;",
        "      fill-opacity: 0.58;",
        "    }",
        "    .support-guide {",
        "      stroke: #1769aa;",
        "      stroke-width: 0.9;",
        "      stroke-dasharray: 3 3;",
        "      opacity: 0.65;",
        "    }",
        "    .incidence-point {",
        "      fill: #111111;",
        "      stroke: none;",
        "    }",
        "    .tangency-point {",
        "      fill: #1769aa;",
        "      stroke: #ffffff;",
        "      stroke-width: 0.025;",
        "      vector-effect: non-scaling-stroke;",
        "    }",
        "    .side-label {",
        "      font-size: 12px;",
        "      font-weight: 700;",
        "      text-anchor: middle;",
        "      dominant-baseline: central;",
        "    }",
        "    .side-label-short {",
        "      fill: #9a4f00;",
        "    }",
        "    .side-label-long {",
        "      fill: #0d5f45;",
        "    }",
        "    .panel-rule {",
        "      stroke: #d0d0d0;",
        "      stroke-width: 1;",
        "    }",
        "    .panel-heading {",
        "      font-size: 17px;",
        "      font-weight: 600;",
        "    }",
        "    .metric-label {",
        "      font-size: 13px;",
        "      fill: #555555;",
        "    }",
        "    .metric-value {",
        "      font-size: 15px;",
        "      font-weight: 600;",
        "    }",
        "    .comparison-value {",
        "      font-size: 13px;",
        "    }",
        "    .note {",
        "      font-size: 12px;",
        "      fill: #555555;",
        "    }",
        "    .status-box {",
        "      fill: #f4f7fa;",
        "      stroke: #cad4de;",
        "      stroke-width: 1;",
        "    }",
        "  </style>",
        (
            f'  <text class="title" '
            f'x="{canvas_width / 2:.6g}" y="31">'
            f"{escape(title)}</text>"
        ),
        (
            f'  <text class="subtitle" '
            f'x="{canvas_width / 2:.6g}" y="53">'
            "Exact-incidence Moon placement with inferred radial "
            "support tangents"
            "</text>"
        ),
        (
            f'  <line class="panel-rule" '
            f'x1="{information_left - 18:.6g}" y1="72" '
            f'x2="{information_left - 18:.6g}" '
            f'y2="{canvas_height - 32}" />'
        ),
        (
            f'  <g id="wall-geometry" '
            f'transform="translate('
            f'{_format_number(centre_x)} '
            f'{_format_number(centre_y)}) '
            f'scale({_format_number(scale)},'
            f'-{_format_number(scale)})">'
        ),
        (
            f'    <polygon class="wall-fill" '
            f'points="{wall_points}" />'
        ),
        (
            '    <circle class="geometry construction-circle" '
            f'cx="{_format_number(diagram.construction_circle.centre.x)}" '
            f'cy="{_format_number(diagram.construction_circle.centre.y)}" '
            f'r="{_format_number(diagram.construction_circle.radius)}" />'
        ),
        (
            '    <rect class="geometry earth-square" '
            f'x="{_format_number(-square_half_side)}" '
            f'y="{_format_number(-square_half_side)}" '
            f'width="{_format_number(diagram.earth_square.side)}" '
            f'height="{_format_number(diagram.earth_square.side)}" />'
        ),
        (
            '    <circle class="geometry earth-circle" '
            f'cx="{_format_number(diagram.earth_circle.centre.x)}" '
            f'cy="{_format_number(diagram.earth_circle.centre.y)}" '
            f'r="{_format_number(diagram.earth_circle.radius)}" />'
        ),
    ]

    for moon_name, moon in wall.moons:
        lines.append(
            (
                f'    <circle id="{escape(moon_name)}" '
                'class="geometry moon-circle" '
                f'cx="{_format_number(moon.centre.x)}" '
                f'cy="{_format_number(moon.centre.y)}" '
                f'r="{_format_number(moon.radius)}" />'
            )
        )

    for moon in placement.moons:
        target = moon.target_intersection.point

        lines.append(
            (
                '    <circle class="incidence-point" '
                f'cx="{_format_number(target.x)}" '
                f'cy="{_format_number(target.y)}" '
                'r="0.075" />'
            )
        )

    moon_lookup = dict(wall.moons)

    for line in wall.lines:
        moon = moon_lookup[line.moon_name]

        lines.extend(
            [
                (
                    '    <line class="geometry support-guide" '
                    f'x1="{_format_number(moon.centre.x)}" '
                    f'y1="{_format_number(moon.centre.y)}" '
                    f'x2="{_format_number(line.tangency_point.x)}" '
                    f'y2="{_format_number(line.tangency_point.y)}" />'
                ),
                (
                    '    <circle class="tangency-point" '
                    f'cx="{_format_number(line.tangency_point.x)}" '
                    f'cy="{_format_number(line.tangency_point.y)}" '
                    'r="0.095" />'
                ),
            ]
        )

    lines.extend(
        [
            (
                f'    <polygon class="geometry wall-outline" '
                f'points="{wall_points}" />'
            ),
            "  </g>",
            '  <g id="side-class-labels">',
        ]
    )

    for index, length in enumerate(side_lengths):
        start, end = wall.side_endpoints(index)
        wall_line = wall.lines[index]

        midpoint_x = (start.x + end.x) / 2.0
        midpoint_y = (start.y + end.y) / 2.0

        label_x = midpoint_x + 0.34 * wall_line.normal.x
        label_y = midpoint_y + 0.34 * wall_line.normal.y

        screen_x, screen_y = _screen_point(
            label_x,
            label_y,
            centre_x=centre_x,
            centre_y=centre_y,
            scale=scale,
        )

        classification = _side_class(
            length,
            short_length=short_length,
            long_length=long_length,
        )

        symbol = "S" if classification == "short" else "L"

        lines.append(
            (
                f'    <text class="side-label '
                f'side-label-{classification}" '
                f'data-side-index="{index}" '
                f'data-side-class="{classification}" '
                f'x="{_format_number(screen_x)}" '
                f'y="{_format_number(screen_y)}">'
                f"{symbol}</text>"
            )
        )

    panel_x = information_left
    panel_right = information_left + information_width

    lines.extend(
        [
            "  </g>",
            (
                f'  <g id="information-panel" '
                f'transform="translate({_format_number(panel_x)} 92)">'
            ),
            '    <text class="panel-heading" x="0" y="0">'
            "Geometric reconstruction</text>",
            '    <text class="metric-label" x="0" y="31">'
            "Model</text>",
            '    <text class="metric-value" x="0" y="51">'
            "NJG_INC + radial support wall</text>",
            '    <text class="metric-label" x="0" y="82">'
            "Verification</text>",
            '    <text class="metric-value" x="0" y="102">'
            "PASS</text>",
            '    <text class="metric-label" x="0" y="133">'
            "Wall structure</text>",
            (
                '    <text class="metric-value" x="0" y="153">'
                f"{short_count} short + {long_count} long sides"
                "</text>"
            ),
            '    <text class="metric-label" x="0" y="184">'
            "Short side</text>",
            (
                '    <text class="metric-value" x="0" y="204">'
                f"{short_length:.9f} u"
                "</text>"
            ),
            '    <text class="metric-label" x="0" y="235">'
            "Long side</text>",
            (
                '    <text class="metric-value" x="0" y="255">'
                f"{long_length:.9f} u"
                "</text>"
            ),
            (
                f'    <line class="panel-rule" '
                f'x1="0" y1="281" '
                f'x2="{_format_number(information_width)}" y2="281" />'
            ),
            '    <text class="panel-heading" x="0" y="313">'
            "Comparison with Michell</text>",
            '    <text class="metric-label" x="0" y="344">'
            "Mean side</text>",
            (
                '    <text class="comparison-value" x="0" y="364">'
                f"Computed: {mean_side_feet:.3f} ft"
                "</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="384">'
                f"Michell: {MICHELL_MEAN_SIDE_FEET:.0f} ft"
                "</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="404">'
                f"Difference: {mean_difference_percent:+.3f}%"
                "</text>"
            ),
            '    <text class="metric-label" x="0" y="439">'
            "Perimeter</text>",
            (
                '    <text class="comparison-value" x="0" y="459">'
                f"Computed: {perimeter_my:.3f} MY"
                "</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="479">'
                f"Michell: {MICHELL_PERIMETER_MY:.0f} MY"
                "</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="499">'
                f"Difference: {perimeter_difference_percent:+.3f}%"
                "</text>"
            ),
            '    <text class="metric-label" x="0" y="534">'
            "Area</text>",
            (
                '    <text class="comparison-value" x="0" y="554">'
                f"Computed: {area_square_feet / 1_000_000:.3f} million ft²"
                "</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="574">'
                f"Michell: {MICHELL_AREA_SQUARE_FEET / 1_000_000:.0f} "
                "million ft²</text>"
            ),
            (
                '    <text class="comparison-value" x="0" y="594">'
                f"Difference: {area_difference_percent:+.3f}%"
                "</text>"
            ),
            (
                f'    <rect class="status-box" x="0" y="625" '
                f'width="{_format_number(information_width)}" '
                'height="104" rx="8" />'
            ),
            '    <text class="note" x="14" y="650">'
            "Source status:</text>",
            '    <text class="note" x="14" y="672">'
            "Moon placement is source-supported.</text>",
            '    <text class="note" x="14" y="694">'
            "The radial support-wall algorithm is</text>",
            '    <text class="note" x="14" y="716">'
            "a tested project inference.</text>",
            "  </g>",
            (
                f'  <text class="note" '
                f'x="{_format_number(plot_left + 6)}" '
                f'y="{canvas_height - 19}">'
                "S = short side; L = long side; blue points = "
                "wall tangencies; black points = square-circle incidences"
                "</text>"
            ),
            (
                f'  <text class="note" text-anchor="end" '
                f'x="{_format_number(panel_right)}" '
                f'y="{canvas_height - 19}">'
                "Scale-free Euclidean reconstruction"
                "</text>"
            ),
            "</svg>",
            "",
        ]
    )

    return "\n".join(lines)


def write_michell_outer_wall_svg(
    diagram: CoreDiagram,
    output_path: str | Path,
    wall: OuterWall | None = None,
    *,
    canvas_width: int = 1200,
    canvas_height: int = 900,
    unit_feet: float = 720.0,
) -> Path:
    """Write the deterministic wall comparison SVG."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        michell_outer_wall_to_svg(
            diagram,
            wall,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            unit_feet=unit_feet,
        ),
        encoding="utf-8",
    )

    return path
