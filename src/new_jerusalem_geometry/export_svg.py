"""Deterministic SVG export for New Jerusalem geometric models."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .core_geometry import CoreDiagram


SVG_NAMESPACE = "http://www.w3.org/2000/svg"


def _format_number(value: float) -> str:
    """Format a floating-point value compactly and deterministically."""

    if abs(value) < 1.0e-15:
        return "0"

    return format(value, ".12g")


def core_diagram_to_svg(
    diagram: CoreDiagram,
    *,
    canvas_size: int = 900,
    title: str = "New Jerusalem cardinal core geometry",
    description: str = (
        "Verified normalized geometry containing the Earth circle, "
        "Earth square, radius-7 construction circle, and four cardinal "
        "Moon circles."
    ),
) -> str:
    """Return a standalone SVG representation of the verified core.

    The SVG uses the same Euclidean coordinates as the computational model.
    A vertical reflection is applied only at rendering time because SVG's
    native y-axis points downward.
    """
    if canvas_size <= 0:
        raise ValueError("SVG canvas size must be positive.")

    dimensions = diagram.dimensions
    unit = dimensions.unit

    margin = 0.5 * unit
    extent = (
        dimensions.construction_radius
        + dimensions.moon_radius
        + margin
    )

    view_box_min = -extent
    view_box_size = 2.0 * extent

    square_half_side = diagram.earth_square.half_side
    stroke_width = 0.045 * unit
    construction_dash = f"{_format_number(0.20 * unit)} {_format_number(0.13 * unit)}"

    lines: list[str] = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="{SVG_NAMESPACE}" '
            f'width="{canvas_size}" '
            f'height="{canvas_size}" '
            f'viewBox="{_format_number(view_box_min)} '
            f'{_format_number(view_box_min)} '
            f'{_format_number(view_box_size)} '
            f'{_format_number(view_box_size)}" '
            'preserveAspectRatio="xMidYMid meet" '
            'role="img" '
            'shape-rendering="geometricPrecision">'
        ),
        f"  <title>{escape(title)}</title>",
        f"  <desc>{escape(description)}</desc>",
        "  <metadata>",
        "    Model: New Jerusalem cardinal core",
        "    Geometry: scale-free Euclidean coordinates",
        "    Status: computationally verified",
        "  </metadata>",
        "  <style>",
        "    .geometry {",
        "      fill: none;",
        "      stroke-linecap: round;",
        "      stroke-linejoin: round;",
        "    }",
        "    .construction-circle {",
        "      stroke: #777777;",
        f"      stroke-width: {_format_number(stroke_width)};",
        f"      stroke-dasharray: {construction_dash};",
        "    }",
        "    .earth-square {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(stroke_width)};",
        "    }",
        "    .earth-circle {",
        "      stroke: #111111;",
        f"      stroke-width: {_format_number(stroke_width)};",
        "    }",
        "    .moon-circle {",
        "      stroke: #444444;",
        f"      stroke-width: {_format_number(stroke_width)};",
        "    }",
        "  </style>",
        "",
        '  <g id="new-jerusalem-cardinal-core" transform="scale(1,-1)">',
        (
            '    <circle '
            'id="construction-circle" '
            'class="geometry construction-circle" '
            f'cx="{_format_number(diagram.construction_circle.centre.x)}" '
            f'cy="{_format_number(diagram.construction_circle.centre.y)}" '
            f'r="{_format_number(diagram.construction_circle.radius)}" />'
        ),
        (
            '    <rect '
            'id="earth-square" '
            'class="geometry earth-square" '
            f'x="{_format_number(-square_half_side)}" '
            f'y="{_format_number(-square_half_side)}" '
            f'width="{_format_number(diagram.earth_square.side)}" '
            f'height="{_format_number(diagram.earth_square.side)}" />'
        ),
        (
            '    <circle '
            'id="earth-circle" '
            'class="geometry earth-circle" '
            f'cx="{_format_number(diagram.earth_circle.centre.x)}" '
            f'cy="{_format_number(diagram.earth_circle.centre.y)}" '
            f'r="{_format_number(diagram.earth_circle.radius)}" />'
        ),
    ]

    for direction, moon in diagram.cardinal_moons:
        lines.append(
            (
                '    <circle '
                f'id="moon-{escape(direction)}" '
                'class="geometry moon-circle" '
                f'cx="{_format_number(moon.centre.x)}" '
                f'cy="{_format_number(moon.centre.y)}" '
                f'r="{_format_number(moon.radius)}" />'
            )
        )

    lines.extend(
        [
            "  </g>",
            "</svg>",
            "",
        ]
    )

    return "\n".join(lines)


def write_core_svg(
    diagram: CoreDiagram,
    output_path: str | Path,
    *,
    canvas_size: int = 900,
) -> Path:
    """Write the verified core geometry to a standalone SVG file."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        core_diagram_to_svg(
            diagram,
            canvas_size=canvas_size,
        ),
        encoding="utf-8",
    )

    return path
