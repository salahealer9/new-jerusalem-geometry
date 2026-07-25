"""Deterministic SVG comparison of the oblique Moon models."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import (
    ObliquePlacement,
    build_oblique_placement,
)
from .oblique_verification import verify_oblique_placement


SVG_NAMESPACE = "http://www.w3.org/2000/svg"

MODEL_LABELS: dict[ObliqueModel, str] = {
    ObliqueModel.INCIDENCE: "Exact incidence",
    ObliqueModel.DIVISION_28: "Exact 28-fold division",
    ObliqueModel.WIKIMEDIA_SVG: "Wikimedia reconstruction",
}

MODEL_CONSTRAINTS: dict[ObliqueModel, str] = {
    ObliqueModel.INCIDENCE: (
        "Moon circumference passes exactly through each target"
    ),
    ObliqueModel.DIVISION_28: (
        "Oblique centre angle is exactly beta = pi/7"
    ),
    ObliqueModel.WIKIMEDIA_SVG: (
        "beta = theta - asin(r/R), as encoded in the SVG"
    ),
}

MODEL_COLOURS: dict[ObliqueModel, str] = {
    ObliqueModel.INCIDENCE: "#1769aa",
    ObliqueModel.DIVISION_28: "#b45f06",
    ObliqueModel.WIKIMEDIA_SVG: "#6a3d9a",
}


def _format_number(value: float) -> str:
    """Format a number compactly and deterministically."""

    if abs(value) < 1.0e-15:
        return "0"

    return format(value, ".12g")


def _format_residual(value: float) -> str:
    """Format an incidence residual for human-readable SVG labels."""

    if abs(value) < 1.0e-12:
        return "numerical zero"

    return f"{value:.12g} u"


def _geometry_group(
    diagram: CoreDiagram,
    placement: ObliquePlacement,
    *,
    panel_centre_x: float,
    panel_centre_y: float,
    scale: float,
) -> list[str]:
    """Return SVG elements for one model's geometric panel."""

    square_half_side = diagram.earth_square.half_side
    model_colour = MODEL_COLOURS[placement.model]

    lines: list[str] = [
        (
            f'    <g id="geometry-{placement.model.value}" '
            f'transform="translate('
            f'{_format_number(panel_centre_x)} '
            f'{_format_number(panel_centre_y)}) '
            f'scale({_format_number(scale)},'
            f'-{_format_number(scale)})">'
        ),
        (
            '      <circle '
            'class="geometry construction-circle" '
            f'cx="{_format_number(diagram.construction_circle.centre.x)}" '
            f'cy="{_format_number(diagram.construction_circle.centre.y)}" '
            f'r="{_format_number(diagram.construction_circle.radius)}" />'
        ),
        (
            '      <rect '
            'class="geometry earth-square" '
            f'x="{_format_number(-square_half_side)}" '
            f'y="{_format_number(-square_half_side)}" '
            f'width="{_format_number(diagram.earth_square.side)}" '
            f'height="{_format_number(diagram.earth_square.side)}" />'
        ),
        (
            '      <circle '
            'class="geometry earth-circle" '
            f'cx="{_format_number(diagram.earth_circle.centre.x)}" '
            f'cy="{_format_number(diagram.earth_circle.centre.y)}" '
            f'r="{_format_number(diagram.earth_circle.radius)}" />'
        ),
    ]

    for direction, moon in diagram.cardinal_moons:
        lines.append(
            (
                '      <circle '
                f'id="{placement.model.value}-moon-{escape(direction)}" '
                'class="geometry cardinal-moon" '
                f'cx="{_format_number(moon.centre.x)}" '
                f'cy="{_format_number(moon.centre.y)}" '
                f'r="{_format_number(moon.radius)}" />'
            )
        )

    for moon in placement.moons:
        centre = moon.circle.centre
        target = moon.target_intersection.point

        lines.extend(
            [
                (
                    '      <line '
                    'class="geometry incidence-guide" '
                    f'style="stroke: {model_colour};" '
                    f'x1="{_format_number(centre.x)}" '
                    f'y1="{_format_number(centre.y)}" '
                    f'x2="{_format_number(target.x)}" '
                    f'y2="{_format_number(target.y)}" />'
                ),
                (
                    '      <circle '
                    'class="target-point" '
                    f'cx="{_format_number(target.x)}" '
                    f'cy="{_format_number(target.y)}" '
                    'r="0.09" />'
                ),
                (
                    '      <circle '
                    'class="moon-centre" '
                    f'style="fill: {model_colour};" '
                    f'cx="{_format_number(centre.x)}" '
                    f'cy="{_format_number(centre.y)}" '
                    'r="0.075" />'
                ),
                (
                    '      <circle '
                    f'id="{placement.model.value}-{escape(moon.name)}" '
                    'class="geometry oblique-moon" '
                    f'style="stroke: {model_colour};" '
                    f'cx="{_format_number(centre.x)}" '
                    f'cy="{_format_number(centre.y)}" '
                    f'r="{_format_number(moon.circle.radius)}" />'
                ),
            ]
        )

    lines.append("    </g>")

    return lines


def oblique_models_comparison_to_svg(
    diagram: CoreDiagram,
    *,
    canvas_width: int = 1800,
    canvas_height: int = 720,
    title: str = "New Jerusalem oblique Moon models",
) -> str:
    """Return a three-panel SVG comparison of the oblique models."""

    if canvas_width < 1200:
        raise ValueError("Comparison SVG width must be at least 1200 px.")

    if canvas_height < 600:
        raise ValueError("Comparison SVG height must be at least 600 px.")

    models = tuple(ObliqueModel)
    panel_width = canvas_width / len(models)

    top_area = 112.0
    bottom_area = 92.0
    usable_height = canvas_height - top_area - bottom_area

    geometry_extent = 9.0
    horizontal_scale = (panel_width - 72.0) / (2.0 * geometry_extent)
    vertical_scale = usable_height / (2.0 * geometry_extent)
    geometry_scale = min(horizontal_scale, vertical_scale)

    geometry_centre_y = top_area + usable_height / 2.0

    placements = {
        model: build_oblique_placement(diagram, model)
        for model in models
    }

    reports = {
        model: verify_oblique_placement(
            diagram,
            placements[model],
        )
        for model in models
    }

    maximum_reference_residual = max(
        reports[model].max_abs_incidence_residual
        for model in models
    )

    if maximum_reference_residual <= 0.0:
        maximum_reference_residual = 1.0

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
            "Side-by-side comparison of the exact-incidence, exact "
            "28-fold-division, and Wikimedia SVG placements of the "
            "eight oblique Moon circles."
            "</desc>"
        ),
        "  <metadata>",
        "    Project: New Jerusalem Geometry",
        "    Figure: Oblique Moon model comparison",
        "    Geometry: Scale-free Euclidean coordinates",
        "  </metadata>",
        "  <style>",
        "    text {",
        "      font-family: system-ui, sans-serif;",
        "      fill: #161616;",
        "    }",
        "    .figure-title {",
        "      font-size: 24px;",
        "      font-weight: 600;",
        "      text-anchor: middle;",
        "    }",
        "    .panel-title {",
        "      font-size: 19px;",
        "      font-weight: 600;",
        "      text-anchor: middle;",
        "    }",
        "    .panel-subtitle {",
        "      font-size: 14px;",
        "      text-anchor: middle;",
        "      fill: #444444;",
        "    }",
        "    .metric-label {",
        "      font-size: 13px;",
        "      text-anchor: middle;",
        "      fill: #333333;",
        "    }",
        "    .constraint-label {",
        "      font-size: 12px;",
        "      text-anchor: middle;",
        "      fill: #555555;",
        "    }",
        "    .geometry {",
        "      fill: none;",
        "      vector-effect: non-scaling-stroke;",
        "      stroke-linecap: round;",
        "      stroke-linejoin: round;",
        "    }",
        "    .construction-circle {",
        "      stroke: #8a8a8a;",
        "      stroke-width: 1.25;",
        "      stroke-dasharray: 5 4;",
        "    }",
        "    .earth-square, .earth-circle {",
        "      stroke: #151515;",
        "      stroke-width: 1.55;",
        "    }",
        "    .cardinal-moon {",
        "      stroke: #5d5d5d;",
        "      stroke-width: 1.25;",
        "    }",
        "    .oblique-moon {",
        "      stroke-width: 1.55;",
        "    }",
        "    .incidence-guide {",
        "      stroke-width: 0.9;",
        "      stroke-dasharray: 3 3;",
        "      opacity: 0.65;",
        "    }",
        "    .target-point {",
        "      fill: #111111;",
        "      stroke: none;",
        "    }",
        "    .moon-centre {",
        "      stroke: none;",
        "    }",
        "    .separator {",
        "      stroke: #d2d2d2;",
        "      stroke-width: 1;",
        "    }",
        "    .residual-track {",
        "      fill: #e5e5e5;",
        "    }",
        "  </style>",
        (
            f'  <text class="figure-title" '
            f'x="{canvas_width / 2:.6g}" y="32">'
            f"{escape(title)}</text>"
        ),
    ]

    for index in range(1, len(models)):
        x = index * panel_width
        lines.append(
            (
                f'  <line class="separator" '
                f'x1="{_format_number(x)}" y1="48" '
                f'x2="{_format_number(x)}" '
                f'y2="{canvas_height - 24}" />'
            )
        )

    for index, model in enumerate(models):
        placement = placements[model]
        report = reports[model]

        panel_left = index * panel_width
        panel_centre_x = panel_left + panel_width / 2.0
        colour = MODEL_COLOURS[model]

        lines.extend(
            [
                f'  <g id="panel-{model.value}" data-model="{model.value}">',
                (
                    f'    <text class="panel-title" '
                    f'style="fill: {colour};" '
                    f'x="{_format_number(panel_centre_x)}" y="62">'
                    f"{escape(model.value)}</text>"
                ),
                (
                    f'    <text class="panel-subtitle" '
                    f'x="{_format_number(panel_centre_x)}" y="84">'
                    f"{escape(MODEL_LABELS[model])}</text>"
                ),
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(panel_centre_x)}" y="104">'
                    f"beta = {placement.beta_degrees:.12f} deg"
                    "</text>"
                ),
            ]
        )

        lines.extend(
            _geometry_group(
                diagram,
                placement,
                panel_centre_x=panel_centre_x,
                panel_centre_y=geometry_centre_y,
                scale=geometry_scale,
            )
        )

        residual = report.max_abs_incidence_residual
        bar_width = panel_width - 180.0
        bar_x = panel_left + 90.0
        bar_y = canvas_height - 66.0
        residual_fraction = min(
            residual / maximum_reference_residual,
            1.0,
        )
        filled_width = bar_width * residual_fraction

        lines.extend(
            [
                (
                    f'    <text class="metric-label" '
                    f'x="{_format_number(panel_centre_x)}" '
                    f'y="{canvas_height - 76}">'
                    "Maximum incidence residual: "
                    f"{escape(_format_residual(residual))}"
                    "</text>"
                ),
                (
                    f'    <rect class="residual-track" '
                    f'x="{_format_number(bar_x)}" '
                    f'y="{_format_number(bar_y)}" '
                    f'width="{_format_number(bar_width)}" '
                    'height="8" rx="4" />'
                ),
                (
                    f'    <rect '
                    f'style="fill: {colour};" '
                    f'x="{_format_number(bar_x)}" '
                    f'y="{_format_number(bar_y)}" '
                    f'width="{_format_number(filled_width)}" '
                    'height="8" rx="4" />'
                ),
                (
                    f'    <text class="constraint-label" '
                    f'x="{_format_number(panel_centre_x)}" '
                    f'y="{canvas_height - 28}">'
                    f"{escape(MODEL_CONSTRAINTS[model])}</text>"
                ),
                "  </g>",
            ]
        )

    lines.extend(
        [
            "</svg>",
            "",
        ]
    )

    return "\n".join(lines)


def write_oblique_models_comparison_svg(
    diagram: CoreDiagram,
    output_path: str | Path,
    *,
    canvas_width: int = 1800,
    canvas_height: int = 720,
) -> Path:
    """Write the deterministic oblique-model comparison SVG."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        oblique_models_comparison_to_svg(
            diagram,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
        ),
        encoding="utf-8",
    )

    return path
