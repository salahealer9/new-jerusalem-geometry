"""Deterministic comparison SVG for Michell's Figure 14 heptagram.

The SVG compares three vertex systems:

- an exact regular {7/3} heptagram;
- a {7/3} heptagram selected from Michell's approximate 28-point scaffold;
- a Figure-14-aligned {7/3} heptagram built from the seven stated and
  inferred endpoint constraints.

The SVG is a computational reconstruction, not a facsimile of Michell's
printed plate. Its background is intentionally transparent.
"""

from __future__ import annotations

from html import escape
from pathlib import Path
from statistics import mean, pstdev

from .core_geometry import CoreDiagram
from .heptagram_geometry import (
    AnchorEvidence,
    Figure14Anchor,
    HeptagramGeometry,
    build_figure14_aligned_heptagram,
    build_figure14_anchor_set,
    build_regular_heptagram,
    build_scaffold_heptagram,
)
from .heptagram_verification import (
    HeptagramFit,
    verify_figure14_heptagrams,
)
from .model_variants import ObliqueModel
from .wall_geometry import build_ordered_moon_circles


SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def _format_number(value: float) -> str:
    """Return a compact deterministic decimal representation."""

    if abs(value) < 1.0e-15:
        return "0"

    return format(value, ".12g")


def _edge_coefficient_of_variation(
    candidate: HeptagramGeometry,
) -> float:
    """Return the population coefficient of variation of star edges."""

    lengths = candidate.edge_lengths()

    return pstdev(lengths) / mean(lengths)


def _inferred_anchor_polygon(
    anchor: Figure14Anchor,
) -> str:
    """Return a small diamond centred on an inferred anchor."""

    x = anchor.point.x
    y = anchor.point.y
    radius = 0.14

    return " ".join(
        (
            f"{_format_number(vertex_x)},"
            f"{_format_number(vertex_y)}"
        )
        for vertex_x, vertex_y in (
            (x, y + radius),
            (x + radius, y),
            (x, y - radius),
            (x - radius, y),
        )
    )


def _panel_geometry(
    *,
    panel_index: int,
    centre_x: float,
    centre_y: float,
    scale: float,
    diagram: CoreDiagram,
    anchors: tuple[Figure14Anchor, ...],
    candidate: HeptagramGeometry,
    incidence_moons: tuple[tuple[str, object], ...],
) -> list[str]:
    """Return the geometric contents of one comparison panel."""

    square_half_side = diagram.earth_square.half_side

    lines = [
        (
            f'    <g id="panel-{panel_index}-geometry" '
            f'transform="translate('
            f'{_format_number(centre_x)} '
            f'{_format_number(centre_y)}) '
            f'scale({_format_number(scale)},'
            f'-{_format_number(scale)})">'
        ),
        (
            '      <circle class="geometry construction-circle" '
            f'cx="{_format_number(diagram.construction_circle.centre.x)}" '
            f'cy="{_format_number(diagram.construction_circle.centre.y)}" '
            f'r="{_format_number(diagram.construction_circle.radius)}" />'
        ),
        (
            '      <rect class="geometry earth-square" '
            f'x="{_format_number(-square_half_side)}" '
            f'y="{_format_number(-square_half_side)}" '
            f'width="{_format_number(diagram.earth_square.side)}" '
            f'height="{_format_number(diagram.earth_square.side)}" />'
        ),
        (
            '      <circle class="geometry earth-circle" '
            f'cx="{_format_number(diagram.earth_circle.centre.x)}" '
            f'cy="{_format_number(diagram.earth_circle.centre.y)}" '
            f'r="{_format_number(diagram.earth_circle.radius)}" />'
        ),
    ]

    for moon_index, (_, moon) in enumerate(incidence_moons):
        lines.append(
            (
                '      <circle '
                'class="geometry incidence-moon" '
                f'data-panel="{panel_index}" '
                f'data-moon-index="{moon_index}" '
                f'cx="{_format_number(moon.centre.x)}" '
                f'cy="{_format_number(moon.centre.y)}" '
                f'r="{_format_number(moon.radius)}" />'
            )
        )

    for edge_index, (start_index, end_index) in enumerate(
        candidate.edge_index_pairs()
    ):
        start = candidate.vertices[start_index]
        end = candidate.vertices[end_index]

        lines.append(
            (
                '      <line class="geometry star-edge" '
                f'data-panel="{panel_index}" '
                f'data-edge-index="{edge_index}" '
                f'x1="{_format_number(start.x)}" '
                f'y1="{_format_number(start.y)}" '
                f'x2="{_format_number(end.x)}" '
                f'y2="{_format_number(end.y)}" />'
            )
        )

    for vertex_index, (vertex, anchor) in enumerate(
        zip(
            candidate.vertices,
            anchors,
            strict=True,
        )
    ):
        residual = vertex.distance_to(anchor.point)

        lines.append(
            (
                '      <line class="geometry residual-vector" '
                f'data-panel="{panel_index}" '
                f'data-vertex-index="{vertex_index}" '
                f'data-residual="{_format_number(residual)}" '
                f'x1="{_format_number(vertex.x)}" '
                f'y1="{_format_number(vertex.y)}" '
                f'x2="{_format_number(anchor.point.x)}" '
                f'y2="{_format_number(anchor.point.y)}" />'
            )
        )

    for vertex_index, vertex in enumerate(candidate.vertices):
        lines.append(
            (
                '      <circle class="candidate-vertex" '
                f'data-panel="{panel_index}" '
                f'data-vertex-index="{vertex_index}" '
                f'cx="{_format_number(vertex.x)}" '
                f'cy="{_format_number(vertex.y)}" '
                'r="0.105" />'
            )
        )

    for anchor in anchors:
        if (
            anchor.evidence
            is AnchorEvidence.SOURCE_TEXT_AND_PLATE
        ):
            lines.append(
                (
                    '      <circle '
                    'class="anchor-marker stated-anchor" '
                    f'data-panel="{panel_index}" '
                    f'data-anchor-index="{anchor.index}" '
                    f'data-evidence="{anchor.evidence.value}" '
                    f'cx="{_format_number(anchor.point.x)}" '
                    f'cy="{_format_number(anchor.point.y)}" '
                    'r="0.145" />'
                )
            )
        else:
            lines.append(
                (
                    '      <polygon '
                    'class="anchor-marker inferred-anchor" '
                    f'data-panel="{panel_index}" '
                    f'data-anchor-index="{anchor.index}" '
                    f'data-evidence="{anchor.evidence.value}" '
                    f'points="{_inferred_anchor_polygon(anchor)}" />'
                )
            )

    lines.append("    </g>")

    return lines


def michell_figure14_heptagram_to_svg(
    diagram: CoreDiagram,
    *,
    canvas_width: int = 1600,
    canvas_height: int = 920,
    title: str = "Michell Figure 14 heptagram comparison",
) -> str:
    """Return a deterministic three-panel Figure 14 comparison SVG."""

    if canvas_width < 1500:
        raise ValueError(
            "Figure 14 SVG width must be at least 1500 px."
        )

    if canvas_height < 850:
        raise ValueError(
            "Figure 14 SVG height must be at least 850 px."
        )

    anchors = build_figure14_anchor_set(diagram)
    regular = build_regular_heptagram(diagram)
    scaffold = build_scaffold_heptagram(diagram)
    aligned = build_figure14_aligned_heptagram(diagram)

    report = verify_figure14_heptagrams(
        diagram,
        anchors,
        regular,
        scaffold,
        aligned,
    )

    if not report.passed:
        raise ValueError(
            "Cannot render Figure 14 candidates that fail verification."
        )

    incidence_moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    panels: tuple[
        tuple[
            str,
            str,
            HeptagramGeometry,
            HeptagramFit,
        ],
        ...,
    ] = (
        (
            "A",
            "Exact regular {7/3}",
            regular,
            report.regular_fit,
        ),
        (
            "B",
            "Michell 28-point {7/3}",
            scaffold,
            report.scaffold_fit,
        ),
        (
            "C",
            "Figure-14-aligned {7/3}",
            aligned,
            report.aligned_fit,
        ),
    )

    outer_margin = 26.0
    panel_gap = 22.0
    panel_width = (
        canvas_width
        - 2.0 * outer_margin
        - 2.0 * panel_gap
    ) / 3.0

    panel_top = 82.0
    panel_height = 748.0
    geometry_centre_y = 398.0

    geometry_extent = (
        diagram.construction_circle.radius
        + diagram.dimensions.moon_radius
        + 0.6
    )

    scale = min(
        (panel_width - 54.0)
        / (2.0 * geometry_extent),
        548.0 / (2.0 * geometry_extent),
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
            "Three computational reconstructions of Michell's "
            "Figure 14 seven-pointed star, comparing exact regular, "
            "approximate twenty-eight-point, and endpoint-aligned "
            "vertex systems."
            "</desc>"
        ),
        "  <metadata>",
        "    Project: New Jerusalem Geometry",
        "    Source: City of Revelation, Figure 14",
        "    Heptagram family: {7/3}",
        "    Endpoint evidence: 5 text-and-plate, 2 plate inference",
        "    Background: transparent",
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
        "    .panel-frame {",
        "      fill: none;",
        "      stroke: #d0d0d0;",
        "      stroke-width: 1;",
        "    }",
        "    .panel-letter {",
        "      font-size: 18px;",
        "      font-weight: 700;",
        "    }",
        "    .panel-title {",
        "      font-size: 17px;",
        "      font-weight: 600;",
        "      text-anchor: middle;",
        "    }",
        "    .geometry {",
        "      fill: none;",
        "      vector-effect: non-scaling-stroke;",
        "      stroke-linecap: round;",
        "      stroke-linejoin: round;",
        "    }",
        "    .construction-circle {",
        "      stroke: #777777;",
        "      stroke-width: 1.25;",
        "    }",
        "    .earth-square {",
        "      stroke: #3e3e3e;",
        "      stroke-width: 1.2;",
        "    }",
        "    .earth-circle {",
        "      stroke: #a0a0a0;",
        "      stroke-width: 0.9;",
        "      stroke-dasharray: 4 4;",
        "    }",
        "    .incidence-moon {",
        "      stroke: #858585;",
        "      stroke-width: 1;",
        "      opacity: 0.62;",
        "    }",
        "    .star-edge {",
        "      stroke: #1769aa;",
        "      stroke-width: 2.1;",
        "    }",
        "    .residual-vector {",
        "      stroke: #b24b18;",
        "      stroke-width: 1.5;",
        "      stroke-dasharray: 3 2;",
        "    }",
        "    .candidate-vertex {",
        "      fill: #1769aa;",
        "      stroke: #ffffff;",
        "      stroke-width: 0.025;",
        "      vector-effect: non-scaling-stroke;",
        "    }",
        "    .anchor-marker {",
        "      vector-effect: non-scaling-stroke;",
        "      stroke-width: 1.1;",
        "    }",
        "    .stated-anchor {",
        "      fill: #111111;",
        "      stroke: #ffffff;",
        "    }",
        "    .inferred-anchor {",
        "      fill: #ffffff;",
        "      stroke: #9a4f00;",
        "    }",
        "    .metric-label {",
        "      font-size: 12px;",
        "      fill: #555555;",
        "    }",
        "    .metric-value {",
        "      font-size: 13px;",
        "      font-weight: 600;",
        "    }",
        "    .panel-note {",
        "      font-size: 11px;",
        "      fill: #666666;",
        "      text-anchor: middle;",
        "    }",
        "    .legend-text {",
        "      font-size: 12px;",
        "    }",
        "    .footer-note {",
        "      font-size: 12px;",
        "      fill: #555555;",
        "      text-anchor: middle;",
        "    }",
        "  </style>",
        (
            f'  <text class="title" '
            f'x="{canvas_width / 2:.6g}" y="30">'
            f"{escape(title)}</text>"
        ),
        (
            f'  <text class="subtitle" '
            f'x="{canvas_width / 2:.6g}" y="53">'
            "Computational reconstruction — not a facsimile "
            "of the printed plate"
            "</text>"
        ),
    ]

    for panel_index, (
        panel_letter,
        panel_title,
        candidate,
        fit,
    ) in enumerate(panels):
        panel_x = (
            outer_margin
            + panel_index * (panel_width + panel_gap)
        )

        panel_centre_x = panel_x + panel_width / 2.0

        edge_cv = _edge_coefficient_of_variation(
            candidate
        )

        lines.extend(
            [
                (
                    f'  <g id="panel-{panel_index}" '
                    f'data-candidate="{escape(candidate.name)}">'
                ),
                (
                    f'    <rect class="panel-frame" '
                    f'x="{_format_number(panel_x)}" '
                    f'y="{_format_number(panel_top)}" '
                    f'width="{_format_number(panel_width)}" '
                    f'height="{_format_number(panel_height)}" '
                    'rx="7" />'
                ),
                (
                    f'    <text class="panel-letter" '
                    f'x="{_format_number(panel_x + 14.0)}" '
                    'y="111">'
                    f"{panel_letter}</text>"
                ),
                (
                    f'    <text class="panel-title" '
                    f'x="{_format_number(panel_centre_x)}" '
                    'y="111">'
                    f"{escape(panel_title)}</text>"
                ),
            ]
        )

        lines.extend(
            _panel_geometry(
                panel_index=panel_index,
                centre_x=panel_centre_x,
                centre_y=geometry_centre_y,
                scale=scale,
                diagram=diagram,
                anchors=anchors,
                candidate=candidate,
                incidence_moons=incidence_moons,
            )
        )

        metric_x = panel_x + 22.0
        second_metric_x = panel_x + panel_width / 2.0 + 6.0

        lines.extend(
            [
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(metric_x)}" y="684">'
                    "Maximum point residual</text>"
                ),
                (
                    f'    <text class="metric-value" '
                    f'x="{_format_number(metric_x)}" y="704">'
                    f"{fit.maximum_point_residual:.12f} u"
                    "</text>"
                ),
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(second_metric_x)}" y="684">'
                    "RMS point residual</text>"
                ),
                (
                    f'    <text class="metric-value" '
                    f'x="{_format_number(second_metric_x)}" y="704">'
                    f"{fit.rms_point_residual:.12f} u"
                    "</text>"
                ),
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(metric_x)}" y="737">'
                    "Maximum angular residual</text>"
                ),
                (
                    f'    <text class="metric-value" '
                    f'x="{_format_number(metric_x)}" y="757">'
                    f"{fit.maximum_angular_residual_degrees:.9f}°"
                    "</text>"
                ),
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(second_metric_x)}" y="737">'
                    "Edge-length coefficient of variation</text>"
                ),
                (
                    f'    <text class="metric-value" '
                    f'x="{_format_number(second_metric_x)}" y="757">'
                    f"{edge_cv:.12f}"
                    "</text>"
                ),
                (
                    f'    <text class="panel-note" '
                    f'x="{_format_number(panel_centre_x)}" y="797">'
                    f"{escape(candidate.name)}"
                    "</text>"
                ),
                "  </g>",
            ]
        )

    legend_y = 858.0

    lines.extend(
        [
            '  <g id="figure14-legend">',
            (
                f'    <line class="star-edge" '
                f'x1="{outer_margin:.6g}" '
                f'y1="{legend_y:.6g}" '
                f'x2="{outer_margin + 23.0:.6g}" '
                f'y2="{legend_y:.6g}" />'
            ),
            (
                f'    <circle class="candidate-vertex" '
                f'cx="{outer_margin + 11.5:.6g}" '
                f'cy="{legend_y:.6g}" r="4.3" />'
            ),
            (
                f'    <text class="legend-text" '
                f'x="{outer_margin + 33.0:.6g}" '
                f'y="{legend_y + 4.0:.6g}">'
                "candidate {7/3}</text>"
            ),
            (
                f'    <circle class="stated-anchor" '
                f'cx="{outer_margin + 175.0:.6g}" '
                f'cy="{legend_y:.6g}" r="5" />'
            ),
            (
                f'    <text class="legend-text" '
                f'x="{outer_margin + 188.0:.6g}" '
                f'y="{legend_y + 4.0:.6g}">'
                "text-and-plate anchor</text>"
            ),
            (
                f'    <polygon class="inferred-anchor" '
                f'points="'
                f'{outer_margin + 387.0:.6g},{legend_y - 6.0:.6g} '
                f'{outer_margin + 393.0:.6g},{legend_y:.6g} '
                f'{outer_margin + 387.0:.6g},{legend_y + 6.0:.6g} '
                f'{outer_margin + 381.0:.6g},{legend_y:.6g}" />'
            ),
            (
                f'    <text class="legend-text" '
                f'x="{outer_margin + 402.0:.6g}" '
                f'y="{legend_y + 4.0:.6g}">'
                "plate-inferred gap anchor</text>"
            ),
            (
                f'    <line class="residual-vector" '
                f'x1="{outer_margin + 635.0:.6g}" '
                f'y1="{legend_y:.6g}" '
                f'x2="{outer_margin + 661.0:.6g}" '
                f'y2="{legend_y:.6g}" />'
            ),
            (
                f'    <text class="legend-text" '
                f'x="{outer_margin + 671.0:.6g}" '
                f'y="{legend_y + 4.0:.6g}">'
                "candidate-to-anchor residual</text>"
            ),
            "  </g>",
            (
                f'  <text class="footer-note" '
                f'x="{canvas_width / 2:.6g}" '
                f'y="{canvas_height - 21}">'
                "Five endpoint identities are source-supported; "
                "two inter-Moon-gap endpoints remain project inferences."
                "</text>"
            ),
            "</svg>",
            "",
        ]
    )

    return "\n".join(lines)


def write_michell_figure14_heptagram_svg(
    diagram: CoreDiagram,
    output_path: str | Path,
    *,
    canvas_width: int = 1600,
    canvas_height: int = 920,
) -> Path:
    """Write the deterministic Figure 14 comparison SVG."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        michell_figure14_heptagram_to_svg(
            diagram,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        ),
        encoding="utf-8",
    )

    return path
