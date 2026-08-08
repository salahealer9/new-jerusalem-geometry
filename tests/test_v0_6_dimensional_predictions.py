from __future__ import annotations

import ast
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pytest

from new_jerusalem_geometry.dimensional_predictions import (
    DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH,
    DEFAULT_PHASE6C_OUTPUT_RELATIVE_PATH,
    DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH,
    EXPECTED_PHASE6B_UNIT_MANIFEST_SHA256,
    EXPECTED_V0_5_GEOMETRY_SHA256,
    FROZEN_V0_5_GEOMETRY_COMMIT,
    SIDE_CLASS_TOLERANCE_U,
    build_frozen_dimensional_predictions,
    canonical_prediction_bytes,
    write_frozen_dimensional_predictions,
)
from new_jerusalem_geometry.michell_composite import (
    build_michell_composite,
)
from new_jerusalem_geometry.polar_pivot_wall import (
    POLAR_INDICES,
    POLAR_PIVOT_WALL_IDS,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

UNIT_MANIFEST = (
    ROOT
    / DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH
)

GEOMETRY_EXPORT = (
    ROOT
    / DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH
)

CANONICAL_OUTPUT = (
    ROOT
    / DEFAULT_PHASE6C_OUTPUT_RELATIVE_PATH
)

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "dimensional_predictions.py"
)

BANNED_GEOMETRIC_TARGET_LITERALS = (
    "3264",
    "3280",
    "3270",
    "36000",
    "120000000",
    "6336",
    "6300",
)

FORBIDDEN_KEY_FRAGMENTS = (
    "target",
    "residual",
    "error_percent",
    "percent_error",
    "historical_match",
    "tolerance_pass",
)

ALLOWED_TARGET_KEY = (
    "historical_targets_loaded"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _report() -> dict[str, object]:
    return build_frozen_dimensional_predictions(
        unit_manifest_path=UNIT_MANIFEST,
        geometry_export_path=GEOMETRY_EXPORT,
    )


def _prediction_value(
    report: dict[str, object],
    name: str,
) -> float:
    predictions = report[
        "dimensional_predictions"
    ]

    assert isinstance(
        predictions,
        dict,
    )

    row = predictions[
        name
    ]

    assert isinstance(
        row,
        dict,
    )

    value = row[
        "value"
    ]

    assert isinstance(
        value,
        float,
    )

    return value


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
    assert (
        _sha256(
            UNIT_MANIFEST
        )
        == EXPECTED_PHASE6B_UNIT_MANIFEST_SHA256
    )

    assert (
        _sha256(
            GEOMETRY_EXPORT
        )
        == EXPECTED_V0_5_GEOMETRY_SHA256
    )


def test_v0_5_geometry_commit_is_recorded() -> None:
    report = _report()

    frozen_inputs = report[
        "frozen_inputs"
    ]

    assert isinstance(
        frozen_inputs,
        dict,
    )

    assert (
        frozen_inputs[
            "v0_5_geometry_commit"
        ]
        == FROZEN_V0_5_GEOMETRY_COMMIT
        == "c3a051f197ef98389605c9e19e3bc83b42ad779c"
    )


def test_scale_derives_exactly_as_7920_over_11() -> None:
    report = _report()

    scale = report[
        "scale_derivation"
    ]

    assert isinstance(
        scale,
        dict,
    )

    linear = scale[
        "current_foot_per_normalized_unit"
    ]

    area = scale[
        "square_current_foot_per_normalized_unit_squared"
    ]

    assert isinstance(
        linear,
        dict,
    )

    assert isinstance(
        area,
        dict,
    )

    assert Fraction(
        linear[
            "numerator"
        ],
        linear[
            "denominator"
        ],
    ) == Fraction(
        7920,
        11,
    ) == Fraction(
        720,
        1,
    )

    assert Fraction(
        area[
            "numerator"
        ],
        area[
            "denominator"
        ],
    ) == Fraction(
        720 * 720,
        1,
    )


def test_wall_structure_is_exactly_registered() -> None:
    composite = build_michell_composite(
        unit=1.0
    )

    wall = composite.wall_reconstruction

    assert len(
        wall.lines
    ) == 12

    assert len(
        wall.vertices
    ) == 12

    assert tuple(
        line.name
        for line in wall.lines
    ) == POLAR_PIVOT_WALL_IDS

    assert len(
        POLAR_INDICES
    ) == 4

    assert len(
        set(
            range(
                12
            )
        )
        - POLAR_INDICES
    ) == 8


def test_side_classes_are_semantic_not_length_selected() -> None:
    assert POLAR_INDICES == frozenset(
        {
            0,
            3,
            6,
            9,
        }
    )

    polar_names = tuple(
        POLAR_PIVOT_WALL_IDS[
            index
        ]
        for index in sorted(
            POLAR_INDICES
        )
    )

    assert polar_names == (
        "wall_east",
        "wall_north",
        "wall_west",
        "wall_south",
    )


def test_four_polar_side_lengths_agree() -> None:
    wall = build_michell_composite(
        unit=1.0
    ).wall_reconstruction

    values = tuple(
        wall.side_lengths[
            index
        ]
        for index in sorted(
            POLAR_INDICES
        )
    )

    assert (
        max(
            values
        )
        - min(
            values
        )
        <= SIDE_CLASS_TOLERANCE_U
    )


def test_eight_oblique_side_lengths_agree() -> None:
    wall = build_michell_composite(
        unit=1.0
    ).wall_reconstruction

    values = tuple(
        wall.side_lengths[
            index
        ]
        for index in range(
            12
        )
        if index not in POLAR_INDICES
    )

    assert len(
        values
    ) == 8

    assert (
        max(
            values
        )
        - min(
            values
        )
        <= SIDE_CLASS_TOLERANCE_U
    )


def test_mean_and_perimeter_use_all_twelve_sides() -> None:
    report = _report()

    wall = build_michell_composite(
        unit=1.0
    ).wall_reconstruction

    normalized = report[
        "normalized_geometry"
    ]

    assert isinstance(
        normalized,
        dict,
    )

    expected_perimeter = sum(
        wall.side_lengths
    )

    expected_mean = (
        expected_perimeter
        / 12
    )

    assert normalized[
        "wall_perimeter_u"
    ] == pytest.approx(
        expected_perimeter,
        abs=1.0e-14,
    )

    assert normalized[
        "mean_side_u"
    ] == pytest.approx(
        expected_mean,
        abs=1.0e-14,
    )


def test_area_comes_from_frozen_wall_polygon() -> None:
    report = _report()

    wall = build_michell_composite(
        unit=1.0
    ).wall_reconstruction

    normalized = report[
        "normalized_geometry"
    ]

    assert isinstance(
        normalized,
        dict,
    )

    assert normalized[
        "wall_area_u2"
    ] == pytest.approx(
        wall.area,
        abs=1.0e-13,
    )


def test_exactly_seven_dimensional_predictions_are_emitted() -> None:
    report = _report()

    predictions = report[
        "dimensional_predictions"
    ]

    assert isinstance(
        predictions,
        dict,
    )

    assert tuple(
        predictions
    ) == (
        "polar_side_current_foot",
        "oblique_side_current_foot",
        "mean_side_current_foot",
        "wall_perimeter_current_foot",
        "wall_perimeter_megalithic_yard",
        "wall_perimeter_old_english_foot",
        "wall_area_square_foot",
    )


def test_current_foot_predictions_use_derived_720_scale() -> None:
    report = _report()

    normalized = report[
        "normalized_geometry"
    ]

    assert isinstance(
        normalized,
        dict,
    )

    assert _prediction_value(
        report,
        "polar_side_current_foot",
    ) == pytest.approx(
        normalized[
            "polar_side_u"
        ]
        * 720.0,
        abs=1.0e-10,
    )

    assert _prediction_value(
        report,
        "oblique_side_current_foot",
    ) == pytest.approx(
        normalized[
            "oblique_side_u"
        ]
        * 720.0,
        abs=1.0e-10,
    )

    assert _prediction_value(
        report,
        "mean_side_current_foot",
    ) == pytest.approx(
        normalized[
            "mean_side_u"
        ]
        * 720.0,
        abs=1.0e-10,
    )

    assert _prediction_value(
        report,
        "wall_perimeter_current_foot",
    ) == pytest.approx(
        normalized[
            "wall_perimeter_u"
        ]
        * 720.0,
        abs=1.0e-9,
    )

    assert _prediction_value(
        report,
        "wall_area_square_foot",
    ) == pytest.approx(
        normalized[
            "wall_area_u2"
        ]
        * 720.0
        * 720.0,
        abs=1.0e-6,
    )


def test_megalithic_yard_conversion_uses_phase6b() -> None:
    report = _report()

    perimeter_foot = _prediction_value(
        report,
        "wall_perimeter_current_foot",
    )

    perimeter_my = _prediction_value(
        report,
        "wall_perimeter_megalithic_yard",
    )

    assert perimeter_my == pytest.approx(
        perimeter_foot
        / (
            68.0
            / 25.0
        ),
        abs=1.0e-10,
    )

    row = report[
        "dimensional_predictions"
    ][
        "wall_perimeter_megalithic_yard"
    ]

    assert row[
        "conversion_source_record_id"
    ] == "UNIT-001"


def test_old_english_conversion_uses_phase6b() -> None:
    report = _report()

    perimeter_foot = _prediction_value(
        report,
        "wall_perimeter_current_foot",
    )

    perimeter_old = _prediction_value(
        report,
        "wall_perimeter_old_english_foot",
    )

    assert perimeter_old == pytest.approx(
        perimeter_foot
        * 11.0
        / 12.0,
        abs=1.0e-10,
    )

    row = report[
        "dimensional_predictions"
    ][
        "wall_perimeter_old_english_foot"
    ]

    assert row[
        "conversion_source_record_id"
    ] == "SOMM-006"


def test_predictor_source_contains_no_geometric_target_literals() -> None:
    text = MODULE.read_text(
        encoding="utf-8"
    )

    for literal in BANNED_GEOMETRIC_TARGET_LITERALS:
        assert literal not in text


def test_predictor_does_not_import_or_load_phase6a_registry() -> None:
    text = MODULE.read_text(
        encoding="utf-8"
    )

    assert "v0.6_metrology_registry.csv" not in text
    assert "load_metrology_registry" not in text
    assert "select_unit_parameter_records" not in text

    tree = ast.parse(
        text
    )

    imported_modules = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            imported_modules.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imported_modules.append(
                node.module
                or ""
            )

    assert not any(
        module == "csv"
        or module.endswith(
            ".csv"
        )
        for module in imported_modules
    )


def test_blind_boundary_is_explicit() -> None:
    report = _report()

    blind = report[
        "blind_boundary"
    ]

    assert isinstance(
        blind,
        dict,
    )

    assert (
        blind[
            "historical_targets_loaded"
        ]
        is False
    )

    assert (
        blind[
            "comparison_metrics_calculated"
        ]
        is False
    )

    assert (
        "residuals were not calculated"
        in blind[
            "scope_statement"
        ]
    )


def test_artifact_keys_contain_no_comparison_metric_fields() -> None:
    report = _report()

    for key in _walk_keys(
        report
    ):
        if key == ALLOWED_TARGET_KEY:
            continue

        lowered = key.lower()

        for fragment in FORBIDDEN_KEY_FRAGMENTS:
            assert fragment not in lowered, (
                key,
                fragment,
            )


def test_artifact_contains_no_absolute_home_path() -> None:
    text = canonical_prediction_bytes(
        _report()
    ).decode(
        "utf-8"
    )

    assert "/home/" not in text
    assert "/Users/" not in text


def test_prediction_serialization_is_deterministic() -> None:
    first = canonical_prediction_bytes(
        _report()
    )

    second = canonical_prediction_bytes(
        _report()
    )

    assert first == second


def test_tracked_prediction_matches_regeneration(
    tmp_path: Path,
) -> None:
    generated = (
        tmp_path
        / "frozen_dimensional_predictions.json"
    )

    generated_bytes = (
        write_frozen_dimensional_predictions(
            unit_manifest_path=UNIT_MANIFEST,
            geometry_export_path=GEOMETRY_EXPORT,
            output_path=generated,
        )
    )

    assert (
        generated.read_bytes()
        == generated_bytes
    )

    if CANONICAL_OUTPUT.exists():
        assert (
            CANONICAL_OUTPUT.read_bytes()
            == generated_bytes
        )


def test_prediction_artifact_is_valid_json() -> None:
    parsed = json.loads(
        canonical_prediction_bytes(
            _report()
        )
    )

    assert parsed[
        "phase"
    ] == "6C"
