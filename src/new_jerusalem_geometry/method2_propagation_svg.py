"""Transparent deterministic SVG for the frozen v0.8 Method 2 geometry.

The renderer consumes already-generated Phase 8E/8F JSON artifacts. It does
not refit, optimize, or alter the geometry.
"""

from __future__ import annotations

from html import escape
import json
from math import (
    atan2,
    cos,
    hypot,
    pi,
    sin,
    tau,
)
from pathlib import Path
from typing import Any


SVG_WIDTH = 1200
SVG_HEIGHT = 500
PANEL_RADIUS = 142.0
PANEL_CENTER_Y = 236.0

PROPAGATION_SHA256 = (
    "5af0b893ef9f18f5bb6c04e013f12298d816f426a2a248eccbd9230ab5ad4a43"
)

SYMBOLIC_AUDIT_SHA256 = (
    "db314c890636a2a435d4065a42c49c08bba8df00c7e29a2cca156b00eef47078"
)


def _fmt(
    value: float,
) -> str:
    text = f"{value:.6f}"

    text = text.rstrip(
        "0"
    ).rstrip(
        "."
    )

    if text == "-0":
        return "0"

    return text


def _svg_point(
    x: float,
    y: float,
    *,
    cx: float,
    cy: float,
    radius: float,
) -> tuple[float, float]:
    return (
        cx
        + radius
        * x,
        cy
        - radius
        * y,
    )


def _point_from_angle(
    angle: float,
    *,
    cx: float,
    cy: float,
    radius: float,
) -> tuple[float, float]:
    return _svg_point(
        cos(
            angle
        ),
        sin(
            angle
        ),
        cx=cx,
        cy=cy,
        radius=radius,
    )


def _polyline_points(
    points: list[dict[str, Any]],
    *,
    cx: float,
    cy: float,
    radius: float,
) -> str:
    values: list[str] = []

    for point in points:
        x, y = _svg_point(
            float(
                point[
                    "x"
                ]
            ),
            float(
                point[
                    "y"
                ]
            ),
            cx=cx,
            cy=cy,
            radius=radius,
        )

        values.append(
            f"{_fmt(x)},{_fmt(y)}"
        )

    return " ".join(
        values
    )


def _carrier_points(
    points: list[dict[str, Any]],
    *,
    carrier_indices: tuple[int, ...],
) -> list[
    dict[str, Any]
]:
    by_index = {
        int(
            point[
                "carrier_index"
            ]
        ): point
        for point in points
        if int(
            point[
                "local_k"
            ]
        ) == 0
    }

    return [
        by_index[
            index
        ]
        for index in carrier_indices
    ]


def _arc_radius_model(
    points: list[dict[str, Any]],
    *,
    carrier_index: int,
) -> float:
    carrier = next(
        point
        for point in points
        if (
            int(
                point[
                    "carrier_index"
                ]
            )
            == carrier_index
            and int(
                point[
                    "local_k"
                ]
            )
            == 0
        )
    )

    adjacent = next(
        point
        for point in points
        if (
            int(
                point[
                    "carrier_index"
                ]
            )
            == carrier_index
            and int(
                point[
                    "local_k"
                ]
            )
            == 1
        )
    )

    return hypot(
        float(
            adjacent[
                "x"
            ]
        )
        - float(
            carrier[
                "x"
            ]
        ),
        float(
            adjacent[
                "y"
            ]
        )
        - float(
            carrier[
                "y"
            ]
        ),
    )


def _draw_outer_circle(
    *,
    cx: float,
    cy: float,
    clip_id: str,
) -> list[str]:
    return [
        (
            f'<clipPath id="{clip_id}">'
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" '
            f'r="{_fmt(PANEL_RADIUS)}"/>'
            "</clipPath>"
        ),
        (
            f'<circle class="outer" cx="{_fmt(cx)}" cy="{_fmt(cy)}" '
            f'r="{_fmt(PANEL_RADIUS)}"/>'
        ),
    ]


def _draw_triangle(
    carrier_points: list[dict[str, Any]],
    *,
    cx: float,
    cy: float,
    css_class: str,
) -> str:
    closed = (
        carrier_points
        + [
            carrier_points[
                0
            ]
        ]
    )

    return (
        f'<polyline class="{css_class}" '
        f'points="{_polyline_points(closed, cx=cx, cy=cy, radius=PANEL_RADIUS)}"/>'
    )


def _draw_arc_circles(
    points: list[dict[str, Any]],
    *,
    carrier_indices: tuple[int, ...],
    cx: float,
    cy: float,
    clip_id: str,
    css_class: str,
) -> list[str]:
    lines = [
        f'<g clip-path="url(#{clip_id})">'
    ]

    for carrier_index in carrier_indices:
        carrier = next(
            point
            for point in points
            if (
                int(
                    point[
                        "carrier_index"
                    ]
                )
                == carrier_index
                and int(
                    point[
                        "local_k"
                    ]
                )
                == 0
            )
        )

        px, py = _svg_point(
            float(
                carrier[
                    "x"
                ]
            ),
            float(
                carrier[
                    "y"
                ]
            ),
            cx=cx,
            cy=cy,
            radius=PANEL_RADIUS,
        )

        arc_radius = (
            _arc_radius_model(
                points,
                carrier_index=(
                    carrier_index
                ),
            )
            * PANEL_RADIUS
        )

        lines.append(
            (
                f'<circle class="{css_class}" '
                f'cx="{_fmt(px)}" cy="{_fmt(py)}" '
                f'r="{_fmt(arc_radius)}"/>'
            )
        )

    lines.append(
        "</g>"
    )

    return lines


def _draw_marks(
    points: list[dict[str, Any]],
    *,
    cx: float,
    cy: float,
    point_radius: float,
    carrier_shape: str,
) -> list[str]:
    lines: list[str] = []

    for point in points:
        px, py = _svg_point(
            float(
                point[
                    "x"
                ]
            ),
            float(
                point[
                    "y"
                ]
            ),
            cx=cx,
            cy=cy,
            radius=PANEL_RADIUS,
        )

        local_k = int(
            point[
                "local_k"
            ]
        )

        family = str(
            point.get(
                "carrier_family",
                "",
            )
        )

        if local_k == 0:
            if (
                carrier_shape
                == "mixed"
                and family
                == "reciprocal"
            ):
                size = (
                    point_radius
                    * 2.0
                )

                lines.append(
                    (
                        '<rect class="carrier reciprocal-carrier" '
                        f'x="{_fmt(px - size / 2.0)}" '
                        f'y="{_fmt(py - size / 2.0)}" '
                        f'width="{_fmt(size)}" height="{_fmt(size)}"/>'
                    )
                )
            else:
                lines.append(
                    (
                        '<circle class="carrier" '
                        f'cx="{_fmt(px)}" cy="{_fmt(py)}" '
                        f'r="{_fmt(point_radius * 1.15)}"/>'
                    )
                )
        else:
            lines.append(
                (
                    '<circle class="mark" '
                    f'cx="{_fmt(px)}" cy="{_fmt(py)}" '
                    f'r="{_fmt(point_radius)}"/>'
                )
            )

    return lines


def _gap_midpoint_angle(
    first: float,
    second: float,
) -> float:
    gap = (
        second
        - first
    ) % tau

    return (
        first
        + gap
        / 2.0
    ) % tau


def _draw_small_gap_markers(
    point_set: dict[str, Any],
    pattern: str,
    *,
    cx: float,
    cy: float,
) -> list[str]:
    points = list(
        point_set[
            "sorted_points"
        ]
    )

    if len(
        pattern
    ) != len(
        points
    ):
        raise ValueError(
            "Gap-class pattern length does not match point count."
        )

    lines: list[str] = []

    marker_radius = (
        PANEL_RADIUS
        + 12.0
    )

    for index, gap_class in enumerate(
        pattern
    ):
        if gap_class != "S":
            continue

        first = float(
            points[
                index
            ][
                "angle_radians"
            ]
        )

        second = float(
            points[
                (
                    index
                    + 1
                )
                % len(
                    points
                )
            ][
                "angle_radians"
            ]
        )

        angle = _gap_midpoint_angle(
            first,
            second,
        )

        px, py = _point_from_angle(
            angle,
            cx=cx,
            cy=cy,
            radius=marker_radius,
        )

        lines.append(
            (
                '<circle class="small-gap-marker" '
                f'cx="{_fmt(px)}" cy="{_fmt(py)}" r="3.2"/>'
            )
        )

    return lines


def _label(
    text: str,
    *,
    x: float,
    y: float,
    css_class: str,
) -> str:
    return (
        f'<text class="{css_class}" '
        f'x="{_fmt(x)}" y="{_fmt(y)}">'
        f"{escape(text)}"
        "</text>"
    )


def method2_propagation_to_svg(
    propagation_payload: dict[str, Any],
    symbolic_payload: dict[str, Any],
) -> str:
    """Render the frozen 7/21/42 Method 2 geometry."""

    local_points = list(
        propagation_payload[
            "local_seven"
        ][
            "sorted_points"
        ]
    )

    twenty_one = (
        propagation_payload[
            "twenty_one"
        ]
    )

    twenty_one_points = list(
        twenty_one[
            "sorted_points"
        ]
    )

    forty_two = (
        propagation_payload[
            "forty_two"
        ]
    )

    forty_two_points = list(
        forty_two[
            "sorted_points"
        ]
    )

    pattern_21 = str(
        symbolic_payload[
            "twenty_one"
        ][
            "cyclic_class_pattern"
        ]
    )

    pattern_42 = str(
        symbolic_payload[
            "forty_two"
        ][
            "cyclic_class_pattern"
        ]
    )

    centres = (
        200.0,
        600.0,
        1000.0,
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
            f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
            'role="img" '
            'aria-labelledby="title desc">'
        ),
        '<title id="title">Michell Figure 194 Method 2: 7 to 21 to 42</title>',
        (
            '<desc id="desc">'
            'Transparent three-panel deterministic rendering of the frozen '
            'Method 2 construction. The first panel shows the local seven-mark '
            'completion, the second the original-triangle twenty-one marks, '
            'and the third the original plus reciprocal forty-two marks.'
            '</desc>'
        ),
        '<defs>',
        '<style><![CDATA[',
        'text { font-family: sans-serif; fill: #111; }',
        '.panel-title { font-size: 18px; font-weight: 700; text-anchor: middle; }',
        '.panel-subtitle { font-size: 12px; text-anchor: middle; }',
        '.formula { font-size: 11px; text-anchor: middle; }',
        '.outer { fill: none; stroke: #111; stroke-width: 1.6; }',
        '.triangle-original { fill: none; stroke: #555; stroke-width: 1.25; }',
        '.triangle-reciprocal { fill: none; stroke: #777; stroke-width: 1.25; stroke-dasharray: 5 4; }',
        '.arc-original { fill: none; stroke: #999; stroke-width: 1.0; }',
        '.arc-reciprocal { fill: none; stroke: #aaa; stroke-width: 1.0; stroke-dasharray: 3 3; }',
        '.mark { fill: #111; stroke: none; }',
        '.carrier { fill: none; stroke: #111; stroke-width: 1.4; }',
        '.reciprocal-carrier { stroke-dasharray: 2 1; }',
        '.small-gap-marker { fill: none; stroke: #111; stroke-width: 1.2; }',
        '.legend { font-size: 10.5px; }',
        ']]></style>',
    ]

    for index, cx in enumerate(
        centres
    ):
        lines.extend(
            _draw_outer_circle(
                cx=cx,
                cy=PANEL_CENTER_Y,
                clip_id=(
                    f"clip-{index}"
                ),
            )
        )

    lines.append(
        "</defs>"
    )

    # Panel 1: local seven.
    cx = centres[
        0
    ]

    original_carriers_21 = (
        _carrier_points(
            twenty_one_points,
            carrier_indices=(
                0,
                1,
                2,
            ),
        )
    )

    lines.append(
        _label(
            "Method 2 local step",
            x=cx,
            y=32.0,
            css_class="panel-title",
        )
    )

    lines.append(
        _label(
            "7-mark operational completion",
            x=cx,
            y=51.0,
            css_class="panel-subtitle",
        )
    )

    lines.append(
        _draw_triangle(
            original_carriers_21,
            cx=cx,
            cy=PANEL_CENTER_Y,
            css_class="triangle-original",
        )
    )

    # Use the matching top carrier from the 21-set to draw the source arc.
    lines.extend(
        _draw_arc_circles(
            twenty_one_points,
            carrier_indices=(
                0,
            ),
            cx=cx,
            cy=PANEL_CENTER_Y,
            clip_id="clip-0",
            css_class="arc-original",
        )
    )

    lines.extend(
        _draw_marks(
            local_points,
            cx=cx,
            cy=PANEL_CENTER_Y,
            point_radius=4.0,
            carrier_shape="circle",
        )
    )

    lines.append(
        _label(
            "alpha_2 = acos(5/8)",
            x=cx,
            y=420.0,
            css_class="formula",
        )
    )

    lines.append(
        _label(
            "k = -3,...,+3",
            x=cx,
            y=438.0,
            css_class="formula",
        )
    )

    # Panel 2: 21.
    cx = centres[
        1
    ]

    lines.append(
        _label(
            "Original triangle",
            x=cx,
            y=32.0,
            css_class="panel-title",
        )
    )

    lines.append(
        _label(
            "3 carriers x 7 = 21 semantic marks",
            x=cx,
            y=51.0,
            css_class="panel-subtitle",
        )
    )

    lines.append(
        _draw_triangle(
            original_carriers_21,
            cx=cx,
            cy=PANEL_CENTER_Y,
            css_class="triangle-original",
        )
    )

    lines.extend(
        _draw_arc_circles(
            twenty_one_points,
            carrier_indices=(
                0,
                1,
                2,
            ),
            cx=cx,
            cy=PANEL_CENTER_Y,
            clip_id="clip-1",
            css_class="arc-original",
        )
    )

    lines.extend(
        _draw_marks(
            twenty_one_points,
            cx=cx,
            cy=PANEL_CENTER_Y,
            point_radius=3.1,
            carrier_shape="circle",
        )
    )

    lines.extend(
        _draw_small_gap_markers(
            twenty_one,
            pattern_21,
            cx=cx,
            cy=PANEL_CENTER_Y,
        )
    )

    lines.append(
        _label(
            "15 L : 6 S   |   RMS = sqrt(10) delta",
            x=cx,
            y=420.0,
            css_class="formula",
        )
    )

    lines.append(
        _label(
            "open outer markers identify the 6 S gaps",
            x=cx,
            y=438.0,
            css_class="formula",
        )
    )

    # Panel 3: 42.
    cx = centres[
        2
    ]

    original_carriers_42 = (
        _carrier_points(
            forty_two_points,
            carrier_indices=(
                0,
                2,
                4,
            ),
        )
    )

    reciprocal_carriers_42 = (
        _carrier_points(
            forty_two_points,
            carrier_indices=(
                1,
                3,
                5,
            ),
        )
    )

    lines.append(
        _label(
            "Original + reciprocal",
            x=cx,
            y=32.0,
            css_class="panel-title",
        )
    )

    lines.append(
        _label(
            "6 carriers x 7 = 42 semantic marks",
            x=cx,
            y=51.0,
            css_class="panel-subtitle",
        )
    )

    lines.append(
        _draw_triangle(
            original_carriers_42,
            cx=cx,
            cy=PANEL_CENTER_Y,
            css_class="triangle-original",
        )
    )

    lines.append(
        _draw_triangle(
            reciprocal_carriers_42,
            cx=cx,
            cy=PANEL_CENTER_Y,
            css_class="triangle-reciprocal",
        )
    )

    lines.extend(
        _draw_arc_circles(
            forty_two_points,
            carrier_indices=(
                0,
                2,
                4,
            ),
            cx=cx,
            cy=PANEL_CENTER_Y,
            clip_id="clip-2",
            css_class="arc-original",
        )
    )

    lines.extend(
        _draw_arc_circles(
            forty_two_points,
            carrier_indices=(
                1,
                3,
                5,
            ),
            cx=cx,
            cy=PANEL_CENTER_Y,
            clip_id="clip-2",
            css_class="arc-reciprocal",
        )
    )

    lines.extend(
        _draw_marks(
            forty_two_points,
            cx=cx,
            cy=PANEL_CENTER_Y,
            point_radius=2.45,
            carrier_shape="mixed",
        )
    )

    lines.extend(
        _draw_small_gap_markers(
            forty_two,
            pattern_42,
            cx=cx,
            cy=PANEL_CENTER_Y,
        )
    )

    lines.append(
        _label(
            "36 L : 6 S   |   RMS = sqrt(6) delta",
            x=cx,
            y=420.0,
            css_class="formula",
        )
    )

    lines.append(
        _label(
            "solid triangle = original; dashed = reciprocal",
            x=cx,
            y=438.0,
            css_class="formula",
        )
    )

    lines.append(
        _label(
            (
                "Visualization only — geometry and symbolic classes are "
                "read from frozen Phase 8E/8F artifacts."
            ),
            x=SVG_WIDTH / 2.0,
            y=478.0,
            css_class="legend",
        )
    )

    lines.append(
        "</svg>"
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


def write_method2_propagation_svg(
    propagation_json: str | Path,
    symbolic_json: str | Path,
    output_path: str | Path,
) -> Path:
    """Load frozen artifacts and write the deterministic transparent SVG."""

    propagation_path = Path(
        propagation_json
    )

    symbolic_path = Path(
        symbolic_json
    )

    output = Path(
        output_path
    )

    propagation = json.loads(
        propagation_path.read_text(
            encoding="utf-8"
        )
    )

    symbolic = json.loads(
        symbolic_path.read_text(
            encoding="utf-8"
        )
    )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.write_text(
        method2_propagation_to_svg(
            propagation,
            symbolic,
        ),
        encoding="utf-8",
    )

    return output
