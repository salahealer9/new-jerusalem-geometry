"""Formal source-defined metrology for the v0.6 audit.

This module implements only the unit conventions preregistered for Phase 6B.
It does not contain historical wall/decagon target values and performs no
geometric residual analysis.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction
from math import pi
from pathlib import Path
from typing import Iterable, Mapping, Sequence


EXPECTED_REGISTRY_SHA256 = (
    "8c534ddc1a6fe6f2b233b4352202d753"
    "8a5379787bc4313a3759916f8b150f5e"
)

DEFAULT_REGISTRY_RELATIVE_PATH = Path(
    "docs/sources/v0.6_metrology_registry.csv"
)

ALLOWED_UNIT_RECORD_IDS = (
    "SCALE-001",
    "UNIT-001",
    "UNIT-002",
    "UNIT-003",
    "UNIT-004",
    "SOMM-006",
)

MICHELL_PI_22_OVER_7 = Fraction(
    22,
    7,
)


@dataclass(frozen=True)
class UnitDefinition:
    """One exact linear conversion into the canonical current-foot base."""

    unit: str
    to_current_foot: Fraction
    source_record_id: str | None
    provenance_class: str


@dataclass(frozen=True)
class ModelScale:
    """Separate numeric mapping for the source-mile/model-foot correspondence."""

    source_record_id: str
    source_unit: str
    model_unit: str
    source_to_model_numeric_factor: Fraction


@dataclass(frozen=True)
class UnitSystem:
    """Exact Phase 6B unit system."""

    definitions: tuple[UnitDefinition, ...]
    model_scale: ModelScale

    def definition_map(
        self,
    ) -> dict[str, UnitDefinition]:
        return {
            definition.unit: definition
            for definition in self.definitions
        }

    def linear_factor(
        self,
        unit: str,
    ) -> Fraction:
        """Return exact current-foot length represented by one unit."""
        definitions = self.definition_map()

        try:
            return definitions[
                unit
            ].to_current_foot
        except KeyError as exc:
            raise KeyError(
                f"Unknown Phase 6B linear unit: {unit!r}"
            ) from exc

    def convert_linear(
        self,
        value: int | Fraction,
        *,
        from_unit: str,
        to_unit: str,
    ) -> Fraction:
        """Convert an exact linear value between registered units."""
        quantity = Fraction(
            value
        )

        return (
            quantity
            * self.linear_factor(
                from_unit
            )
            / self.linear_factor(
                to_unit
            )
        )

    def convert_area(
        self,
        value: int | Fraction,
        *,
        from_linear_unit: str,
        to_linear_unit: str,
    ) -> Fraction:
        """Convert area by the square of the corresponding linear factor."""
        quantity = Fraction(
            value
        )

        ratio = (
            self.linear_factor(
                from_linear_unit
            )
            / self.linear_factor(
                to_linear_unit
            )
        )

        return (
            quantity
            * ratio
            * ratio
        )

    def source_miles_to_model_feet(
        self,
        value: int | Fraction,
    ) -> Fraction:
        """Apply the source-mile -> model-foot numeric scale mapping."""
        return (
            Fraction(
                value
            )
            * self.model_scale.source_to_model_numeric_factor
        )

    def model_feet_to_source_miles(
        self,
        value: int | Fraction,
    ) -> Fraction:
        """Invert the model-foot -> source-mile numeric scale mapping."""
        return (
            Fraction(
                value
            )
            / self.model_scale.source_to_model_numeric_factor
        )


def fraction_from_decimal_text(
    text: str,
) -> Fraction:
    """Convert a finite decimal/integer source string exactly."""
    return Fraction(
        text.strip()
    )


def sha256_file(
    path: Path,
) -> str:
    """Return the SHA-256 hash of a file."""
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def load_metrology_registry(
    path: Path,
) -> tuple[dict[str, str], ...]:
    """Load the frozen Phase 6A CSV registry."""
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

    if not rows:
        raise ValueError(
            "Metrology registry is empty."
        )

    record_ids = [
        row[
            "record_id"
        ]
        for row in rows
    ]

    if len(
        record_ids
    ) != len(
        set(
            record_ids
        )
    ):
        raise ValueError(
            "Metrology registry contains duplicate record IDs."
        )

    return rows


def select_unit_parameter_records(
    rows: Iterable[Mapping[str, str]],
) -> tuple[dict[str, str], ...]:
    """Extract exactly the six preregistered Phase 6B parameter records."""
    by_id = {
        row[
            "record_id"
        ]: dict(
            row
        )
        for row in rows
    }

    missing = [
        record_id
        for record_id in ALLOWED_UNIT_RECORD_IDS
        if record_id not in by_id
    ]

    if missing:
        raise ValueError(
            "Missing Phase 6B source records: "
            + ", ".join(
                missing
            )
        )

    selected = tuple(
        by_id[
            record_id
        ]
        for record_id in ALLOWED_UNIT_RECORD_IDS
    )

    for row in selected:
        if row[
            "record_type"
        ] != "unit_definition":
            raise ValueError(
                "Phase 6B parameter is not a unit definition: "
                f"{row['record_id']}"
            )

        if row[
            "prediction_status"
        ] == "development_used_target":
            raise ValueError(
                "Development-used target cannot parameterize "
                "the Phase 6B unit system: "
                f"{row['record_id']}"
            )

        if row[
            "prediction_status"
        ] != "unit_definition":
            raise ValueError(
                "Phase 6B parameter does not carry unit_definition "
                "prediction status: "
                f"{row['record_id']}"
            )

    return selected


def _require_exact_record_set(
    records: Sequence[Mapping[str, str]],
) -> dict[str, Mapping[str, str]]:
    record_ids = tuple(
        row[
            "record_id"
        ]
        for row in records
    )

    if set(
        record_ids
    ) != set(
        ALLOWED_UNIT_RECORD_IDS
    ):
        raise ValueError(
            "Unit-system builder requires exactly the frozen "
            "Phase 6B source-record set."
        )

    if len(
        record_ids
    ) != len(
        ALLOWED_UNIT_RECORD_IDS
    ):
        raise ValueError(
            "Unit-system builder received duplicate or extra records."
        )

    for row in records:
        if row[
            "prediction_status"
        ] == "development_used_target":
            raise ValueError(
                "Development-used target cannot parameterize "
                "the Phase 6B unit system."
            )

    return {
        row[
            "record_id"
        ]: row
        for row in records
    }


def _require_relation_fields(
    row: Mapping[str, str],
    *,
    source_value: str,
    source_unit: str,
    secondary_value: str,
    secondary_unit: str,
) -> None:
    actual = (
        row[
            "source_value"
        ],
        row[
            "source_unit"
        ],
        row[
            "secondary_value"
        ],
        row[
            "secondary_unit"
        ],
    )

    expected = (
        source_value,
        source_unit,
        secondary_value,
        secondary_unit,
    )

    if actual != expected:
        raise ValueError(
            "Frozen source relation does not match Phase 6B protocol: "
            f"{row['record_id']}: {actual!r} != {expected!r}"
        )


def build_unit_system(
    records: Sequence[Mapping[str, str]],
) -> UnitSystem:
    """Build the exact unit system from the six preregistered records."""
    by_id = _require_exact_record_set(
        records
    )

    scale = by_id[
        "SCALE-001"
    ]
    _require_relation_fields(
        scale,
        source_value="1",
        source_unit="foot",
        secondary_value="1",
        secondary_unit="mile",
    )

    megalithic = by_id[
        "UNIT-001"
    ]
    _require_relation_fields(
        megalithic,
        source_value="2.72",
        source_unit="foot",
        secondary_value="1",
        secondary_unit="megalithic_yard",
    )
    megalithic_factor = fraction_from_decimal_text(
        megalithic[
            "source_value"
        ]
    )

    sumerian = by_id[
        "UNIT-002"
    ]
    _require_relation_fields(
        sumerian,
        source_value="13.2",
        source_unit="inch",
        secondary_value="1.1",
        secondary_unit="foot",
    )

    sumerian_from_inches = (
        fraction_from_decimal_text(
            sumerian[
                "source_value"
            ]
        )
        / 12
    )

    sumerian_from_feet = fraction_from_decimal_text(
        sumerian[
            "secondary_value"
        ]
    )

    if (
        sumerian_from_inches
        != sumerian_from_feet
    ):
        raise ValueError(
            "The two registered Sumerian-foot expressions do not close."
        )

    stadion = by_id[
        "UNIT-003"
    ]
    _require_relation_fields(
        stadion,
        source_value="600",
        source_unit="sumerian_foot",
        secondary_value="660",
        secondary_unit="foot",
    )

    stadion_from_sumerian = (
        fraction_from_decimal_text(
            stadion[
                "source_value"
            ]
        )
        * sumerian_from_feet
    )

    stadion_from_feet = fraction_from_decimal_text(
        stadion[
            "secondary_value"
        ]
    )

    if (
        stadion_from_sumerian
        != stadion_from_feet
    ):
        raise ValueError(
            "The registered stadion relation does not close."
        )

    cubit = by_id[
        "UNIT-004"
    ]
    _require_relation_fields(
        cubit,
        source_value="1.728",
        source_unit="foot",
        secondary_value="1",
        secondary_unit="cubit",
    )
    cubit_factor = fraction_from_decimal_text(
        cubit[
            "source_value"
        ]
    )

    old_english = by_id[
        "SOMM-006"
    ]
    _require_relation_fields(
        old_english,
        source_value="12",
        source_unit="old_english_foot",
        secondary_value="11",
        secondary_unit="current_foot",
    )

    old_english_factor = (
        fraction_from_decimal_text(
            old_english[
                "source_value"
            ]
        )
        / fraction_from_decimal_text(
            old_english[
                "secondary_value"
            ]
        )
    )

    definitions = (
        UnitDefinition(
            unit="current_foot",
            to_current_foot=Fraction(
                1,
                1,
            ),
            source_record_id=None,
            provenance_class="implementation_base",
        ),
        UnitDefinition(
            unit="foot",
            to_current_foot=Fraction(
                1,
                1,
            ),
            source_record_id=None,
            provenance_class="registry_label_alias",
        ),
        UnitDefinition(
            unit="inch",
            to_current_foot=Fraction(
                1,
                12,
            ),
            source_record_id=None,
            provenance_class="standard_identity",
        ),
        UnitDefinition(
            unit="megalithic_yard",
            to_current_foot=megalithic_factor,
            source_record_id="UNIT-001",
            provenance_class=megalithic[
                "attribution_class"
            ],
        ),
        UnitDefinition(
            unit="sumerian_foot",
            to_current_foot=sumerian_from_feet,
            source_record_id="UNIT-002",
            provenance_class=sumerian[
                "attribution_class"
            ],
        ),
        UnitDefinition(
            unit="new_jerusalem_stadion",
            to_current_foot=stadion_from_feet,
            source_record_id="UNIT-003",
            provenance_class=stadion[
                "attribution_class"
            ],
        ),
        UnitDefinition(
            unit="furlong",
            to_current_foot=stadion_from_feet,
            source_record_id="UNIT-003",
            provenance_class=stadion[
                "attribution_class"
            ],
        ),
        UnitDefinition(
            unit="new_jerusalem_cubit",
            to_current_foot=cubit_factor,
            source_record_id="UNIT-004",
            provenance_class=cubit[
                "attribution_class"
            ],
        ),
        UnitDefinition(
            unit="old_english_foot",
            to_current_foot=old_english_factor,
            source_record_id="SOMM-006",
            provenance_class=old_english[
                "attribution_class"
            ],
        ),
    )

    model_scale = ModelScale(
        source_record_id="SCALE-001",
        source_unit="source_mile",
        model_unit="model_foot",
        source_to_model_numeric_factor=Fraction(
            1,
            1,
        ),
    )

    return UnitSystem(
        definitions=definitions,
        model_scale=model_scale,
    )


def circumference_22_over_7(
    radius: int | Fraction,
) -> Fraction:
    """Return exact conventional circumference under pi = 22/7."""
    return (
        2
        * MICHELL_PI_22_OVER_7
        * Fraction(
            radius
        )
    )


def circumference_euclidean(
    radius: float,
) -> float:
    """Return Euclidean circumference using runtime mathematical pi."""
    return (
        2.0
        * pi
        * float(
            radius
        )
    )


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


def build_unit_manifest(
    *,
    registry_path: Path,
) -> dict[str, object]:
    """Build the deterministic Phase 6B machine-readable manifest."""
    registry_sha256 = sha256_file(
        registry_path
    )

    if (
        registry_sha256
        != EXPECTED_REGISTRY_SHA256
    ):
        raise ValueError(
            "Phase 6A registry hash does not match the frozen input."
        )

    rows = load_metrology_registry(
        registry_path
    )
    records = select_unit_parameter_records(
        rows
    )
    system = build_unit_system(
        records
    )

    return {
        "schema_version": 1,
        "phase": "6B",
        "purpose": "formal_source_defined_unit_system",
        "source_registry": {
            "path": str(
                DEFAULT_REGISTRY_RELATIVE_PATH
            ),
            "sha256": registry_sha256,
            "allowed_record_ids": list(
                ALLOWED_UNIT_RECORD_IDS
            ),
        },
        "canonical_linear_base": "current_foot",
        "linear_units": [
            {
                "unit": definition.unit,
                "to_current_foot": _fraction_payload(
                    definition.to_current_foot
                ),
                "source_record_id": definition.source_record_id,
                "provenance_class": definition.provenance_class,
            }
            for definition in system.definitions
        ],
        "model_scale": {
            "source_record_id": system.model_scale.source_record_id,
            "source_unit": system.model_scale.source_unit,
            "model_unit": system.model_scale.model_unit,
            "numeric_factor": _fraction_payload(
                system.model_scale.source_to_model_numeric_factor
            ),
            "physical_unit_conversion": False,
        },
        "pi_conventions": {
            "michell_22_over_7": {
                "exact_in_convention": True,
                "value": _fraction_payload(
                    MICHELL_PI_22_OVER_7
                ),
            },
            "euclidean": {
                "exact_in_convention": True,
                "implementation": "math.pi",
                "rationalized": False,
            },
        },
        "area_rule": {
            "method": "square_registered_linear_factor",
            "free_area_fit_parameter": False,
        },
        "target_leakage": {
            "geometric_target_records_used_as_parameters": [],
            "development_used_target_parameters": [],
        },
    }


def canonical_manifest_bytes(
    manifest: Mapping[str, object],
) -> bytes:
    """Serialize the unit manifest deterministically."""
    text = json.dumps(
        manifest,
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


def write_unit_manifest(
    *,
    registry_path: Path,
    output_path: Path,
) -> bytes:
    """Write and return canonical manifest bytes."""
    manifest = build_unit_manifest(
        registry_path=registry_path
    )
    payload = canonical_manifest_bytes(
        manifest
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_bytes(
        payload
    )

    return payload
