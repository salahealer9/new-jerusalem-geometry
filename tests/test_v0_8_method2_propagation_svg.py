from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.method2_propagation_svg import (
    PROPAGATION_SHA256,
    SYMBOLIC_AUDIT_SHA256,
    method2_propagation_to_svg,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

PROPAGATION_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

SYMBOLIC_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_symbolic_gap_audit.json"
)

SVG = (
    ROOT
    / "figures"
    / "generated"
    / "v0.8_method2_7_21_42.svg"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _payload(
    path: Path,
):
    return json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )


def _render() -> str:
    return method2_propagation_to_svg(
        _payload(
            PROPAGATION_JSON
        ),
        _payload(
            SYMBOLIC_JSON
        ),
    )


def test_frozen_input_hashes() -> None:
    assert (
        _sha256(
            PROPAGATION_JSON
        )
        == PROPAGATION_SHA256
        == "5af0b893ef9f18f5bb6c04e013f12298d816f426a2a248eccbd9230ab5ad4a43"
    )

    assert (
        _sha256(
            SYMBOLIC_JSON
        )
        == SYMBOLIC_AUDIT_SHA256
        == "db314c890636a2a435d4065a42c49c08bba8df00c7e29a2cca156b00eef47078"
    )


def test_svg_exists() -> None:
    assert SVG.is_file()


def test_svg_is_valid_xml() -> None:
    root = ET.fromstring(
        SVG.read_text(
            encoding="utf-8"
        )
    )

    assert root.tag.endswith(
        "svg"
    )


def test_svg_is_deterministic() -> None:
    assert (
        _render()
        == _render()
    )


def test_tracked_svg_matches_canonical_render() -> None:
    assert (
        SVG.read_text(
            encoding="utf-8"
        )
        == _render()
    )


def test_svg_has_transparent_background() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    assert (
        "<rect"
        not in text
        or "reciprocal-carrier"
        in text
    )

    forbidden_backgrounds = (
        'class="background"',
        'id="background"',
        'fill="white"',
        'fill="#fff" width="1200"',
    )

    for token in forbidden_backgrounds:
        assert token not in text


def test_svg_has_three_named_panels() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    required = (
        "Method 2 local step",
        "Original triangle",
        "Original + reciprocal",
    )

    for phrase in required:
        assert phrase in text


def test_svg_exposes_7_21_42_counts() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    required = (
        "7-mark operational completion",
        "3 carriers x 7 = 21 semantic marks",
        "6 carriers x 7 = 42 semantic marks",
    )

    for phrase in required:
        assert phrase in text


def test_svg_exposes_only_frozen_symbolic_summaries() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    required = (
        "alpha_2 = acos(5/8)",
        "15 L : 6 S",
        "RMS = sqrt(10) delta",
        "36 L : 6 S",
        "RMS = sqrt(6) delta",
    )

    for phrase in required:
        assert phrase in text


def test_svg_has_exactly_six_small_gap_markers_per_propagated_panel() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    assert (
        text.count(
            'class="small-gap-marker"'
        )
        == 12
    )


def test_svg_distinguishes_reciprocal_triangle_without_new_data() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    assert (
        'class="triangle-reciprocal"'
        in text
    )

    assert (
        "solid triangle = original; dashed = reciprocal"
        in text
    )


def test_svg_declares_visualization_only_boundary() -> None:
    text = SVG.read_text(
        encoding="utf-8"
    )

    assert (
        "Visualization only"
        in text
    )

    assert (
        "frozen Phase 8E/8F artifacts"
        in text
    )


def test_package_version_is_0_8_0_at_release_closeout() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
