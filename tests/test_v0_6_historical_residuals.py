from __future__ import annotations

import ast
import csv
import hashlib
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from io import StringIO
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.historical_residuals import (
    DEFAULT_CSV_OUTPUT_RELATIVE_PATH,
    DEFAULT_JSON_OUTPUT_RELATIVE_PATH,
    DEFAULT_MARKDOWN_OUTPUT_RELATIVE_PATH,
    DEFAULT_PHASE6C_RELATIVE_PATH,
    DEFAULT_PHASE6D_RELATIVE_PATH,
    DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH,
    DEFAULT_REGISTRY_RELATIVE_PATH,
    DEFAULT_UNIT_MANIFEST_RELATIVE_PATH,
    DECIMAL_PRECISION,
    DUPLICATE_AREA_GROUP,
    DUPLICATE_AREA_RECORDS,
    EXPECTED_COMPARISON_RECORD_ORDER,
    EXPECTED_PHASE6C_SHA256,
    EXPECTED_PHASE6D_SHA256,
    EXPECTED_PHASE6E_PROTOCOL_SHA256,
    EXPECTED_REGISTRY_SHA256,
    EXPECTED_UNIT_MANIFEST_SHA256,
    FORBIDDEN_AGGREGATE_KEYS,
    UNIT_INVARIANCE_TOLERANCE,
    build_historical_residual_report,
    canonical_csv_text,
    canonical_json_bytes,
    canonical_markdown_text,
    convert_value,
    load_registry_rows,
    load_unit_manifest,
    write_historical_residual_outputs,
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

UNIT_MANIFEST = (
    ROOT
    / DEFAULT_UNIT_MANIFEST_RELATIVE_PATH
)

PHASE6C = (
    ROOT
    / DEFAULT_PHASE6C_RELATIVE_PATH
)

PHASE6D = (
    ROOT
    / DEFAULT_PHASE6D_RELATIVE_PATH
)

PROTOCOL = (
    ROOT
    / DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH
)

JSON_OUTPUT = (
    ROOT
    / DEFAULT_JSON_OUTPUT_RELATIVE_PATH
)

CSV_OUTPUT = (
    ROOT
    / DEFAULT_CSV_OUTPUT_RELATIVE_PATH
)

MARKDOWN_OUTPUT = (
    ROOT
    / DEFAULT_MARKDOWN_OUTPUT_RELATIVE_PATH
)

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "historical_residuals.py"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _report() -> dict[str, object]:
    return build_historical_residual_report(
        registry_path=REGISTRY,
        unit_manifest_path=UNIT_MANIFEST,
        phase6c_path=PHASE6C,
        phase6d_path=PHASE6D,
        protocol_path=PROTOCOL,
    )


def _comparisons() -> list[dict[str, object]]:
    rows = _report()[
        "comparisons"
    ]

    assert isinstance(
        rows,
        list,
    )

    return rows


def _by_id() -> dict[str, dict[str, object]]:
    return {
        str(
            row[
                "record_id"
            ]
        ): row
        for row in _comparisons()
    }


def _walk_keys(
    value: object,
):
    if isinstance(
        value,
        dict,
    ):
        for key, child in value.items():
            yield key
            yield from _walk_keys(
                child
            )

    elif isinstance(
        value,
        list,
    ):
        for child in value:
            yield from _walk_keys(
                child
            )


def test_frozen_input_hashes() -> None:
    assert _sha256(
        REGISTRY
    ) == EXPECTED_REGISTRY_SHA256

    assert _sha256(
        UNIT_MANIFEST
    ) == EXPECTED_UNIT_MANIFEST_SHA256

    assert _sha256(
        PHASE6C
    ) == EXPECTED_PHASE6C_SHA256

    assert _sha256(
        PHASE6D
    ) == EXPECTED_PHASE6D_SHA256

    assert _sha256(
        PROTOCOL
    ) == EXPECTED_PHASE6E_PROTOCOL_SHA256


def test_exactly_seven_comparison_rows_in_frozen_order() -> None:
    rows = _comparisons()

    assert len(
        rows
    ) == 7

    assert tuple(
        row[
            "record_id"
        ]
        for row in rows
    ) == EXPECTED_COMPARISON_RECORD_ORDER


def test_six_retrospective_and_one_descriptive() -> None:
    rows = _comparisons()

    retrospective = [
        row
        for row in rows
        if row[
            "comparison_policy"
        ]
        == "retrospective_residual"
    ]

    descriptive = [
        row
        for row in rows
        if row[
            "comparison_policy"
        ]
        == "descriptive_residual"
    ]

    assert len(
        retrospective
    ) == 6

    assert len(
        descriptive
    ) == 1

    assert descriptive[
        0
    ][
        "record_id"
    ] == "WALL12-002"


def test_no_comparison_is_independent_forward_prediction() -> None:
    assert all(
        row[
            "independent_forward_prediction"
        ]
        is False
        for row in _comparisons()
    )


def test_source_values_come_directly_from_frozen_registry() -> None:
    registry = {
        row[
            "record_id"
        ]: row
        for row in load_registry_rows(
            REGISTRY
        )
    }

    for row in _comparisons():
        source = row[
            "source"
        ]

        assert isinstance(
            source,
            dict,
        )

        frozen = registry[
            row[
                "record_id"
            ]
        ]

        assert (
            source[
                "value"
            ]
            == frozen[
                "source_value"
            ]
        )

        assert (
            source[
                "unit"
            ]
            == frozen[
                "source_unit"
            ]
        )


def test_phase6c_quantity_names_are_inherited_from_phase6d() -> None:
    audit = json.loads(
        PHASE6D.read_text(
            encoding="utf-8"
        )
    )

    mapping = {
        row[
            "record_id"
        ]: row[
            "phase6c_prediction_quantity"
        ]
        for row in audit[
            "records"
        ]
    }

    for row in _comparisons():
        assert (
            row[
                "phase6c_prediction_quantity"
            ]
            == mapping[
                row[
                    "record_id"
                ]
            ]
        )


def test_prediction_values_are_loaded_from_phase6c() -> None:
    phase6c = json.loads(
        PHASE6C.read_text(
            encoding="utf-8"
        ),
        parse_float=Decimal,
    )

    predictions = phase6c[
        "dimensional_predictions"
    ]

    for row in _comparisons():
        quantity = row[
            "phase6c_prediction_quantity"
        ]

        source_prediction = predictions[
            quantity
        ]

        original = row[
            "prediction_original"
        ]

        assert isinstance(
            original,
            dict,
        )

        assert Decimal(
            original[
                "value"
            ]
        ) == source_prediction[
            "value"
        ]

        assert (
            original[
                "unit"
            ]
            == source_prediction[
                "unit"
            ]
        )


def test_phase6e_module_does_not_import_geometry_builders() -> None:
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

    forbidden_fragments = (
        "michell_composite",
        "polar_pivot_wall",
        "core_geometry",
        "wall_geometry",
    )

    assert not any(
        fragment in module
        for module in imported
        for fragment in forbidden_fragments
    )


def test_signed_residual_is_prediction_minus_source() -> None:
    for row in _comparisons():
        prediction = Decimal(
            row[
                "prediction_in_source_unit"
            ][
                "value"
            ]
        )

        source = Decimal(
            row[
                "source"
            ][
                "value"
            ]
        )

        expected = (
            prediction
            - source
        )

        assert Decimal(
            row[
                "signed_residual"
            ]
        ) == expected


def test_absolute_residual_is_absolute_signed_residual() -> None:
    for row in _comparisons():
        assert Decimal(
            row[
                "absolute_residual"
            ]
        ) == abs(
            Decimal(
                row[
                    "signed_residual"
                ]
            )
        )


def test_relative_residual_formula() -> None:
    for row in _comparisons():
        prediction = Decimal(
            row[
                "prediction_in_source_unit"
            ][
                "value"
            ]
        )

        source = Decimal(
            row[
                "source"
            ][
                "value"
            ]
        )

        with __import__(
            "decimal"
        ).localcontext() as context:
            context.prec = 50

            expected = (
                prediction
                - source
            ) / source

        assert Decimal(
            row[
                "relative_residual"
            ]
        ) == expected


def test_percent_residual_formula() -> None:
    for row in _comparisons():
        with localcontext() as context:
            context.prec = DECIMAL_PRECISION

            expected = (
                Decimal(
                    100
                )
                * Decimal(
                    row[
                        "relative_residual"
                    ]
                )
            )

        assert Decimal(
            row[
                "percent_residual"
            ]
        ) == expected


def test_absolute_percent_residual_formula() -> None:
    for row in _comparisons():
        value = Decimal(
            row[
                "absolute_percent_residual"
            ]
        )

        with localcontext() as context:
            context.prec = DECIMAL_PRECISION

            expected = abs(
                Decimal(
                    row[
                        "percent_residual"
                    ]
                )
            )

        assert value >= 0
        assert value == expected


def test_all_source_values_are_nonzero() -> None:
    assert all(
        not Decimal(
            row[
                "source"
            ][
                "value"
            ]
        ).is_zero()
        for row in _comparisons()
    )


def test_unit_reexpression_preserves_relative_residual() -> None:
    for row in _comparisons():
        sensitivity = row[
            "unit_reexpression_sensitivity"
        ]

        assert isinstance(
            sensitivity,
            dict,
        )

        difference = Decimal(
            sensitivity[
                "absolute_relative_difference"
            ]
        )

        assert (
            difference
            <= UNIT_INVARIANCE_TOLERANCE
        )

        assert (
            sensitivity[
                "passed"
            ]
            is True
        )


def test_secondary_expressions_do_not_create_extra_rows() -> None:
    rows = _comparisons()

    checked = [
        row
        for row in rows
        if row[
            "secondary_expression_consistency"
        ][
            "checked"
        ]
    ]

    assert len(
        rows
    ) == 7

    for row in checked:
        assert (
            row[
                "secondary_expression_consistency"
            ][
                "equivalent"
            ]
            is True
        )


def test_area_conversion_squares_linear_factor() -> None:
    manifest = load_unit_manifest(
        UNIT_MANIFEST
    )

    one = Decimal(
        1
    )

    linear = convert_value(
        one,
        from_unit="megalithic_yard",
        to_unit="current_foot",
        manifest=manifest,
    )

    area = convert_value(
        one,
        from_unit="square_megalithic_yard",
        to_unit="square_current_foot",
        manifest=manifest,
    )

    assert area == (
        linear
        * linear
    )


def test_duplicate_area_rows_are_not_independent_numeric_evidence() -> None:
    rows = _by_id()

    for record_id in DUPLICATE_AREA_RECORDS:
        row = rows[
            record_id
        ]

        assert (
            row[
                "duplicate_numeric_evidence_group"
            ]
            == DUPLICATE_AREA_GROUP
        )

        assert (
            row[
                "independent_numeric_evidence"
            ]
            is False
        )


def test_somm_004_has_no_residual() -> None:
    report = _report()

    assert (
        "SOMM-004"
        in report[
            "excluded_from_residuals"
        ]
    )

    assert (
        "SOMM-004"
        not in {
            row[
                "record_id"
            ]
            for row in _comparisons()
        }
    )

    assert (
        report[
            "interpretation_boundary"
        ][
            "somm_004_used_as_pass_fail_threshold"
        ]
        is False
    )


def test_decagon_rows_have_no_residual() -> None:
    report = _report()

    comparison_ids = {
        row[
            "record_id"
        ]
        for row in _comparisons()
    }

    for record_id in (
        "DECAGON-001",
        "DECAGON-002",
        "DECAGON-003",
        "DECAGON-004",
    ):
        assert (
            record_id
            in report[
                "excluded_from_residuals"
            ]
        )

        assert (
            record_id
            not in comparison_ids
        )

    assert (
        report[
            "interpretation_boundary"
        ][
            "decagon_geometry_extended"
        ]
        is False
    )


def test_no_aggregate_goodness_of_fit_or_ranking_fields() -> None:
    report = _report()

    keys = set(
        _walk_keys(
            report
        )
    )

    assert not (
        keys
        & FORBIDDEN_AGGREGATE_KEYS
    )

    assert (
        report[
            "summary"
        ][
            "aggregate_goodness_of_fit_calculated"
        ]
        is False
    )

    assert (
        report[
            "summary"
        ][
            "ranking_calculated"
        ]
        is False
    )


def test_no_posthoc_tolerance_or_inferred_uncertainty() -> None:
    report = _report()

    assert (
        report[
            "interpretation_boundary"
        ][
            "posthoc_tolerance"
        ]
        is None
    )

    assert (
        report[
            "interpretation_boundary"
        ][
            "inferred_source_uncertainty"
        ]
        is None
    )

    for row in _comparisons():
        assert (
            row[
                "posthoc_tolerance"
            ]
            is None
        )

        assert (
            row[
                "inferred_source_uncertainty"
            ]
            is None
        )


def test_canonical_csv_has_exactly_seven_data_rows() -> None:
    text = canonical_csv_text(
        _report()
    )

    rows = list(
        csv.DictReader(
            StringIO(
                text
            )
        )
    )

    assert len(
        rows
    ) == 7

    assert tuple(
        row[
            "record_id"
        ]
        for row in rows
    ) == EXPECTED_COMPARISON_RECORD_ORDER


def test_markdown_preserves_interpretation_boundary() -> None:
    text = canonical_markdown_text(
        _report()
    )

    assert (
        "No registered wall row is treated as an independent "
        "forward prediction."
        in text
    )

    assert (
        "not used as a Phase 6E pass/fail threshold"
        in text
    )

    assert (
        "No aggregate goodness-of-fit statistic"
        in text
    )


def test_all_serializations_are_deterministic() -> None:
    report = _report()

    assert canonical_json_bytes(
        report
    ) == canonical_json_bytes(
        report
    )

    assert canonical_csv_text(
        report
    ) == canonical_csv_text(
        report
    )

    assert canonical_markdown_text(
        report
    ) == canonical_markdown_text(
        report
    )


def test_tracked_outputs_match_regeneration(
    tmp_path: Path,
) -> None:
    generated_json = (
        tmp_path
        / "historical_residuals.json"
    )

    generated_csv = (
        tmp_path
        / "historical_residuals.csv"
    )

    generated_md = (
        tmp_path
        / "historical_residuals.md"
    )

    outputs = write_historical_residual_outputs(
        registry_path=REGISTRY,
        unit_manifest_path=UNIT_MANIFEST,
        phase6c_path=PHASE6C,
        phase6d_path=PHASE6D,
        protocol_path=PROTOCOL,
        json_path=generated_json,
        csv_path=generated_csv,
        markdown_path=generated_md,
    )

    assert generated_json.read_bytes() == outputs[
        0
    ]

    assert generated_csv.read_bytes() == outputs[
        1
    ]

    assert generated_md.read_bytes() == outputs[
        2
    ]

    if JSON_OUTPUT.exists():
        assert (
            JSON_OUTPUT.read_bytes()
            == outputs[
                0
            ]
        )

    if CSV_OUTPUT.exists():
        assert (
            CSV_OUTPUT.read_bytes()
            == outputs[
                1
            ]
        )

    if MARKDOWN_OUTPUT.exists():
        assert (
            MARKDOWN_OUTPUT.read_bytes()
            == outputs[
                2
            ]
        )


def test_generated_artifacts_have_no_absolute_home_paths() -> None:
    report = _report()

    combined = (
        canonical_json_bytes(
            report
        )
        + canonical_csv_text(
            report
        ).encode(
            "utf-8"
        )
        + canonical_markdown_text(
            report
        ).encode(
            "utf-8"
        )
    )

    assert b"/home/" not in combined
    assert b"/Users/" not in combined


def test_package_version_remains_0_5_0() -> None:
    assert njg.__version__ == "0.5.0"


def test_dimensionless_secondary_is_not_forced_into_physical_conversion() -> None:
    affected = [
        row
        for row in _comparisons()
        if row[
            "source"
        ][
            "secondary_unit"
        ]
        == "dimensionless"
    ]

    assert affected

    for row in affected:
        check = row[
            "secondary_expression_consistency"
        ]

        assert check["present"] is True
        assert check["unit_equivalence_applicable"] is False
        assert check["checked"] is False
        assert check["equivalent"] is None
        assert "different_physical_dimension" in check["reason"]


def test_same_dimension_secondary_expressions_remain_equivalence_checked() -> None:
    applicable = [
        row
        for row in _comparisons()
        if row[
            "secondary_expression_consistency"
        ][
            "unit_equivalence_applicable"
        ]
    ]

    assert applicable

    for row in applicable:
        check = row[
            "secondary_expression_consistency"
        ]

        assert check["checked"] is True
        assert check["equivalent"] is True
