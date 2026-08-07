from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
)
from new_jerusalem_geometry.michell_phase_selection import (
    ATOL,
    PHASE_AUDIT_SCHEMA_NAME,
    PHASE_AUDIT_SCHEMA_VERSION,
    REGISTERED_PHASES,
    REGISTERED_QUARTER_TURN_ORBIT,
    RTOL,
    STEP2_EDGE_PAIRS,
    build_sevenfold_phase_selection_stage_a,
    sevenfold_phase_selection_to_json,
    write_sevenfold_phase_selection_json,
)


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_phase_selection.py"
)

PROTOCOL_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "v0.5_sevenfold_phase_selection_protocol.md"
)

NODES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

DEPENDENCIES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

CLAIMS_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _build():
    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    audit = (
        build_sevenfold_phase_selection_stage_a(
            composite,
            protocol_path=(
                PROTOCOL_PATH
            ),
            construction_nodes_path=(
                NODES_PATH
            ),
            construction_dependencies_path=(
                DEPENDENCIES_PATH
            ),
            claim_matrix_path=(
                CLAIMS_PATH
            ),
        )
    )

    return (
        composite,
        audit,
    )


def _phases():
    return _build()[1][
        "stage_a"
    ]["phases"]


def test_registered_phase_definitions_and_tolerances_are_frozen() -> None:
    assert REGISTERED_PHASES == {
        0: (0, 4, 8, 12, 16, 20, 24),
        1: (1, 5, 9, 13, 17, 21, 25),
        2: (2, 6, 10, 14, 18, 22, 26),
        3: (3, 7, 11, 15, 19, 23, 27),
    }

    assert STEP2_EDGE_PAIRS == (
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 1),
        (1, 3),
        (3, 5),
        (5, 0),
    )

    assert (
        REGISTERED_QUARTER_TURN_ORBIT
        == {
            0: 3,
            3: 2,
            2: 1,
            1: 0,
        }
    )

    assert RTOL == 1.0e-12
    assert ATOL == 1.0e-12


def test_stage_a_requires_a_supplied_composite() -> None:
    signature = inspect.signature(
        build_sevenfold_phase_selection_stage_a
    )

    assert (
        tuple(
            signature.parameters
        )
        == (
            "composite",
            "protocol_path",
            "construction_nodes_path",
            "construction_dependencies_path",
            "claim_matrix_path",
        )
    )

    assert (
        signature.parameters[
            "composite"
        ].default
        is inspect.Parameter.empty
    )

    assert (
        "unit"
        not in signature.parameters
    )


def test_stage_a_module_imports_no_calibration_or_geometry_builder() -> None:
    tree = ast.parse(
        SOURCE.read_text(
            encoding="utf-8"
        )
    )

    modules: list[str] = []
    names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            modules.append(
                node.module or ""
            )
            names.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            modules.extend(
                alias.name
                for alias in node.names
            )

    forbidden_fragments = (
        "calibration",
        "digitisation",
        "registration",
        "registered_landmarks",
        "source_geometry",
        "figure12_",
        "figure14_",
    )

    violations = [
        module
        for module in modules
        if any(
            fragment in module
            for fragment
            in forbidden_fragments
        )
    ]

    assert violations == []

    forbidden_builders = {
        "build_michell_composite",
        "build_michell_28_point_scaffold",
        "build_scaffold_heptagram",
        "build_figure14_anchor_set",
        "build_figure14_aligned_heptagram",
    }

    assert (
        names
        & forbidden_builders
    ) == set()


def test_stage_a_schema_and_candidate_count() -> None:
    _, audit = _build()

    assert (
        audit["schema_name"]
        == PHASE_AUDIT_SCHEMA_NAME
        == "njg_michell_sevenfold_phase_selection"
    )

    assert (
        audit["schema_version"]
        == PHASE_AUDIT_SCHEMA_VERSION
        == "1.0"
    )

    assert (
        audit[
            "stage_a"
        ][
            "candidate_count"
        ]
        == 4
    )


def test_all_four_candidates_have_unique_complete_point_sets() -> None:
    for candidate in _phases():
        assert (
            candidate[
                "unique_index_count"
            ]
            == 7
        )
        assert (
            candidate[
                "unique_point_count"
            ]
            == 7
        )
        assert (
            candidate[
                "radius_check"
            ][
                "passes"
            ]
            is True
        )
        assert (
            candidate[
                "candidate_valid"
            ]
            is True
        )


def test_all_four_candidates_satisfy_same_source_role_counts() -> None:
    expected = {
        "moon_centre": 3,
        "intersection_positioner": 2,
        "inter_moon_gap": 2,
    }

    for candidate in _phases():
        assert (
            candidate[
                "role_counts"
            ]
            == expected
        )
        assert (
            candidate[
                "source_stated_role_criterion"
            ][
                "passes"
            ]
            is True
        )
        assert (
            candidate[
                "project_inferred_gap_completion"
            ][
                "inter_moon_gap_count"
            ]
            == 2
        )
        assert (
            candidate[
                "project_inferred_gap_completion"
            ][
                "status"
            ]
            == "project_inference"
        )


def test_all_cyclic_role_words_are_equivalent() -> None:
    _, audit = _build()

    role = audit[
        "stage_a"
    ][
        "role_equivalence"
    ]

    assert (
        role[
            "all_role_counts_equal"
        ]
        is True
    )
    assert (
        role[
            "all_cyclic_role_words_equivalent"
        ]
        is True
    )

    canonical = {
        tuple(
            candidate[
                "canonical_cyclic_role_sequence"
            ]
        )
        for candidate in _phases()
    }

    assert len(canonical) == 1


def test_quarter_turn_action_forms_registered_c4_orbit() -> None:
    _, audit = _build()

    quarter = audit[
        "stage_a"
    ][
        "quarter_turn_orbit"
    ]

    assert (
        quarter[
            "observed_phase_orbit"
        ]
        == {
            "0": 3,
            "3": 2,
            "2": 1,
            "1": 0,
        }
    )
    assert (
        quarter[
            "coordinate_rotation_passes"
        ]
        is True
    )
    assert (
        quarter[
            "role_rotation_passes"
        ]
        is True
    )
    assert (
        quarter[
            "orbit_passes"
        ]
        is True
    )
    assert (
        quarter[
            "max_coordinate_residual"
        ]
        <= ATOL
    )


def test_all_phases_use_same_step2_topology() -> None:
    expected = [
        list(pair)
        for pair in STEP2_EDGE_PAIRS
    ]

    for candidate in _phases():
        assert (
            candidate[
                "step2_edge_pairs"
            ]
            == expected
        )
        assert len(
            candidate[
                "edge_lengths"
            ]
        ) == 7


def test_all_four_phase_geometries_are_metric_equivalent() -> None:
    _, audit = _build()

    metric = audit[
        "stage_a"
    ][
        "metric_equivalence"
    ]

    assert (
        metric[
            "all_phases_metric_equivalent"
        ]
        is True
    )

    for item in metric[
        "comparisons"
    ]:
        assert (
            item[
                "equivalent_to_phase_0"
            ]
            is True
        )
        assert (
            item[
                "max_sorted_edge_length_residual"
            ]
            <= ATOL
        )
        assert (
            item[
                "max_sorted_angular_gap_residual"
            ]
            <= ATOL
        )
        assert (
            item[
                "star_edge_perimeter_residual"
            ]
            <= ATOL
        )


def test_primary_and_reciprocal_correspondence_is_descriptive_only() -> None:
    _, audit = _build()

    correspondence = audit[
        "stage_a"
    ][
        "primary_reciprocal_correspondence"
    ]

    assert (
        correspondence[
            "primary_phase_id"
        ]
        == 1
    )
    assert (
        correspondence[
            "reciprocal_phase_id"
        ]
        == 3
    )
    assert (
        correspondence[
            "primary_scaffold_indices"
        ]
        == [
            1,
            5,
            9,
            13,
            17,
            21,
            25,
        ]
    )
    assert (
        correspondence[
            "reciprocal_scaffold_indices"
        ]
        == [
            3,
            7,
            11,
            15,
            19,
            23,
            27,
        ]
    )
    assert (
        correspondence[
            "selection_status"
        ]
        == "descriptive_only"
    )


def test_existing_composite_candidate_resolves_to_phase3_without_becoming_evidence() -> None:
    _, audit = _build()

    state = audit[
        "stage_a"
    ][
        "existing_candidate_state"
    ]

    assert (
        state[
            "ordered_scaffold_indices"
        ]
        == [
            7,
            11,
            15,
            19,
            23,
            27,
            3,
        ]
    )
    assert (
        state[
            "phase_id"
        ]
        == 3
    )
    assert (
        state[
            "cyclic_origin_scaffold_index"
        ]
        == 7
    )
    assert (
        state[
            "used_as_selection_evidence"
        ]
        is False
    )


def test_existing_phase_grammar_edges_remain_excluded_as_selection_evidence() -> None:
    _, audit = _build()

    grammar = audit[
        "stage_a"
    ][
        "grammar_boundary"
    ]

    assert (
        grammar[
            "candidate_node"
        ][
            "node_type"
        ]
        == "project_candidate"
    )
    assert (
        grammar[
            "excluded_existing_phase_evidence"
        ]
        == {
            "DEP-022": (
                "implementation_only"
            ),
            "DEP-024": (
                "hypothesis_to_test"
            ),
        }
    )
    assert (
        grammar[
            "existing_phase_node_is_admissible_selection_evidence"
        ]
        is False
    )


def test_source_grounded_star_claims_have_no_named_cardinal_condition() -> None:
    _, audit = _build()

    scan = audit[
        "stage_a"
    ][
        "source_orientation_scan"
    ]

    assert (
        scan[
            "named_cardinal_matches"
        ]
        == []
    )
    assert (
        scan[
            "named_cardinal_orientation_condition_present"
        ]
        is False
    )
    assert len(
        scan[
            "admissible_source_claim_ids"
        ]
    ) >= 1


def test_stage_a_result_is_preregistered_grammar_underdetermined() -> None:
    _, audit = _build()

    stage_a = audit[
        "stage_a"
    ]

    assert (
        stage_a[
            "grammar_selection_result"
        ]
        == "GRAMMAR_UNDERDETERMINED"
    )
    assert (
        stage_a[
            "surviving_phase_ids"
        ]
        == [
            0,
            1,
            2,
            3,
        ]
    )
    assert (
        stage_a[
            "discriminating_grammar_condition"
        ]
        is None
    )
    assert (
        stage_a[
            "feeds_back_into_builder"
        ]
        is False
    )


def test_stage_b_is_explicitly_not_run() -> None:
    _, audit = _build()

    assert (
        audit[
            "stage_b"
        ][
            "status"
        ]
        == "NOT_RUN"
    )
    assert (
        audit[
            "stage_b"
        ][
            "independent_validation"
        ]
        is False
    )
    assert (
        audit[
            "stage_b"
        ][
            "feeds_back_into_builder"
        ]
        is False
    )


def test_stage_a_records_exact_protocol_and_source_hashes() -> None:
    _, audit = _build()

    protocol = audit[
        "protocol"
    ]

    assert (
        protocol[
            "protocol_sha256"
        ]
        == _sha256(
            PROTOCOL_PATH
        )
    )
    assert (
        protocol[
            "construction_nodes_sha256"
        ]
        == _sha256(
            NODES_PATH
        )
    )
    assert (
        protocol[
            "construction_dependencies_sha256"
        ]
        == _sha256(
            DEPENDENCIES_PATH
        )
    )
    assert (
        protocol[
            "claim_matrix_sha256"
        ]
        == _sha256(
            CLAIMS_PATH
        )
    )


def test_stage_a_artifact_contains_no_stage_b_residuals() -> None:
    _, audit = _build()

    text = (
        sevenfold_phase_selection_to_json(
            audit
        )
    )

    forbidden = (
        '"rms_residual"',
        '"mean_residual"',
        '"max_residual"',
        '"best_correspondence"',
        '"rank"',
    )

    for token in forbidden:
        assert token not in text


def test_stage_a_json_is_deterministic_and_writer_preserves_bytes(
    tmp_path: Path,
) -> None:
    _, first_audit = _build()
    _, second_audit = _build()

    first = (
        sevenfold_phase_selection_to_json(
            first_audit
        )
    )

    second = (
        sevenfold_phase_selection_to_json(
            second_audit
        )
    )

    assert first == second

    path = (
        write_sevenfold_phase_selection_json(
            first_audit,
            tmp_path
            / "sevenfold_phase_selection.json",
        )
    )

    assert (
        path.read_text(
            encoding="utf-8"
        )
        == first
    )
