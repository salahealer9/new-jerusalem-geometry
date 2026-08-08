"""Frozen dimensional predictions for the v0.6 historical-metrology audit.

The predictor combines the signed v0.5 NJG_MICHELL geometry with the frozen
Phase 6B unit manifest.

Historical comparison values are not loaded here. This module produces
dimensional predictions only.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Mapping

from .michell_composite import (
    build_michell_composite,
)
from .polar_pivot_wall import (
    POLAR_INDICES,
    POLAR_PIVOT_WALL_IDS,
)


FROZEN_V0_5_GEOMETRY_COMMIT = (
    "c3a051f197ef98389605c9e19e3bc83b42ad779c"
)

EXPECTED_V0_5_GEOMETRY_SHA256 = (
    "19e22356378d581a2adb35c8f8b8ee02"
    "37f61ab365d8cbc05abc378568e3b6cb"
)

EXPECTED_PHASE6B_UNIT_MANIFEST_SHA256 = (
    "cdd009dd0ea8e398d51ad3c9d3285741"
    "e207f18b45030a177cbf01d3bf0329c3"
)

DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH = Path(
    "data/geometry/njg_michell_v0_5/"
    "njg_michell_geometry.json"
)

DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "unit_system.json"
)

DEFAULT_PHASE6C_OUTPUT_RELATIVE_PATH = Path(
    "data/metrology/njg_michell_v0_6/"
    "frozen_dimensional_predictions.json"
)

SOURCE_EARTH_SQUARE_MILES = Fraction(
    7920,
    1,
)

SIDE_CLASS_TOLERANCE_U = 1.0e-12


def sha256_file(
    path: Path,
) -> str:
    """Return SHA-256 for one frozen input artifact."""
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _fraction_payload(
    value: Fraction,
) -> dict[str, int | str]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": format(
            float(
                value
            ),
            ".15g",
        ),
    }


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
            "Exact unit factor lacks integer numerator."
        )

    if not isinstance(
        denominator,
        int,
    ):
        raise ValueError(
            "Exact unit factor lacks integer denominator."
        )

    return Fraction(
        numerator,
        denominator,
    )


def load_phase6b_unit_manifest(
    path: Path,
) -> dict[str, object]:
    """Load and verify the frozen Phase 6B manifest."""
    actual_hash = sha256_file(
        path
    )

    if (
        actual_hash
        != EXPECTED_PHASE6B_UNIT_MANIFEST_SHA256
    ):
        raise ValueError(
            "Phase 6B unit manifest hash does not match "
            "the frozen prediction input."
        )

    payload = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    if payload.get(
        "phase"
    ) != "6B":
        raise ValueError(
            "Unexpected unit-manifest phase."
        )

    return payload


def verify_v0_5_geometry_export(
    path: Path,
) -> str:
    """Verify and return the frozen v0.5 geometry-export hash."""
    actual_hash = sha256_file(
        path
    )

    if (
        actual_hash
        != EXPECTED_V0_5_GEOMETRY_SHA256
    ):
        raise ValueError(
            "v0.5 geometry export hash does not match "
            "the frozen prediction input."
        )

    return actual_hash


def _linear_unit_record(
    manifest: Mapping[str, object],
    unit: str,
) -> Mapping[str, object]:
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

    matches = [
        row
        for row in rows
        if isinstance(
            row,
            dict,
        )
        and row.get(
            "unit"
        )
        == unit
    ]

    if len(
        matches
    ) != 1:
        raise ValueError(
            f"Expected one Phase 6B definition for {unit!r}."
        )

    return matches[
        0
    ]


def _linear_factor_to_current_foot(
    manifest: Mapping[str, object],
    unit: str,
) -> Fraction:
    row = _linear_unit_record(
        manifest,
        unit,
    )

    factor = row.get(
        "to_current_foot"
    )

    if not isinstance(
        factor,
        dict,
    ):
        raise ValueError(
            f"Unit {unit!r} lacks exact current-foot factor."
        )

    return _fraction_from_payload(
        factor
    )


def _unit_source_record_id(
    manifest: Mapping[str, object],
    unit: str,
) -> str | None:
    row = _linear_unit_record(
        manifest,
        unit,
    )

    source_record_id = row.get(
        "source_record_id"
    )

    if (
        source_record_id is not None
        and not isinstance(
            source_record_id,
            str,
        )
    ):
        raise ValueError(
            f"Invalid source record ID for {unit!r}."
        )

    return source_record_id


def _model_scale_factor(
    manifest: Mapping[str, object],
) -> Fraction:
    model_scale = manifest.get(
        "model_scale"
    )

    if not isinstance(
        model_scale,
        dict,
    ):
        raise ValueError(
            "Phase 6B manifest lacks model_scale."
        )

    if (
        model_scale.get(
            "source_record_id"
        )
        != "SCALE-001"
    ):
        raise ValueError(
            "Unexpected model-scale source record."
        )

    if (
        model_scale.get(
            "source_unit"
        )
        != "source_mile"
    ):
        raise ValueError(
            "Unexpected model-scale source unit."
        )

    if (
        model_scale.get(
            "model_unit"
        )
        != "model_foot"
    ):
        raise ValueError(
            "Unexpected model-scale model unit."
        )

    if (
        model_scale.get(
            "physical_unit_conversion"
        )
        is not False
    ):
        raise ValueError(
            "Model scale must remain distinct from "
            "physical unit conversion."
        )

    factor = model_scale.get(
        "numeric_factor"
    )

    if not isinstance(
        factor,
        dict,
    ):
        raise ValueError(
            "Model scale lacks exact numeric factor."
        )

    return _fraction_from_payload(
        factor
    )


def _multiply_float_by_fraction(
    value: float,
    factor: Fraction,
) -> float:
    return (
        value
        * factor.numerator
        / factor.denominator
    )


def _divide_float_by_fraction(
    value: float,
    factor: Fraction,
) -> float:
    return (
        value
        * factor.denominator
        / factor.numerator
    )


def _class_spread(
    values: tuple[float, ...],
) -> float:
    return (
        max(
            values
        )
        - min(
            values
        )
    )


def build_frozen_dimensional_predictions(
    *,
    unit_manifest_path: Path,
    geometry_export_path: Path,
) -> dict[str, object]:
    """Build the seven preregistered Phase 6C dimensional predictions."""
    geometry_sha256 = verify_v0_5_geometry_export(
        geometry_export_path
    )

    unit_manifest = load_phase6b_unit_manifest(
        unit_manifest_path
    )

    composite = build_michell_composite(
        unit=1.0
    )

    wall = composite.wall_reconstruction

    if len(
        wall.lines
    ) != 12:
        raise ValueError(
            "Frozen wall must contain exactly twelve sides."
        )

    if len(
        wall.vertices
    ) != 12:
        raise ValueError(
            "Frozen wall must contain exactly twelve vertices."
        )

    line_names = tuple(
        line.name
        for line in wall.lines
    )

    if (
        line_names
        != POLAR_PIVOT_WALL_IDS
    ):
        raise ValueError(
            "Frozen semantic wall ordering has changed."
        )

    polar_indices = tuple(
        sorted(
            POLAR_INDICES
        )
    )

    oblique_indices = tuple(
        index
        for index in range(
            len(
                wall.lines
            )
        )
        if index not in POLAR_INDICES
    )

    if len(
        polar_indices
    ) != 4:
        raise ValueError(
            "Expected exactly four semantic polar sides."
        )

    if len(
        oblique_indices
    ) != 8:
        raise ValueError(
            "Expected exactly eight semantic oblique sides."
        )

    side_lengths = tuple(
        wall.side_lengths
    )

    polar_lengths = tuple(
        side_lengths[
            index
        ]
        for index in polar_indices
    )

    oblique_lengths = tuple(
        side_lengths[
            index
        ]
        for index in oblique_indices
    )

    polar_spread = _class_spread(
        polar_lengths
    )

    oblique_spread = _class_spread(
        oblique_lengths
    )

    if (
        polar_spread
        > SIDE_CLASS_TOLERANCE_U
    ):
        raise ValueError(
            "Frozen polar-side class no longer agrees "
            "within preregistered tolerance."
        )

    if (
        oblique_spread
        > SIDE_CLASS_TOLERANCE_U
    ):
        raise ValueError(
            "Frozen oblique-side class no longer agrees "
            "within preregistered tolerance."
        )

    polar_side_u = polar_lengths[
        0
    ]

    oblique_side_u = oblique_lengths[
        0
    ]

    perimeter_u = sum(
        side_lengths
    )

    mean_side_u = (
        perimeter_u
        / len(
            side_lengths
        )
    )

    area_u2 = wall.area

    earth_square_u = Fraction(
        str(
            composite.core.earth_square.side
        )
    )

    model_scale_factor = _model_scale_factor(
        unit_manifest
    )

    earth_square_model_foot = (
        SOURCE_EARTH_SQUARE_MILES
        * model_scale_factor
    )

    linear_scale = (
        earth_square_model_foot
        / earth_square_u
    )

    area_scale = (
        linear_scale
        * linear_scale
    )

    if (
        linear_scale
        != Fraction(
            720,
            1,
        )
    ):
        raise ValueError(
            "Derived dimensional scale is not 720."
        )

    if (
        area_scale
        != Fraction(
            518400,
            1,
        )
    ):
        raise ValueError(
            "Derived area scale is not 720 squared."
        )

    megalithic_yard_factor = (
        _linear_factor_to_current_foot(
            unit_manifest,
            "megalithic_yard",
        )
    )

    old_english_foot_factor = (
        _linear_factor_to_current_foot(
            unit_manifest,
            "old_english_foot",
        )
    )

    if (
        _unit_source_record_id(
            unit_manifest,
            "megalithic_yard",
        )
        != "UNIT-001"
    ):
        raise ValueError(
            "Unexpected Megalithic-Yard source record."
        )

    if (
        _unit_source_record_id(
            unit_manifest,
            "old_english_foot",
        )
        != "SOMM-006"
    ):
        raise ValueError(
            "Unexpected old-English-foot source record."
        )

    polar_side_current_foot = (
        _multiply_float_by_fraction(
            polar_side_u,
            linear_scale,
        )
    )

    oblique_side_current_foot = (
        _multiply_float_by_fraction(
            oblique_side_u,
            linear_scale,
        )
    )

    mean_side_current_foot = (
        _multiply_float_by_fraction(
            mean_side_u,
            linear_scale,
        )
    )

    wall_perimeter_current_foot = (
        _multiply_float_by_fraction(
            perimeter_u,
            linear_scale,
        )
    )

    wall_perimeter_megalithic_yard = (
        _divide_float_by_fraction(
            wall_perimeter_current_foot,
            megalithic_yard_factor,
        )
    )

    wall_perimeter_old_english_foot = (
        _divide_float_by_fraction(
            wall_perimeter_current_foot,
            old_english_foot_factor,
        )
    )

    wall_area_square_foot = (
        _multiply_float_by_fraction(
            area_u2,
            area_scale,
        )
    )

    return {
        "schema_version": 1,
        "phase": "6C",
        "analysis_id": (
            "njg-michell-v0-6-frozen-dimensional-predictions-v1"
        ),
        "frozen_inputs": {
            "v0_5_geometry_commit": (
                FROZEN_V0_5_GEOMETRY_COMMIT
            ),
            "v0_5_geometry_export": {
                "path": str(
                    DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH
                ),
                "sha256": geometry_sha256,
            },
            "phase6b_unit_manifest": {
                "path": str(
                    DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH
                ),
                "sha256": (
                    EXPECTED_PHASE6B_UNIT_MANIFEST_SHA256
                ),
            },
        },
        "scale_derivation": {
            "source_earth_square_miles": (
                _fraction_payload(
                    SOURCE_EARTH_SQUARE_MILES
                )
            ),
            "model_scale_source_record_id": "SCALE-001",
            "model_scale_numeric_factor": (
                _fraction_payload(
                    model_scale_factor
                )
            ),
            "earth_square_normalized_units": (
                _fraction_payload(
                    earth_square_u
                )
            ),
            "current_foot_per_normalized_unit": (
                _fraction_payload(
                    linear_scale
                )
            ),
            "square_current_foot_per_normalized_unit_squared": (
                _fraction_payload(
                    area_scale
                )
            ),
            "free_wall_scale_parameter": False,
        },
        "wall_structure": {
            "wall_model": "POLAR_PIVOT_TANGENT",
            "side_count": len(
                wall.lines
            ),
            "vertex_count": len(
                wall.vertices
            ),
            "polar_side_count": len(
                polar_indices
            ),
            "oblique_side_count": len(
                oblique_indices
            ),
            "semantic_wall_ids": list(
                line_names
            ),
            "polar_indices": list(
                polar_indices
            ),
            "oblique_indices": list(
                oblique_indices
            ),
            "class_tolerance_u": (
                SIDE_CLASS_TOLERANCE_U
            ),
            "polar_class_spread_u": (
                polar_spread
            ),
            "oblique_class_spread_u": (
                oblique_spread
            ),
        },
        "normalized_geometry": {
            "polar_side_u": (
                polar_side_u
            ),
            "oblique_side_u": (
                oblique_side_u
            ),
            "mean_side_u": (
                mean_side_u
            ),
            "wall_perimeter_u": (
                perimeter_u
            ),
            "wall_area_u2": (
                area_u2
            ),
        },
        "dimensional_predictions": {
            "polar_side_current_foot": {
                "value": (
                    polar_side_current_foot
                ),
                "unit": "current_foot",
            },
            "oblique_side_current_foot": {
                "value": (
                    oblique_side_current_foot
                ),
                "unit": "current_foot",
            },
            "mean_side_current_foot": {
                "value": (
                    mean_side_current_foot
                ),
                "unit": "current_foot",
            },
            "wall_perimeter_current_foot": {
                "value": (
                    wall_perimeter_current_foot
                ),
                "unit": "current_foot",
            },
            "wall_perimeter_megalithic_yard": {
                "value": (
                    wall_perimeter_megalithic_yard
                ),
                "unit": "megalithic_yard",
                "conversion_source_record_id": (
                    "UNIT-001"
                ),
            },
            "wall_perimeter_old_english_foot": {
                "value": (
                    wall_perimeter_old_english_foot
                ),
                "unit": "old_english_foot",
                "conversion_source_record_id": (
                    "SOMM-006"
                ),
            },
            "wall_area_square_foot": {
                "value": (
                    wall_area_square_foot
                ),
                "unit": "square_current_foot",
            },
        },
        "blind_boundary": {
            "historical_targets_loaded": False,
            "comparison_metrics_calculated": False,
            "scope_statement": (
                "Historical targets were not loaded and "
                "residuals were not calculated."
            ),
        },
    }


def canonical_prediction_bytes(
    payload: Mapping[str, object],
) -> bytes:
    """Serialize Phase 6C output deterministically."""
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


def write_frozen_dimensional_predictions(
    *,
    unit_manifest_path: Path,
    geometry_export_path: Path,
    output_path: Path,
) -> bytes:
    """Generate and write the canonical Phase 6C artifact."""
    payload = build_frozen_dimensional_predictions(
        unit_manifest_path=unit_manifest_path,
        geometry_export_path=geometry_export_path,
    )

    encoded = canonical_prediction_bytes(
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
