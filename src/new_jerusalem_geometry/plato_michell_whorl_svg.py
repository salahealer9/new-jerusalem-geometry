"""Deterministic SVG capstone for the frozen Plato–Michell whorl reconstruction.

The renderer is a pure downstream view of the Phase 10E reconstruction data.
It performs no fitting, optimisation, permutation search, scale estimation, or
historical inference.

All mathematical quantities rendered in the geometry are supplied by the
reconstruction mapping. Fixed colours, typography, canvas dimensions, and
annotation wording are presentation constants only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from html import escape
import math
import textwrap
from typing import Any


SVG_NS = "http://www.w3.org/2000/svg"

CANVAS_WIDTH = 1800
CANVAS_HEIGHT = 1080

DIAGRAM_CX = 470.0
DIAGRAM_CY = 560.0
DIAGRAM_RADIUS_PX = 380.0

# Presentation palette only. These values do not encode geometry.
BACKGROUND = "#fbfaf7"
INK = "#17212b"
MUTED = "#5d6771"
GRID = "#aab3bb"
PANEL = "#f1f3f4"
PLATO = "#72538a"
MICHELL = "#ad6b19"
PROJECT = "#35636f"
FIRST_CORRESPONDENCE = "#b8860b"
SECOND_CORRESPONDENCE = "#255c99"
OUTER_BOUNDARY = "#7a3f32"

RING_FILLS = (
    "#e8edf0",
    "#dce5e9",
    "#e9e5ef",
    "#e7ebdf",
    "#eee5dd",
    "#dde9e4",
    "#e8e2dc",
    "#dfe3ea",
)

# Presentation labels only; the numerical values are always read from Phase 10E.
FIRST_CORRESPONDENCE_LABEL = "Earth-radius / Magnesia correspondence"
SECOND_CORRESPONDENCE_LABEL = "New Jerusalem outer-circle correspondence"
OUTER_CORRESPONDENCE_LABEL = "Michell precessional correspondence"


def _number(value: Any) -> str:
    """Return stable human-readable scalar text."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("SVG input contains a non-finite number")
        return f"{value:.12g}"
    return str(value)


def _require_sequence(
    mapping: Mapping[str, Any],
    key: str,
    expected_length: int,
) -> Sequence[Any]:
    value = mapping.get(key)
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError(f"{key!r} must be a sequence")
    if len(value) != expected_length:
        raise ValueError(
            f"{key!r} must contain {expected_length} entries; got {len(value)}"
        )
    return value


def _validate_reconstruction(data: Mapping[str, Any]) -> None:
    """Validate the structural invariants required by the visual capstone."""
    if data.get("audit_phase") != "10E":
        raise ValueError("Phase 10G requires the frozen Phase 10E reconstruction")

    if data.get("provenance_class") != "PROJECT_RECONSTRUCTION":
        raise ValueError("Unexpected reconstruction provenance class")

    if data.get("status") != "MICHELL_PLATO_NUMERICAL_RECONSTRUCTION_COMPLETE":
        raise ValueError("Phase 10E reconstruction is not marked complete")

    algorithm = data.get("deterministic_algorithm")
    if not isinstance(algorithm, Mapping):
        raise ValueError("Missing deterministic_algorithm mapping")

    zero_search_fields = (
        "free_parameters",
        "nearest_match_choices",
        "optimizations",
        "permutation_searches",
        "scale_fits",
    )
    for key in zero_search_fields:
        if algorithm.get(key) != 0:
            raise ValueError(f"Phase 10G requires {key}=0")

    source = data.get("source_inputs")
    reconstructed = data.get("reconstructed")
    boundary = data.get("historical_boundary")

    if not isinstance(source, Mapping):
        raise ValueError("Missing source_inputs mapping")
    if not isinstance(reconstructed, Mapping):
        raise ValueError("Missing reconstructed mapping")
    if not isinstance(boundary, Mapping):
        raise ValueError("Missing historical_boundary mapping")

    whorls = _require_sequence(reconstructed, "center_out_whorls", 8)
    widths = _require_sequence(reconstructed, "center_out_ring_widths", 8)
    radii = _require_sequence(
        reconstructed,
        "cumulative_radii_including_shaft",
        9,
    )
    scaled_radii = _require_sequence(
        reconstructed,
        "scaled_cumulative_radii_including_shaft",
        9,
    )
    scaled_widths = _require_sequence(reconstructed, "scaled_ring_widths", 8)

    shaft_radius = reconstructed.get("shaft_radius")
    scale_factor = reconstructed.get("scale_factor")
    full_radius = reconstructed.get("full_radius")

    if shaft_radius != radii[0]:
        raise ValueError("shaft_radius does not equal first cumulative radius")
    if full_radius != radii[-1]:
        raise ValueError("full_radius does not equal final cumulative radius")

    for index, width in enumerate(widths):
        if radii[index] + width != radii[index + 1]:
            raise ValueError(
                "cumulative radii are inconsistent with center-out ring widths"
            )

    if reconstructed.get("scaled_shaft_radius") != shaft_radius * scale_factor:
        raise ValueError("scaled shaft radius is inconsistent with scale factor")

    if reconstructed.get("scaled_outer_radius") != full_radius * scale_factor:
        raise ValueError("scaled outer radius is inconsistent with scale factor")

    if list(scaled_widths) != [width * scale_factor for width in widths]:
        raise ValueError("scaled ring widths are inconsistent with scale factor")

    if list(scaled_radii) != [radius * scale_factor for radius in radii]:
        raise ValueError(
            "scaled cumulative radii are inconsistent with scale factor"
        )

    source_whorls = _require_sequence(source, "michell_center_out_whorls", 8)
    if list(source_whorls) != list(whorls):
        raise ValueError("reconstructed whorl order differs from source input")

    plato_order = _require_sequence(
        source,
        "plato_width_order_broadest_to_narrowest",
        8,
    )
    michell_order = _require_sequence(
        source,
        "michell_width_order_broadest_to_narrowest",
        8,
    )
    if list(plato_order) != list(michell_order):
        raise ValueError("Plato/Michell ordinal width orders are not equal")

    if boundary.get("plato_supplies_numeric_widths") is not False:
        raise ValueError("Historical boundary must retain ordinal-only Plato data")
    if boundary.get("michell_supplies_numeric_interpretation") is not True:
        raise ValueError("Historical boundary lost Michell numeric provenance")
    if boundary.get("project_arithmetic_reproduces_michell") is not True:
        raise ValueError("Historical boundary lost project reconstruction status")
    if boundary.get("plato_intention_established") is not False:
        raise ValueError("Renderer must not imply Plato intention is established")


def _text(
    parts: list[str],
    x: float,
    y: float,
    text: str,
    *,
    css_class: str = "",
    anchor: str | None = None,
    size: int | None = None,
    weight: str | None = None,
) -> None:
    attrs = [
        f'x="{x:.2f}"',
        f'y="{y:.2f}"',
    ]
    if css_class:
        attrs.append(f'class="{escape(css_class)}"')
    if anchor is not None:
        attrs.append(f'text-anchor="{escape(anchor)}"')
    if size is not None:
        attrs.append(f'font-size="{size}"')
    if weight is not None:
        attrs.append(f'font-weight="{escape(weight)}"')
    parts.append(f"<text {' '.join(attrs)}>{escape(text)}</text>")


def _line(
    parts: list[str],
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    css_class: str = "",
    stroke: str | None = None,
    width: float | None = None,
    dash: str | None = None,
) -> None:
    attrs = [
        f'x1="{x1:.2f}"',
        f'y1="{y1:.2f}"',
        f'x2="{x2:.2f}"',
        f'y2="{y2:.2f}"',
    ]
    if css_class:
        attrs.append(f'class="{escape(css_class)}"')
    if stroke is not None:
        attrs.append(f'stroke="{escape(stroke)}"')
    if width is not None:
        attrs.append(f'stroke-width="{width:.2f}"')
    if dash is not None:
        attrs.append(f'stroke-dasharray="{escape(dash)}"')
    parts.append(f"<line {' '.join(attrs)} />")


def _circle(
    parts: list[str],
    *,
    cx: float,
    cy: float,
    r: float,
    fill: str,
    stroke: str,
    stroke_width: float,
    element_id: str | None = None,
    extra_attrs: Mapping[str, Any] | None = None,
) -> None:
    attrs = [
        f'cx="{cx:.2f}"',
        f'cy="{cy:.2f}"',
        f'r="{r:.2f}"',
        f'fill="{escape(fill)}"',
        f'stroke="{escape(stroke)}"',
        f'stroke-width="{stroke_width:.2f}"',
    ]
    if element_id is not None:
        attrs.insert(0, f'id="{escape(element_id)}"')
    if extra_attrs:
        for key, value in extra_attrs.items():
            attrs.append(f'{escape(key)}="{escape(_number(value))}"')
    parts.append(f"<circle {' '.join(attrs)} />")


def plato_michell_whorl_capstone_to_svg(
    data: Mapping[str, Any],
) -> str:
    """Render the frozen Phase 10E reconstruction as a deterministic SVG."""
    _validate_reconstruction(data)

    source = data["source_inputs"]
    reconstructed = data["reconstructed"]
    historical_boundary = data["historical_boundary"]
    algorithm = data["deterministic_algorithm"]

    whorls = list(reconstructed["center_out_whorls"])
    widths = list(reconstructed["center_out_ring_widths"])
    radii = list(reconstructed["cumulative_radii_including_shaft"])
    scaled_radii = list(
        reconstructed["scaled_cumulative_radii_including_shaft"]
    )
    shaft_radius = reconstructed["shaft_radius"]
    full_radius = reconstructed["full_radius"]
    scale_factor = reconstructed["scale_factor"]
    base_sequence = list(source["michell_base_sequence"])
    plato_order = list(source["plato_width_order_broadest_to_narrowest"])
    michell_order = list(source["michell_width_order_broadest_to_narrowest"])

    px_per_unit = DIAGRAM_RADIUS_PX / float(full_radius)

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="{SVG_NS}" '
        f'width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" '
        f'viewBox="0 0 {CANVAS_WIDTH} {CANVAS_HEIGHT}" '
        f'data-upstream-audit-phase="{escape(str(data["audit_phase"]))}" '
        f'data-provenance-class="{escape(str(data["provenance_class"]))}" '
        f'data-free-parameters="{algorithm["free_parameters"]}">'
    )
    parts.append(
        "<title>The Spindle of Necessity — Plato's Eight Whorls</title>"
    )
    parts.append(
        "<desc>"
        "Deterministic reconstruction from Plato's ordinal ranking and "
        "Michell's musical-number interpretation. Eight concentric whorls and "
        "a central shaft show the cumulative radial construction, with the "
        "first two New Jerusalem correspondences and the outer boundary "
        "highlighted. The provenance boundary distinguishes Plato's ordinal "
        "information, Michell's numerical interpretation, and the project's "
        "arithmetic reconstruction."
        "</desc>"
    )
    parts.append(
        "<style>"
        "text{font-family:Arial,Helvetica,sans-serif;fill:" + INK + ";}"
        ".title{font-size:34px;font-weight:700;}"
        ".subtitle{font-size:18px;fill:" + MUTED + ";}"
        ".section{font-size:20px;font-weight:700;}"
        ".body{font-size:16px;}"
        ".small{font-size:14px;fill:" + MUTED + ";}"
        ".tiny{font-size:12px;fill:" + MUTED + ";}"
        ".table-head{font-size:14px;font-weight:700;fill:" + MUTED + ";}"
        ".table-text{font-size:15px;}"
        ".ring-label{font-size:14px;font-weight:700;}"
        ".callout{font-size:15px;font-weight:700;}"
        "</style>"
    )
    parts.append(
        f'<rect x="0" y="0" width="{CANVAS_WIDTH}" height="{CANVAS_HEIGHT}" '
        f'fill="{BACKGROUND}" />'
    )

    _text(
        parts,
        60,
        62,
        "The Spindle of Necessity — Plato's Eight Whorls",
        css_class="title",
    )
    _text(
        parts,
        60,
        94,
        (
            "Deterministic reconstruction from Plato's ordinal ranking and "
            "Michell's musical-number interpretation"
        ),
        css_class="subtitle",
    )

    # ------------------------------------------------------------------
    # Left: exact annular geometry
    # ------------------------------------------------------------------
    parts.append('<g id="whorl-geometry">')

    # Draw each annulus by using its exact mean radius and exact radial width.
    # Stroke geometry therefore spans [inner_radius, outer_radius] exactly.
    for index, (whorl, width) in enumerate(zip(whorls, widths, strict=True)):
        inner_radius = radii[index]
        outer_radius = radii[index + 1]
        mean_radius = (inner_radius + outer_radius) / 2.0
        ring_radius_px = mean_radius * px_per_unit
        ring_width_px = width * px_per_unit

        _circle(
            parts,
            cx=DIAGRAM_CX,
            cy=DIAGRAM_CY,
            r=ring_radius_px,
            fill="none",
            stroke=RING_FILLS[index % len(RING_FILLS)],
            stroke_width=ring_width_px,
            element_id=f"whorl-{whorl}",
            extra_attrs={
                "data-whorl": whorl,
                "data-width": width,
                "data-inner-radius": inner_radius,
                "data-outer-radius": outer_radius,
                "data-scaled-outer-radius": scaled_radii[index + 1],
            },
        )

    # Shaft.
    _circle(
        parts,
        cx=DIAGRAM_CX,
        cy=DIAGRAM_CY,
        r=float(shaft_radius) * px_per_unit,
        fill=INK,
        stroke=INK,
        stroke_width=1.0,
        element_id="shaft",
        extra_attrs={
            "data-radius": shaft_radius,
            "data-scaled-radius": scaled_radii[0],
        },
    )

    # All exact cumulative boundaries.
    parts.append('<g id="cumulative-boundaries">')
    for index, radius in enumerate(radii[1:], start=1):
        _circle(
            parts,
            cx=DIAGRAM_CX,
            cy=DIAGRAM_CY,
            r=float(radius) * px_per_unit,
            fill="none",
            stroke=GRID,
            stroke_width=1.2,
            element_id=f"boundary-{index}",
            extra_attrs={
                "data-cumulative-index": index,
                "data-radius": radius,
                "data-scaled-radius": scaled_radii[index],
            },
        )
    parts.append("</g>")

    # Highlight the first and second cumulative boundaries and the full radius.
    highlight_specs = (
        (
            "first-cumulative-correspondence",
            1,
            FIRST_CORRESPONDENCE,
            FIRST_CORRESPONDENCE_LABEL,
        ),
        (
            "second-cumulative-correspondence",
            2,
            SECOND_CORRESPONDENCE,
            SECOND_CORRESPONDENCE_LABEL,
        ),
        (
            "outer-boundary-correspondence",
            len(radii) - 1,
            OUTER_BOUNDARY,
            OUTER_CORRESPONDENCE_LABEL,
        ),
    )
    parts.append('<g id="key-correspondences">')
    for element_id, index, colour, label in highlight_specs:
        radius = radii[index]
        scaled = scaled_radii[index]
        _circle(
            parts,
            cx=DIAGRAM_CX,
            cy=DIAGRAM_CY,
            r=float(radius) * px_per_unit,
            fill="none",
            stroke=colour,
            stroke_width=4.0 if index != len(radii) - 1 else 5.0,
            element_id=element_id,
            extra_attrs={
                "data-radius": radius,
                "data-scaled-radius": scaled,
                "data-label": label,
            },
        )
    parts.append("</g>")

    # Direct whorl identifiers placed deterministically at each annulus midpoint.
    # Angles are presentation choices only and do not drive the geometry.
    label_angles_deg = (-22, 24, 66, 108, 150, 192, 234, 276)
    for index, (whorl, width, angle_deg) in enumerate(
        zip(whorls, widths, label_angles_deg, strict=True)
    ):
        inner_radius = radii[index]
        outer_radius = radii[index + 1]
        mean_radius_px = ((inner_radius + outer_radius) / 2.0) * px_per_unit
        angle = math.radians(angle_deg)
        x = DIAGRAM_CX + mean_radius_px * math.cos(angle)
        y = DIAGRAM_CY + mean_radius_px * math.sin(angle)
        _text(
            parts,
            x,
            y,
            f"W{whorl}",
            css_class="ring-label",
            anchor="middle",
        )

    # Centre label.
    _text(
        parts,
        DIAGRAM_CX,
        DIAGRAM_CY + 5,
        _number(shaft_radius),
        css_class="tiny",
        anchor="middle",
    )

    parts.append("</g>")

    _text(
        parts,
        72,
        986,
        (
            f"Exact radial geometry: shaft r={_number(shaft_radius)}; "
            f"outer r={_number(full_radius)}; scale ×{_number(scale_factor)}"
        ),
        css_class="small",
    )

    # ------------------------------------------------------------------
    # Right: provenance, table, and deterministic chain
    # ------------------------------------------------------------------
    panel_x = 900
    panel_width = 830
    parts.append(
        f'<rect x="{panel_x}" y="135" width="{panel_width}" height="845" '
        f'rx="14" fill="{PANEL}" stroke="#d2d7db" stroke-width="1.5" />'
    )

    _text(parts, 930, 178, "Provenance boundary", css_class="section")

    legend = (
        (PLATO, "PLATO", "ordinal rim-width order only"),
        (
            MICHELL,
            "MICHELL",
            f"musical numbers, shaft rule, and scale ×{_number(scale_factor)}",
        ),
        (
            PROJECT,
            "PROJECT",
            "exact cumulative reconstruction; 0 free parameters",
        ),
    )
    legend_y = 214
    for colour, label, detail in legend:
        parts.append(
            f'<rect x="932" y="{legend_y - 15}" width="18" height="18" '
            f'rx="3" fill="{colour}" />'
        )
        _text(
            parts,
            962,
            legend_y,
            f"{label}: {detail}",
            css_class="body",
        )
        legend_y += 30

    _text(parts, 930, 325, "Whorl construction", css_class="section")

    table_x = (932, 1030, 1130, 1280, 1455)
    headers = ("Layer", "Whorl", "Width", "Cum. radius", f"×{scale_factor}")
    for x, header in zip(table_x, headers, strict=True):
        _text(parts, x, 356, header, css_class="table-head")

    _line(parts, 930, 366, 1695, 366, stroke="#c2c8cd", width=1.0)

    table_rows: list[tuple[str, str, str, str, str]] = [
        (
            "Shaft",
            "—",
            "—",
            _number(radii[0]),
            _number(scaled_radii[0]),
        )
    ]
    for index, (whorl, width) in enumerate(zip(whorls, widths, strict=True)):
        table_rows.append(
            (
                f"Whorl {whorl}",
                _number(whorl),
                _number(width),
                _number(radii[index + 1]),
                _number(scaled_radii[index + 1]),
            )
        )

    row_y = 395
    for row_index, row in enumerate(table_rows):
        # Highlight the two key cumulative rows and the outermost row.
        if row_index == 1:
            fill = "#f6edcf"
        elif row_index == 2:
            fill = "#dfeaf7"
        elif row_index == len(table_rows) - 1:
            fill = "#eee2dd"
        else:
            fill = "#ffffff"

        parts.append(
            f'<rect x="924" y="{row_y - 22}" width="780" height="31" '
            f'rx="5" fill="{fill}" opacity="0.92" />'
        )
        for x, value in zip(table_x, row, strict=True):
            _text(parts, x, row_y, value, css_class="table-text")
        row_y += 34

    _text(parts, 930, 726, "Deterministic chain", css_class="section")

    sequence_text = ", ".join(_number(v) for v in base_sequence)
    order_text = ", ".join(_number(v) for v in plato_order)
    center_out_text = ", ".join(_number(v) for v in widths)
    cumulative_text = ", ".join(_number(v) for v in radii)

    _text(
        parts,
        930,
        758,
        f"Michell musical sequence: {sequence_text}",
        css_class="body",
    )
    _text(
        parts,
        930,
        788,
        f"Plato = Michell width order: {order_text}",
        css_class="body",
    )
    _text(
        parts,
        930,
        818,
        f"Centre-out widths: {center_out_text}",
        css_class="body",
    )
    _text(
        parts,
        930,
        848,
        f"Cumulative radii: {cumulative_text}",
        css_class="body",
    )

    _text(parts, 930, 891, "Key highlighted boundaries", css_class="section")
    callouts = (
        (
            FIRST_CORRESPONDENCE,
            FIRST_CORRESPONDENCE_LABEL,
            radii[1],
            scaled_radii[1],
        ),
        (
            SECOND_CORRESPONDENCE,
            SECOND_CORRESPONDENCE_LABEL,
            radii[2],
            scaled_radii[2],
        ),
        (
            OUTER_BOUNDARY,
            OUTER_CORRESPONDENCE_LABEL,
            radii[-1],
            scaled_radii[-1],
        ),
    )
    callout_y = 920
    for colour, label, radius, scaled in callouts:
        parts.append(
            f'<circle cx="942" cy="{callout_y - 5}" r="6" fill="{colour}" />'
        )
        _text(
            parts,
            958,
            callout_y,
            f"{label}: r={_number(radius)} → {_number(scaled)}",
            css_class="callout",
        )
        callout_y += 27

    # Historical-boundary note comes directly from the frozen 10E JSON.
    note = str(historical_boundary.get("note", "")).strip()
    note_lines = textwrap.wrap(note, width=105) or [""]
    note_y = 1010
    for line in note_lines[:2]:
        _text(parts, 60, note_y, line, css_class="tiny")
        note_y += 18

    # Machine-readable source/order metadata.
    parts.append(
        '<metadata id="phase-10g-metadata">'
        f'<upstream-audit-phase>{escape(str(data["audit_phase"]))}</upstream-audit-phase>'
        f'<upstream-status>{escape(str(data["status"]))}</upstream-status>'
        f'<provenance-class>{escape(str(data["provenance_class"]))}</provenance-class>'
        f'<scale-factor>{escape(_number(scale_factor))}</scale-factor>'
        f'<plato-width-order>{escape(",".join(_number(v) for v in plato_order))}</plato-width-order>'
        f'<michell-width-order>{escape(",".join(_number(v) for v in michell_order))}</michell-width-order>'
        f'<free-parameters>{escape(_number(algorithm["free_parameters"]))}</free-parameters>'
        "</metadata>"
    )

    parts.append("</svg>")
    return "\n".join(parts)
