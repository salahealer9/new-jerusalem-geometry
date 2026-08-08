"""Historical residual and sensitivity analysis for v0.6 Phase 6E.

This module compares frozen Phase 6C dimensional predictions with the exact
historical target rows selected by the frozen Phase 6D evidential audit.

It does not import or regenerate geometric models.
"""

from __future__ import annotations

import csv
import hashlib
import json
from decimal import (
    Decimal,
    localcontext,
)
from fractions import Fraction
from pathlib import Path
from typing import (
    Iterable,
    Mapping,
    Sequence,
)


EXPECTED_REGISTRY_SHA256 = (
    "8c534ddc1a6fe6f2b233b4352202d753"
    "8a5379787bc4313a3759916f8b150f5e"
)

EXPECTED_UNIT_MANIFEST_SHA256 = (
    "cdd009dd0ea8e398d51ad3c9d3285741"
    "e207f18b45030a177cbf01d3bf0329c3"
)

EXPECTED_PHASE6C_SHA256 = (
    "d8399adbfd4c679ebb0ad93dc787049c9"
    "8a084cb01b033d42e99a97aecc90d46"
)

EXPECTED_PHASE6D_SHA256 = (
    "dfc6e88ab1c91d96c9b35e204e71d394"
    "61b1a656b4344b6e22a6e95ef1d8e7a1"
)

EXPECTED_PHASE6E_PROTOCOL_SHA256 = (
    "e0ecd914cba79dbab02ac4eefb93691f"
    "fdc17b77b93789d8c8b3b917c6c09d3e"
)

DEFAULT_REGISTRY_RELATIVE_PATH = Path(
    "docs/sources/v0.6_metrology_registry.csv"
)

DEFAULT_UNIT_MANIFEST_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "unit_system.json"
)

DEFAULT_PHASE6C_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "frozen_dimensional_predictions.json"
)

DEFAULT_PHASE6D_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "prediction_status_audit.json"
)

DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH = Path(
    "docs/specification/"
    "v0.6_historical_residual_sensitivity_protocol.md"
)

DEFAULT_JSON_OUTPUT_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "historical_residuals.json"
)

DEFAULT_CSV_OUTPUT_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "historical_residuals.csv"
)

DEFAULT_MARKDOWN_OUTPUT_RELATIVE_PATH = Path(
    "docs/geometry/"
    "v0.6_historical_residual_sensitivity_report.md"
)

COMPARISON_POLICIES = frozenset(
    {
        "retrospective_residual",
        "descriptive_residual",
    }
)

EXPECTED_COMPARISON_RECORD_ORDER = (
    "WALL12-001",
    "WALL12-002",
    "WALL12-003",
    "SOMM-001",
    "SOMM-002",
    "SOMM-003",
    "SOMM-005",
)

DUPLICATE_AREA_RECORDS = frozenset(
    {
        "WALL12-003",
        "SOMM-003",
    }
)

DUPLICATE_AREA_GROUP = (
    "wall_area_120m"
)

UNIT_INVARIANCE_TOLERANCE = Decimal(
    "1e-12"
)

DECIMAL_PRECISION = 50

CSV_FIELDNAMES = (
    "record_id",
    "frozen_prediction_status",
    "comparison_policy",
    "independent_forward_prediction",
    "source_value",
    "source_unit",
    "secondary_value",
    "secondary_unit",
    "phase6c_prediction_quantity",
    "prediction_original_value",
    "prediction_original_unit",
    "prediction_value_in_source_unit",
    "signed_residual",
    "absolute_residual",
    "relative_residual",
    "percent_residual",
    "absolute_percent_residual",
    "unit_invariance_relative_residual",
    "unit_invariance_absolute_difference",
    "unit_invariance_pass",
    "secondary_expression_checked",
    "secondary_expression_equivalent",
    "duplicate_numeric_evidence_group",
    "independent_numeric_evidence",
    "inferred_source_uncertainty",
    "posthoc_tolerance",
)

FORBIDDEN_AGGREGATE_KEYS = frozenset(
    {
        "mean_percent_residual",
        "rms_percent_residual",
        "chi_square",
        "combined_p_value",
        "likelihood",
        "bayes_factor",
        "success_count",
        "pass_fraction",
        "overall_score",
        "ranking",
    }
)


def sha256_file(
    path: Path,
) -> str:
    """Return a SHA-256 hash."""
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _verify_hash(
    path: Path,
    expected: str,
    label: str,
) -> str:
    actual = sha256_file(
        path
    )

    if actual != expected:
        raise ValueError(
            f"{label} hash does not match frozen input: "
            f"{actual} != {expected}"
        )

    return actual


def _load_json_decimal(
    path: Path,
) -> dict[str, object]:
    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        ),
        parse_float=Decimal,
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            f"Expected JSON object in {path}."
        )

    return payload


def _decimal_text(
    value: Decimal,
) -> str:
    """Return deterministic non-exponent decimal text."""
    if value.is_zero():
        return "0"

    text = format(
        value,
        "f",
    )

    if "." in text:
        text = text.rstrip(
            "0"
        ).rstrip(
            "."
        )

    if text == "-0":
        return "0"

    return text


def _display_decimal(
    value: Decimal,
    significant_places: int = 12,
) -> str:
    """Compact human-readable decimal, without changing canonical values."""
    if value.is_zero():
        return "0"

    return format(
        value,
        f".{significant_places}g",
    )


def _fraction_from_payload(
    payload: Mapping[str, object],
) -> Fraction:
    numerator = payload.get(
        "numerator"
    )

    denominator = payload.get(
        "denominator"
    )

    if not isinstance(
        numerator,
        int,
    ):
        raise ValueError(
            "Exact factor lacks integer numerator."
        )

    if not isinstance(
        denominator,
        int,
    ):
        raise ValueError(
            "Exact factor lacks integer denominator."
        )

    if denominator == 0:
        raise ValueError(
            "Exact factor denominator cannot be zero."
        )

    return Fraction(
        numerator,
        denominator,
    )


def _decimal_from_fraction(
    value: Fraction,
) -> Decimal:
    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        return (
            Decimal(
                value.numerator
            )
            / Decimal(
                value.denominator
            )
        )


def load_registry_rows(
    path: Path,
) -> tuple[dict[str, str], ...]:
    """Load and verify the frozen Phase 6A registry."""
    _verify_hash(
        path,
        EXPECTED_REGISTRY_SHA256,
        "Phase 6A registry",
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

    if len(
        rows
    ) != 24:
        raise ValueError(
            "Frozen Phase 6A registry must contain 24 records."
        )

    return rows


def load_unit_manifest(
    path: Path,
) -> dict[str, object]:
    """Load and verify the frozen Phase 6B unit manifest."""
    _verify_hash(
        path,
        EXPECTED_UNIT_MANIFEST_SHA256,
        "Phase 6B unit manifest",
    )

    payload = _load_json_decimal(
        path
    )

    if payload.get(
        "phase"
    ) != "6B":
        raise ValueError(
            "Unexpected Phase 6B manifest phase."
        )

    return payload


def load_phase6c_predictions(
    path: Path,
) -> dict[str, object]:
    """Load and verify the frozen Phase 6C prediction artifact."""
    _verify_hash(
        path,
        EXPECTED_PHASE6C_SHA256,
        "Phase 6C prediction artifact",
    )

    payload = _load_json_decimal(
        path
    )

    if payload.get(
        "phase"
    ) != "6C":
        raise ValueError(
            "Unexpected Phase 6C artifact phase."
        )

    return payload


def load_phase6d_audit(
    path: Path,
) -> dict[str, object]:
    """Load and verify the frozen Phase 6D audit."""
    _verify_hash(
        path,
        EXPECTED_PHASE6D_SHA256,
        "Phase 6D audit",
    )

    payload = _load_json_decimal(
        path
    )

    if payload.get(
        "phase"
    ) != "6D":
        raise ValueError(
            "Unexpected Phase 6D artifact phase."
        )

    return payload


def verify_phase6e_protocol(
    path: Path,
) -> str:
    """Verify the frozen Phase 6E.1 protocol."""
    return _verify_hash(
        path,
        EXPECTED_PHASE6E_PROTOCOL_SHA256,
        "Phase 6E protocol",
    )


def _linear_unit_factors(
    manifest: Mapping[str, object],
) -> dict[str, Fraction]:
    rows = manifest.get(
        "linear_units"
    )

    if not isinstance(
        rows,
        list,
    ):
        raise ValueError(
            "Phase 6B manifest lacks linear_units."
        )

    factors: dict[str, Fraction] = {
        "current_foot": Fraction(
            1,
            1,
        ),
    }

    for row in rows:
        if not isinstance(
            row,
            dict,
        ):
            raise ValueError(
                "Invalid linear-unit record."
            )

        unit = row.get(
            "unit"
        )

        factor_payload = row.get(
            "to_current_foot"
        )

        if not isinstance(
            unit,
            str,
        ):
            raise ValueError(
                "Linear-unit record lacks unit name."
            )

        if not isinstance(
            factor_payload,
            dict,
        ):
            raise ValueError(
                f"Linear unit {unit!r} lacks exact factor."
            )

        factors[
            unit
        ] = _fraction_from_payload(
            factor_payload
        )

    return factors


def _normalize_unit_token(
    unit: str,
) -> str:
    token = (
        unit
        .strip()
        .lower()
        .replace(
            "-",
            "_",
        )
        .replace(
            " ",
            "_",
        )
    )

    aliases = {
        "foot": "current_foot",
        "feet": "current_foot",
        "current_feet": "current_foot",
        "ft": "current_foot",
        "my": "megalithic_yard",
        "megalithic_yards": "megalithic_yard",
        "old_english_feet": "old_english_foot",
        "square_foot": "square_current_foot",
        "square_feet": "square_current_foot",
        "square_current_feet": "square_current_foot",
        "sq_ft": "square_current_foot",
    }

    return aliases.get(
        token,
        token,
    )


def _unit_dimension_and_factor(
    unit: str,
    manifest: Mapping[str, object],
) -> tuple[str, Fraction]:
    """Return dimension and exact factor to current-foot base."""
    normalized = _normalize_unit_token(
        unit
    )

    linear = _linear_unit_factors(
        manifest
    )

    if normalized == "dimensionless":
        return (
            "dimensionless",
            Fraction(
                1,
                1,
            ),
        )

    if normalized in linear:
        return (
            "linear",
            linear[
                normalized
            ],
        )

    if normalized == "square_current_foot":
        return (
            "area",
            Fraction(
                1,
                1,
            ),
        )

    if normalized.startswith(
        "square_"
    ):
        linear_name = normalized[
            len(
                "square_"
            ):
        ]

        if linear_name in linear:
            factor = linear[
                linear_name
            ]

            return (
                "area",
                factor
                * factor,
            )

    raise ValueError(
        f"Unsupported frozen unit token: {unit!r}"
    )


def convert_value(
    value: Decimal,
    *,
    from_unit: str,
    to_unit: str,
    manifest: Mapping[str, object],
) -> Decimal:
    """Convert with exact Phase 6B factors."""
    from_dimension, from_factor = (
        _unit_dimension_and_factor(
            from_unit,
            manifest,
        )
    )

    to_dimension, to_factor = (
        _unit_dimension_and_factor(
            to_unit,
            manifest,
        )
    )

    if from_dimension != to_dimension:
        raise ValueError(
            "Cannot convert between incompatible dimensions: "
            f"{from_unit!r} -> {to_unit!r}"
        )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        current_base = (
            value
            * _decimal_from_fraction(
                from_factor
            )
        )

        return (
            current_base
            / _decimal_from_fraction(
                to_factor
            )
        )


def _current_base_unit(
    unit: str,
    manifest: Mapping[str, object],
) -> str:
    dimension, _ = (
        _unit_dimension_and_factor(
            unit,
            manifest,
        )
    )

    if dimension == "linear":
        return "current_foot"

    if dimension == "area":
        return "square_current_foot"

    raise AssertionError(
        dimension
    )


def _source_by_id(
    rows: Sequence[Mapping[str, str]],
) -> dict[str, Mapping[str, str]]:
    result: dict[
        str,
        Mapping[str, str],
    ] = {}

    for row in rows:
        record_id = row[
            "record_id"
        ]

        if record_id in result:
            raise ValueError(
                f"Duplicate registry record: {record_id}"
            )

        result[
            record_id
        ] = row

    return result


def _comparison_audit_rows(
    audit: Mapping[str, object],
) -> tuple[Mapping[str, object], ...]:
    rows = audit.get(
        "records"
    )

    if not isinstance(
        rows,
        list,
    ):
        raise ValueError(
            "Phase 6D audit lacks records."
        )

    selected = tuple(
        row
        for row in rows
        if isinstance(
            row,
            dict,
        )
        and row.get(
            "comparison_policy"
        )
        in COMPARISON_POLICIES
    )

    actual_order = tuple(
        str(
            row[
                "record_id"
            ]
        )
        for row in selected
    )

    if (
        actual_order
        != EXPECTED_COMPARISON_RECORD_ORDER
    ):
        raise ValueError(
            "Phase 6D comparison order differs from "
            "the frozen Phase 6E protocol."
        )

    return selected


def _prediction_row(
    phase6c: Mapping[str, object],
    quantity_name: str,
) -> Mapping[str, object]:
    predictions = phase6c.get(
        "dimensional_predictions"
    )

    if not isinstance(
        predictions,
        dict,
    ):
        raise ValueError(
            "Phase 6C artifact lacks dimensional_predictions."
        )

    row = predictions.get(
        quantity_name
    )

    if not isinstance(
        row,
        dict,
    ):
        raise ValueError(
            f"Missing frozen Phase 6C quantity: {quantity_name}"
        )

    value = row.get(
        "value"
    )

    unit = row.get(
        "unit"
    )

    if not isinstance(
        value,
        Decimal,
    ):
        raise ValueError(
            f"Frozen prediction {quantity_name} is not numeric."
        )

    if not isinstance(
        unit,
        str,
    ):
        raise ValueError(
            f"Frozen prediction {quantity_name} lacks unit."
        )

    return row


def _calculate_residual_metrics(
    prediction: Decimal,
    source: Decimal,
) -> dict[str, Decimal]:
    if source.is_zero():
        raise ValueError(
            "Historical source target cannot be zero."
        )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        signed = (
            prediction
            - source
        )

        absolute = abs(
            signed
        )

        relative = (
            signed
            / source
        )

        percent = (
            Decimal(
                100
            )
            * relative
        )

        absolute_percent = abs(
            percent
        )

    return {
        "signed_residual": signed,
        "absolute_residual": absolute,
        "relative_residual": relative,
        "percent_residual": percent,
        "absolute_percent_residual": absolute_percent,
    }


def _secondary_expression_check(
    source_row: Mapping[str, str],
    *,
    manifest: Mapping[str, object],
) -> dict[str, object]:
    """Check secondary unit-equivalence only when dimensions match."""
    secondary_value_text = (
        source_row.get(
            "secondary_value",
            "",
        )
        or ""
    ).strip()

    secondary_unit = (
        source_row.get(
            "secondary_unit",
            "",
        )
        or ""
    ).strip()

    if (
        not secondary_value_text
        and not secondary_unit
    ):
        return {
            "present": False,
            "unit_equivalence_applicable": False,
            "checked": False,
            "equivalent": None,
            "reason": "no_secondary_expression",
            "primary_current_base_value": None,
            "secondary_current_base_value": None,
            "absolute_current_base_difference": None,
        }

    if (
        not secondary_value_text
        or not secondary_unit
    ):
        raise ValueError(
            "Secondary historical expression is incomplete."
        )

    primary = Decimal(
        source_row[
            "source_value"
        ]
    )
    primary_unit = source_row[
        "source_unit"
    ]
    secondary = Decimal(
        secondary_value_text
    )

    primary_dimension, _ = (
        _unit_dimension_and_factor(
            primary_unit,
            manifest,
        )
    )
    secondary_dimension, _ = (
        _unit_dimension_and_factor(
            secondary_unit,
            manifest,
        )
    )

    if (
        primary_dimension
        != secondary_dimension
    ):
        return {
            "present": True,
            "unit_equivalence_applicable": False,
            "checked": False,
            "equivalent": None,
            "reason": (
                "different_physical_dimension:"
                f"{primary_dimension}:"
                f"{secondary_dimension}"
            ),
            "primary_current_base_value": None,
            "secondary_current_base_value": None,
            "absolute_current_base_difference": None,
        }

    base_unit = _current_base_unit(
        primary_unit,
        manifest,
    )

    primary_base = convert_value(
        primary,
        from_unit=primary_unit,
        to_unit=base_unit,
        manifest=manifest,
    )

    secondary_base = convert_value(
        secondary,
        from_unit=secondary_unit,
        to_unit=base_unit,
        manifest=manifest,
    )

    difference = (
        secondary_base
        - primary_base
    )

    return {
        "present": True,
        "unit_equivalence_applicable": True,
        "checked": True,
        "equivalent": difference.is_zero(),
        "reason": "same_dimension_unit_equivalence",
        "primary_current_base_value": _decimal_text(
            primary_base
        ),
        "secondary_current_base_value": _decimal_text(
            secondary_base
        ),
        "absolute_current_base_difference": _decimal_text(
            abs(difference)
        ),
    }


def _unit_invariance_check(
    *,
    prediction_original_value: Decimal,
    prediction_original_unit: str,
    source_value: Decimal,
    source_unit: str,
    canonical_relative_residual: Decimal,
    manifest: Mapping[str, object],
) -> dict[str, object]:
    base_unit = _current_base_unit(
        source_unit,
        manifest,
    )

    prediction_base = convert_value(
        prediction_original_value,
        from_unit=prediction_original_unit,
        to_unit=base_unit,
        manifest=manifest,
    )

    source_base = convert_value(
        source_value,
        from_unit=source_unit,
        to_unit=base_unit,
        manifest=manifest,
    )

    metrics = _calculate_residual_metrics(
        prediction_base,
        source_base,
    )

    reexpressed_relative = metrics[
        "relative_residual"
    ]

    difference = abs(
        reexpressed_relative
        - canonical_relative_residual
    )

    return {
        "base_unit": base_unit,
        "prediction_value": _decimal_text(
            prediction_base
        ),
        "source_value": _decimal_text(
            source_base
        ),
        "relative_residual": _decimal_text(
            reexpressed_relative
        ),
        "absolute_relative_difference": _decimal_text(
            difference
        ),
        "tolerance": _decimal_text(
            UNIT_INVARIANCE_TOLERANCE
        ),
        "passed": (
            difference
            <= UNIT_INVARIANCE_TOLERANCE
        ),
    }


def _build_comparison_row(
    *,
    audit_row: Mapping[str, object],
    source_row: Mapping[str, str],
    phase6c: Mapping[str, object],
    manifest: Mapping[str, object],
) -> dict[str, object]:
    record_id = str(
        audit_row[
            "record_id"
        ]
    )

    quantity_name = audit_row.get(
        "phase6c_prediction_quantity"
    )

    if not isinstance(
        quantity_name,
        str,
    ):
        raise ValueError(
            f"{record_id} lacks Phase 6C quantity mapping."
        )

    prediction = _prediction_row(
        phase6c,
        quantity_name,
    )

    prediction_value = prediction[
        "value"
    ]

    prediction_unit = prediction[
        "unit"
    ]

    assert isinstance(
        prediction_value,
        Decimal,
    )

    assert isinstance(
        prediction_unit,
        str,
    )

    source_value_text = source_row.get(
        "source_value",
        "",
    ).strip()

    source_unit = source_row.get(
        "source_unit",
        "",
    ).strip()

    if (
        not source_value_text
        or not source_unit
    ):
        raise ValueError(
            f"{record_id} lacks canonical source value/unit."
        )

    source_value = Decimal(
        source_value_text
    )

    if source_value.is_zero():
        raise ValueError(
            f"{record_id} source target is zero."
        )

    prediction_in_source_unit = convert_value(
        prediction_value,
        from_unit=prediction_unit,
        to_unit=source_unit,
        manifest=manifest,
    )

    residuals = _calculate_residual_metrics(
        prediction_in_source_unit,
        source_value,
    )

    invariance = _unit_invariance_check(
        prediction_original_value=prediction_value,
        prediction_original_unit=prediction_unit,
        source_value=source_value,
        source_unit=source_unit,
        canonical_relative_residual=(
            residuals[
                "relative_residual"
            ]
        ),
        manifest=manifest,
    )

    if not invariance[
        "passed"
    ]:
        raise ValueError(
            f"{record_id} failed unit-reexpression invariance."
        )

    secondary = _secondary_expression_check(
        source_row,
        manifest=manifest,
    )

    duplicate_group = (
        DUPLICATE_AREA_GROUP
        if record_id
        in DUPLICATE_AREA_RECORDS
        else None
    )

    return {
        "record_id": record_id,
        "frozen_prediction_status": audit_row[
            "frozen_prediction_status"
        ],
        "comparison_policy": audit_row[
            "comparison_policy"
        ],
        "independent_forward_prediction": False,
        "source": {
            "value": source_value_text,
            "unit": source_unit,
            "secondary_value": (
                source_row.get(
                    "secondary_value",
                    "",
                )
                or None
            ),
            "secondary_unit": (
                source_row.get(
                    "secondary_unit",
                    "",
                )
                or None
            ),
        },
        "phase6c_prediction_quantity": quantity_name,
        "prediction_original": {
            "value": _decimal_text(
                prediction_value
            ),
            "unit": prediction_unit,
        },
        "prediction_in_source_unit": {
            "value": _decimal_text(
                prediction_in_source_unit
            ),
            "unit": source_unit,
        },
        "signed_residual": _decimal_text(
            residuals[
                "signed_residual"
            ]
        ),
        "absolute_residual": _decimal_text(
            residuals[
                "absolute_residual"
            ]
        ),
        "relative_residual": _decimal_text(
            residuals[
                "relative_residual"
            ]
        ),
        "percent_residual": _decimal_text(
            residuals[
                "percent_residual"
            ]
        ),
        "absolute_percent_residual": _decimal_text(
            residuals[
                "absolute_percent_residual"
            ]
        ),
        "unit_reexpression_sensitivity": invariance,
        "secondary_expression_consistency": secondary,
        "duplicate_numeric_evidence_group": duplicate_group,
        "independent_numeric_evidence": False,
        "inferred_source_uncertainty": None,
        "posthoc_tolerance": None,
    }


def build_historical_residual_report(
    *,
    registry_path: Path,
    unit_manifest_path: Path,
    phase6c_path: Path,
    phase6d_path: Path,
    protocol_path: Path,
) -> dict[str, object]:
    """Build the canonical seven-row Phase 6E report."""
    registry_rows = load_registry_rows(
        registry_path
    )

    manifest = load_unit_manifest(
        unit_manifest_path
    )

    phase6c = load_phase6c_predictions(
        phase6c_path
    )

    phase6d = load_phase6d_audit(
        phase6d_path
    )

    protocol_hash = verify_phase6e_protocol(
        protocol_path
    )

    registry = _source_by_id(
        registry_rows
    )

    audit_rows = _comparison_audit_rows(
        phase6d
    )

    comparisons = tuple(
        _build_comparison_row(
            audit_row=audit_row,
            source_row=registry[
                str(
                    audit_row[
                        "record_id"
                    ]
                )
            ],
            phase6c=phase6c,
            manifest=manifest,
        )
        for audit_row in audit_rows
    )

    if len(
        comparisons
    ) != 7:
        raise ValueError(
            "Phase 6E must emit exactly seven comparisons."
        )

    retrospective_count = sum(
        row[
            "comparison_policy"
        ]
        == "retrospective_residual"
        for row in comparisons
    )

    descriptive_count = sum(
        row[
            "comparison_policy"
        ]
        == "descriptive_residual"
        for row in comparisons
    )

    if retrospective_count != 6:
        raise ValueError(
            "Expected exactly six retrospective residuals."
        )

    if descriptive_count != 1:
        raise ValueError(
            "Expected exactly one descriptive residual."
        )

    secondary_present = sum(
        bool(
            row[
                "secondary_expression_consistency"
            ][
                "present"
            ]
        )
        for row in comparisons
    )

    secondary_checks = sum(
        bool(
            row[
                "secondary_expression_consistency"
            ][
                "unit_equivalence_applicable"
            ]
        )
        for row in comparisons
    )

    secondary_not_applicable = (
        secondary_present
        - secondary_checks
    )

    secondary_failures = sum(
        bool(
            row[
                "secondary_expression_consistency"
            ][
                "unit_equivalence_applicable"
            ]
        )
        and (
            row[
                "secondary_expression_consistency"
            ][
                "equivalent"
            ]
            is False
        )
        for row in comparisons
    )

    if secondary_failures:
        raise ValueError(
            "Registered equivalent historical expressions "
            "are inconsistent under Phase 6B units."
        )

    excluded_no_residual = tuple(
        str(
            row[
                "record_id"
            ]
        )
        for row in phase6d[
            "records"
        ]
        if row[
            "comparison_policy"
        ]
        in {
            "no_residual",
            "context_only",
            "not_evaluable",
        }
    )

    return {
        "schema_version": 1,
        "phase": "6E",
        "analysis_id": (
            "njg-michell-v0-6-historical-residual-sensitivity-v1"
        ),
        "frozen_inputs": {
            "registry": {
                "path": str(
                    DEFAULT_REGISTRY_RELATIVE_PATH
                ),
                "sha256": EXPECTED_REGISTRY_SHA256,
            },
            "unit_manifest": {
                "path": str(
                    DEFAULT_UNIT_MANIFEST_RELATIVE_PATH
                ),
                "sha256": EXPECTED_UNIT_MANIFEST_SHA256,
            },
            "phase6c_predictions": {
                "path": str(
                    DEFAULT_PHASE6C_RELATIVE_PATH
                ),
                "sha256": EXPECTED_PHASE6C_SHA256,
            },
            "phase6d_audit": {
                "path": str(
                    DEFAULT_PHASE6D_RELATIVE_PATH
                ),
                "sha256": EXPECTED_PHASE6D_SHA256,
            },
            "phase6e_protocol": {
                "path": str(
                    DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH
                ),
                "sha256": protocol_hash,
            },
        },
        "residual_definition": {
            "signed_residual": "prediction - source",
            "relative_residual": "(prediction - source) / source",
            "percent_residual": (
                "100 * (prediction - source) / source"
            ),
        },
        "summary": {
            "comparison_count": len(
                comparisons
            ),
            "retrospective_residual_count": retrospective_count,
            "descriptive_residual_count": descriptive_count,
            "independent_forward_prediction_count": 0,
            "secondary_expression_present_count": secondary_present,
            "secondary_expression_check_count": secondary_checks,
            "secondary_expression_not_applicable_count": (
                secondary_not_applicable
            ),
            "secondary_expression_failure_count": secondary_failures,
            "aggregate_goodness_of_fit_calculated": False,
            "ranking_calculated": False,
            "posthoc_threshold_applied": False,
        },
        "interpretation_boundary": {
            "registered_wall_comparisons_are_independent_predictions": False,
            "development_used_targets_are_retrospective": True,
            "somm_004_used_as_pass_fail_threshold": False,
            "decagon_geometry_extended": False,
            "inferred_source_uncertainty": None,
            "posthoc_tolerance": None,
        },
        "excluded_from_residuals": list(
            excluded_no_residual
        ),
        "duplicate_numeric_evidence_groups": {
            DUPLICATE_AREA_GROUP: sorted(
                DUPLICATE_AREA_RECORDS
            ),
        },
        "comparisons": list(
            comparisons
        ),
    }


def canonical_json_bytes(
    payload: Mapping[str, object],
) -> bytes:
    """Serialize canonical JSON."""
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


def _csv_row(
    row: Mapping[str, object],
) -> dict[str, object]:
    source = row[
        "source"
    ]

    prediction_original = row[
        "prediction_original"
    ]

    prediction_source = row[
        "prediction_in_source_unit"
    ]

    invariance = row[
        "unit_reexpression_sensitivity"
    ]

    secondary = row[
        "secondary_expression_consistency"
    ]

    assert isinstance(
        source,
        dict,
    )

    assert isinstance(
        prediction_original,
        dict,
    )

    assert isinstance(
        prediction_source,
        dict,
    )

    assert isinstance(
        invariance,
        dict,
    )

    assert isinstance(
        secondary,
        dict,
    )

    return {
        "record_id": row[
            "record_id"
        ],
        "frozen_prediction_status": row[
            "frozen_prediction_status"
        ],
        "comparison_policy": row[
            "comparison_policy"
        ],
        "independent_forward_prediction": (
            "false"
        ),
        "source_value": source[
            "value"
        ],
        "source_unit": source[
            "unit"
        ],
        "secondary_value": (
            source[
                "secondary_value"
            ]
            or ""
        ),
        "secondary_unit": (
            source[
                "secondary_unit"
            ]
            or ""
        ),
        "phase6c_prediction_quantity": row[
            "phase6c_prediction_quantity"
        ],
        "prediction_original_value": prediction_original[
            "value"
        ],
        "prediction_original_unit": prediction_original[
            "unit"
        ],
        "prediction_value_in_source_unit": prediction_source[
            "value"
        ],
        "signed_residual": row[
            "signed_residual"
        ],
        "absolute_residual": row[
            "absolute_residual"
        ],
        "relative_residual": row[
            "relative_residual"
        ],
        "percent_residual": row[
            "percent_residual"
        ],
        "absolute_percent_residual": row[
            "absolute_percent_residual"
        ],
        "unit_invariance_relative_residual": invariance[
            "relative_residual"
        ],
        "unit_invariance_absolute_difference": invariance[
            "absolute_relative_difference"
        ],
        "unit_invariance_pass": (
            "true"
            if invariance[
                "passed"
            ]
            else "false"
        ),
        "secondary_expression_checked": (
            "true"
            if secondary[
                "checked"
            ]
            else "false"
        ),
        "secondary_expression_equivalent": (
            ""
            if secondary[
                "equivalent"
            ]
            is None
            else (
                "true"
                if secondary[
                    "equivalent"
                ]
                else "false"
            )
        ),
        "duplicate_numeric_evidence_group": (
            row[
                "duplicate_numeric_evidence_group"
            ]
            or ""
        ),
        "independent_numeric_evidence": "false",
        "inferred_source_uncertainty": "",
        "posthoc_tolerance": "",
    }


def canonical_csv_text(
    payload: Mapping[str, object],
) -> str:
    """Serialize the seven canonical rows to deterministic CSV."""
    from io import StringIO

    comparisons = payload.get(
        "comparisons"
    )

    if not isinstance(
        comparisons,
        list,
    ):
        raise ValueError(
            "Phase 6E payload lacks comparisons."
        )

    stream = StringIO(
        newline=""
    )

    writer = csv.DictWriter(
        stream,
        fieldnames=CSV_FIELDNAMES,
        lineterminator="\n",
    )

    writer.writeheader()

    for row in comparisons:
        if not isinstance(
            row,
            dict,
        ):
            raise ValueError(
                "Invalid comparison row."
            )

        writer.writerow(
            _csv_row(
                row
            )
        )

    return stream.getvalue()


def canonical_markdown_text(
    payload: Mapping[str, object],
) -> str:
    """Render the human-readable Phase 6E report."""
    comparisons = payload.get(
        "comparisons"
    )

    if not isinstance(
        comparisons,
        list,
    ):
        raise ValueError(
            "Phase 6E payload lacks comparisons."
        )

    lines = [
        "# v0.6 historical residual and sensitivity report",
        "",
        "## Status",
        "",
        "Frozen-artifact historical comparison under the preregistered "
        "Phase 6E protocol.",
        "",
        "No geometry, unit parameter, historical target, comparison mapping, "
        "or tolerance was fitted in this phase.",
        "",
        "Residual sign convention:",
        "",
        "```text",
        "signed residual = frozen prediction - historical source value",
        "```",
        "",
        "## Historical residuals",
        "",
        "| Record | Policy | Historical target | Frozen value | Signed residual | Percent residual |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]

    for row in comparisons:
        if not isinstance(
            row,
            dict,
        ):
            raise ValueError(
                "Invalid comparison row."
            )

        source = row[
            "source"
        ]

        prediction = row[
            "prediction_in_source_unit"
        ]

        assert isinstance(
            source,
            dict,
        )

        assert isinstance(
            prediction,
            dict,
        )

        percent = Decimal(
            str(
                row[
                    "percent_residual"
                ]
            )
        )

        signed = Decimal(
            str(
                row[
                    "signed_residual"
                ]
            )
        )

        prediction_value = Decimal(
            str(
                prediction[
                    "value"
                ]
            )
        )

        lines.append(
            "| "
            + str(
                row[
                    "record_id"
                ]
            )
            + " | `"
            + str(
                row[
                    "comparison_policy"
                ]
            )
            + "` | "
            + str(
                source[
                    "value"
                ]
            )
            + " "
            + str(
                source[
                    "unit"
                ]
            )
            + " | "
            + _display_decimal(
                prediction_value
            )
            + " "
            + str(
                source[
                    "unit"
                ]
            )
            + " | "
            + _display_decimal(
                signed
            )
            + " | "
            + _display_decimal(
                percent
            )
            + "% |"
        )

    lines.extend(
        [
            "",
            "The six `development_used_target` rows are retrospective "
            "comparisons. `WALL12-002` is descriptive only.",
            "",
            "No registered wall row is treated as an independent forward "
            "prediction.",
            "",
            "## Sensitivity checks",
            "",
            "### Unit re-expression",
            "",
        ]
    )

    for row in comparisons:
        assert isinstance(
            row,
            dict,
        )

        sensitivity = row[
            "unit_reexpression_sensitivity"
        ]

        assert isinstance(
            sensitivity,
            dict,
        )

        lines.append(
            "- `"
            + str(
                row[
                    "record_id"
                ]
            )
            + "`: relative-residual invariance "
            + (
                "PASS"
                if sensitivity[
                    "passed"
                ]
                else "FAIL"
            )
            + " (absolute difference "
            + str(
                sensitivity[
                    "absolute_relative_difference"
                ]
            )
            + ")."
        )

    lines.extend(
        [
            "",
            "### Equivalent historical expressions",
            "",
        ]
    )

    checked_rows = [
        row
        for row in comparisons
        if isinstance(
            row,
            dict,
        )
        and isinstance(
            row.get(
                "secondary_expression_consistency"
            ),
            dict,
        )
        and row[
            "secondary_expression_consistency"
        ][
            "checked"
        ]
    ]

    if checked_rows:
        for row in checked_rows:
            check = row[
                "secondary_expression_consistency"
            ]

            assert isinstance(
                check,
                dict,
            )

            lines.append(
                "- `"
                + str(
                    row[
                        "record_id"
                    ]
                )
                + "`: "
                + (
                    "equivalent under the frozen Phase 6B unit system."
                    if check[
                        "equivalent"
                    ]
                    else "NOT equivalent under the frozen Phase 6B unit system."
                )
            )
    else:
        lines.append(
            "- No comparison row contains a registered secondary expression."
        )

    lines.extend(
        [
            "",
            "### Duplicate numerical evidence",
            "",
            "`WALL12-003` and `SOMM-003` are retained as distinct historical "
            "registry rows but share the duplicate numerical-evidence group "
            "`wall_area_120m`. They are not two independent numerical "
            "confirmations.",
            "",
            "### Approximation and tolerance boundary",
            "",
            "No numerical source uncertainty was inferred from qualitative "
            "words such as *close*, *approximately*, or *virtually*.",
            "",
            "`SOMM-004` remains historical context only. Its reported working "
            "tolerance is not used as a Phase 6E pass/fail threshold.",
            "",
            "The four decagon records remain unevaluable from the frozen v0.5 "
            "geometry.",
            "",
            "## Interpretation",
            "",
            "This report quantifies retrospective or descriptive agreement "
            "between a frozen reconstruction and registered historical "
            "quantities. It does not convert development-used targets into "
            "forward-prediction evidence.",
            "",
            "No aggregate goodness-of-fit statistic, ranking, success count, "
            "or post-hoc threshold is calculated.",
            "",
        ]
    )

    return "\n".join(
        lines
    )


def write_historical_residual_outputs(
    *,
    registry_path: Path,
    unit_manifest_path: Path,
    phase6c_path: Path,
    phase6d_path: Path,
    protocol_path: Path,
    json_path: Path,
    csv_path: Path,
    markdown_path: Path,
) -> tuple[bytes, bytes, bytes]:
    """Generate all three deterministic Phase 6E outputs."""
    payload = build_historical_residual_report(
        registry_path=registry_path,
        unit_manifest_path=unit_manifest_path,
        phase6c_path=phase6c_path,
        phase6d_path=phase6d_path,
        protocol_path=protocol_path,
    )

    json_bytes = canonical_json_bytes(
        payload
    )

    csv_bytes = canonical_csv_text(
        payload
    ).encode(
        "utf-8"
    )

    markdown_bytes = canonical_markdown_text(
        payload
    ).encode(
        "utf-8"
    )

    for path in (
        json_path,
        csv_path,
        markdown_path,
    ):
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    json_path.write_bytes(
        json_bytes
    )

    csv_path.write_bytes(
        csv_bytes
    )

    markdown_path.write_bytes(
        markdown_bytes
    )

    return (
        json_bytes,
        csv_bytes,
        markdown_bytes,
    )
