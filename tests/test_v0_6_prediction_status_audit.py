from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

from new_jerusalem_geometry.prediction_status_audit import (
    DECAGON_IDS,
    DEFAULT_OUTPUT_RELATIVE_PATH,
    DEFAULT_PHASE6C_RELATIVE_PATH,
    DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH,
    DEFAULT_REGISTRY_RELATIVE_PATH,
    DEVELOPMENT_USED_TARGET_IDS,
    EXPECTED_PHASE6C_QUANTITIES,
    EXPECTED_PHASE6C_SHA256,
    EXPECTED_PHASE6D_PROTOCOL_SHA256,
    EXPECTED_POLICY,
    EXPECTED_RECORD_ORDER,
    EXPECTED_REGISTRY_SHA256,
    EXPECTED_STATUS,
    FROZEN_V0_5_COMMIT,
    HISTORICAL_EVIDENCE_COMMIT,
    NUMERIC_COMPARISON_POLICY_IDS,
    build_prediction_status_audit,
    canonical_audit_bytes,
    load_phase6c_prediction_names,
    load_registry,
    verify_evidence_commit_precedes_v0_5,
    write_prediction_status_audit,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

REGISTRY = (
    ROOT
    / DEFAULT_REGISTRY_RELATIVE_PATH
)

PHASE6C = (
    ROOT
    / DEFAULT_PHASE6C_RELATIVE_PATH
)

PROTOCOL = (
    ROOT
    / DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH
)

CANONICAL_OUTPUT = (
    ROOT
    / DEFAULT_OUTPUT_RELATIVE_PATH
)

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "prediction_status_audit.py"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _audit() -> dict[str, object]:
    return build_prediction_status_audit(
        registry_path=REGISTRY,
        phase6c_path=PHASE6C,
        protocol_path=PROTOCOL,
    )


def _records(
    audit: dict[str, object],
) -> list[dict[str, object]]:
    rows = audit[
        "records"
    ]

    assert isinstance(
        rows,
        list,
    )

    return rows


def _by_id(
    audit: dict[str, object],
) -> dict[str, dict[str, object]]:
    return {
        row[
            "record_id"
        ]: row
        for row in _records(
            audit
        )
    }


def test_frozen_input_hashes() -> None:
    assert _sha256(
        REGISTRY
    ) == EXPECTED_REGISTRY_SHA256

    assert _sha256(
        PHASE6C
    ) == EXPECTED_PHASE6C_SHA256

    assert _sha256(
        PROTOCOL
    ) == EXPECTED_PHASE6D_PROTOCOL_SHA256


def test_registry_contains_exactly_24_records_in_frozen_order() -> None:
    rows = load_registry(
        REGISTRY
    )

    assert len(
        rows
    ) == 24

    assert tuple(
        row[
            "record_id"
        ]
        for row in rows
    ) == EXPECTED_RECORD_ORDER

    assert len(
        set(
            EXPECTED_RECORD_ORDER
        )
    ) == 24


def test_every_frozen_phase6a_status_is_confirmed() -> None:
    audit = _audit()
    rows = _records(
        audit
    )

    assert len(
        rows
    ) == 24

    for row in rows:
        record_id = row[
            "record_id"
        ]

        assert (
            row[
                "frozen_prediction_status"
            ]
            == EXPECTED_STATUS[
                record_id
            ]
        )

        assert (
            row[
                "audit_verdict"
            ]
            == "CONFIRMED"
        )


def test_six_development_used_targets_are_exactly_frozen_set() -> None:
    audit = _audit()

    actual = {
        row[
            "record_id"
        ]
        for row in _records(
            audit
        )
        if row[
            "frozen_prediction_status"
        ]
        == "development_used_target"
    }

    assert actual == DEVELOPMENT_USED_TARGET_IDS

    assert len(
        actual
    ) == 6


def test_pre_v0_5_evidence_commit_is_verified() -> None:
    historical_full = (
        verify_evidence_commit_precedes_v0_5()
    )

    expected_full = subprocess.check_output(
        [
            "git",
            "rev-parse",
            HISTORICAL_EVIDENCE_COMMIT,
        ],
        text=True,
    ).strip()

    assert historical_full == expected_full

    completed = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            historical_full,
            FROZEN_V0_5_COMMIT,
        ],
        check=False,
    )

    assert completed.returncode == 0


def test_each_development_used_target_has_verified_evidence() -> None:
    audit = _audit()
    rows = _by_id(
        audit
    )

    for record_id in DEVELOPMENT_USED_TARGET_IDS:
        row = rows[
            record_id
        ]

        assert (
            row[
                "development_exposure"
            ]
            is True
        )

        evidence = row[
            "development_evidence"
        ]

        assert isinstance(
            evidence,
            list,
        )

        assert evidence

        for item in evidence:
            assert (
                item[
                    "verified"
                ]
                is True
            )

            assert (
                item[
                    "commit"
                ]
            )

            assert (
                item[
                    "path"
                ]
            )

            assert len(
                item[
                    "blob_sha256"
                ]
            ) == 64


def test_no_development_target_is_independent() -> None:
    audit = _audit()
    rows = _by_id(
        audit
    )

    for record_id in DEVELOPMENT_USED_TARGET_IDS:
        assert (
            rows[
                record_id
            ][
                "independent_forward_prediction"
            ]
            is False
        )


def test_frozen_unused_target_count_is_zero() -> None:
    audit = _audit()

    summary = audit[
        "summary"
    ]

    assert isinstance(
        summary,
        dict,
    )

    assert (
        summary[
            "frozen_unused_target_count"
        ]
        == 0
    )


def test_independent_forward_prediction_count_is_zero() -> None:
    audit = _audit()

    summary = audit[
        "summary"
    ]

    assert isinstance(
        summary,
        dict,
    )

    assert (
        summary[
            "independent_forward_prediction_count"
        ]
        == 0
    )

    assert all(
        row[
            "independent_forward_prediction"
        ]
        is False
        for row in _records(
            audit
        )
    )


def test_all_decagon_records_remain_not_evaluable() -> None:
    audit = _audit()
    rows = _by_id(
        audit
    )

    for record_id in DECAGON_IDS:
        row = rows[
            record_id
        ]

        assert (
            row[
                "frozen_prediction_status"
            ]
            == "not_evaluable_from_v0_5"
        )

        assert (
            row[
                "comparison_policy"
            ]
            == "not_evaluable"
        )

        assert (
            row[
                "phase6c_prediction_quantity"
            ]
            is None
        )


def test_somm_004_is_context_only() -> None:
    row = _by_id(
        _audit()
    )[
        "SOMM-004"
    ]

    assert (
        row[
            "frozen_prediction_status"
        ]
        == "descriptive_correspondence"
    )

    assert (
        row[
            "comparison_policy"
        ]
        == "context_only"
    )

    assert (
        row[
            "phase6c_prediction_quantity"
        ]
        is None
    )


def test_somm_006_remains_unit_definition() -> None:
    row = _by_id(
        _audit()
    )[
        "SOMM-006"
    ]

    assert (
        row[
            "frozen_prediction_status"
        ]
        == "unit_definition"
    )

    assert (
        row[
            "comparison_policy"
        ]
        == "no_residual"
    )


def test_phase6c_prediction_name_inventory_is_unchanged() -> None:
    names = load_phase6c_prediction_names(
        PHASE6C
    )

    assert frozenset(
        names
    ) == EXPECTED_PHASE6C_QUANTITIES

    assert len(
        names
    ) == 7


def test_exactly_seven_rows_have_numeric_comparison_policy() -> None:
    audit = _audit()

    actual = {
        row[
            "record_id"
        ]
        for row in _records(
            audit
        )
        if row[
            "comparison_policy"
        ]
        in {
            "retrospective_residual",
            "descriptive_residual",
        }
    }

    assert actual == NUMERIC_COMPARISON_POLICY_IDS
    assert len(
        actual
    ) == 7

    retrospective = {
        row[
            "record_id"
        ]
        for row in _records(
            audit
        )
        if row[
            "comparison_policy"
        ]
        == "retrospective_residual"
    }

    descriptive = {
        row[
            "record_id"
        ]
        for row in _records(
            audit
        )
        if row[
            "comparison_policy"
        ]
        == "descriptive_residual"
    }

    assert retrospective == DEVELOPMENT_USED_TARGET_IDS
    assert descriptive == {
        "WALL12-002"
    }


def test_policy_mapping_is_exactly_preregistered() -> None:
    audit = _audit()

    for row in _records(
        audit
    ):
        assert (
            row[
                "comparison_policy"
            ]
            == EXPECTED_POLICY[
                row[
                    "record_id"
                ]
            ]
        )


def test_phase6d_source_never_reads_numeric_source_or_prediction_values() -> None:
    tree = ast.parse(
        MODULE.read_text(
            encoding="utf-8"
        )
    )

    forbidden_subscript_keys = {
        "source_value",
        "secondary_value",
        "value",
    }

    seen = set()

    for node in ast.walk(
        tree
    ):
        if not isinstance(
            node,
            ast.Subscript,
        ):
            continue

        slice_node = node.slice

        if isinstance(
            slice_node,
            ast.Constant,
        ) and isinstance(
            slice_node.value,
            str,
        ):
            seen.add(
                slice_node.value
            )

    assert not (
        seen
        & forbidden_subscript_keys
    ), (
        seen
        & forbidden_subscript_keys
    )


def test_phase6d_source_imports_no_numeric_analysis_library() -> None:
    tree = ast.parse(
        MODULE.read_text(
            encoding="utf-8"
        )
    )

    imported = set()

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            imported.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported.add(
                node.module
                or ""
            )

    forbidden = {
        "math",
        "statistics",
        "numpy",
        "scipy",
        "pandas",
    }

    assert not (
        imported
        & forbidden
    ), (
        imported
        & forbidden
    )


def test_phase6d_artifact_contains_no_numeric_comparison_fields() -> None:
    audit = _audit()

    forbidden_keys = {
        "source_value",
        "secondary_value",
        "prediction_value",
        "signed_residual",
        "absolute_residual",
        "relative_residual",
        "percent_residual",
        "prediction_to_source_ratio",
        "tolerance_pass",
    }

    def walk(
        value: object,
    ):
        if isinstance(
            value,
            dict,
        ):
            for key, child in value.items():
                yield key
                yield from walk(
                    child
                )

        elif isinstance(
            value,
            list,
        ):
            for child in value:
                yield from walk(
                    child
                )

    keys = set(
        walk(
            audit
        )
    )

    assert not (
        keys
        & forbidden_keys
    )


def test_summary_records_no_numerical_comparisons() -> None:
    audit = _audit()

    boundary = audit[
        "interpretation_boundary"
    ]

    assert isinstance(
        boundary,
        dict,
    )

    assert (
        boundary[
            "classification_uses_numeric_source_values"
        ]
        is False
    )

    assert (
        boundary[
            "classification_uses_numeric_prediction_values"
        ]
        is False
    )

    assert (
        boundary[
            "numerical_comparisons_calculated"
        ]
        is False
    )

    assert (
        boundary[
            "independent_validation_language_permitted_for_registered_wall_targets"
        ]
        is False
    )


def test_all_audit_verdicts_are_confirmed_and_phase6e_unblocked() -> None:
    audit = _audit()

    summary = audit[
        "summary"
    ]

    assert (
        summary[
            "registry_record_count"
        ]
        == 24
    )

    assert (
        summary[
            "confirmed_record_count"
        ]
        == 24
    )

    assert (
        summary[
            "contradiction_count"
        ]
        == 0
    )

    assert (
        summary[
            "phase6e_blocked"
        ]
        is False
    )


def test_artifact_contains_no_absolute_home_path() -> None:
    text = canonical_audit_bytes(
        _audit()
    ).decode(
        "utf-8"
    )

    assert "/home/" not in text
    assert "/Users/" not in text


def test_audit_serialization_is_deterministic() -> None:
    first = canonical_audit_bytes(
        _audit()
    )

    second = canonical_audit_bytes(
        _audit()
    )

    assert first == second


def test_tracked_audit_matches_regeneration(
    tmp_path: Path,
) -> None:
    generated = (
        tmp_path
        / "prediction_status_audit.json"
    )

    generated_bytes = (
        write_prediction_status_audit(
            registry_path=REGISTRY,
            phase6c_path=PHASE6C,
            protocol_path=PROTOCOL,
            output_path=generated,
        )
    )

    assert generated.read_bytes() == generated_bytes

    if CANONICAL_OUTPUT.exists():
        assert (
            CANONICAL_OUTPUT.read_bytes()
            == generated_bytes
        )


def test_audit_artifact_is_valid_json() -> None:
    parsed = json.loads(
        canonical_audit_bytes(
            _audit()
        )
    )

    assert parsed[
        "phase"
    ] == "6D"
