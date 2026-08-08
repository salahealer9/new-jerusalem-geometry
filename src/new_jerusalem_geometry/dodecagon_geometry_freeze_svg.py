"""Phase 7C geometry-freeze SVG rendering.

The renderer consumes the frozen Phase 7B JSON artifact only.  It does not
rebuild the polar-pivot wall and does not load metrological or historical
comparison data.
"""

from __future__ import annotations

from html import escape
import hashlib
import json
from pathlib import Path
from typing import Any


PHASE = "7C"

STOPPING_STATUS = (
    "EXISTING_FROZEN_WALL_IS_COMPLETE_DODECAGON_GEOMETRY"
)

RECONSTRUCTION_ID = (
    "SOMMERVILLE_DODECAGON_RECONSTRUCTION"
)

PROTOCOL_PATH = (
    "docs/specification/"
    "v0.7_dodecagon_geometry_freeze_protocol.md"
)

PROTOCOL_SHA256 = (
    "58afeb921591d8504018d356cd72cf2b"
    "47e6488f118460c90443cbe88d67d6d5"
)

PHASE7B_JSON_PATH = (
    "data/analysis/njg_michell_v0_7/"
    "dodecagon_vertex_radius_audit.json"
)

PHASE7B_JSON_SHA256 = (
    "7093250082940c16b1d1df240e791ba5"
    "d5e31b7aa10a1866d58ec8e00d3c96b5"
)

FROZEN_V05_GEOMETRY_PATH = (
    "data/geometry/njg_michell_v0_5/"
    "njg_michell_geometry.json"
)

FROZEN_V05_GEOMETRY_SHA256 = (
    "19e22356378d581a2adb35c8f8b8ee023"
    "7f61ab365d8cbc05abc378568e3b6cb"
)

POLAR_ADJACENT_VERTEX = (
    "POLAR_ADJACENT_VERTEX"
)

OBLIQUE_PAIR_VERTEX = (
    "OBLIQUE_PAIR_VERTEX"
)

VIEW_WIDTH = 960
VIEW_HEIGHT = 1140
GEOMETRY_SIZE = 960

SCALE = 44.0
CX = GEOMETRY_SIZE / 2.0
CY = GEOMETRY_SIZE / 2.0

LEGEND_X = 78.0
LEGEND_SEPARATOR_Y = 930.0
LEGEND_TITLE_Y = 975.0
LEGEND_LINE_1_Y = 1007.0
LEGEND_LINE_2_Y = 1035.0
LEGEND_LINE_3_Y = 1063.0
LEGEND_LINE_4_Y = 1091.0


def _sha256(
    path: str | Path,
) -> str:
    return hashlib.sha256(
        Path(
            path
        ).read_bytes()
    ).hexdigest()


def verify_frozen_inputs() -> None:
    checks = (
        (
            PROTOCOL_PATH,
            PROTOCOL_SHA256,
        ),
        (
            PHASE7B_JSON_PATH,
            PHASE7B_JSON_SHA256,
        ),
        (
            FROZEN_V05_GEOMETRY_PATH,
            FROZEN_V05_GEOMETRY_SHA256,
        ),
    )

    for path, expected in checks:
        actual = _sha256(
            path
        )

        if actual != expected:
            raise ValueError(
                "Frozen input hash mismatch: "
                f"{path}: {actual} != {expected}"
            )


def load_frozen_phase7b_audit() -> dict[str, Any]:
    verify_frozen_inputs()

    document = json.loads(
        Path(
            PHASE7B_JSON_PATH
        ).read_text(
            encoding="utf-8"
        )
    )

    if (
        document[
            "stopping_status"
        ]
        != "TWO_SEMANTIC_RADIUS_CLASSES_CONFIRMED"
    ):
        raise ValueError(
            "Unexpected Phase 7B stopping status."
        )

    determinacy = document[
        "determinacy"
    ]

    if (
        determinacy[
            "historical_dimensional_targets_loaded"
        ]
        is not False
    ):
        raise ValueError(
            "Phase 7B target-loading boundary violated."
        )

    if (
        determinacy[
            "historical_comparison_metrics_calculated"
        ]
        is not False
    ):
        raise ValueError(
            "Phase 7B comparison boundary violated."
        )

    return document


def _fmt(
    value: float,
) -> str:
    return (
        f"{value:.6f}"
    )


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


def _metadata(
    *,
    figure_role: str,
    audit: dict[str, Any],
) -> str:
    metadata = {
        "phase": PHASE,
        "figure_role": figure_role,
        "reconstruction_id": (
            RECONSTRUCTION_ID
        ),
        "stopping_status": (
            STOPPING_STATUS
        ),
        "protocol": {
            "path": PROTOCOL_PATH,
            "sha256": PROTOCOL_SHA256,
        },
        "phase7b_input": {
            "path": PHASE7B_JSON_PATH,
            "sha256": PHASE7B_JSON_SHA256,
        },
        "frozen_v0_5_geometry": {
            "path": (
                FROZEN_V05_GEOMETRY_PATH
            ),
            "sha256": (
                FROZEN_V05_GEOMETRY_SHA256
            ),
        },
        "wall_model": (
            audit[
                "frozen_geometry_input"
            ][
                "wall_model"
            ]
        ),
        "historical_targets_loaded": False,
        "historical_comparison_metrics_calculated": False,
        "new_continuous_geometric_parameters": 0,
        "new_fitted_scale_parameters": 0,
        "new_discrete_candidate_choices": 0,
        "new_wall_vertices": 0,
        "new_wall_sides": 0,
    }

    return json.dumps(
        metadata,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=True,
        allow_nan=False,
    )


def _svg_open(
    *,
    title: str,
    description: str,
    figure_role: str,
    audit: dict[str, Any],
) -> list[str]:
    return [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{VIEW_WIDTH}" height="{VIEW_HEIGHT}" '
            f'viewBox="0 0 {VIEW_WIDTH} {VIEW_HEIGHT}" '
            'role="img">'
        ),
        (
            f"<title>{escape(title)}</title>"
        ),
        (
            f"<desc>{escape(description)}</desc>"
        ),
        (
            "<metadata>"
            + escape(
                _metadata(
                    figure_role=figure_role,
                    audit=audit,
                )
            )
            + "</metadata>"
        ),
        (
            '<g id="coordinate-frame" '
            'fill="none" stroke="currentColor" '
            'stroke-width="1" opacity="0.16">'
        ),
        (
            f'<line id="axis-x" x1="70" '
            f'y1="{_fmt(CY)}" x2="890" '
            f'y2="{_fmt(CY)}"/>'
        ),
        (
            f'<line id="axis-y" x1="{_fmt(CX)}" '
            f'y1="70" x2="{_fmt(CX)}" '
            f'y2="890"/>'
        ),
        "</g>",
    ]


def _text(
    *,
    x: float,
    y: float,
    text: str,
    element_id: str,
    anchor: str = "start",
    size: int = 15,
    opacity: float = 0.82,
) -> str:
    return (
        f'<text id="{escape(element_id)}" '
        f'x="{_fmt(x)}" y="{_fmt(y)}" '
        f'text-anchor="{anchor}" '
        f'font-size="{size}" '
        'font-family="sans-serif" '
        'fill="currentColor" '
        f'opacity="{opacity:.2f}">'
        f"{escape(text)}"
        "</text>"
    )


def reconstruction_svg(
    audit: dict[str, Any],
) -> str:
    lines = _svg_open(
        title=(
            "Frozen Sommerville dodecagon reconstruction"
        ),
        description=(
            "The frozen v0.5 polar-pivot wall interpreted as the complete "
            "Figure 30 irregular dodecagon geometry, with two semantic "
            "vertex-radius classes in normalized units."
        ),
        figure_role=(
            "canonical_reconstruction"
        ),
        audit=audit,
    )

    wall_points = _wall_points(
        audit
    )

    lines.append(
        (
            '<polygon id="sommerville-dodecagon-reconstruction" '
            f'points="{_point_string(wall_points)}" '
            'fill="none" stroke="currentColor" '
            'stroke-width="2.8"/>'
        )
    )

    lines.append(
        (
            '<circle id="construction-centre" '
            f'cx="{_fmt(CX)}" cy="{_fmt(CY)}" '
            'r="4.8" fill="currentColor"/>'
        )
    )

    polar_side_indices = set(
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

        is_polar = (
            index
            in polar_side_indices
        )

        lines.append(
            (
                f'<line id="wall-side-{index:02d}-'
                f'{"polar" if is_polar else "oblique"}" '
                f'x1="{_fmt(_sx(x1))}" y1="{_fmt(_sy(y1))}" '
                f'x2="{_fmt(_sx(x2))}" y2="{_fmt(_sy(y2))}" '
                'stroke="currentColor" '
                f'stroke-width="{"4.0" if is_polar else "2.0"}" '
                f'opacity="{"0.90" if is_polar else "0.48"}"/>'
            )
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

        is_polar_adjacent = (
            vertex_class
            == POLAR_ADJACENT_VERTEX
        )

        lines.append(
            (
                f'<line id="radius-{escape(vertex_id)}" '
                f'x1="{_fmt(CX)}" y1="{_fmt(CY)}" '
                f'x2="{_fmt(_sx(x))}" y2="{_fmt(_sy(y))}" '
                'stroke="currentColor" stroke-width="1.1" '
                f'opacity="{"0.24" if is_polar_adjacent else "0.62"}"/>'
            )
        )

        lines.append(
            (
                f'<circle id="{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(x))}" cy="{_fmt(_sy(y))}" '
                f'r="{"5.0" if is_polar_adjacent else "7.0"}" '
                'fill="none" stroke="currentColor" '
                f'stroke-width="{"1.8" if is_polar_adjacent else "2.5"}" '
                f'opacity="{"0.74" if is_polar_adjacent else "1.00"}"/>'
            )
        )

    comparison = audit[
        "normalized_comparison"
    ]

    lines.append(
        (
            '<line id="legend-separator" '
            f'x1="70" y1="{_fmt(LEGEND_SEPARATOR_Y)}" '
            f'x2="890" y2="{_fmt(LEGEND_SEPARATOR_Y)}" '
            'stroke="currentColor" stroke-width="1" '
            'opacity="0.24"/>'
        )
    )

    lines.extend(
        [
            _text(
                x=LEGEND_X,
                y=LEGEND_TITLE_Y,
                text=(
                    "Frozen v0.5 POLAR_PIVOT_WALL"
                ),
                element_id="label-reconstruction",
                size=18,
                opacity=0.95,
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_1_Y,
                text=(
                    "8 polar-adjacent vertices: "
                    f"r = {comparison['polar_adjacent_mean_radius']:.12f} u"
                ),
                element_id="label-polar-radius",
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_2_Y,
                text=(
                    "4 oblique-pair vertices: "
                    f"r = {comparison['oblique_pair_mean_radius']:.12f} u"
                ),
                element_id="label-oblique-radius",
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_3_Y,
                text=(
                    "No new geometry; historical targets not loaded"
                ),
                element_id="label-boundary",
                opacity=0.66,
            ),
        ]
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


def comparison_svg(
    audit: dict[str, Any],
) -> str:
    lines = _svg_open(
        title=(
            "Regular dodecagon versus frozen polar-pivot wall"
        ),
        description=(
            "Geometry-only comparison showing that eight polar-adjacent "
            "vertices remain on the regular circumradius while four "
            "oblique-pair vertices are displaced inward."
        ),
        figure_role=(
            "regular_vs_frozen_comparison"
        ),
        audit=audit,
    )

    wall_points = _wall_points(
        audit
    )

    regular_points = _regular_points(
        audit
    )

    lines.extend(
        [
            (
                '<polygon id="regular-dodecagon-baseline" '
                f'points="{_point_string(regular_points)}" '
                'fill="none" stroke="currentColor" '
                'stroke-width="1.8" stroke-dasharray="10 7" '
                'opacity="0.45"/>'
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
                'r="4.8" fill="currentColor"/>'
            ),
        ]
    )

    for row in audit[
        "vertices"
    ]:
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

        is_oblique_pair = (
            vertex_class
            == OBLIQUE_PAIR_VERTEX
        )

        lines.append(
            (
                f'<circle id="regular-{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(rx))}" cy="{_fmt(_sy(ry))}" '
                'r="4.0" fill="none" stroke="currentColor" '
                'stroke-width="1.2" opacity="0.42"/>'
            )
        )

        lines.append(
            (
                f'<circle id="frozen-{escape(vertex_id)}" '
                f'cx="{_fmt(_sx(x))}" cy="{_fmt(_sy(y))}" '
                f'r="{"7.0" if is_oblique_pair else "4.8"}" '
                'fill="none" stroke="currentColor" '
                f'stroke-width="{"2.6" if is_oblique_pair else "1.6"}" '
                f'opacity="{"1.00" if is_oblique_pair else "0.72"}"/>'
            )
        )

        if is_oblique_pair:
            lines.append(
                (
                    f'<line id="inward-displacement-{escape(vertex_id)}" '
                    f'x1="{_fmt(_sx(rx))}" y1="{_fmt(_sy(ry))}" '
                    f'x2="{_fmt(_sx(x))}" y2="{_fmt(_sy(y))}" '
                    'stroke="currentColor" stroke-width="3.0" '
                    'opacity="0.92"/>'
                )
            )

    comparison = audit[
        "normalized_comparison"
    ]

    lines.append(
        (
            '<line id="legend-separator" '
            f'x1="70" y1="{_fmt(LEGEND_SEPARATOR_Y)}" '
            f'x2="890" y2="{_fmt(LEGEND_SEPARATOR_Y)}" '
            'stroke="currentColor" stroke-width="1" '
            'opacity="0.24"/>'
        )
    )

    lines.extend(
        [
            _text(
                x=LEGEND_X,
                y=LEGEND_TITLE_Y,
                text=(
                    "Regular baseline vs frozen polar-pivot wall"
                ),
                element_id="label-comparison",
                size=18,
                opacity=0.95,
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_1_Y,
                text=(
                    "regular radius = "
                    f"{comparison['regular_baseline_radius']:.12f} u"
                ),
                element_id="label-regular-radius",
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_2_Y,
                text=(
                    "oblique-pair inward displacement = "
                    f"{comparison['oblique_pair_minus_regular']:.12f} u"
                ),
                element_id="label-inward-displacement",
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_3_Y,
                text=(
                    "raw normalized class ratio = "
                    f"{comparison['polar_adjacent_to_oblique_pair_ratio']:.12f}"
                ),
                element_id="label-class-ratio",
            ),
            _text(
                x=LEGEND_X,
                y=LEGEND_LINE_4_Y,
                text=(
                    "8 vertices unchanged; 4 vertices displaced inward"
                ),
                element_id="label-eight-four",
                opacity=0.70,
            ),
        ]
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


def write_phase7c_svgs(
    directory: str | Path,
) -> tuple[
    Path,
    Path,
]:
    audit = load_frozen_phase7b_audit()

    directory = Path(
        directory
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    reconstruction_path = (
        directory
        / "sommerville_dodecagon_reconstruction.svg"
    )

    comparison_path = (
        directory
        / "sommerville_dodecagon_comparison.svg"
    )

    reconstruction_path.write_text(
        reconstruction_svg(
            audit
        ),
        encoding="utf-8",
        newline="\n",
    )

    comparison_path.write_text(
        comparison_svg(
            audit
        ),
        encoding="utf-8",
        newline="\n",
    )

    return (
        reconstruction_path,
        comparison_path,
    )
