from __future__ import annotations

import ast
import hashlib
import json
from math import cos, isclose, pi
from pathlib import Path

from new_jerusalem_geometry.dodecagon_vertex_radius_audit import (
    ABS_TOL,
    OBLIQUE_PAIR_VERTEX,
    POLAR_ADJACENT_VERTEX,
    PROTOCOL_SHA256,
    REGULAR_APOTHEM,
    build_vertex_radius_audit,
    canonical_json_bytes,
    classify_vertex,
    incident_side_indices,
    regular_circumradius,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

ARTIFACT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_7"
    / "dodecagon_vertex_radius_audit.json"
)

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "dodecagon_vertex_radius_audit.py"
)

SVG_MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "dodecagon_vertex_radius_svg.py"
)


def _document() -> dict:
    return (
        build_vertex_radius_audit()
    )


def test_protocol_hash_is_frozen() -> None:
    path = (
        ROOT
        / "docs"
        / "specification"
        / "v0.7_dodecagon_vertex_radius_audit_protocol.md"
    )

    assert (
        hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        == PROTOCOL_SHA256
    )


def test_frozen_wall_has_twelve_vertices() -> None:
    document = _document()

    assert (
        document[
            "wall_topology"
        ][
            "vertex_count"
        ]
        == 12
    )


def test_semantic_class_counts() -> None:
    document = _document()

    assert (
        document[
            "semantic_vertex_classes"
        ][
            "observed_counts"
        ]
        == {
            POLAR_ADJACENT_VERTEX: 8,
            OBLIQUE_PAIR_VERTEX: 4,
        }
    )


def test_classes_are_assigned_from_side_semantics() -> None:
    expected_oblique_pair = {
        1,
        4,
        7,
        10,
    }

    observed = {
        index
        for index in range(
            12
        )
        if classify_vertex(
            index
        )
        == OBLIQUE_PAIR_VERTEX
    }

    assert (
        observed
        == expected_oblique_pair
    )

    for index in range(
        12
    ):
        sides = (
            incident_side_indices(
                index
            )
        )

        assert len(
            sides
        ) == 2


def test_regular_baseline_has_no_fitted_parameter() -> None:
    document = _document()

    baseline = document[
        "regular_dodecagon_baseline"
    ]

    assert (
        baseline[
            "free_parameters"
        ]
        == 0
    )

    assert isclose(
        baseline[
            "apothem_normalized"
        ],
        REGULAR_APOTHEM,
        rel_tol=0.0,
        abs_tol=0.0,
    )


def test_regular_radius_is_derived_from_apothem() -> None:
    expected = (
        REGULAR_APOTHEM
        / cos(
            pi
            / 12.0
        )
    )

    assert isclose(
        regular_circumradius(),
        expected,
        rel_tol=1.0e-15,
        abs_tol=1.0e-15,
    )


def test_both_semantic_classes_are_radius_degenerate() -> None:
    document = _document()

    summaries = document[
        "class_summaries"
    ]

    assert (
        summaries[
            POLAR_ADJACENT_VERTEX
        ][
            "within_class_spread_normalized"
        ]
        <= ABS_TOL
    )

    assert (
        summaries[
            OBLIQUE_PAIR_VERTEX
        ][
            "within_class_spread_normalized"
        ]
        <= ABS_TOL
    )


def test_polar_adjacent_vertices_match_regular_baseline() -> None:
    document = _document()

    comparison = document[
        "normalized_comparison"
    ]

    assert (
        comparison[
            "polar_adjacent_matches_regular"
        ]
        is True
    )

    assert abs(
        comparison[
            "polar_adjacent_minus_regular"
        ]
    ) <= ABS_TOL


def test_oblique_pair_vertices_are_inward() -> None:
    document = _document()

    comparison = document[
        "normalized_comparison"
    ]

    assert (
        comparison[
            "oblique_pair_vertices_all_inward"
        ]
        is True
    )

    assert (
        comparison[
            "oblique_pair_minus_regular"
        ]
        < -ABS_TOL
    )


def test_exactly_four_vertices_have_nonzero_radial_displacement() -> None:
    document = _document()

    displaced = [
        row
        for row in document[
            "vertices"
        ]
        if abs(
            row[
                "radial_difference_from_regular_normalized"
            ]
        )
        > ABS_TOL
    ]

    assert len(
        displaced
    ) == 4

    assert all(
        row[
            "vertex_class"
        ]
        == OBLIQUE_PAIR_VERTEX
        for row in displaced
    )


def test_stopping_status_confirms_two_classes() -> None:
    document = _document()

    assert (
        document[
            "stopping_status"
        ]
        == "TWO_SEMANTIC_RADIUS_CLASSES_CONFIRMED"
    )


def test_no_new_parameters_or_target_loading() -> None:
    document = _document()

    determinacy = document[
        "determinacy"
    ]

    assert (
        determinacy[
            "new_continuous_parameters_introduced"
        ]
        == 0
    )

    assert (
        determinacy[
            "new_fitted_scale_parameters_introduced"
        ]
        == 0
    )

    assert (
        determinacy[
            "new_discrete_candidate_choices_introduced"
        ]
        == 0
    )

    assert (
        determinacy[
            "historical_dimensional_targets_loaded"
        ]
        is False
    )

    assert (
        determinacy[
            "historical_comparison_metrics_calculated"
        ]
        is False
    )


def test_artifact_matches_canonical_generation() -> None:
    assert (
        ARTIFACT.read_bytes()
        == canonical_json_bytes(
            _document()
        )
    )


def test_artifact_contains_no_absolute_repository_path() -> None:
    document = json.loads(
        ARTIFACT.read_text(
            encoding="utf-8"
        )
    )

    text = json.dumps(
        document
    )

    assert (
        "/home/"
        not in text
    )

    assert (
        "\\Users\\"
        not in text
    )


def test_geometry_module_import_boundary() -> None:
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


def test_exposed_dimensional_targets_absent_from_geometry_modules() -> None:
    text = (
        MODULE.read_text(
            encoding="utf-8"
        )
        + "\n"
        + SVG_MODULE.read_text(
            encoding="utf-8"
        )
    )

    # Construct strings so the exposed source numerals are not themselves
    # present as executable geometry-module literals.
    banned = (
        "63" + "36",
        "63" + "00",
        "17" + "6:17" + "5",
        "316" + "80",
    )

    found = [
        token
        for token in banned
        if token in text
    ]

    assert not found
