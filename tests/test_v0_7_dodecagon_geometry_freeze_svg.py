from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

from new_jerusalem_geometry.dodecagon_geometry_freeze_svg import (
    PHASE7B_JSON_SHA256,
    PROTOCOL_SHA256,
    STOPPING_STATUS,
    comparison_svg,
    load_frozen_phase7b_audit,
    reconstruction_svg,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "dodecagon_geometry_freeze_svg.py"
)

RECONSTRUCTION_SVG = (
    ROOT
    / "figures"
    / "generated"
    / "sommerville_dodecagon_reconstruction.svg"
)

COMPARISON_SVG = (
    ROOT
    / "figures"
    / "generated"
    / "sommerville_dodecagon_comparison.svg"
)


def test_phase7c_protocol_hash_is_frozen() -> None:
    path = (
        ROOT
        / "docs"
        / "specification"
        / "v0.7_dodecagon_geometry_freeze_protocol.md"
    )

    assert (
        hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        == PROTOCOL_SHA256
    )


def test_phase7b_json_hash_is_frozen() -> None:
    path = (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_7"
        / "dodecagon_vertex_radius_audit.json"
    )

    assert (
        hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        == PHASE7B_JSON_SHA256
    )


def test_renderer_consumes_frozen_phase7b_result() -> None:
    audit = load_frozen_phase7b_audit()

    assert (
        audit[
            "stopping_status"
        ]
        == "TWO_SEMANTIC_RADIUS_CLASSES_CONFIRMED"
    )


def test_reconstruction_svg_is_deterministic() -> None:
    audit = load_frozen_phase7b_audit()

    assert (
        RECONSTRUCTION_SVG.read_text(
            encoding="utf-8"
        )
        == reconstruction_svg(
            audit
        )
    )


def test_comparison_svg_is_deterministic() -> None:
    audit = load_frozen_phase7b_audit()

    assert (
        COMPARISON_SVG.read_text(
            encoding="utf-8"
        )
        == comparison_svg(
            audit
        )
    )


def test_svg_backgrounds_are_transparent() -> None:
    for path in (
        RECONSTRUCTION_SVG,
        COMPARISON_SVG,
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        assert (
            "<rect"
            not in text
        )


def test_reconstruction_contains_all_twelve_frozen_vertices() -> None:
    text = RECONSTRUCTION_SVG.read_text(
        encoding="utf-8"
    )

    for index in range(
        12
    ):
        assert (
            f'id="wall_vertex_{index:02d}"'
            in text
        )


def test_comparison_contains_four_inward_displacement_lines() -> None:
    text = COMPARISON_SVG.read_text(
        encoding="utf-8"
    )

    assert (
        text.count(
            'id="inward-displacement-wall_vertex_'
        )
        == 4
    )


def test_phase7c_stopping_status_is_frozen() -> None:
    assert (
        STOPPING_STATUS
        == "EXISTING_FROZEN_WALL_IS_COMPLETE_DODECAGON_GEOMETRY"
    )


def test_metadata_records_no_new_geometry() -> None:
    text = RECONSTRUCTION_SVG.read_text(
        encoding="utf-8"
    )

    required = (
        "&quot;new_continuous_geometric_parameters&quot;:0",
        "&quot;new_fitted_scale_parameters&quot;:0",
        "&quot;new_discrete_candidate_choices&quot;:0",
        "&quot;new_wall_vertices&quot;:0",
        "&quot;new_wall_sides&quot;:0",
        "&quot;historical_targets_loaded&quot;:false",
        "&quot;historical_comparison_metrics_calculated&quot;:false",
    )

    for token in required:
        assert token in text


def test_renderer_import_boundary_is_frozen_artifact_only() -> None:
    tree = ast.parse(
        MODULE.read_text(
            encoding="utf-8"
        )
    )

    imports = []

    for node in tree.body:
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                node.module
                or ""
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                alias.name
                for alias in node.names
            )

    forbidden = (
        "michell_composite",
        "polar_pivot_wall",
        "historical_residuals",
        "metrology",
        "prediction_status",
    )

    assert not any(
        fragment
        in imported
        for imported in imports
        for fragment in forbidden
    )


def test_exposed_historical_targets_absent_from_renderer_and_svgs() -> None:
    text = (
        MODULE.read_text(
            encoding="utf-8"
        )
        + "\n"
        + RECONSTRUCTION_SVG.read_text(
            encoding="utf-8"
        )
        + "\n"
        + COMPARISON_SVG.read_text(
            encoding="utf-8"
        )
    )

    banned = (
        "63" + "36",
        "63" + "00",
        "17" + "6:17" + "5",
        "316" + "80",
    )

    assert not any(
        token in text
        for token in banned
    )



def test_visible_annotations_are_below_geometry_panel() -> None:
    for path in (
        RECONSTRUCTION_SVG,
        COMPARISON_SVG,
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        assert (
            'height="1140"'
            in text
        )

        assert (
            'viewBox="0 0 960 1140"'
            in text
        )

        assert (
            'id="legend-separator"'
            in text
        )

        y_values = [
            float(
                value
            )
            for value in re.findall(
                r'<text[^>]*\sy="([0-9.]+)"',
                text,
            )
        ]

        assert y_values

        # The geometry/axis panel ends below y=900.
        # Keep every visible annotation in the dedicated footer.
        assert min(
            y_values
        ) >= 960.0



def test_no_absolute_machine_paths_in_svgs() -> None:
    for path in (
        RECONSTRUCTION_SVG,
        COMPARISON_SVG,
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        assert (
            "/home/"
            not in text
        )

        assert (
            "\\Users\\"
            not in text
        )
