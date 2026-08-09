from __future__ import annotations

import ast
import csv
import hashlib
import json
from decimal import (
    Decimal,
    localcontext,
)
from io import StringIO
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.dodecagon_dimensional_audit import (
    COMPARISON_ORDER,
    DECIMAL_PRECISION,
    CSV_OUTPUT_PATH,
    JSON_OUTPUT_PATH,
    MARKDOWN_OUTPUT_PATH,
    PHASE7B_SHA256,
    PHASE6C_SHA256,
    PROTOCOL_SHA256,
    REGISTRY_SHA256,
    SVG_OUTPUT_PATH,
    UNIT_SYSTEM_SHA256,
    build_dodecagon_dimensional_audit,
    canonical_csv_text,
    canonical_json_bytes,
    canonical_markdown_text,
    canonical_svg_text,
    write_dodecagon_dimensional_audit_outputs,
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
    / "dodecagon_dimensional_audit.py"
)


def _payload() -> dict:
    return (
        build_dodecagon_dimensional_audit()
    )


def test_protocol_hash_is_frozen() -> None:
    path = (
        ROOT
        / "docs"
        / "specification"
        / "v0.7_dodecagon_dimensional_audit_protocol.md"
    )

    assert (
        hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
        == PROTOCOL_SHA256
    )


def test_all_frozen_input_hashes() -> None:
    expected = {
        (
            ROOT
            / "data"
            / "analysis"
            / "njg_michell_v0_7"
            / "dodecagon_vertex_radius_audit.json"
        ): PHASE7B_SHA256,
        (
            ROOT
            / "data"
            / "metrology"
            / "njg_michell_v0_6"
            / "frozen_dimensional_predictions.json"
        ): PHASE6C_SHA256,
        (
            ROOT
            / "data"
            / "metrology"
            / "njg_michell_v0_6"
            / "unit_system.json"
        ): UNIT_SYSTEM_SHA256,
        (
            ROOT
            / "docs"
            / "sources"
            / "v0.6_metrology_registry.csv"
        ): REGISTRY_SHA256,
    }

    for path, expected_hash in expected.items():
        assert (
            hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            == expected_hash
        )


def test_scale_is_exactly_720_and_not_fitted() -> None:
    payload = _payload()

    scale = payload[
        "frozen_scale"
    ]

    assert (
        scale[
            "current_foot_per_normalized_unit"
        ]
        == "720"
    )

    assert (
        scale[
            "exact_fraction"
        ]
        == {
            "numerator": 720,
            "denominator": 1,
        }
    )

    assert (
        scale[
            "free_scale_parameter"
        ]
        is False
    )


def test_comparison_order_is_preregistered() -> None:
    payload = _payload()

    assert tuple(
        row[
            "comparison_id"
        ]
        for row in payload[
            "comparisons"
        ]
    ) == COMPARISON_ORDER


def test_source_record_mapping_is_frozen() -> None:
    payload = _payload()

    assert tuple(
        row[
            "source_record_id"
        ]
        for row in payload[
            "comparisons"
        ]
    ) == (
        "DECAGON-001",
        "DECAGON-002",
        "DECAGON-003",
        "DECAGON-004",
    )


def test_two_primary_historical_observations_only() -> None:
    payload = _payload()

    primary = [
        row[
            "comparison_id"
        ]
        for row in payload[
            "comparisons"
        ]
        if row[
            "primary_historical_observation"
        ]
    ]

    assert primary == [
        "D7-001",
        "D7-002",
    ]


def test_long_and_short_predictions_use_frozen_scale() -> None:
    payload = _payload()

    frozen = payload[
        "frozen_geometry_quantities"
    ]

    predictions = payload[
        "dimensional_predictions"
    ]

    long_expected = (
        Decimal(
            frozen[
                "polar_adjacent_radius_normalized"
            ]
        )
        * Decimal(
            720
        )
    )

    short_expected = (
        Decimal(
            frozen[
                "oblique_pair_radius_normalized"
            ]
        )
        * Decimal(
            720
        )
    )

    assert (
        Decimal(
            predictions[
                "long_radius_current_foot"
            ]
        )
        == long_expected
    )

    assert (
        Decimal(
            predictions[
                "short_radius_current_foot"
            ]
        )
        == short_expected
    )


def test_ratio_target_is_176_over_175_from_registry() -> None:
    payload = _payload()

    row = payload[
        "comparisons"
    ][
        2
    ]

    assert (
        row[
            "comparison_id"
        ]
        == "D7-003"
    )

    with localcontext() as context:
        context.prec = DECIMAL_PRECISION

        expected = (
            Decimal(
                176
            )
            / Decimal(
                175
            )
        )

    assert (
        Decimal(
            row[
                "historical_target"
            ][
                "value"
            ]
        )
        == expected
    )

    assert (
        row[
            "comparison_role"
        ]
        == "retrospective_derived_relation"
    )


def test_one_fifth_relation_is_duplicate_of_long_target() -> None:
    payload = _payload()

    long_row = payload[
        "comparisons"
    ][
        0
    ]
    fifth_row = payload[
        "comparisons"
    ][
        3
    ]

    assert (
        long_row[
            "historical_target"
        ][
            "value"
        ]
        == fifth_row[
            "historical_target"
        ][
            "value"
        ]
    )

    assert (
        long_row[
            "duplicate_numeric_evidence_group"
        ]
        == fifth_row[
            "duplicate_numeric_evidence_group"
        ]
    )

    assert (
        fifth_row[
            "historical_dependency"
        ]
        == "equivalent_to_D7-001"
    )


def test_residual_formulas_hold_for_all_rows() -> None:
    payload = _payload()

    for row in payload[
        "comparisons"
    ]:
        prediction = Decimal(
            row[
                "prediction"
            ][
                "value"
            ]
        )

        target = Decimal(
            row[
                "historical_target"
            ][
                "value"
            ]
        )

        with localcontext() as context:
            context.prec = DECIMAL_PRECISION

            signed = (
                prediction
                - target
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

            absolute = abs(
                signed
            )

            absolute_percent = abs(
                percent
            )

        assert (
            Decimal(
                row[
                    "signed_residual"
                ]
            )
            == signed
        )

        assert (
            Decimal(
                row[
                    "absolute_residual"
                ]
            )
            == absolute
        )

        assert (
            Decimal(
                row[
                    "relative_residual"
                ]
            )
            == relative
        )

        assert (
            Decimal(
                row[
                    "percent_residual"
                ]
            )
            == percent
        )

        assert (
            Decimal(
                row[
                    "absolute_percent_residual"
                ]
            )
            == absolute_percent
        )


def test_no_independent_forward_prediction_claim() -> None:
    payload = _payload()

    assert all(
        row[
            "independent_forward_prediction"
        ]
        is False
        for row in payload[
            "comparisons"
        ]
    )

    assert (
        payload[
            "summary"
        ][
            "independent_forward_prediction_count"
        ]
        == 0
    )


def test_historical_tolerance_is_context_only() -> None:
    payload = _payload()

    tolerance = payload[
        "historical_tolerance_context"
    ]

    assert (
        tolerance[
            "source_record_id"
        ]
        == "SOMM-004"
    )

    assert (
        tolerance[
            "used_as_acceptance_threshold"
        ]
        is False
    )

    assert (
        tolerance[
            "used_as_pass_fail_rule"
        ]
        is False
    )


def test_no_aggregate_score_ranking_or_posthoc_threshold() -> None:
    payload = _payload()

    summary = payload[
        "summary"
    ]

    assert (
        summary[
            "aggregate_goodness_of_fit_calculated"
        ]
        is False
    )

    assert (
        summary[
            "ranking_calculated"
        ]
        is False
    )

    assert (
        summary[
            "posthoc_threshold_applied"
        ]
        is False
    )


def test_audit_module_does_not_import_geometry_builders() -> None:
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
        "dodecagon_vertex_radius_audit",
        "polar_pivot",
        "wall_reconstruction",
    )

    assert not any(
        fragment
        in imported
        for imported in imports
        for fragment in forbidden
    )


def test_csv_has_exactly_four_rows() -> None:
    text = canonical_csv_text(
        _payload()
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
    ) == 4

    assert tuple(
        row[
            "comparison_id"
        ]
        for row in rows
    ) == COMPARISON_ORDER


def test_markdown_preserves_evidential_boundary() -> None:
    text = canonical_markdown_text(
        _payload()
    )

    assert (
        "not independent forward predictions"
        in text
    )

    assert (
        "must not be described as four independent matches"
        in text
    )

    assert (
        "not used here as an acceptance threshold"
        in text
    )

    assert (
        "No aggregate goodness-of-fit statistic"
        in text
    )


def test_svg_is_transparent_and_has_clear_sections() -> None:
    text = canonical_svg_text(
        _payload()
    )

    assert (
        "<rect"
        not in text
    )

    for comparison_id in COMPARISON_ORDER:
        assert (
            comparison_id
            in text
        )

    assert (
        "retrospective / no-refit"
        in text
    )

    assert (
        "No independent forward-prediction claim"
        in text
    )


def test_serializations_are_deterministic() -> None:
    payload = _payload()

    assert (
        canonical_json_bytes(
            payload
        )
        == canonical_json_bytes(
            payload
        )
    )

    assert (
        canonical_csv_text(
            payload
        )
        == canonical_csv_text(
            payload
        )
    )

    assert (
        canonical_markdown_text(
            payload
        )
        == canonical_markdown_text(
            payload
        )
    )

    assert (
        canonical_svg_text(
            payload
        )
        == canonical_svg_text(
            payload
        )
    )


def test_tracked_outputs_match_regeneration(
    tmp_path: Path,
) -> None:
    outputs = (
        write_dodecagon_dimensional_audit_outputs()
    )

    paths = (
        ROOT
        / JSON_OUTPUT_PATH,
        ROOT
        / CSV_OUTPUT_PATH,
        ROOT
        / MARKDOWN_OUTPUT_PATH,
        ROOT
        / SVG_OUTPUT_PATH,
    )

    for path, body in zip(
        paths,
        outputs,
        strict=True,
    ):
        assert (
            path.read_bytes()
            == body
        )


def test_generated_outputs_have_no_absolute_home_paths() -> None:
    payload = _payload()

    combined = (
        canonical_json_bytes(
            payload
        )
        + canonical_csv_text(
            payload
        ).encode(
            "utf-8"
        )
        + canonical_markdown_text(
            payload
        ).encode(
            "utf-8"
        )
        + canonical_svg_text(
            payload
        ).encode(
            "utf-8"
        )
    )

    assert b"/home/" not in combined
    assert b"/Users/" not in combined


def test_package_version_is_0_8_0_at_release_closeout() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
