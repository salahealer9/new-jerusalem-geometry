from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from new_jerusalem_geometry.metrology import (
    ALLOWED_UNIT_RECORD_IDS,
    DEFAULT_REGISTRY_RELATIVE_PATH,
    EXPECTED_REGISTRY_SHA256,
    MICHELL_PI_22_OVER_7,
    build_unit_manifest,
    build_unit_system,
    canonical_manifest_bytes,
    circumference_22_over_7,
    circumference_euclidean,
    load_metrology_registry,
    select_unit_parameter_records,
    sha256_file,
    write_unit_manifest,
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

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "metrology.py"
)

CANONICAL_MANIFEST = (
    ROOT
    / "data"
    / "metrology"
    / "njg_michell_v0_6"
    / "unit_system.json"
)

TARGET_LITERALS = (
    "3264",
    "3280",
    "3270",
    "36000",
    "120000000",
    "6336",
    "6300",
)


def _registry_rows() -> tuple[dict[str, str], ...]:
    return load_metrology_registry(
        REGISTRY
    )


def _records() -> tuple[dict[str, str], ...]:
    return select_unit_parameter_records(
        _registry_rows()
    )


def _system():
    return build_unit_system(
        _records()
    )


def test_frozen_registry_hash() -> None:
    assert (
        sha256_file(
            REGISTRY
        )
        == EXPECTED_REGISTRY_SHA256
    )


def test_allowed_unit_record_ids_are_exactly_preregistered() -> None:
    assert ALLOWED_UNIT_RECORD_IDS == (
        "SCALE-001",
        "UNIT-001",
        "UNIT-002",
        "UNIT-003",
        "UNIT-004",
        "SOMM-006",
    )


def test_exactly_six_unit_parameter_records_are_selected() -> None:
    records = _records()

    assert len(
        records
    ) == 6

    assert tuple(
        row[
            "record_id"
        ]
        for row in records
    ) == ALLOWED_UNIT_RECORD_IDS


def test_selected_parameters_are_unit_definitions_not_targets() -> None:
    for row in _records():
        assert (
            row[
                "record_type"
            ]
            == "unit_definition"
        )

        assert (
            row[
                "prediction_status"
            ]
            == "unit_definition"
        )

        assert (
            row[
                "prediction_status"
            ]
            != "development_used_target"
        )


def test_megalithic_yard_exact_conversion() -> None:
    system = _system()

    assert (
        system.linear_factor(
            "megalithic_yard"
        )
        == Fraction(
            68,
            25,
        )
    )

    assert (
        system.convert_linear(
            1,
            from_unit="megalithic_yard",
            to_unit="current_foot",
        )
        == Fraction(
            68,
            25,
        )
    )


def test_sumerian_foot_exact_conversion() -> None:
    system = _system()

    assert (
        system.linear_factor(
            "sumerian_foot"
        )
        == Fraction(
            11,
            10,
        )
    )

    assert (
        Fraction(
            "13.2"
        )
        * system.linear_factor(
            "inch"
        )
        == Fraction(
            11,
            10,
        )
    )


def test_stadion_closes_exactly() -> None:
    system = _system()

    assert (
        system.linear_factor(
            "new_jerusalem_stadion"
        )
        == Fraction(
            660,
            1,
        )
    )

    assert (
        system.linear_factor(
            "furlong"
        )
        == Fraction(
            660,
            1,
        )
    )

    assert (
        600
        * system.linear_factor(
            "sumerian_foot"
        )
        == system.linear_factor(
            "new_jerusalem_stadion"
        )
    )


def test_new_jerusalem_cubit_exact_conversion() -> None:
    system = _system()

    assert (
        system.linear_factor(
            "new_jerusalem_cubit"
        )
        == Fraction(
            216,
            125,
        )
    )


def test_old_english_foot_direction_is_frozen() -> None:
    system = _system()

    assert (
        system.linear_factor(
            "old_english_foot"
        )
        == Fraction(
            12,
            11,
        )
    )

    assert (
        system.convert_linear(
            12,
            from_unit="current_foot",
            to_unit="old_english_foot",
        )
        == Fraction(
            11,
            1,
        )
    )


def test_old_english_foot_round_trip() -> None:
    system = _system()

    starting = Fraction(
        37,
        5,
    )

    old_english = system.convert_linear(
        starting,
        from_unit="current_foot",
        to_unit="old_english_foot",
    )

    recovered = system.convert_linear(
        old_english,
        from_unit="old_english_foot",
        to_unit="current_foot",
    )

    assert recovered == starting


def test_area_conversion_is_square_of_linear_factor() -> None:
    system = _system()

    assert (
        system.convert_area(
            1,
            from_linear_unit="megalithic_yard",
            to_linear_unit="current_foot",
        )
        == Fraction(
            68 * 68,
            25 * 25,
        )
    )


def test_model_scale_is_separate_from_physical_unit_graph() -> None:
    system = _system()

    assert (
        system.source_miles_to_model_feet(
            Fraction(
                17,
                3,
            )
        )
        == Fraction(
            17,
            3,
        )
    )

    assert (
        system.model_feet_to_source_miles(
            Fraction(
                17,
                3,
            )
        )
        == Fraction(
            17,
            3,
        )
    )

    with pytest.raises(
        KeyError
    ):
        system.linear_factor(
            "mile"
        )


def test_pi_conventions_remain_distinct() -> None:
    assert (
        MICHELL_PI_22_OVER_7
        == Fraction(
            22,
            7,
        )
    )

    conventional = circumference_22_over_7(
        1
    )

    euclidean = circumference_euclidean(
        1.0
    )

    assert conventional == Fraction(
        44,
        7,
    )

    assert float(
        conventional
    ) != euclidean


def test_builder_rejects_extra_development_used_target() -> None:
    rows = _registry_rows()
    records = list(
        _records()
    )

    target = next(
        row
        for row in rows
        if row[
            "prediction_status"
        ]
        == "development_used_target"
    )

    records.append(
        target
    )

    with pytest.raises(
        ValueError
    ):
        build_unit_system(
            records
        )


def test_phase6b_module_contains_no_geometric_target_literals() -> None:
    text = MODULE.read_text(
        encoding="utf-8"
    )

    for literal in TARGET_LITERALS:
        assert literal not in text


def test_manifest_contains_only_allowed_source_records() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    source_registry = manifest[
        "source_registry"
    ]

    assert (
        tuple(
            source_registry[
                "allowed_record_ids"
            ]
        )
        == ALLOWED_UNIT_RECORD_IDS
    )

    manifest_text = canonical_manifest_bytes(
        manifest
    ).decode(
        "utf-8"
    )

    for literal in TARGET_LITERALS:
        assert literal not in manifest_text


def test_manifest_contains_no_absolute_home_path() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    text = canonical_manifest_bytes(
        manifest
    ).decode(
        "utf-8"
    )

    assert "/home/" not in text
    assert "/Users/" not in text


def test_manifest_records_separate_model_scale() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    model_scale = manifest[
        "model_scale"
    ]

    assert (
        model_scale[
            "source_record_id"
        ]
        == "SCALE-001"
    )

    assert (
        model_scale[
            "physical_unit_conversion"
        ]
        is False
    )


def test_manifest_records_both_pi_conventions() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    pi_conventions = manifest[
        "pi_conventions"
    ]

    assert set(
        pi_conventions
    ) == {
        "euclidean",
        "michell_22_over_7",
    }

    assert (
        pi_conventions[
            "michell_22_over_7"
        ][
            "value"
        ][
            "numerator"
        ]
        == 22
    )

    assert (
        pi_conventions[
            "michell_22_over_7"
        ][
            "value"
        ][
            "denominator"
        ]
        == 7
    )


def test_manifest_target_leakage_lists_are_empty() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    leakage = manifest[
        "target_leakage"
    ]

    assert (
        leakage[
            "geometric_target_records_used_as_parameters"
        ]
        == []
    )

    assert (
        leakage[
            "development_used_target_parameters"
        ]
        == []
    )


def test_manifest_serialization_is_deterministic() -> None:
    first = canonical_manifest_bytes(
        build_unit_manifest(
            registry_path=REGISTRY
        )
    )

    second = canonical_manifest_bytes(
        build_unit_manifest(
            registry_path=REGISTRY
        )
    )

    assert first == second


def test_tracked_manifest_matches_regeneration(
    tmp_path: Path,
) -> None:
    generated = (
        tmp_path
        / "unit_system.json"
    )

    generated_bytes = write_unit_manifest(
        registry_path=REGISTRY,
        output_path=generated,
    )

    assert generated_bytes == generated.read_bytes()

    if CANONICAL_MANIFEST.exists():
        assert (
            CANONICAL_MANIFEST.read_bytes()
            == generated_bytes
        )


def test_manifest_is_valid_json() -> None:
    manifest = build_unit_manifest(
        registry_path=REGISTRY
    )

    parsed = json.loads(
        canonical_manifest_bytes(
            manifest
        )
    )

    assert (
        parsed[
            "phase"
        ]
        == "6B"
    )
