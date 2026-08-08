"""Frozen-artifact dodecagon dimensional audit for v0.7 Phase 7D.

This module combines:
- the frozen Phase 7B radius-class artifact;
- the frozen v0.6 source-defined scale;
- the frozen v0.6 historical registry;
- the frozen Phase 7A source clarification.

It does not import or rebuild geometric models.
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
from html import escape
from io import StringIO
from pathlib import Path
from typing import (
    Any,
    Mapping,
    Sequence,
)


SCHEMA_VERSION = "1.0"
PHASE = "7D"

STOPPING_STATUS = (
    "DIMENSIONAL_COMPARISON_CALCULATED_NO_REFIT"
)

DECIMAL_PRECISION = 60

PROTOCOL_PATH = (
    "docs/specification/"
    "v0.7_dodecagon_dimensional_audit_protocol.md"
)
PROTOCOL_SHA256 = (
    "1acd1d2a895f64463ce58ba69a19c53e"
    "39c0b373b1d378183d10f548aa1351d9"
)

PHASE7B_PATH = (
    "data/analysis/njg_michell_v0_7/"
    "dodecagon_vertex_radius_audit.json"
)
PHASE7B_SHA256 = (
    "7093250082940c16b1d1df240e791ba5"
    "d5e31b7aa10a1866d58ec8e00d3c96b5"
)

PHASE6C_PATH = (
    "data/metrology/njg_michell_v0_6/"
    "frozen_dimensional_predictions.json"
)
PHASE6C_SHA256 = (
    "d8399adbfd4c679ebb0ad93dc787049c9"
    "8a084cb01b033d42e99a97aecc90d46"
)

UNIT_SYSTEM_PATH = (
    "data/metrology/njg_michell_v0_6/"
    "unit_system.json"
)
UNIT_SYSTEM_SHA256 = (
    "cdd009dd0ea8e398d51ad3c9d3285741"
    "e207f18b45030a177cbf01d3bf0329c3"
)

REGISTRY_PATH = (
    "docs/sources/v0.6_metrology_registry.csv"
)
REGISTRY_SHA256 = (
    "8c534ddc1a6fe6f2b233b4352202d753"
    "8a5379787bc4313a3759916f8b150f5e"
)

PHASE7A_CLARIFICATION_PATH = (
    "docs/sources/"
    "v0.7_sommerville_dodecagon_source_clarification.md"
)
PHASE7A_CLARIFICATION_SHA256 = (
    "da8f237ae413c85b755a6e148a62fd9d"
    "402c63ffd833d50e110d1c1c5520bae2"
)

JSON_OUTPUT_PATH = (
    "data/analysis/njg_michell_v0_7/"
    "dodecagon_dimensional_audit.json"
)
CSV_OUTPUT_PATH = (
    "data/analysis/njg_michell_v0_7/"
    "dodecagon_dimensional_audit.csv"
)
MARKDOWN_OUTPUT_PATH = (
    "docs/geometry/"
    "v0.7_dodecagon_dimensional_audit_report.md"
)
SVG_OUTPUT_PATH = (
    "figures/generated/"
    "sommerville_dodecagon_dimensional_audit.svg"
)

COMPARISON_ORDER = (
    "D7-001",
    "D7-002",
    "D7-003",
    "D7-004",
)

SOURCE_RECORD_ORDER = (
    "DECAGON-001",
    "DECAGON-002",
    "DECAGON-003",
    "DECAGON-004",
)

LONG_DUPLICATE_GROUP = (
    "long_radius_6336_equivalence"
)

RATIO_DEPENDENCY_GROUP = (
    "derived_from_long_short_radius_pair"
)

CSV_FIELDNAMES = (
    "comparison_id",
    "source_record_id",
    "comparison_role",
    "independent_forward_prediction",
    "blind_target",
    "primary_historical_observation",
    "duplicate_numeric_evidence_group",
    "historical_dependency",
    "prediction_normalized_value",
    "prediction_normalized_unit",
    "scale_current_foot_per_normalized_unit",
    "prediction_value",
    "comparison_unit",
    "historical_target_value",
    "historical_target_expression",
    "signed_residual",
    "absolute_residual",
    "relative_residual",
    "percent_residual",
    "absolute_percent_residual",
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
    path: str | Path,
) -> str:
    return hashlib.sha256(
        Path(
            path
        ).read_bytes()
    ).hexdigest()


def _verify_hash(
    path: str | Path,
    expected: str,
    label: str,
) -> str:
    actual = sha256_file(
        path
    )

    if actual != expected:
        raise ValueError(
            f"{label} hash mismatch: "
            f"{actual} != {expected}"
        )

    return actual


def verify_frozen_inputs() -> None:
    checks = (
        (
            PROTOCOL_PATH,
            PROTOCOL_SHA256,
            "Phase 7D protocol",
        ),
        (
            PHASE7B_PATH,
            PHASE7B_SHA256,
            "Phase 7B geometry audit",
        ),
        (
            PHASE6C_PATH,
            PHASE6C_SHA256,
            "Phase 6C dimensional predictions",
        ),
        (
            UNIT_SYSTEM_PATH,
            UNIT_SYSTEM_SHA256,
            "Phase 6B unit system",
        ),
        (
            REGISTRY_PATH,
            REGISTRY_SHA256,
            "Phase 6A metrology registry",
        ),
        (
            PHASE7A_CLARIFICATION_PATH,
            PHASE7A_CLARIFICATION_SHA256,
            "Phase 7A source clarification",
        ),
    )

    for path, expected, label in checks:
        _verify_hash(
            path,
            expected,
            label,
        )


def _load_json_decimal(
    path: str | Path,
) -> dict[str, Any]:
    payload = json.loads(
        Path(
            path
        ).read_text(
            encoding="utf-8"
        ),
        parse_float=Decimal,
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            f"Expected JSON object: {path}"
        )

    return payload


def _fraction_from_payload(
    payload: Mapping[str, Any],
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
            "Fraction numerator must be integer."
        )

    if not isinstance(
        denominator,
        int,
    ):
        raise ValueError(
            "Fraction denominator must be integer."
        )

    if denominator == 0:
        raise ValueError(
            "Fraction denominator cannot be zero."
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


def _decimal_text(
    value: Decimal,
) -> str:
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
    value: str | Decimal,
    significant_places: int = 14,
) -> str:
    decimal = (
        value
        if isinstance(
            value,
            Decimal,
        )
        else Decimal(
            str(
                value
            )
        )
    )

    if decimal.is_zero():
        return "0"

    return format(
        decimal,
        f".{significant_places}g",
    )


def _load_registry_rows() -> tuple[
    dict[str, str],
    ...,
]:
    _verify_hash(
        REGISTRY_PATH,
        REGISTRY_SHA256,
        "Phase 6A metrology registry",
    )

    with Path(
        REGISTRY_PATH
    ).open(
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
            "Frozen registry must contain 24 rows."
        )

    return rows


def _registry_by_id(
    rows: Sequence[
        Mapping[str, str]
    ],
) -> dict[
    str,
    Mapping[str, str],
]:
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
                f"Duplicate registry ID: {record_id}"
            )

        result[
            record_id
        ] = row

    return result


def _residual_metrics(
    prediction: Decimal,
    target: Decimal,
) -> dict[str, Decimal]:
    if target.is_zero():
        raise ValueError(
            "Historical target cannot be zero."
        )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        signed = (
            prediction
            - target
        )
        absolute = abs(
            signed
        )
        relative = (
            signed
            / target
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


def _comparison_row(
    *,
    comparison_id: str,
    source_row: Mapping[str, str],
    comparison_role: str,
    prediction_normalized: Decimal,
    prediction_normalized_unit: str,
    prediction_value: Decimal,
    comparison_unit: str,
    historical_target: Decimal,
    historical_target_expression: str,
    scale: Decimal | None,
    primary_historical_observation: bool,
    duplicate_numeric_evidence_group: str | None,
    historical_dependency: str | None,
) -> dict[str, Any]:
    metrics = _residual_metrics(
        prediction_value,
        historical_target,
    )

    return {
        "comparison_id": comparison_id,
        "source_record_id": source_row[
            "record_id"
        ],
        "source_book": source_row[
            "book"
        ],
        "source_figure": source_row[
            "figure"
        ],
        "source_relation": source_row[
            "relation"
        ],
        "frozen_v0_6_prediction_status": source_row[
            "prediction_status"
        ],
        "comparison_role": (
            comparison_role
        ),
        "independent_forward_prediction": False,
        "blind_target": False,
        "primary_historical_observation": (
            primary_historical_observation
        ),
        "prediction": {
            "normalized_value": _decimal_text(
                prediction_normalized
            ),
            "normalized_unit": (
                prediction_normalized_unit
            ),
            "scale_current_foot_per_normalized_unit": (
                None
                if scale is None
                else _decimal_text(
                    scale
                )
            ),
            "value": _decimal_text(
                prediction_value
            ),
            "unit": comparison_unit,
        },
        "historical_target": {
            "value": _decimal_text(
                historical_target
            ),
            "unit": comparison_unit,
            "expression": (
                historical_target_expression
            ),
        },
        "signed_residual": _decimal_text(
            metrics[
                "signed_residual"
            ]
        ),
        "absolute_residual": _decimal_text(
            metrics[
                "absolute_residual"
            ]
        ),
        "relative_residual": _decimal_text(
            metrics[
                "relative_residual"
            ]
        ),
        "percent_residual": _decimal_text(
            metrics[
                "percent_residual"
            ]
        ),
        "absolute_percent_residual": _decimal_text(
            metrics[
                "absolute_percent_residual"
            ]
        ),
        "duplicate_numeric_evidence_group": (
            duplicate_numeric_evidence_group
        ),
        "historical_dependency": (
            historical_dependency
        ),
        "inferred_source_uncertainty": None,
        "posthoc_tolerance": None,
    }


def build_dodecagon_dimensional_audit() -> dict[str, Any]:
    verify_frozen_inputs()

    phase7b = _load_json_decimal(
        PHASE7B_PATH
    )
    phase6c = _load_json_decimal(
        PHASE6C_PATH
    )
    unit_system = _load_json_decimal(
        UNIT_SYSTEM_PATH
    )

    if phase7b.get(
        "phase"
    ) != "7B":
        raise ValueError(
            "Unexpected Phase 7B artifact."
        )

    if phase7b.get(
        "stopping_status"
    ) != "TWO_SEMANTIC_RADIUS_CLASSES_CONFIRMED":
        raise ValueError(
            "Phase 7B two-class result is not frozen as expected."
        )

    if phase6c.get(
        "phase"
    ) != "6C":
        raise ValueError(
            "Unexpected Phase 6C artifact."
        )

    if unit_system.get(
        "phase"
    ) != "6B":
        raise ValueError(
            "Unexpected Phase 6B unit manifest."
        )

    if unit_system.get(
        "canonical_linear_base"
    ) != "current_foot":
        raise ValueError(
            "Unexpected Phase 6B canonical linear base."
        )

    determinacy = phase7b.get(
        "determinacy"
    )

    if not isinstance(
        determinacy,
        dict,
    ):
        raise ValueError(
            "Phase 7B determinacy metadata missing."
        )

    if (
        determinacy.get(
            "historical_dimensional_targets_loaded"
        )
        is not False
    ):
        raise ValueError(
            "Phase 7B historical-target boundary violated."
        )

    if (
        determinacy.get(
            "historical_comparison_metrics_calculated"
        )
        is not False
    ):
        raise ValueError(
            "Phase 7B historical-comparison boundary violated."
        )

    comparison = phase7b.get(
        "normalized_comparison"
    )

    if not isinstance(
        comparison,
        dict,
    ):
        raise ValueError(
            "Phase 7B normalized comparison missing."
        )

    long_normalized = comparison.get(
        "polar_adjacent_mean_radius"
    )
    short_normalized = comparison.get(
        "oblique_pair_mean_radius"
    )
    frozen_ratio = comparison.get(
        "polar_adjacent_to_oblique_pair_ratio"
    )

    for label, value in (
        (
            "long normalized radius",
            long_normalized,
        ),
        (
            "short normalized radius",
            short_normalized,
        ),
        (
            "frozen class ratio",
            frozen_ratio,
        ),
    ):
        if not isinstance(
            value,
            Decimal,
        ):
            raise ValueError(
                f"Missing Decimal {label}."
            )

    scale_derivation = phase6c.get(
        "scale_derivation"
    )

    if not isinstance(
        scale_derivation,
        dict,
    ):
        raise ValueError(
            "Phase 6C scale derivation missing."
        )

    scale_payload = scale_derivation.get(
        "current_foot_per_normalized_unit"
    )

    if not isinstance(
        scale_payload,
        dict,
    ):
        raise ValueError(
            "Frozen current-foot scale payload missing."
        )

    scale_fraction = _fraction_from_payload(
        scale_payload
    )

    if scale_fraction != Fraction(
        720,
        1,
    ):
        raise ValueError(
            "Frozen scale is not exactly 720 current ft/u."
        )

    if (
        scale_derivation.get(
            "free_wall_scale_parameter"
        )
        is not False
    ):
        raise ValueError(
            "Unexpected free wall scale parameter."
        )

    scale = _decimal_from_fraction(
        scale_fraction
    )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        long_current_foot = (
            long_normalized
            * scale
        )
        short_current_foot = (
            short_normalized
            * scale
        )

    rows = _load_registry_rows()
    registry = _registry_by_id(
        rows
    )

    for record_id in SOURCE_RECORD_ORDER:
        if record_id not in registry:
            raise ValueError(
                f"Missing frozen source record: {record_id}"
            )

    source_1 = registry[
        "DECAGON-001"
    ]
    source_2 = registry[
        "DECAGON-002"
    ]
    source_3 = registry[
        "DECAGON-003"
    ]
    source_4 = registry[
        "DECAGON-004"
    ]

    if source_1[
        "source_unit"
    ] != "foot":
        raise ValueError(
            "DECAGON-001 unit changed."
        )

    if source_2[
        "source_unit"
    ] != "foot":
        raise ValueError(
            "DECAGON-002 unit changed."
        )

    long_target = Decimal(
        source_1[
            "source_value"
        ]
    )

    short_target = Decimal(
        source_2[
            "source_value"
        ]
    )

    ratio_numerator = Decimal(
        source_3[
            "source_value"
        ]
    )
    ratio_denominator = Decimal(
        source_3[
            "secondary_value"
        ]
    )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        ratio_target = (
            ratio_numerator
            / ratio_denominator
        )

    source4_primary = Decimal(
        source_4[
            "source_value"
        ]
    )
    source4_secondary = Decimal(
        source_4[
            "secondary_value"
        ]
    )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        one_fifth_target = (
            source4_secondary
            / Decimal(
                5
            )
        )

    if (
        source4_primary
        != one_fifth_target
    ):
        raise ValueError(
            "DECAGON-004 source relation is not numerically self-consistent."
        )

    if (
        long_target
        != one_fifth_target
    ):
        raise ValueError(
            "D7-001 and D7-004 no longer share the frozen target."
        )

    comparisons = [
        _comparison_row(
            comparison_id="D7-001",
            source_row=source_1,
            comparison_role=(
                "retrospective_no_refit_source_consistency"
            ),
            prediction_normalized=long_normalized,
            prediction_normalized_unit="normalized_unit",
            prediction_value=long_current_foot,
            comparison_unit="current_foot",
            historical_target=long_target,
            historical_target_expression=(
                source_1[
                    "source_value"
                ]
                + " current feet"
            ),
            scale=scale,
            primary_historical_observation=True,
            duplicate_numeric_evidence_group=(
                LONG_DUPLICATE_GROUP
            ),
            historical_dependency=None,
        ),
        _comparison_row(
            comparison_id="D7-002",
            source_row=source_2,
            comparison_role=(
                "retrospective_no_refit_source_consistency"
            ),
            prediction_normalized=short_normalized,
            prediction_normalized_unit="normalized_unit",
            prediction_value=short_current_foot,
            comparison_unit="current_foot",
            historical_target=short_target,
            historical_target_expression=(
                source_2[
                    "source_value"
                ]
                + " current feet"
            ),
            scale=scale,
            primary_historical_observation=True,
            duplicate_numeric_evidence_group=None,
            historical_dependency=None,
        ),
        _comparison_row(
            comparison_id="D7-003",
            source_row=source_3,
            comparison_role=(
                "retrospective_derived_relation"
            ),
            prediction_normalized=frozen_ratio,
            prediction_normalized_unit="dimensionless",
            prediction_value=frozen_ratio,
            comparison_unit="dimensionless",
            historical_target=ratio_target,
            historical_target_expression=(
                source_3[
                    "source_value"
                ]
                + "/"
                + source_3[
                    "secondary_value"
                ]
            ),
            scale=None,
            primary_historical_observation=False,
            duplicate_numeric_evidence_group=None,
            historical_dependency=(
                RATIO_DEPENDENCY_GROUP
            ),
        ),
        _comparison_row(
            comparison_id="D7-004",
            source_row=source_4,
            comparison_role=(
                "retrospective_equivalent_relation"
            ),
            prediction_normalized=long_normalized,
            prediction_normalized_unit="normalized_unit",
            prediction_value=long_current_foot,
            comparison_unit="current_foot",
            historical_target=one_fifth_target,
            historical_target_expression=(
                source_4[
                    "secondary_value"
                ]
                + "/5 current feet"
            ),
            scale=scale,
            primary_historical_observation=False,
            duplicate_numeric_evidence_group=(
                LONG_DUPLICATE_GROUP
            ),
            historical_dependency="equivalent_to_D7-001",
        ),
    ]

    actual_order = tuple(
        row[
            "comparison_id"
        ]
        for row in comparisons
    )

    if actual_order != COMPARISON_ORDER:
        raise ValueError(
            "Comparison order differs from frozen protocol."
        )

    tolerance_row = registry.get(
        "SOMM-004"
    )

    if tolerance_row is None:
        raise ValueError(
            "Frozen SOMM-004 tolerance context missing."
        )

    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "analysis_id": (
            "njg-michell-v0-7-dodecagon-dimensional-audit-v1"
        ),
        "stopping_status": STOPPING_STATUS,
        "frozen_inputs": {
            "phase7d_protocol": {
                "path": PROTOCOL_PATH,
                "sha256": PROTOCOL_SHA256,
            },
            "phase7b_geometry_audit": {
                "path": PHASE7B_PATH,
                "sha256": PHASE7B_SHA256,
            },
            "phase6c_dimensional_predictions": {
                "path": PHASE6C_PATH,
                "sha256": PHASE6C_SHA256,
            },
            "phase6b_unit_system": {
                "path": UNIT_SYSTEM_PATH,
                "sha256": UNIT_SYSTEM_SHA256,
            },
            "phase6a_registry": {
                "path": REGISTRY_PATH,
                "sha256": REGISTRY_SHA256,
            },
            "phase7a_source_clarification": {
                "path": PHASE7A_CLARIFICATION_PATH,
                "sha256": PHASE7A_CLARIFICATION_SHA256,
            },
        },
        "frozen_scale": {
            "current_foot_per_normalized_unit": (
                _decimal_text(
                    scale
                )
            ),
            "exact_fraction": {
                "numerator": (
                    scale_fraction.numerator
                ),
                "denominator": (
                    scale_fraction.denominator
                ),
            },
            "free_scale_parameter": False,
            "source": (
                "frozen Phase 6C scale_derivation"
            ),
        },
        "frozen_geometry_quantities": {
            "polar_adjacent_radius_normalized": (
                _decimal_text(
                    long_normalized
                )
            ),
            "oblique_pair_radius_normalized": (
                _decimal_text(
                    short_normalized
                )
            ),
            "radius_class_ratio_normalized": (
                _decimal_text(
                    frozen_ratio
                )
            ),
            "geometry_modified_in_phase7d": False,
        },
        "dimensional_predictions": {
            "long_radius_current_foot": (
                _decimal_text(
                    long_current_foot
                )
            ),
            "short_radius_current_foot": (
                _decimal_text(
                    short_current_foot
                )
            ),
            "radius_class_ratio": (
                _decimal_text(
                    frozen_ratio
                )
            ),
        },
        "residual_definition": {
            "signed_residual": (
                "prediction - historical_target"
            ),
            "relative_residual": (
                "(prediction - historical_target) / historical_target"
            ),
            "percent_residual": (
                "100 * (prediction - historical_target) / historical_target"
            ),
        },
        "evidential_policy": {
            "comparison_role": (
                "retrospective_no_refit_source_consistency"
            ),
            "independent_forward_prediction": False,
            "blind_target": False,
            "geometry_fitted_to_phase7d_targets": False,
            "scale_fitted_to_phase7d_targets": False,
            "aggregate_goodness_of_fit_calculated": False,
            "ranking_calculated": False,
            "posthoc_threshold_applied": False,
        },
        "historical_tolerance_context": {
            "source_record_id": "SOMM-004",
            "source_value": tolerance_row[
                "source_value"
            ],
            "secondary_value": tolerance_row[
                "secondary_value"
            ],
            "relation": tolerance_row[
                "relation"
            ],
            "used_as_acceptance_threshold": False,
            "used_as_pass_fail_rule": False,
        },
        "duplicate_and_derived_evidence": {
            "primary_dimensional_observations": [
                "D7-001",
                "D7-002",
            ],
            LONG_DUPLICATE_GROUP: [
                "D7-001",
                "D7-004",
            ],
            RATIO_DEPENDENCY_GROUP: [
                "D7-001",
                "D7-002",
                "D7-003",
            ],
            "four_independent_matches_claim_permitted": False,
        },
        "summary": {
            "comparison_count": 4,
            "primary_dimensional_observation_count": 2,
            "independent_forward_prediction_count": 0,
            "aggregate_goodness_of_fit_calculated": False,
            "ranking_calculated": False,
            "posthoc_threshold_applied": False,
        },
        "comparisons": comparisons,
    }

    payload_keys = set(
        payload
    )

    forbidden_found = (
        payload_keys
        & FORBIDDEN_AGGREGATE_KEYS
    )

    if forbidden_found:
        raise ValueError(
            "Forbidden aggregate result keys present: "
            f"{sorted(forbidden_found)}"
        )

    return payload


def canonical_json_bytes(
    payload: Mapping[str, Any],
) -> bytes:
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode(
        "utf-8"
    )


def _csv_row(
    row: Mapping[str, Any],
) -> dict[str, Any]:
    prediction = row[
        "prediction"
    ]
    target = row[
        "historical_target"
    ]

    assert isinstance(
        prediction,
        dict,
    )
    assert isinstance(
        target,
        dict,
    )

    return {
        "comparison_id": row[
            "comparison_id"
        ],
        "source_record_id": row[
            "source_record_id"
        ],
        "comparison_role": row[
            "comparison_role"
        ],
        "independent_forward_prediction": "false",
        "blind_target": "false",
        "primary_historical_observation": (
            "true"
            if row[
                "primary_historical_observation"
            ]
            else "false"
        ),
        "duplicate_numeric_evidence_group": (
            row[
                "duplicate_numeric_evidence_group"
            ]
            or ""
        ),
        "historical_dependency": (
            row[
                "historical_dependency"
            ]
            or ""
        ),
        "prediction_normalized_value": prediction[
            "normalized_value"
        ],
        "prediction_normalized_unit": prediction[
            "normalized_unit"
        ],
        "scale_current_foot_per_normalized_unit": (
            prediction[
                "scale_current_foot_per_normalized_unit"
            ]
            or ""
        ),
        "prediction_value": prediction[
            "value"
        ],
        "comparison_unit": prediction[
            "unit"
        ],
        "historical_target_value": target[
            "value"
        ],
        "historical_target_expression": target[
            "expression"
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
    }


def canonical_csv_text(
    payload: Mapping[str, Any],
) -> str:
    comparisons = payload.get(
        "comparisons"
    )

    if not isinstance(
        comparisons,
        list,
    ):
        raise ValueError(
            "Payload lacks comparisons."
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
    payload: Mapping[str, Any],
) -> str:
    comparisons = payload.get(
        "comparisons"
    )

    if not isinstance(
        comparisons,
        list,
    ):
        raise ValueError(
            "Payload lacks comparisons."
        )

    predictions = payload[
        "dimensional_predictions"
    ]

    assert isinstance(
        predictions,
        dict,
    )

    lines = [
        "# v0.7 dodecagon dimensional audit",
        "",
        "## Status",
        "",
        "Frozen-artifact historical comparison under the preregistered "
        "Phase 7D protocol.",
        "",
        "No geometry or scale was refitted after the Figure 30 dimensional "
        "quantities entered the v0.7 workflow.",
        "",
        "The comparisons are retrospective no-refit source-consistency checks, "
        "not independent forward predictions.",
        "",
        "## Frozen dimensional predictions",
        "",
        "- Long / polar-adjacent dodecagon vertex radius: `"
        + str(
            predictions[
                "long_radius_current_foot"
            ]
        )
        + " current ft`.",
        "- Short / oblique-pair dodecagon vertex radius: `"
        + str(
            predictions[
                "short_radius_current_foot"
            ]
        )
        + " current ft`.",
        "- Frozen normalized radius-class ratio: `"
        + str(
            predictions[
                "radius_class_ratio"
            ]
        )
        + "`.",
        "",
        "## Registered historical comparisons",
        "",
        "| ID | Historical expression | Frozen prediction | Signed residual | Percent residual | Role |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]

    for row in comparisons:
        assert isinstance(
            row,
            dict,
        )

        prediction = row[
            "prediction"
        ]
        target = row[
            "historical_target"
        ]

        assert isinstance(
            prediction,
            dict,
        )
        assert isinstance(
            target,
            dict,
        )

        unit = str(
            prediction[
                "unit"
            ]
        )

        unit_label = (
            ""
            if unit
            == "dimensionless"
            else " current ft"
        )

        lines.append(
            "| "
            + str(
                row[
                    "comparison_id"
                ]
            )
            + " | "
            + str(
                target[
                    "expression"
                ]
            )
            + " | "
            + _display_decimal(
                str(
                    prediction[
                        "value"
                    ]
                )
            )
            + unit_label
            + " | "
            + _display_decimal(
                str(
                    row[
                        "signed_residual"
                    ]
                )
            )
            + " | "
            + _display_decimal(
                str(
                    row[
                        "percent_residual"
                    ]
                )
            )
            + "% | `"
            + str(
                row[
                    "comparison_role"
                ]
            )
            + "` |"
        )

    lines.extend(
        [
            "",
            "Residual sign convention:",
            "",
            "```text",
            "signed residual = frozen prediction - historical source value",
            "```",
            "",
            "## Evidential dependence",
            "",
            "- `D7-001` and `D7-002` are the two primary historical dimensional "
            "observations.",
            "- `D7-003` is a historical ratio derived from the same long/short "
            "radius pair and is not an additional independent numerical target.",
            "- `D7-004` is numerically equivalent to `D7-001` because the source "
            "relation states that the long radius is one fifth of 31680.",
            "- The four rows must not be described as four independent matches.",
            "",
            "## Historical tolerance context",
            "",
            "Figure 30 reports Sommerville working to a tolerance of `1:2500` "
            "in the surrounding dodecagon discussion.",
            "",
            "That historical tolerance is not used here as an acceptance "
            "threshold or pass/fail rule.",
            "",
            "## Interpretation",
            "",
            "This audit asks only how closely the already-frozen project "
            "geometry reproduces the Figure 30 radius quantities under the "
            "already-frozen source-defined scale.",
            "",
            "It does not establish independent prediction, statistical "
            "significance, ancient intentionality, physical law, archaeological "
            "validation, or independent verification of Sommerville's 1974 "
            "paper.",
            "",
            "No aggregate goodness-of-fit statistic, ranking, success count, "
            "or post-hoc threshold is calculated.",
            "",
        ]
    )

    return "\n".join(
        lines
    )


SVG_WIDTH = 1100
SVG_HEIGHT = 900


def _svg_text(
    *,
    x: int,
    y: int,
    text: str,
    size: int = 18,
    weight: str = "normal",
    opacity: float = 1.0,
) -> str:
    return (
        f'<text x="{x}" y="{y}" '
        f'font-family="sans-serif" font-size="{size}" '
        f'font-weight="{weight}" fill="currentColor" '
        f'opacity="{opacity:.2f}">'
        f"{escape(text)}"
        "</text>"
    )


def canonical_svg_text(
    payload: Mapping[str, Any],
) -> str:
    comparisons = payload.get(
        "comparisons"
    )

    if not isinstance(
        comparisons,
        list,
    ):
        raise ValueError(
            "Payload lacks comparisons."
        )

    by_id = {
        str(
            row[
                "comparison_id"
            ]
        ): row
        for row in comparisons
        if isinstance(
            row,
            dict,
        )
    }

    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
            f'viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" '
            'role="img">'
        ),
        "<title>Sommerville dodecagon dimensional audit</title>",
        (
            "<desc>Historical Figure 30 radius comparison against frozen "
            "v0.7 geometry under the frozen current-foot scale. "
            "Retrospective no-refit comparison.</desc>"
        ),
        (
            "<metadata>"
            + escape(
                json.dumps(
                    {
                        "phase": PHASE,
                        "protocol_sha256": (
                            PROTOCOL_SHA256
                        ),
                        "phase7b_sha256": (
                            PHASE7B_SHA256
                        ),
                        "comparison_role": (
                            "retrospective_no_refit_source_consistency"
                        ),
                        "independent_forward_prediction": False,
                        "geometry_refit": False,
                        "scale_refit": False,
                    },
                    sort_keys=True,
                    separators=(
                        ",",
                        ":",
                    ),
                )
            )
            + "</metadata>"
        ),
        _svg_text(
            x=60,
            y=60,
            text=(
                "Sommerville dodecagon — frozen dimensional audit"
            ),
            size=27,
            weight="bold",
        ),
        _svg_text(
            x=60,
            y=92,
            text=(
                "Figure 30 source values compared only after the "
                "geometry and scale were frozen"
            ),
            size=16,
            opacity=0.72,
        ),
        (
            '<line x1="60" y1="116" x2="1040" y2="116" '
            'stroke="currentColor" stroke-width="1" opacity="0.25"/>'
        ),
    ]

    row_y = {
        "D7-001": 170,
        "D7-002": 315,
        "D7-003": 460,
        "D7-004": 605,
    }

    labels = {
        "D7-001": "Long / polar-adjacent radius",
        "D7-002": "Short / oblique-pair radius",
        "D7-003": "Radius-class ratio",
        "D7-004": "Long radius = one fifth relation",
    }

    for comparison_id in COMPARISON_ORDER:
        row = by_id[
            comparison_id
        ]
        prediction = row[
            "prediction"
        ]
        target = row[
            "historical_target"
        ]

        assert isinstance(
            prediction,
            dict,
        )
        assert isinstance(
            target,
            dict,
        )

        y = row_y[
            comparison_id
        ]

        lines.extend(
            [
                _svg_text(
                    x=70,
                    y=y,
                    text=(
                        comparison_id
                        + " — "
                        + labels[
                            comparison_id
                        ]
                    ),
                    size=20,
                    weight="bold",
                ),
                _svg_text(
                    x=90,
                    y=y + 34,
                    text=(
                        "Frozen prediction: "
                        + _display_decimal(
                            str(
                                prediction[
                                    "value"
                                ]
                            )
                        )
                        + (
                            ""
                            if prediction[
                                "unit"
                            ]
                            == "dimensionless"
                            else " current ft"
                        )
                    ),
                    size=17,
                ),
                _svg_text(
                    x=90,
                    y=y + 62,
                    text=(
                        "Historical source: "
                        + str(
                            target[
                                "expression"
                            ]
                        )
                    ),
                    size=17,
                ),
                _svg_text(
                    x=90,
                    y=y + 90,
                    text=(
                        "Residual: "
                        + _display_decimal(
                            str(
                                row[
                                    "signed_residual"
                                ]
                            )
                        )
                        + "   ("
                        + _display_decimal(
                            str(
                                row[
                                    "percent_residual"
                                ]
                            )
                        )
                        + "%)"
                    ),
                    size=17,
                ),
                _svg_text(
                    x=650,
                    y=y + 34,
                    text=(
                        "retrospective / no-refit"
                    ),
                    size=16,
                    opacity=0.72,
                ),
                _svg_text(
                    x=650,
                    y=y + 62,
                    text=(
                        (
                            "primary historical observation"
                            if row[
                                "primary_historical_observation"
                            ]
                            else (
                                "derived / equivalent relation"
                            )
                        )
                    ),
                    size=16,
                    opacity=0.72,
                ),
                (
                    f'<line x1="60" y1="{y + 116}" '
                    f'x2="1040" y2="{y + 116}" '
                    'stroke="currentColor" stroke-width="1" '
                    'opacity="0.18"/>'
                ),
            ]
        )

    lines.extend(
        [
            _svg_text(
                x=60,
                y=790,
                text=(
                    "Evidence note"
                ),
                size=18,
                weight="bold",
            ),
            _svg_text(
                x=60,
                y=820,
                text=(
                    "D7-001 and D7-004 are the same numerical evidence; "
                    "D7-003 is derived from the long/short pair."
                ),
                size=15,
                opacity=0.72,
            ),
            _svg_text(
                x=60,
                y=846,
                text=(
                    "No independent forward-prediction claim and no "
                    "1:2500 pass/fail threshold."
                ),
                size=15,
                opacity=0.72,
            ),
            "</svg>",
        ]
    )

    return (
        "\n".join(
            lines
        )
        + "\n"
    )


def write_dodecagon_dimensional_audit_outputs() -> tuple[
    bytes,
    bytes,
    bytes,
    bytes,
]:
    payload = build_dodecagon_dimensional_audit()

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

    svg_bytes = canonical_svg_text(
        payload
    ).encode(
        "utf-8"
    )

    outputs = (
        (
            Path(
                JSON_OUTPUT_PATH
            ),
            json_bytes,
        ),
        (
            Path(
                CSV_OUTPUT_PATH
            ),
            csv_bytes,
        ),
        (
            Path(
                MARKDOWN_OUTPUT_PATH
            ),
            markdown_bytes,
        ),
        (
            Path(
                SVG_OUTPUT_PATH
            ),
            svg_bytes,
        ),
    )

    for path, body in outputs:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_bytes(
            body
        )

    return (
        json_bytes,
        csv_bytes,
        markdown_bytes,
        svg_bytes,
    )
