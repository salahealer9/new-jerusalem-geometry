from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import importlib.util
import json


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "synthesize_v1_0_plato_michell_history.py"
)

JSON_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_historical_synthesis.json"
)

CSV_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_michell_claim_matrix.csv"
)

MARKDOWN_PATH = (
    ROOT
    / "docs"
    / "geometry"
    / "v1.0_plato_michell_historical_synthesis.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _payload() -> dict:
    return json.loads(
        JSON_PATH.read_text(
            encoding="utf-8"
        )
    )


def _claims() -> list[dict[str, str]]:
    with CSV_PATH.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(
                handle
            )
        )


def _load_script_module():
    spec = importlib.util.spec_from_file_location(
        "phase10f_synthesis",
        SCRIPT,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def test_phase10f_status() -> None:
    assert (
        _payload()[
            "status"
        ]
        == "PLATO_MICHELL_HISTORICAL_SYNTHESIS_COMPLETE"
    )


def test_phase10f_provenance_layers_are_separate() -> None:
    layers = _payload()[
        "provenance_layers"
    ]

    assert (
        layers[
            "plato"
        ]
        == "DIRECT_PLATO_TEXT"
    )

    assert (
        layers[
            "michell"
        ]
        == "MICHELL_EXPLICIT"
    )

    assert (
        layers[
            "reconstruction"
        ]
        == "PROJECT_RECONSTRUCTION"
    )


def test_phase10f_established_plato_boundary() -> None:
    plato = _payload()[
        "established"
    ][
        "plato"
    ]

    assert (
        plato[
            "total_whorls"
        ]
        == 8
    )

    assert (
        plato[
            "width_order_broadest_to_narrowest"
        ]
        == [
            1,
            6,
            4,
            8,
            7,
            5,
            3,
            2,
        ]
    )

    assert (
        plato[
            "numeric_width_values_stated"
        ]
        is False
    )


def test_phase10f_established_michell_layer() -> None:
    michell = _payload()[
        "established"
    ][
        "michell"
    ]

    assert (
        michell[
            "same_ordinal_width_order"
        ]
        is True
    )

    assert (
        michell[
            "musical_number_sequence"
        ]
        == [
            6,
            8,
            9,
            12,
            18,
            24,
            27,
            36,
        ]
    )

    assert (
        michell[
            "shaft_radius"
        ]
        == 4
    )

    assert (
        michell[
            "scale_factor"
        ]
        == 180
    )


def test_phase10f_project_reconstruction_has_zero_fit() -> None:
    project = _payload()[
        "established"
    ][
        "project_reconstruction"
    ]

    assert (
        project[
            "all_printed_values_reproduced_exactly"
        ]
        is True
    )

    assert (
        project[
            "free_parameters"
        ]
        == 0
    )

    assert (
        project[
            "permutation_searches"
        ]
        == 0
    )


def test_phase10f_comparative_findings() -> None:
    findings = _payload()[
        "comparative_findings"
    ]

    assert (
        findings[
            "ordinal_continuity_plato_to_michell"
        ]
        is True
    )

    assert (
        findings[
            "numerical_magnitudes_added_in_michell_layer"
        ]
        is True
    )

    assert (
        findings[
            "michell_numeric_sequence_is_direct_plato_text"
        ]
        is False
    )

    assert (
        findings[
            "numerical_reproducibility_implies_historical_transmission"
        ]
        is False
    )


def test_phase10f_historical_boundary() -> None:
    boundary = _payload()[
        "historical_boundary"
    ]

    assert (
        boundary[
            "plato_numeric_intention_established"
        ]
        is False
    )

    assert (
        boundary[
            "ancient_transmission_established"
        ]
        is False
    )

    assert (
        boundary[
            "michell_numerical_interpretation_documented"
        ]
        is True
    )

    assert (
        boundary[
            "michell_internal_arithmetic_reproduced"
        ]
        is True
    )

    assert (
        boundary[
            "sommerville_archival_status"
        ]
        == "archival_pending"
    )

    assert (
        boundary[
            "interpretive_framework_status"
        ]
        == "deferred"
    )


def test_phase10f_claim_matrix_has_unique_ids_and_classes() -> None:
    rows = _claims()

    assert (
        len(
            rows
        )
        == 13
    )

    ids = [
        row[
            "claim_id"
        ]
        for row in rows
    ]

    assert (
        len(
            set(
                ids
            )
        )
        == len(
            ids
        )
    )

    allowed = {
        "DIRECT_PLATO_TEXT",
        "MICHELL_EXPLICIT",
        "PROJECT_RECONSTRUCTION",
        "SUPPORTING_HISTORICAL_CONTEXT",
        "ARCHIVAL_PENDING",
        "INTERPRETIVE_EXCLUDED",
    }

    assert all(
        row[
            "provenance_class"
        ]
        in allowed
        for row in rows
    )


def test_phase10f_claim_matrix_expected_claims() -> None:
    by_id = {
        row[
            "claim_id"
        ]: row
        for row in _claims()
    }

    assert (
        by_id[
            "V10-PLATO-003"
        ][
            "status"
        ]
        == "verified_negative"
    )

    assert (
        by_id[
            "V10-MICHELL-002"
        ][
            "provenance_class"
        ]
        == "MICHELL_EXPLICIT"
    )

    assert (
        by_id[
            "V10-RECON-001"
        ][
            "provenance_class"
        ]
        == "PROJECT_RECONSTRUCTION"
    )

    assert (
        by_id[
            "V10-ARCHIVE-001"
        ][
            "provenance_class"
        ]
        == "ARCHIVAL_PENDING"
    )

    assert (
        by_id[
            "V10-INTERP-001"
        ][
            "provenance_class"
        ]
        == "INTERPRETIVE_EXCLUDED"
    )


def test_phase10f_regeneration_is_deterministic() -> None:
    module = _load_script_module()

    before_json = JSON_PATH.read_bytes()
    before_csv = CSV_PATH.read_bytes()
    before_markdown = MARKDOWN_PATH.read_bytes()

    module.write_outputs()

    assert (
        JSON_PATH.read_bytes()
        == before_json
    )

    assert (
        CSV_PATH.read_bytes()
        == before_csv
    )

    assert (
        MARKDOWN_PATH.read_bytes()
        == before_markdown
    )


def test_phase10f_markdown_has_required_boundary_language() -> None:
    text = MARKDOWN_PATH.read_text(
        encoding="utf-8"
    )

    required = (
        "Plato provides an ordinal eight-whorl structure",
        "Michell documents a later numerical interpretation",
        "does **not** establish that Plato supplied or intended",
        "does **not** establish historical transmission",
        "`ARCHIVAL_PENDING`",
        "`INTERPRETIVE_EXCLUDED`",
    )

    for phrase in required:
        assert phrase in text

