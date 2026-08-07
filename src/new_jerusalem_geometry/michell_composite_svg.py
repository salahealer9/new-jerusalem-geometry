"""Deterministic SVG renderer for the complete NJG_MICHELL composite.

The renderer is deliberately a pure view of ``MichellComposite``.

It does not construct or fit geometry. In particular it does not consume
Figure 12 or Figure 14 plate calibration, digitisation, registration, or
source-derived coordinates.

All rendered geometric elements are read directly from the supplied composite.
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from .michell_composite import MichellComposite
from .septenary_geometry import ScaffoldRole


SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def _format_number(
    value: float,
) -> str:
    """Return a compact deterministic decimal representation."""

    if abs(value) < 1.0e-15:
        return "0"

    return format(
        value,
        ".12g",
    )


def _geometry_extent(
    composite: MichellComposite,
) -> float:
    """Return a symmetric extent containing the complete rendered geometry."""

    unit = composite.unit

    candidates: list[float] = [
        composite.core.earth_circle.radius,
        composite.core.construction_circle.radius,
        composite.core.earth_square.half_side,
    ]

    for vertex in composite.wall_reconstruction.vertices:
        candidates.extend(
            (
                abs(vertex.x),
                abs(vertex.y),
            )
        )

    for _, moon in composite.wall_reconstruction.moons:
        candidates.extend(
            (
                abs(moon.centre.x)
                + moon.radius,
                abs(moon.centre.y)
                + moon.radius,
            )
        )

    return max(candidates) + 0.6 * unit


def _scaffold_marker(
    *,
    role: ScaffoldRole,
    index: int,
    x: float,
    y: float,
    unit: float,
) -> str:
    """Return one deterministic role-coded scaffold marker."""

    role_name = role.value
    object_id = (
        f"scaffold-point-{index:02d}"
    )

    if role is ScaffoldRole.MOON_CENTRE:
        return (
            '      <circle '
            f'id="{object_id}" '
            'class="scaffold-marker scaffold-moon-centre" '
            f'data-provenance-id="{object_id}" '
            f'data-scaffold-index="{index}" '
            f'data-role="{escape(role_name)}" '
            f'cx="{_format_number(x)}" '
            f'cy="{_format_number(y)}" '
            f'r="{_format_number(0.085 * unit)}" />'
        )

    if role is ScaffoldRole.INTER_MOON_GAP:
        half = 0.065 * unit

        return (
            '      <rect '
            f'id="{object_id}" '
            'class="scaffold-marker scaffold-gap" '
            f'data-provenance-id="{object_id}" '
            f'data-scaffold-index="{index}" '
            f'data-role="{escape(role_name)}" '
            f'x="{_format_number(x - half)}" '
            f'y="{_format_number(y - half)}" '
            f'width="{_format_number(2.0 * half)}" '
            f'height="{_format_number(2.0 * half)}" />'
        )

    radius = 0.095 * unit

    points = " ".join(
        (
            f"{_format_number(px)},"
            f"{_format_number(py)}"
        )
        for px, py in (
            (x, y + radius),
            (x + radius, y),
            (x, y - radius),
            (x - radius, y),
        )
    )

    return (
        '      <polygon '
        f'id="{object_id}" '
        'class="scaffold-marker scaffold-intersection" '
        f'data-provenance-id="{object_id}" '
        f'data-scaffold-index="{index}" '
        f'data-role="{escape(role_name)}" '
        f'points="{points}" />'
    )


def michell_composite_to_svg(
    composite: MichellComposite,
    *,
    canvas_size: int = 1200,
    title: str = "NJG_MICHELL complete generative reconstruction",
    description: str = (
        "Unit-only generative New Jerusalem reconstruction containing "
        "the Earth-square-circle core, twelve incidence Moon circles, "
        "polar-pivot wall, approximate 28-point scaffold, and "
        "scaffold-derived {7/2} heptagram candidate."
    ),
) -> str:
    """Return a transparent standalone SVG of one supplied composite.

    No geometry is reconstructed by this function. Every plotted coordinate is
    taken from ``composite``.
    """

    if canvas_size <= 0:
        raise ValueError(
            "SVG canvas size must be positive."
        )

    unit = composite.unit
    core = composite.core
    wall = composite.wall_reconstruction
    scaffold = composite.scaffold
    star = composite.scaffold_heptagram_candidate

    extent = _geometry_extent(
        composite
    )

    view_min = -extent
    view_size = 2.0 * extent

    square_half_side = (
        core.earth_square.half_side
    )

    base_stroke = 0.040 * unit
    strong_stroke = 0.055 * unit
    scaffold_stroke = 0.025 * unit

    construction_dash = (
        f"{_format_number(0.18 * unit)} "
        f"{_format_number(0.12 * unit)}"
    )

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
            f'width="{canvas_size}" '
            f'height="{canvas_size}" '
            f'viewBox="{_format_number(view_min)} '
            f'{_format_number(view_min)} '
            f'{_format_number(view_size)} '
            f'{_format_number(view_size)}" '
            'preserveAspectRatio="xMidYMid meet" '
            'role="img" '
            'shape-rendering="geometricPrecision">'
        ),
        f"  <title>{escape(title)}</title>",
        f"  <desc>{escape(description)}</desc>",
        "  <metadata>",
        "    Project: New Jerusalem Geometry",
        "    Model: NJG_MICHELL",
        "    Geometry source: supplied MichellComposite",
        "    Caller-supplied geometric quantity: scale unit only",
        "    Plate-calibration inputs: none",
        "    Rendering background: transparent",
        "  </metadata>",
        "  <style>",
        "    .geometry {",
        "      fill: none;",
        "      stroke-linecap: round;",
        "      stroke-linejoin: round;",
        "    }",
        "    .wall {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(strong_stroke)};",
        "    }",
        "    .construction-circle {",
        "      stroke: #777777;",
        f"      stroke-width: {_format_number(base_stroke)};",
        f"      stroke-dasharray: {construction_dash};",
        "    }",
        "    .earth-square {",
        "      stroke: #333333;",
        f"      stroke-width: {_format_number(base_stroke)};",
        "    }",
        "    .earth-circle {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(strong_stroke)};",
        "    }",
        "    .moon-circle {",
        "      stroke: #555555;",
        f"      stroke-width: {_format_number(base_stroke)};",
        "    }",
        "    .scaffold-marker {",
        "      stroke: #777777;",
        f"      stroke-width: {_format_number(scaffold_stroke)};",
        "      fill: #ffffff;",
        "      fill-opacity: 0.85;",
        "    }",
        "    .scaffold-gap {",
        "      fill: #b8b8b8;",
        "    }",
        "    .scaffold-intersection {",
        "      fill: #777777;",
        "    }",
        "    .heptagram-edge {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(strong_stroke)};",
        "    }",
        "    .heptagram-vertex {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(scaffold_stroke)};",
        "      fill: #111111;",
        "    }",
        "  </style>",
        "",
        (
            '  <g id="njg-michell-composite" '
            'transform="scale(1,-1)" '
            'data-model="NJG_MICHELL" '
            'data-provenance-id="njg-michell-composite">'
        ),
        (
            '    <g id="wall" '
            'data-grammar-node="POLAR_PIVOT_WALL">'
        ),
        (
            '      <polygon '
            'id="polar-pivot-wall" '
            'class="geometry wall" '
            'data-provenance-id="polar-pivot-wall" '
            f'points="{wall_points}" />'
        ),
        "    </g>",
        "",
        (
            '    <g id="construction-circle-layer" '
            'data-grammar-node="CONSTRUCTION_CIRCLE">'
        ),
        (
            '      <circle '
            'id="construction-circle" '
            'class="geometry construction-circle" '
            'data-provenance-id="construction-circle" '
            f'cx="{_format_number(core.construction_circle.centre.x)}" '
            f'cy="{_format_number(core.construction_circle.centre.y)}" '
            f'r="{_format_number(core.construction_circle.radius)}" />'
        ),
        "    </g>",
        "",
        (
            '    <g id="earth-square-layer" '
            'data-grammar-node="EARTH_SQUARE">'
        ),
        (
            '      <rect '
            'id="earth-square" '
            'class="geometry earth-square" '
            'data-provenance-id="earth-square" '
            f'x="{_format_number(-square_half_side)}" '
            f'y="{_format_number(-square_half_side)}" '
            f'width="{_format_number(core.earth_square.side)}" '
            f'height="{_format_number(core.earth_square.side)}" />'
        ),
        "    </g>",
        "",
        (
            '    <g id="earth-circle-layer" '
            'data-grammar-node="EARTH_CIRCLE">'
        ),
        (
            '      <circle '
            'id="earth-circle" '
            'class="geometry earth-circle" '
            'data-provenance-id="earth-circle" '
            f'cx="{_format_number(core.earth_circle.centre.x)}" '
            f'cy="{_format_number(core.earth_circle.centre.y)}" '
            f'r="{_format_number(core.earth_circle.radius)}" />'
        ),
        "    </g>",
        "",
        (
            '    <g id="moon-system" '
            'data-grammar-node="MOON_GROUPS_4X3">'
        ),
    ]

    for moon_name, moon in wall.moons:
        lines.append(
            (
                '      <circle '
                f'id="{escape(moon_name)}" '
                'class="geometry moon-circle" '
                f'data-provenance-id="{escape(moon_name)}" '
                f'data-moon="{escape(moon_name)}" '
                f'cx="{_format_number(moon.centre.x)}" '
                f'cy="{_format_number(moon.centre.y)}" '
                f'r="{_format_number(moon.radius)}" />'
            )
        )

    lines.extend(
        [
            "    </g>",
            "",
            (
                '    <g id="scaffold" '
                'data-grammar-node="SCAFFOLD_28">'
            ),
        ]
    )

    for index, point in enumerate(
        scaffold.points
    ):
        lines.append(
            _scaffold_marker(
                role=point.role,
                index=index,
                x=point.point.x,
                y=point.point.y,
                unit=unit,
            )
        )

    lines.extend(
        [
            "    </g>",
            "",
            (
                '    <g id="heptagram" '
                'data-grammar-node="FIG14_HEPTAGRAM_7_2" '
                'data-vertex-source="FIG14_SCAFFOLD_VERTICES">'
            ),
        ]
    )

    for edge_index, (
        start_index,
        end_index,
    ) in enumerate(
        star.edge_index_pairs()
    ):
        start = star.vertices[
            start_index
        ]
        end = star.vertices[
            end_index
        ]

        lines.append(
            (
                '      <line '
                f'id="heptagram-edge-{edge_index:02d}" '
                'class="geometry heptagram-edge" '
                f'data-provenance-id="heptagram-edge-{edge_index:02d}" '
                f'data-start-index="{start_index}" '
                f'data-end-index="{end_index}" '
                f'x1="{_format_number(start.x)}" '
                f'y1="{_format_number(start.y)}" '
                f'x2="{_format_number(end.x)}" '
                f'y2="{_format_number(end.y)}" />'
            )
        )

    for vertex_index, vertex in enumerate(
        star.vertices
    ):
        lines.append(
            (
                '      <circle '
                f'id="heptagram-vertex-{vertex_index:02d}" '
                'class="heptagram-vertex" '
                f'data-provenance-id="heptagram-vertex-{vertex_index:02d}" '
                f'data-vertex-index="{vertex_index}" '
                f'cx="{_format_number(vertex.x)}" '
                f'cy="{_format_number(vertex.y)}" '
                f'r="{_format_number(0.060 * unit)}" />'
            )
        )

    lines.extend(
        [
            "    </g>",
            "  </g>",
            "</svg>",
            "",
        ]
    )

    return "\n".join(
        lines
    )


def write_michell_composite_svg(
    composite: MichellComposite,
    output_path: str | Path,
    *,
    canvas_size: int = 1200,
) -> Path:
    """Write a supplied NJG_MICHELL composite as a standalone SVG."""

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        michell_composite_to_svg(
            composite,
            canvas_size=canvas_size,
        ),
        encoding="utf-8",
    )

    return path
