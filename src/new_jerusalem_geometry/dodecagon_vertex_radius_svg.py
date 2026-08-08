"""Deterministic Phase 7B geometry-only SVGs.

Historical dimensional targets are intentionally absent.
"""

from __future__ import annotations

from html import escape
from math import cos, pi, sin
from pathlib import Path
from typing import Any

from .dodecagon_vertex_radius_audit import (
    OBLIQUE_PAIR_VERTEX,
    POLAR_ADJACENT_VERTEX,
    REGULAR_APOTHEM,
    build_vertex_radius_audit,
)


VIEW_SIZE = 900
SCALE = 42.0
CX = VIEW_SIZE / 2.0
CY = VIEW_SIZE / 2.0


def _sx(
    x: float,
) -> float:
    return (
        CX
        + SCALE
        * x
    )


def _sy(
    y: float,
) -> float:
    return (
        CY
        - SCALE
        * y
    )


def _fmt(
    value: float,
) -> str:
    return (
        f"{value:.6f}"
    )


def _point_string(
    points: list[
        tuple[
            float,
            float,
        ]
    ],
) -> str:
    return " ".join(
        (
            f"{_fmt(_sx(x))},"
            f"{_fmt(_sy(y))}"
        )
        for x, y in points
    )


def _svg_open(
    title: str,
    description: str,
) -> list[str]:
    return [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{VIEW_SIZE}" height="{VIEW_SIZE}" '
            f'viewBox="0 0 {VIEW_SIZE} {VIEW_SIZE}" '
            'role="img">'
        ),
        (
            f"<title>{escape(title)}</title>"
        ),
        (
            f"<desc>{escape(description)}</desc>"
        ),
        (
            '<g id="coordinate-frame" '
            'fill="none" stroke="currentColor" '
            'stroke-width="1">'
        ),
        (
            f'<line id="axis-x" x1="70" '
            f'y1="{_fmt(CY)}" x2="830" '
            f'y2="{_fmt(CY)}" opacity="0.18"/>'
        ),
        (
            f'<line id="axis-y" x1="{_fmt(CX)}" '
            f'y1="70" x2="{_fmt(CX)}" '
            f'y2="830" opacity="0.18"/>'
        ),
        "</g>",
    ]


def _svg_close() -> list[str]:
    return [
        "</svg>",
    ]


def _wall_points(
    audit: dict[str, Any],
) -> list[
    tuple[
        float,
        float,
    ]
]:
    return [
        (
            float(
                row[
                    "x_normalized"
                ]
            ),
            float(
                row[
                    "y_normalized"
                ]
            ),
        )
        for row in audit[
            "vertices"
        ]
    ]


def _regular_points(
    audit: dict[str, Any],
) -> list[
    tuple[
        float,
        float,
    ]
]:
    return [
        (
            float(
                row[
                    "regular_x_normalized"
                ]
            ),
            float(
                row[
                    "regular_y_normalized"
                ]
            ),
        )
        for row in audit[
            "vertices"
        ]
    ]


def source_constraints_svg(
    audit: dict[str, Any],
) -> str:
    lines = _svg_open(
        (
            "Sommerville dodecagon "
            "source constraints"
        ),
        (
            "Frozen polar-pivot outer wall "
            "with semantic side and vertex "
            "classes in normalized units."
        ),
    )

    wall_points = (
        _wall_points(
            audit
        )
    )

    lines.extend(
        [
            (
                '<polygon id="frozen-polar-pivot-wall" '
                f'points="{_point_string(wall_points)}" '
                'fill="none" stroke="currentColor" '
                'stroke-width="2.4"/>'
            ),
            (
                '<circle id="construction-centre" '
                f'cx="{_fmt(CX)}" cy="{_fmt(CY)}" '
                'r="4.5" fill="currentColor"/>'
            ),
        ]
    )

    vertices = audit[
        "vertices"
    ]

    for row in vertices:
        x = float(
            row[
                "x_normalized"
            ]
        )
        y = float(
            row[
                "y_normalized"
            ]
        )
        vertex_id = str(
            row[
                "vertex_id"
            ]
        )
        vertex_class = str(
            row[
                "vertex_class"
            ]
        )

        opacity = (
            "0.90"
            if vertex_class
            == POLAR_ADJACENT_VERTEX
            else "0.52"
        )

        lines.append(
            (
                f'<line id="radius-ray-{escape(vertex_id)}" '
                f'x1="{_fmt(CX)}" y1="{_fmt(CY)}" '
                f'x2="{_fmt(_sx(x))}" y2="{_fmt(_sy(y))}" '
                'stroke="currentColor" stroke-width="1.2" '
                f'opacity="{opacity}"/>'
            )
        )

        radius_px = (
            "5.0"
            if vertex_class
            == POLAR_ADJACENT_VERTEX
            else "6.5"
        )

        lines.append(
            (
                f'<circle id="{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(x))}" cy="{_fmt(_sy(y))}" '
                f'r="{radius_px}" fill="none" '
                'stroke="currentColor" stroke-width="2"/>'
            )
        )

    # Semantic side overlays. Side i runs from vertex i-1 to vertex i.
    polar_indices = set(
        audit[
            "wall_topology"
        ][
            "polar_side_indices"
        ]
    )

    for index in range(
        len(
            wall_points
        )
    ):
        x1, y1 = wall_points[
            (
                index
                - 1
            )
            % len(
                wall_points
            )
        ]
        x2, y2 = wall_points[
            index
        ]

        side_class = (
            "polar"
            if index
            in polar_indices
            else "oblique"
        )

        width = (
            "4.0"
            if side_class
            == "polar"
            else "2.2"
        )

        opacity = (
            "0.88"
            if side_class
            == "polar"
            else "0.48"
        )

        lines.append(
            (
                f'<line id="wall-side-{index:02d}-{side_class}" '
                f'x1="{_fmt(_sx(x1))}" y1="{_fmt(_sy(y1))}" '
                f'x2="{_fmt(_sx(x2))}" y2="{_fmt(_sy(y2))}" '
                'stroke="currentColor" '
                f'stroke-width="{width}" opacity="{opacity}"/>'
            )
        )

    lines.extend(
        [
            (
                '<g id="normalized-apothem" '
                'stroke="currentColor" '
                'fill="none" opacity="0.60">'
            ),
            (
                f'<line x1="{_fmt(CX)}" y1="{_fmt(CY)}" '
                f'x2="{_fmt(_sx(REGULAR_APOTHEM))}" '
                f'y2="{_fmt(CY)}" '
                'stroke-width="1.4" stroke-dasharray="7 5"/>'
            ),
            "</g>",
        ]
    )

    lines.extend(
        _svg_close()
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


def regular_baseline_svg(
    audit: dict[str, Any],
) -> str:
    lines = _svg_open(
        (
            "Regular dodecagon baseline "
            "and frozen wall"
        ),
        (
            "Parameter-free regular "
            "dodecagon baseline using "
            "the inherited normalized "
            "apothem, compared geometrically "
            "with the frozen polar-pivot wall."
        ),
    )

    wall_points = (
        _wall_points(
            audit
        )
    )

    regular_points = (
        _regular_points(
            audit
        )
    )

    lines.extend(
        [
            (
                '<polygon id="regular-dodecagon-baseline" '
                f'points="{_point_string(regular_points)}" '
                'fill="none" stroke="currentColor" '
                'stroke-width="1.8" stroke-dasharray="9 6" '
                'opacity="0.55"/>'
            ),
            (
                '<polygon id="frozen-polar-pivot-wall" '
                f'points="{_point_string(wall_points)}" '
                'fill="none" stroke="currentColor" '
                'stroke-width="2.8"/>'
            ),
            (
                '<circle id="construction-centre" '
                f'cx="{_fmt(CX)}" cy="{_fmt(CY)}" '
                'r="4.5" fill="currentColor"/>'
            ),
        ]
    )

    for row in audit[
        "vertices"
    ]:
        x = float(
            row[
                "x_normalized"
            ]
        )
        y = float(
            row[
                "y_normalized"
            ]
        )
        rx = float(
            row[
                "regular_x_normalized"
            ]
        )
        ry = float(
            row[
                "regular_y_normalized"
            ]
        )
        vertex_id = str(
            row[
                "vertex_id"
            ]
        )
        vertex_class = str(
            row[
                "vertex_class"
            ]
        )

        lines.append(
            (
                f'<line id="baseline-displacement-{escape(vertex_id)}" '
                f'x1="{_fmt(_sx(rx))}" y1="{_fmt(_sy(ry))}" '
                f'x2="{_fmt(_sx(x))}" y2="{_fmt(_sy(y))}" '
                'stroke="currentColor" stroke-width="1.5" '
                'opacity="0.70"/>'
            )
        )

        lines.append(
            (
                f'<circle id="regular-{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(rx))}" cy="{_fmt(_sy(ry))}" '
                'r="4.5" fill="none" stroke="currentColor" '
                'stroke-width="1.4" opacity="0.55"/>'
            )
        )

        radius_px = (
            "4.8"
            if vertex_class
            == POLAR_ADJACENT_VERTEX
            else "6.2"
        )

        lines.append(
            (
                f'<circle id="frozen-{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(x))}" cy="{_fmt(_sy(y))}" '
                f'r="{radius_px}" fill="none" '
                'stroke="currentColor" stroke-width="2.0"/>'
            )
        )

    # Draw the 12 regular baseline side normals from the inherited apothem.
    lines.append(
        (
            '<g id="regular-side-normal-guides" '
            'stroke="currentColor" fill="none" '
            'opacity="0.22">'
        )
    )

    for index in range(
        12
    ):
        angle = (
            index
            * pi
            / 6.0
        )

        x = (
            REGULAR_APOTHEM
            * cos(
                angle
            )
        )
        y = (
            REGULAR_APOTHEM
            * sin(
                angle
            )
        )

        lines.append(
            (
                f'<line id="regular-normal-{index:02d}" '
                f'x1="{_fmt(CX)}" y1="{_fmt(CY)}" '
                f'x2="{_fmt(_sx(x))}" y2="{_fmt(_sy(y))}" '
                'stroke-width="1"/>'
            )
        )

    lines.append(
        "</g>"
    )

    lines.extend(
        _svg_close()
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


def write_phase7b_svgs(
    directory: str | Path,
) -> tuple[
    Path,
    Path,
]:
    directory = Path(
        directory
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    audit = (
        build_vertex_radius_audit()
    )

    source_path = (
        directory
        / "sommerville_dodecagon_source_constraints.svg"
    )

    baseline_path = (
        directory
        / "sommerville_dodecagon_regular_baseline.svg"
    )

    source_path.write_text(
        source_constraints_svg(
            audit
        ),
        encoding="utf-8",
        newline="\n",
    )

    baseline_path.write_text(
        regular_baseline_svg(
            audit
        ),
        encoding="utf-8",
        newline="\n",
    )

    return (
        source_path,
        baseline_path,
    )
