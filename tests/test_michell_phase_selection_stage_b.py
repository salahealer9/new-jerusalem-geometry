from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
from math import hypot, sqrt
from pathlib import Path
from statistics import fmean

import pytest

from new_jerusalem_geometry import (
    build_michell_composite,
)
from new_jerusalem_geometry.michell_phase_selection_stage_b import (
    ATOL,
    CORRESPONDENCE_COUNT,
    FROZEN_STAGE_A_SHA256,
    HISTORICAL_STAGE_A_COMMIT,
    HISTORICAL_STAGE_A_SHA256,
    ORIENTATIONS,
    RTOL,
    STAGE_A_NOT_RUN,
    STAGE_B_SCHEMA_VERSION,
    _candidate_index_sequence,
    _frozen_stage_a_input,
    _load_source_endpoints,
    build_sevenfold_phase_selection_stage_b,
    sevenfold_phase_selection_stage_b_to_json,
    write_sevenfold_phase_selection_stage_b_json,
)


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_phase_selection_stage_b.py"
)

STAGE_A_ARTIFACT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_5"
    / "sevenfold_phase_selection.json"
)

REGISTERED_LANDMARKS = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "registered_landmark_centroids.csv"
)

ENDPOINT_GEOMETRY = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "star_endpoint_geometry.json"
)

AFFINE_MATRIX = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "affine_registration_matrix.json"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _build(
    *,
    artifact_path: Path = (
        STAGE_A_ARTIFACT
    ),
):
    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    audit = (
        build_sevenfold_phase_selection_stage_b(
            composite,
            stage_a_artifact_path=(
                artifact_path
            ),
            registered_landmarks_path=(
                REGISTERED_LANDMARKS
            ),
            endpoint_geometry_path=(
                ENDPOINT_GEOMETRY
            ),
            affine_matrix_path=(
                AFFINE_MATRIX
            ),
        )
    )

    return (
        composite,
        audit,
    )


def test_stage_a_hashes_record_portable_and_historical_boundaries() -> None:
    assert (
        FROZEN_STAGE_A_SHA256
        == "6bfb543d5fbb98cbd383a242eac109d1ff0f7a96a68410d370ed294ec119613b"
    )

    assert (
        HISTORICAL_STAGE_A_SHA256
        == (
            "48a96dc7e160365cafc9114d7586ce94"
            "b070ebbe0403d759e71e8795c28d6d7d"
        )
    )

    assert (
        HISTORICAL_STAGE_A_COMMIT
        == "a84949a"
    )


def test_stage_b_requires_supplied_composite_and_artifact_paths() -> None:
    signature = inspect.signature(
        build_sevenfold_phase_selection_stage_b
    )

    assert (
        tuple(
            signature.parameters
        )
        == (
            "composite",
            "stage_a_artifact_path",
            "registered_landmarks_path",
            "endpoint_geometry_path",
            "affine_matrix_path",
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


def test_stage_b_module_imports_no_registration_or_fitting_api() -> None:
    tree = ast.parse(
        SOURCE.read_text(
            encoding="utf-8"
        )
    )

    imported_modules: list[str] = []
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imported_modules.append(
                node.module or ""
            )

            imported_names.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            imported_modules.extend(
                alias.name
                for alias in node.names
            )

    forbidden_modules = (
        "figure14_registration",
        "figure14_registered_landmarks",
        "figure14_endpoint_geometry",
        "figure14_semantic_correspondence",
        "heptagram_geometry",
    )

    assert not any(
        forbidden in module
        for forbidden in forbidden_modules
        for module in imported_modules
    )

    forbidden_names = {
        "apply_registration_matrix",
        "fit_registration_matrix",
        "derive_affine_registered_landmarks",
        "fit_free_regular_seven_vertices",
        "fit_origin_radius7_with_free_phase",
        "fit_canonical_origin_radius7",
        "build_figure14_aligned_heptagram",
        "build_scaffold_heptagram",
    }

    assert (
        imported_names
        & forbidden_names
    ) == set()


def test_stage_a_frozen_projection_has_registered_hash_and_result() -> None:
    (
        frozen,
        frozen_hash,
    ) = _frozen_stage_a_input(
        STAGE_A_ARTIFACT
    )

    assert (
        frozen_hash
        == FROZEN_STAGE_A_SHA256
    )

    assert (
        frozen[
            "stage_a"
        ][
            "grammar_selection_result"
        ]
        == "GRAMMAR_UNDERDETERMINED"
    )

    assert (
        frozen[
            "stage_a"
        ][
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
        frozen[
            "stage_b"
        ]
        == STAGE_A_NOT_RUN
    )


def test_source_loader_uses_exact_seven_promoted_endpoint_ids_and_order() -> None:
    (
        endpoints,
        registration_scale,
    ) = _load_source_endpoints(
        registered_landmarks_path=(
            REGISTERED_LANDMARKS
        ),
        endpoint_geometry_path=(
            ENDPOINT_GEOMETRY
        ),
    )

    assert len(
        endpoints
    ) == 7

    assert [
        item[
            "endpoint_id"
        ]
        for item in endpoints
    ] == [
        "star_endpoint_00_top",
        "star_endpoint_01_upper_left",
        "star_endpoint_02_lower_left",
        "star_endpoint_03_bottom_left",
        "star_endpoint_04_bottom_right",
        "star_endpoint_05_lower_right",
        "star_endpoint_06_upper_right",
    ]

    assert (
        registration_scale[
            "loo_rms_equivalent_normalized"
        ]
        == pytest.approx(
            0.03560774729496293
        )
    )


def test_source_loader_reads_normalized_coordinates_without_refitting() -> None:
    (
        endpoints,
        _,
    ) = _load_source_endpoints(
        registered_landmarks_path=(
            REGISTERED_LANDMARKS
        ),
        endpoint_geometry_path=(
            ENDPOINT_GEOMETRY
        ),
    )

    assert (
        endpoints[0]["x"]
        == pytest.approx(
            -0.014399324384
        )
    )

    assert (
        endpoints[0]["y"]
        == pytest.approx(
            6.992516630180
        )
    )

    assert (
        endpoints[6]["x"]
        == pytest.approx(
            5.487155791243
        )
    )

    assert (
        endpoints[6]["y"]
        == pytest.approx(
            4.375535737781
        )
    )


def test_registered_correspondence_family_is_exactly_fourteen() -> None:
    assert ORIENTATIONS == (
        "forward",
        "reverse",
    )

    assert (
        CORRESPONDENCE_COUNT
        == 14
    )

    assert RTOL == 1.0e-12
    assert ATOL == 1.0e-12


def test_each_correspondence_is_only_a_cyclic_permutation_or_reversal() -> None:
    indices = [
        3,
        7,
        11,
        15,
        19,
        23,
        27,
    ]

    sequences = []

    for orientation in (
        "forward",
        "reverse",
    ):
        for shift in range(7):
            sequence = (
                _candidate_index_sequence(
                    indices,
                    orientation=orientation,
                    shift=shift,
                )
            )

            assert sorted(
                sequence
            ) == sorted(
                indices
            )

            assert len(
                set(
                    sequence
                )
            ) == 7

            sequences.append(
                tuple(
                    sequence
                )
            )

    assert len(
        sequences
    ) == 14

    assert len(
        set(
            sequences
        )
    ) == 14


def test_every_phase_evaluates_exactly_fourteen_correspondences() -> None:
    _, audit = _build()

    for phase in audit[
        "stage_b"
    ][
        "phase_results"
    ]:
        assert (
            phase[
                "comparison_count"
            ]
            == 14
        )

        assert len(
            phase[
                "all_correspondences"
            ]
        ) == 14


def test_recorded_best_metrics_are_recomputed_from_best_point_pairs() -> None:
    _, audit = _build()

    for phase in audit[
        "stage_b"
    ][
        "phase_results"
    ]:
        residuals = [
            pair[
                "residual"
            ]
            for pair in phase[
                "best_point_pairs"
            ]
        ]

        expected_rms = sqrt(
            fmean(
                value
                * value
                for value in residuals
            )
        )

        assert (
            phase[
                "rms_residual"
            ]
            == pytest.approx(
                expected_rms
            )
        )

        assert (
            phase[
                "mean_residual"
            ]
            == pytest.approx(
                fmean(
                    residuals
                )
            )
        )

        assert (
            phase[
                "max_residual"
            ]
            == pytest.approx(
                max(
                    residuals
                )
            )
        )


def test_best_correspondence_is_minimum_raw_rms_with_registered_tie_break() -> None:
    _, audit = _build()

    orientation_rank = {
        "forward": 0,
        "reverse": 1,
    }

    for phase in audit[
        "stage_b"
    ][
        "phase_results"
    ]:
        expected = min(
            phase[
                "all_correspondences"
            ],
            key=lambda item: (
                item[
                    "rms_residual"
                ],
                orientation_rank[
                    item[
                        "orientation"
                    ]
                ],
                item[
                    "cyclic_shift"
                ],
            ),
        )

        assert (
            phase[
                "best_correspondence"
            ][
                "orientation"
            ]
            == expected[
                "orientation"
            ]
        )

        assert (
            phase[
                "best_correspondence"
            ][
                "cyclic_shift"
            ]
            == expected[
                "cyclic_shift"
            ]
        )

        assert (
            phase[
                "rms_residual"
            ]
            == expected[
                "rms_residual"
            ]
        )


def test_stage_b_has_zero_continuous_fit_degrees_of_freedom() -> None:
    _, audit = _build()

    rule = audit[
        "stage_b"
    ][
        "comparison_rule"
    ]

    assert (
        rule[
            "continuous_fit_parameters"
        ]
        == 0
    )

    for key in (
        "candidate_translation_fit",
        "candidate_rotation_fit",
        "candidate_scale_fit",
        "candidate_phase_fit",
        "candidate_centre_fit",
        "candidate_radius_fit",
        "registration_refit",
    ):
        assert (
            rule[key]
            is False
        )


def test_stage_a_section_is_preserved_exactly() -> None:
    (
        frozen,
        _,
    ) = _frozen_stage_a_input(
        STAGE_A_ARTIFACT
    )

    _, audit = _build()

    assert (
        audit[
            "protocol"
        ]
        == frozen[
            "protocol"
        ]
    )

    assert (
        audit[
            "stage_a"
        ]
        == frozen[
            "stage_a"
        ]
    )


def test_phase_ranking_is_a_complete_permutation_and_matches_raw_rms() -> None:
    _, audit = _build()

    stage_b = audit[
        "stage_b"
    ]

    assert sorted(
        stage_b[
            "ranking_phase_ids"
        ]
    ) == [
        0,
        1,
        2,
        3,
    ]

    ranked = sorted(
        stage_b[
            "phase_results"
        ],
        key=lambda item: (
            item[
                "rms_residual"
            ],
            item[
                "phase_id"
            ],
        ),
    )

    assert (
        stage_b[
            "ranking_phase_ids"
        ]
        == [
            item[
                "phase_id"
            ]
            for item in ranked
        ]
    )

    assert (
        sorted(
            item[
                "rank"
            ]
            for item in stage_b[
                "phase_results"
            ]
        )
        == [
            1,
            2,
            3,
            4,
        ]
    )


def test_winner_and_runner_up_are_descriptive_only() -> None:
    _, audit = _build()

    stage_b = audit[
        "stage_b"
    ]

    assert (
        stage_b[
            "winner"
        ][
            "phase_id"
        ]
        == stage_b[
            "ranking_phase_ids"
        ][0]
    )

    assert (
        stage_b[
            "runner_up"
        ][
            "phase_id"
        ]
        == stage_b[
            "ranking_phase_ids"
        ][1]
    )

    assert (
        stage_b[
            "independent_validation"
        ]
        is False
    )

    assert (
        stage_b[
            "feeds_back_into_builder"
        ]
        is False
    )

    assert (
        stage_b[
            "interpretation"
        ][
            "comparison_type"
        ]
        == "descriptive_source_consistency"
    )


def test_stage_a_conclusion_cannot_be_changed_by_stage_b() -> None:
    _, audit = _build()

    assert (
        audit[
            "stage_a"
        ][
            "grammar_selection_result"
        ]
        == "GRAMMAR_UNDERDETERMINED"
    )

    assert (
        audit[
            "stage_b"
        ][
            "stage_a_result_preserved"
        ]
        == "GRAMMAR_UNDERDETERMINED"
    )

    assert (
        audit[
            "stage_b"
        ][
            "interpretation"
        ][
            "grammar_selection_changed"
        ]
        is False
    )

    assert (
        audit[
            "stage_b"
        ][
            "interpretation"
        ][
            "stage_a_remains_grammar_underdetermined"
        ]
        is True
    )


def test_stage_b_source_hashes_match_promoted_files() -> None:
    _, audit = _build()

    bindings = audit[
        "stage_b"
    ][
        "source_bindings"
    ]

    assert (
        bindings[
            "registered_landmarks"
        ][
            "sha256"
        ]
        == _sha256(
            REGISTERED_LANDMARKS
        )
    )

    assert (
        bindings[
            "endpoint_geometry"
        ][
            "sha256"
        ]
        == _sha256(
            ENDPOINT_GEOMETRY
        )
    )

    assert (
        bindings[
            "affine_registration_matrix"
        ][
            "sha256"
        ]
        == _sha256(
            AFFINE_MATRIX
        )
    )

    assert (
        bindings[
            "affine_registration_matrix"
        ][
            "selected_model"
        ]
        == "affine"
    )

    assert (
        bindings[
            "affine_registration_matrix"
        ][
            "applied_in_stage_b"
        ]
        is False
    )


def test_stage_b_is_deterministic_from_frozen_stage_a_input(
    tmp_path: Path,
) -> None:
    (
        frozen,
        _,
    ) = _frozen_stage_a_input(
        STAGE_A_ARTIFACT
    )

    input_path = (
        tmp_path
        / "stage_a.json"
    )

    input_path.write_text(
        json.dumps(
            frozen,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _, first = _build(
        artifact_path=(
            input_path
        )
    )

    _, second = _build(
        artifact_path=(
            input_path
        )
    )

    assert (
        sevenfold_phase_selection_stage_b_to_json(
            first
        )
        == sevenfold_phase_selection_stage_b_to_json(
            second
        )
    )


def test_stage_b_is_idempotently_rebuildable_from_completed_artifact(
    tmp_path: Path,
) -> None:
    (
        frozen,
        _,
    ) = _frozen_stage_a_input(
        STAGE_A_ARTIFACT
    )

    stage_a_path = (
        tmp_path
        / "sevenfold_phase_selection.json"
    )

    stage_a_path.write_text(
        json.dumps(
            frozen,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _, first = _build(
        artifact_path=(
            stage_a_path
        )
    )

    write_sevenfold_phase_selection_stage_b_json(
        first,
        stage_a_path,
    )

    _, second = _build(
        artifact_path=(
            stage_a_path
        )
    )

    assert first == second


def test_stage_b_writer_preserves_deterministic_bytes(
    tmp_path: Path,
) -> None:
    _, audit = _build()

    expected = (
        sevenfold_phase_selection_stage_b_to_json(
            audit
        )
    )

    path = (
        write_sevenfold_phase_selection_stage_b_json(
            audit,
            tmp_path
            / "sevenfold_phase_selection.json",
        )
    )

    assert (
        path.read_text(
            encoding="utf-8"
        )
        == expected
    )

    assert (
        audit[
            "stage_b"
        ][
            "schema_version"
        ]
        == STAGE_B_SCHEMA_VERSION
    )


def test_stage_b_source_binding_paths_are_repository_relative() -> None:
    _, audit = _build()

    bindings = audit[
        "stage_b"
    ][
        "source_bindings"
    ]

    observed = {
        name: item[
            "path"
        ]
        for name, item
        in bindings.items()
    }

    assert observed == {
        "registered_landmarks": (
            "data/calibration/figure14/derived/"
            "registered_landmark_centroids.csv"
        ),
        "endpoint_geometry": (
            "data/calibration/figure14/derived/"
            "star_endpoint_geometry.json"
        ),
        "affine_registration_matrix": (
            "data/calibration/figure14/derived/"
            "affine_registration_matrix.json"
        ),
    }

    assert all(
        not Path(value).is_absolute()
        for value
        in observed.values()
    )



def test_completed_stage_b_records_historical_and_portable_stage_a_bindings() -> None:
    _, audit = _build()

    stage_b = audit[
        "stage_b"
    ]

    assert (
        stage_b[
            "stage_a_input_sha256"
        ]
        == FROZEN_STAGE_A_SHA256
    )

    assert (
        stage_b[
            "historical_stage_a_input_sha256"
        ]
        == HISTORICAL_STAGE_A_SHA256
    )

    assert (
        stage_b[
            "historical_stage_a_commit"
        ]
        == HISTORICAL_STAGE_A_COMMIT
    )

    normalization = stage_b[
        "portability_normalization"
    ]

    assert (
        normalization[
            "field"
        ]
        == "protocol.protocol_path"
    )

    assert (
        normalization[
            "change"
        ]
        == "machine_absolute_to_repository_relative"
    )

    assert (
        normalization[
            "scientific_values_changed"
        ]
        is False
    )

    protocol_path = audit[
        "protocol"
    ][
        "protocol_path"
    ]

    assert not Path(
        protocol_path
    ).is_absolute()

    assert (
        protocol_path
        == (
            "docs/specification/"
            "v0.5_sevenfold_phase_selection_protocol.md"
        )
    )
