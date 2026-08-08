"""Prediction-status and development-leakage audit for v0.6 Phase 6D.

This module classifies the evidential role of the frozen Phase 6A registry
records before any Phase 6E numerical comparison is performed.

It intentionally does not read historical source-value fields and does not
read numerical values from the Phase 6C prediction rows.
"""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


EXPECTED_REGISTRY_SHA256 = (
    "8c534ddc1a6fe6f2b233b4352202d753"
    "8a5379787bc4313a3759916f8b150f5e"
)

EXPECTED_PHASE6C_SHA256 = (
    "d8399adbfd4c679ebb0ad93dc787049c9"
    "8a084cb01b033d42e99a97aecc90d46"
)

EXPECTED_PHASE6D_PROTOCOL_SHA256 = (
    "d6f2616201192b37ee863ab15d194a8b"
    "8726977284c6f89a6a3aaa44b9c2fa6d"
)

FROZEN_V0_5_COMMIT = (
    "c3a051f197ef98389605c9e19e3bc83b42ad779c"
)

HISTORICAL_EVIDENCE_COMMIT = "44c6283"

DEFAULT_REGISTRY_RELATIVE_PATH = Path(
    "docs/sources/v0.6_metrology_registry.csv"
)

DEFAULT_PHASE6C_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "frozen_dimensional_predictions.json"
)

DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH = Path(
    "docs/specification/"
    "v0.6_prediction_status_leakage_protocol.md"
)

DEFAULT_OUTPUT_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "prediction_status_audit.json"
)

EXPECTED_RECORD_ORDER = (
    "CORE-001",
    "CORE-002",
    "CORE-003",
    "CORE-004",
    "CORE-005",
    "SCALE-001",
    "SCALE-002",
    "UNIT-001",
    "UNIT-002",
    "UNIT-003",
    "UNIT-004",
    "WALL12-001",
    "WALL12-002",
    "WALL12-003",
    "SOMM-001",
    "SOMM-002",
    "SOMM-003",
    "SOMM-004",
    "SOMM-005",
    "SOMM-006",
    "DECAGON-001",
    "DECAGON-002",
    "DECAGON-003",
    "DECAGON-004",
)

EXPECTED_STATUS = {
    "CORE-001": "construction_input",
    "CORE-002": "construction_input",
    "CORE-003": "construction_identity",
    "CORE-004": "construction_identity",
    "CORE-005": "construction_identity",
    "SCALE-001": "unit_definition",
    "SCALE-002": "construction_input",
    "UNIT-001": "unit_definition",
    "UNIT-002": "unit_definition",
    "UNIT-003": "unit_definition",
    "UNIT-004": "unit_definition",
    "WALL12-001": "development_used_target",
    "WALL12-002": "construction_identity",
    "WALL12-003": "development_used_target",
    "SOMM-001": "development_used_target",
    "SOMM-002": "development_used_target",
    "SOMM-003": "development_used_target",
    "SOMM-004": "descriptive_correspondence",
    "SOMM-005": "development_used_target",
    "SOMM-006": "unit_definition",
    "DECAGON-001": "not_evaluable_from_v0_5",
    "DECAGON-002": "not_evaluable_from_v0_5",
    "DECAGON-003": "not_evaluable_from_v0_5",
    "DECAGON-004": "not_evaluable_from_v0_5",
}

EXPECTED_POLICY = {
    "CORE-001": "no_residual",
    "CORE-002": "no_residual",
    "CORE-003": "no_residual",
    "CORE-004": "no_residual",
    "CORE-005": "no_residual",
    "SCALE-001": "no_residual",
    "SCALE-002": "no_residual",
    "UNIT-001": "no_residual",
    "UNIT-002": "no_residual",
    "UNIT-003": "no_residual",
    "UNIT-004": "no_residual",
    "WALL12-001": "retrospective_residual",
    "WALL12-002": "descriptive_residual",
    "WALL12-003": "retrospective_residual",
    "SOMM-001": "retrospective_residual",
    "SOMM-002": "retrospective_residual",
    "SOMM-003": "retrospective_residual",
    "SOMM-004": "context_only",
    "SOMM-005": "retrospective_residual",
    "SOMM-006": "no_residual",
    "DECAGON-001": "not_evaluable",
    "DECAGON-002": "not_evaluable",
    "DECAGON-003": "not_evaluable",
    "DECAGON-004": "not_evaluable",
}

EXPECTED_PHASE6C_QUANTITY = {
    "WALL12-001": "mean_side_current_foot",
    "WALL12-002": "wall_perimeter_megalithic_yard",
    "WALL12-003": "wall_area_square_foot",
    "SOMM-001": "polar_side_current_foot",
    "SOMM-002": "oblique_side_current_foot",
    "SOMM-003": "wall_area_square_foot",
    "SOMM-005": "wall_perimeter_old_english_foot",
}

EXPECTED_PHASE6C_QUANTITIES = frozenset(
    {
        "mean_side_current_foot",
        "oblique_side_current_foot",
        "polar_side_current_foot",
        "wall_area_square_foot",
        "wall_perimeter_current_foot",
        "wall_perimeter_megalithic_yard",
        "wall_perimeter_old_english_foot",
    }
)

DEVELOPMENT_USED_TARGET_IDS = frozenset(
    {
        "WALL12-001",
        "WALL12-003",
        "SOMM-001",
        "SOMM-002",
        "SOMM-003",
        "SOMM-005",
    }
)

NUMERIC_COMPARISON_POLICY_IDS = frozenset(
    {
        "WALL12-001",
        "WALL12-002",
        "WALL12-003",
        "SOMM-001",
        "SOMM-002",
        "SOMM-003",
        "SOMM-005",
    }
)

DECAGON_IDS = frozenset(
    {
        "DECAGON-001",
        "DECAGON-002",
        "DECAGON-003",
        "DECAGON-004",
    }
)


@dataclass(frozen=True)
class EvidenceSpec:
    """One immutable Git-history evidence requirement."""

    commit: str
    path: str
    exposure_kinds: tuple[str, ...]
    required_fragments: tuple[str, ...]


DEVELOPMENT_EVIDENCE = {
    "WALL12-001": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="docs/sources/geometric_claim_matrix.csv",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
            ),
            required_fragments=(
                "WALL-003",
                (
                    "Provides a numerical target for candidate "
                    "wall reconstructions"
                ),
            ),
        ),
    ),
    "WALL12-003": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="docs/sources/geometric_claim_matrix.csv",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
            ),
            required_fragments=(
                "WALL-004",
                (
                    "Provides an area target for candidate "
                    "wall reconstructions"
                ),
            ),
        ),
    ),
    "SOMM-001": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="README.md",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
                "target_used_in_model_preference",
            ),
            required_fragments=(
                "four polar sides",
                "current preferred combined reconstruction because",
                "POLAR_PIVOT_TANGENT",
            ),
        ),
    ),
    "SOMM-002": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="README.md",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
                "target_used_in_model_preference",
            ),
            required_fragments=(
                "eight oblique sides",
                "current preferred combined reconstruction because",
                "POLAR_PIVOT_TANGENT",
            ),
        ),
    ),
    "SOMM-003": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="README.md",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
                "target_used_in_model_preference",
            ),
            required_fragments=(
                "* area:",
                "current preferred combined reconstruction because",
                "POLAR_PIVOT_TANGENT",
            ),
        ),
    ),
    "SOMM-005": (
        EvidenceSpec(
            commit=HISTORICAL_EVIDENCE_COMMIT,
            path="README.md",
            exposure_kinds=(
                "target_known_before_freeze",
                "target_used_in_model_assessment",
                "target_used_in_model_preference",
            ),
            required_fragments=(
                "old-English-foot perimeter",
                "current preferred combined reconstruction because",
                "POLAR_PIVOT_TANGENT",
            ),
        ),
    ),
}

NOTES = {
    "CORE-001": (
        "Frozen construction input; no predictive residual is permitted."
    ),
    "CORE-002": (
        "Frozen construction input; no predictive residual is permitted."
    ),
    "CORE-003": (
        "Construction identity; numerical agreement is not an independent test."
    ),
    "CORE-004": (
        "Construction identity; numerical agreement is not an independent test."
    ),
    "CORE-005": (
        "Construction identity under the registered source convention."
    ),
    "SCALE-001": (
        "Model-scale definition; not a prediction target."
    ),
    "SCALE-002": (
        "Frozen construction input used to derive dimensional scale."
    ),
    "UNIT-001": (
        "Unit definition used by Phase 6B; not a prediction target."
    ),
    "UNIT-002": (
        "Unit definition used by Phase 6B; not a prediction target."
    ),
    "UNIT-003": (
        "Unit definition used by Phase 6B; not a prediction target."
    ),
    "UNIT-004": (
        "Unit definition used by Phase 6B; not a prediction target."
    ),
    "WALL12-001": (
        "Historical mean-side quantity was already registered as a wall "
        "reconstruction target before the v0.5 freeze."
    ),
    "WALL12-002": (
        "Source arithmetic identity; Phase 6E may show a descriptive "
        "difference but no predictive interpretation."
    ),
    "WALL12-003": (
        "Historical area quantity was already registered as a wall "
        "reconstruction target before the v0.5 freeze."
    ),
    "SOMM-001": (
        "Later polar-side quantity was known and its dimensional closure "
        "contributed to preference for the polar-pivot wall."
    ),
    "SOMM-002": (
        "Later oblique-side quantity was known and its dimensional closure "
        "contributed to preference for the polar-pivot wall."
    ),
    "SOMM-003": (
        "Later area quantity was known and its dimensional closure contributed "
        "to preference for the polar-pivot wall."
    ),
    "SOMM-004": (
        "Historical working tolerance is context only and cannot become a "
        "post-hoc pass/fail rule."
    ),
    "SOMM-005": (
        "Later old-English-foot perimeter was known and its dimensional "
        "closure contributed to preference for the polar-pivot wall."
    ),
    "SOMM-006": (
        "Unit-length ratio parameterizes Phase 6B and is not a prediction."
    ),
    "DECAGON-001": (
        "The required decagon object is absent from frozen v0.5 geometry."
    ),
    "DECAGON-002": (
        "The required decagon object is absent from frozen v0.5 geometry."
    ),
    "DECAGON-003": (
        "The required decagon object is absent from frozen v0.5 geometry."
    ),
    "DECAGON-004": (
        "The required decagon object is absent from frozen v0.5 geometry."
    ),
}


def sha256_file(
    path: Path,
) -> str:
    """Return a file SHA-256."""
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load_registry(
    path: Path,
) -> tuple[dict[str, str], ...]:
    """Load the frozen Phase 6A registry without interpreting numeric fields."""
    if (
        sha256_file(
            path
        )
        != EXPECTED_REGISTRY_SHA256
    ):
        raise ValueError(
            "Phase 6A registry hash does not match the frozen input."
        )

    with path.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = tuple(
            dict(
                row
            )
            for row in csv.DictReader(
                handle
            )
        )

    record_ids = tuple(
        row[
            "record_id"
        ]
        for row in rows
    )

    if (
        record_ids
        != EXPECTED_RECORD_ORDER
    ):
        raise ValueError(
            "Phase 6A registry record order differs from "
            "the frozen Phase 6D protocol."
        )

    return rows


def load_phase6c_prediction_names(
    path: Path,
) -> tuple[str, ...]:
    """Verify Phase 6C and return prediction names only."""
    if (
        sha256_file(
            path
        )
        != EXPECTED_PHASE6C_SHA256
    ):
        raise ValueError(
            "Phase 6C prediction hash does not match the frozen input."
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    predictions = payload.get(
        "dimensional_predictions"
    )

    if not isinstance(
        predictions,
        dict,
    ):
        raise ValueError(
            "Phase 6C artifact lacks dimensional_predictions."
        )

    names = tuple(
        predictions.keys()
    )

    if (
        frozenset(
            names
        )
        != EXPECTED_PHASE6C_QUANTITIES
    ):
        raise ValueError(
            "Phase 6C prediction-name inventory has changed."
        )

    return names


def verify_phase6d_protocol(
    path: Path,
) -> str:
    """Verify the corrected preregistered Phase 6D protocol."""
    actual = sha256_file(
        path
    )

    if (
        actual
        != EXPECTED_PHASE6D_PROTOCOL_SHA256
    ):
        raise ValueError(
            "Phase 6D protocol hash does not match the corrected freeze."
        )

    return actual


def _git_output(
    *args: str,
) -> str:
    try:
        return subprocess.check_output(
            [
                "git",
                *args,
            ],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        raise ValueError(
            "Git provenance command failed: "
            + " ".join(
                exc.cmd
            )
            + "\n"
            + exc.output
        ) from exc


def verify_evidence_commit_precedes_v0_5() -> str:
    """Verify the historical evidence commit is an ancestor of v0.5."""
    historical_full = _git_output(
        "rev-parse",
        HISTORICAL_EVIDENCE_COMMIT,
    ).strip()

    frozen_full = _git_output(
        "rev-parse",
        FROZEN_V0_5_COMMIT,
    ).strip()

    if (
        frozen_full
        != FROZEN_V0_5_COMMIT
    ):
        raise ValueError(
            "Frozen v0.5 commit identifier did not resolve exactly."
        )

    completed = subprocess.run(
        [
            "git",
            "merge-base",
            "--is-ancestor",
            historical_full,
            frozen_full,
        ],
        check=False,
    )

    if completed.returncode != 0:
        raise ValueError(
            "Historical evidence commit is not an ancestor of v0.5."
        )

    return historical_full


def verify_development_evidence(
    spec: EvidenceSpec,
) -> dict[str, object]:
    """Verify one immutable pre-v0.5 evidence item."""
    commit_full = _git_output(
        "rev-parse",
        spec.commit,
    ).strip()

    historical_full = verify_evidence_commit_precedes_v0_5()

    if (
        commit_full
        != historical_full
    ):
        raise ValueError(
            "Unexpected development-evidence commit."
        )

    content = _git_output(
        "show",
        f"{commit_full}:{spec.path}",
    )

    missing = tuple(
        fragment
        for fragment in spec.required_fragments
        if fragment not in content
    )

    if missing:
        raise ValueError(
            f"Historical evidence missing required fragments "
            f"for {spec.path}: {missing!r}"
        )

    return {
        "commit": commit_full,
        "path": spec.path,
        "blob_sha256": hashlib.sha256(
            content.encode(
                "utf-8"
            )
        ).hexdigest(),
        "exposure_kinds": list(
            spec.exposure_kinds
        ),
        "verified": True,
    }


def _audit_row(
    row: Mapping[str, str],
) -> dict[str, object]:
    record_id = row[
        "record_id"
    ]

    frozen_status = row[
        "prediction_status"
    ]

    expected_status = EXPECTED_STATUS[
        record_id
    ]

    verdict = (
        "CONFIRMED"
        if frozen_status == expected_status
        else "CONTRADICTION"
    )

    development_used = (
        record_id
        in DEVELOPMENT_USED_TARGET_IDS
    )

    evidence_specs = DEVELOPMENT_EVIDENCE.get(
        record_id,
        (),
    )

    evidence = [
        verify_development_evidence(
            spec
        )
        for spec in evidence_specs
    ]

    exposure_kinds = sorted(
        {
            kind
            for item in evidence
            for kind in item[
                "exposure_kinds"
            ]
        }
    )

    if development_used and not evidence:
        raise ValueError(
            f"{record_id} lacks required pre-v0.5 development evidence."
        )

    if (
        not development_used
        and evidence
    ):
        raise ValueError(
            f"{record_id} unexpectedly carries development evidence."
        )

    return {
        "record_id": record_id,
        "frozen_prediction_status": frozen_status,
        "audit_verdict": verdict,
        "comparison_policy": EXPECTED_POLICY[
            record_id
        ],
        "phase6c_prediction_quantity": (
            EXPECTED_PHASE6C_QUANTITY.get(
                record_id
            )
        ),
        "development_exposure": development_used,
        "development_exposure_kinds": exposure_kinds,
        "development_evidence": evidence,
        "independent_forward_prediction": False,
        "notes": NOTES[
            record_id
        ],
    }


def build_prediction_status_audit(
    *,
    registry_path: Path,
    phase6c_path: Path,
    protocol_path: Path,
) -> dict[str, object]:
    """Build the complete 24-record Phase 6D audit."""
    rows = load_registry(
        registry_path
    )

    prediction_names = load_phase6c_prediction_names(
        phase6c_path
    )

    protocol_sha256 = verify_phase6d_protocol(
        protocol_path
    )

    historical_commit_full = (
        verify_evidence_commit_precedes_v0_5()
    )

    audit_rows = tuple(
        _audit_row(
            row
        )
        for row in rows
    )

    contradictions = tuple(
        row[
            "record_id"
        ]
        for row in audit_rows
        if row[
            "audit_verdict"
        ]
        != "CONFIRMED"
    )

    if contradictions:
        raise ValueError(
            "Phase 6D classification contradiction(s): "
            + ", ".join(
                contradictions
            )
        )

    status_counts = Counter(
        row[
            "frozen_prediction_status"
        ]
        for row in audit_rows
    )

    policy_counts = Counter(
        row[
            "comparison_policy"
        ]
        for row in audit_rows
    )

    development_count = sum(
        bool(
            row[
                "development_exposure"
            ]
        )
        for row in audit_rows
    )

    frozen_unused_count = status_counts.get(
        "frozen_unused_target",
        0,
    )

    independent_count = sum(
        bool(
            row[
                "independent_forward_prediction"
            ]
        )
        for row in audit_rows
    )

    numeric_policy_count = sum(
        row[
            "comparison_policy"
        ]
        in {
            "retrospective_residual",
            "descriptive_residual",
        }
        for row in audit_rows
    )

    if development_count != 6:
        raise ValueError(
            "Expected exactly six development-used targets."
        )

    if frozen_unused_count != 0:
        raise ValueError(
            "Frozen-unused target count must remain zero."
        )

    if independent_count != 0:
        raise ValueError(
            "Independent-forward-prediction count must remain zero."
        )

    if numeric_policy_count != 7:
        raise ValueError(
            "Corrected Phase 6D protocol requires exactly seven "
            "numeric-comparison-policy rows."
        )

    return {
        "schema_version": 1,
        "phase": "6D",
        "analysis_id": (
            "njg-michell-v0-6-prediction-status-audit-v1"
        ),
        "frozen_inputs": {
            "registry": {
                "path": str(
                    DEFAULT_REGISTRY_RELATIVE_PATH
                ),
                "sha256": EXPECTED_REGISTRY_SHA256,
            },
            "phase6c_predictions": {
                "path": str(
                    DEFAULT_PHASE6C_RELATIVE_PATH
                ),
                "sha256": EXPECTED_PHASE6C_SHA256,
            },
            "phase6d_protocol": {
                "path": str(
                    DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH
                ),
                "sha256": protocol_sha256,
            },
            "v0_5_geometry_commit": FROZEN_V0_5_COMMIT,
            "historical_evidence_commit": historical_commit_full,
        },
        "prediction_name_inventory": list(
            prediction_names
        ),
        "summary": {
            "registry_record_count": len(
                audit_rows
            ),
            "confirmed_record_count": len(
                audit_rows
            ),
            "contradiction_count": 0,
            "development_used_target_count": development_count,
            "frozen_unused_target_count": frozen_unused_count,
            "independent_forward_prediction_count": independent_count,
            "numeric_comparison_policy_count": numeric_policy_count,
            "status_counts": dict(
                sorted(
                    status_counts.items()
                )
            ),
            "comparison_policy_counts": dict(
                sorted(
                    policy_counts.items()
                )
            ),
            "phase6e_blocked": False,
        },
        "interpretation_boundary": {
            "classification_uses_numeric_source_values": False,
            "classification_uses_numeric_prediction_values": False,
            "numerical_comparisons_calculated": False,
            "independent_validation_language_permitted_for_registered_wall_targets": (
                False
            ),
        },
        "records": list(
            audit_rows
        ),
    }


def canonical_audit_bytes(
    payload: Mapping[str, object],
) -> bytes:
    """Serialize the Phase 6D artifact deterministically."""
    text = json.dumps(
        payload,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
    )

    return (
        text
        + "\n"
    ).encode(
        "utf-8"
    )


def write_prediction_status_audit(
    *,
    registry_path: Path,
    phase6c_path: Path,
    protocol_path: Path,
    output_path: Path,
) -> bytes:
    """Build and write the deterministic Phase 6D audit."""
    payload = build_prediction_status_audit(
        registry_path=registry_path,
        phase6c_path=phase6c_path,
        protocol_path=protocol_path,
    )

    encoded = canonical_audit_bytes(
        payload
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(
        encoded
    )

    return encoded
