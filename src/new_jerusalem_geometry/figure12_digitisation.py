"""Source-plate observation schema for Michell's Figure 12.

The acquisition design deliberately separates:

- twelve registration landmarks with known core-model coordinates;
- seventy-two Moon-circumference samples with no assumed Moon model;
- thirty-six wall-line samples with no assumed wall model.

No transformation fitting, circle fitting, wall-line fitting, or candidate
model comparison is performed in this module.
"""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import Iterable, Sequence


SCHEMA_FIELDNAMES = (
    "sequence_index",
    "observation_id",
    "category",
    "object_id",
    "sample_index",
    "description",
    "model_x",
    "model_y",
    "registration_default",
)

PASS_FIELDNAMES = (
    "pass_id",
    "sequence_index",
    "observation_id",
    "category",
    "object_id",
    "sample_index",
    "description",
    "model_x",
    "model_y",
    "registration_default",
    "pixel_x",
    "pixel_y",
    "source_image",
    "source_image_sha256",
    "image_width_pixels",
    "image_height_pixels",
)


MOON_OBJECT_IDS = (
    "moon_north_west",
    "moon_north",
    "moon_north_east",
    "moon_east_north",
    "moon_east",
    "moon_east_south",
    "moon_south_east",
    "moon_south",
    "moon_south_west",
    "moon_west_south",
    "moon_west",
    "moon_west_north",
)

WALL_OBJECT_IDS = (
    "wall_north_west",
    "wall_north",
    "wall_north_east",
    "wall_east_north",
    "wall_east",
    "wall_east_south",
    "wall_south_east",
    "wall_south",
    "wall_south_west",
    "wall_west_south",
    "wall_west",
    "wall_west_north",
)


@dataclass(frozen=True, slots=True)
class Figure12Observation:
    """One fixed source-plate observation role."""

    sequence_index: int
    observation_id: str
    category: str
    object_id: str
    sample_index: int
    description: str
    model_x: float | None
    model_y: float | None
    registration_default: bool


@dataclass(frozen=True, slots=True)
class Figure12DigitisedObservation:
    """One completed source-plate observation."""

    pass_id: str
    definition: Figure12Observation
    pixel_x: float
    pixel_y: float
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int


def _append(
    observations: list[Figure12Observation],
    *,
    observation_id: str,
    category: str,
    object_id: str,
    sample_index: int,
    description: str,
    model_x: float | None = None,
    model_y: float | None = None,
    registration_default: bool = False,
) -> None:
    observations.append(
        Figure12Observation(
            sequence_index=len(observations),
            observation_id=observation_id,
            category=category,
            object_id=object_id,
            sample_index=sample_index,
            description=description,
            model_x=model_x,
            model_y=model_y,
            registration_default=registration_default,
        )
    )


def build_figure12_observation_schema() -> tuple[Figure12Observation, ...]:
    """Build the fixed 120-observation Figure 12 acquisition schema."""

    observations: list[Figure12Observation] = []

    half_side = 11.0 / 2.0
    junction_coordinate = sqrt(
        7.0 * 7.0
        - half_side * half_side
    )

    corners = (
        (
            "square_corner_top_left",
            -half_side,
            +half_side,
        ),
        (
            "square_corner_top_right",
            +half_side,
            +half_side,
        ),
        (
            "square_corner_bottom_right",
            +half_side,
            -half_side,
        ),
        (
            "square_corner_bottom_left",
            -half_side,
            -half_side,
        ),
    )

    for object_id, x, y in corners:
        _append(
            observations,
            observation_id=object_id,
            category="square_corner",
            object_id=object_id,
            sample_index=1,
            description=(
                "Earth-square corner: "
                + object_id.removeprefix(
                    "square_corner_"
                ).replace("_", " ")
            ),
            model_x=x,
            model_y=y,
            registration_default=True,
        )

    junctions = (
        (
            "junction_top_left",
            -junction_coordinate,
            +half_side,
        ),
        (
            "junction_top_right",
            +junction_coordinate,
            +half_side,
        ),
        (
            "junction_right_upper",
            +half_side,
            +junction_coordinate,
        ),
        (
            "junction_right_lower",
            +half_side,
            -junction_coordinate,
        ),
        (
            "junction_bottom_right",
            +junction_coordinate,
            -half_side,
        ),
        (
            "junction_bottom_left",
            -junction_coordinate,
            -half_side,
        ),
        (
            "junction_left_lower",
            -half_side,
            -junction_coordinate,
        ),
        (
            "junction_left_upper",
            -half_side,
            +junction_coordinate,
        ),
    )

    for object_id, x, y in junctions:
        _append(
            observations,
            observation_id=object_id,
            category="square_circle_junction",
            object_id=object_id,
            sample_index=1,
            description=(
                "Earth-square / construction-circle junction: "
                + object_id.removeprefix(
                    "junction_"
                ).replace("_", " ")
            ),
            model_x=x,
            model_y=y,
            registration_default=True,
        )

    for moon_id in MOON_OBJECT_IDS:
        readable = moon_id.removeprefix(
            "moon_"
        ).replace("_", " ")

        for sample_index in range(1, 7):
            _append(
                observations,
                observation_id=(
                    f"{moon_id}_arc_{sample_index:02d}"
                ),
                category="moon_circumference",
                object_id=moon_id,
                sample_index=sample_index,
                description=(
                    f"Visible circumference sample "
                    f"{sample_index}/6 for {readable} Moon."
                ),
            )

    for wall_id in WALL_OBJECT_IDS:
        readable = wall_id.removeprefix(
            "wall_"
        ).replace("_", " ")

        for sample_index in range(1, 4):
            _append(
                observations,
                observation_id=(
                    f"{wall_id}_line_{sample_index:02d}"
                ),
                category="wall_line",
                object_id=wall_id,
                sample_index=sample_index,
                description=(
                    f"Printed wall-line sample "
                    f"{sample_index}/3 for {readable} side."
                ),
            )

    schema = tuple(observations)
    validate_figure12_observation_schema(schema)
    return schema


def validate_figure12_observation_schema(
    schema: Sequence[Figure12Observation],
) -> None:
    """Validate the fixed acquisition design."""

    if len(schema) != 120:
        raise ValueError(
            f"Expected 120 observations; received {len(schema)}."
        )

    expected_sequence = tuple(
        range(len(schema))
    )

    actual_sequence = tuple(
        item.sequence_index
        for item in schema
    )

    if actual_sequence != expected_sequence:
        raise ValueError(
            "Observation sequence indices are not contiguous."
        )

    observation_ids = tuple(
        item.observation_id
        for item in schema
    )

    if len(set(observation_ids)) != len(
        observation_ids
    ):
        raise ValueError(
            "Observation identifiers are not unique."
        )

    counts = Counter(
        item.category
        for item in schema
    )

    expected_counts = {
        "square_corner": 4,
        "square_circle_junction": 8,
        "moon_circumference": 72,
        "wall_line": 36,
    }

    if dict(counts) != expected_counts:
        raise ValueError(
            f"Unexpected category counts: {dict(counts)}"
        )

    registration = tuple(
        item
        for item in schema
        if item.registration_default
    )

    if len(registration) != 12:
        raise ValueError(
            "Expected exactly twelve default registration observations."
        )

    for item in schema:
        if item.registration_default:
            if (
                item.model_x is None
                or item.model_y is None
            ):
                raise ValueError(
                    "Registration observation lacks model coordinates: "
                    f"{item.observation_id}"
                )
        else:
            if (
                item.model_x is not None
                or item.model_y is not None
            ):
                raise ValueError(
                    "Source-only observation must not contain model "
                    f"coordinates: {item.observation_id}"
                )

    for moon_id in MOON_OBJECT_IDS:
        rows = tuple(
            item
            for item in schema
            if item.object_id == moon_id
        )

        if len(rows) != 6:
            raise ValueError(
                f"{moon_id} must have six circumference samples."
            )

        if tuple(
            item.sample_index
            for item in rows
        ) != (1, 2, 3, 4, 5, 6):
            raise ValueError(
                f"{moon_id} sample indices are invalid."
            )

    for wall_id in WALL_OBJECT_IDS:
        rows = tuple(
            item
            for item in schema
            if item.object_id == wall_id
        )

        if len(rows) != 3:
            raise ValueError(
                f"{wall_id} must have three line samples."
            )

        if tuple(
            item.sample_index
            for item in rows
        ) != (1, 2, 3):
            raise ValueError(
                f"{wall_id} sample indices are invalid."
            )


def _format_optional_float(
    value: float | None,
) -> str:
    if value is None:
        return ""

    return format(
        value,
        ".17g",
    )


def write_figure12_observation_schema_csv(
    path: str | Path,
    schema: Sequence[Figure12Observation],
) -> Path:
    """Write the fixed observation schema."""

    validate_figure12_observation_schema(
        schema
    )

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=SCHEMA_FIELDNAMES,
        )

        writer.writeheader()

        for item in schema:
            writer.writerow(
                {
                    "sequence_index": item.sequence_index,
                    "observation_id": item.observation_id,
                    "category": item.category,
                    "object_id": item.object_id,
                    "sample_index": item.sample_index,
                    "description": item.description,
                    "model_x": _format_optional_float(
                        item.model_x
                    ),
                    "model_y": _format_optional_float(
                        item.model_y
                    ),
                    "registration_default": (
                        "true"
                        if item.registration_default
                        else "false"
                    ),
                }
            )

    return output_path


def read_figure12_observation_schema_csv(
    path: str | Path,
) -> tuple[Figure12Observation, ...]:
    """Read and validate an observation schema."""

    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        if tuple(reader.fieldnames or ()) != SCHEMA_FIELDNAMES:
            raise ValueError(
                "Unexpected Figure 12 schema columns."
            )

        rows = list(reader)

    schema = tuple(
        Figure12Observation(
            sequence_index=int(
                row["sequence_index"]
            ),
            observation_id=row[
                "observation_id"
            ],
            category=row["category"],
            object_id=row["object_id"],
            sample_index=int(
                row["sample_index"]
            ),
            description=row["description"],
            model_x=(
                float(row["model_x"])
                if row["model_x"]
                else None
            ),
            model_y=(
                float(row["model_y"])
                if row["model_y"]
                else None
            ),
            registration_default=(
                row["registration_default"]
                == "true"
            ),
        )
        for row in rows
    )

    validate_figure12_observation_schema(
        schema
    )

    return schema


def write_figure12_digitisation_pass_csv(
    path: str | Path,
    observations: Sequence[
        Figure12DigitisedObservation
    ],
    *,
    require_complete: bool = True,
) -> Path:
    """Write one raw Figure 12 digitisation pass."""

    if not observations:
        raise ValueError(
            "At least one digitised observation is required."
        )

    pass_ids = {
        item.pass_id
        for item in observations
    }

    if len(pass_ids) != 1:
        raise ValueError(
            "A raw digitisation file may contain only one pass ID."
        )

    definitions = tuple(
        item.definition
        for item in observations
    )

    if require_complete:
        validate_figure12_observation_schema(
            definitions
        )
    else:
        sequence = tuple(
            item.sequence_index
            for item in definitions
        )

        if sequence != tuple(
            range(len(sequence))
        ):
            raise ValueError(
                "Partial observations must be a contiguous "
                "prefix of the fixed schema."
            )

    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=PASS_FIELDNAMES,
        )

        writer.writeheader()

        for item in observations:
            definition = item.definition

            writer.writerow(
                {
                    "pass_id": item.pass_id,
                    "sequence_index": (
                        definition.sequence_index
                    ),
                    "observation_id": (
                        definition.observation_id
                    ),
                    "category": definition.category,
                    "object_id": definition.object_id,
                    "sample_index": (
                        definition.sample_index
                    ),
                    "description": (
                        definition.description
                    ),
                    "model_x": (
                        _format_optional_float(
                            definition.model_x
                        )
                    ),
                    "model_y": (
                        _format_optional_float(
                            definition.model_y
                        )
                    ),
                    "registration_default": (
                        "true"
                        if definition.registration_default
                        else "false"
                    ),
                    "pixel_x": format(
                        item.pixel_x,
                        ".17g",
                    ),
                    "pixel_y": format(
                        item.pixel_y,
                        ".17g",
                    ),
                    "source_image": (
                        item.source_image
                    ),
                    "source_image_sha256": (
                        item.source_image_sha256
                    ),
                    "image_width_pixels": (
                        item.image_width_pixels
                    ),
                    "image_height_pixels": (
                        item.image_height_pixels
                    ),
                }
            )

    return output_path


def read_figure12_digitisation_pass_csv(
    path: str | Path,
    *,
    require_complete: bool = True,
) -> tuple[Figure12DigitisedObservation, ...]:
    """Read one raw digitisation pass."""

    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        if tuple(reader.fieldnames or ()) != PASS_FIELDNAMES:
            raise ValueError(
                "Unexpected Figure 12 digitisation-pass columns."
            )

        rows = list(reader)

    observations = tuple(
        Figure12DigitisedObservation(
            pass_id=row["pass_id"],
            definition=Figure12Observation(
                sequence_index=int(
                    row["sequence_index"]
                ),
                observation_id=row[
                    "observation_id"
                ],
                category=row["category"],
                object_id=row["object_id"],
                sample_index=int(
                    row["sample_index"]
                ),
                description=row[
                    "description"
                ],
                model_x=(
                    float(row["model_x"])
                    if row["model_x"]
                    else None
                ),
                model_y=(
                    float(row["model_y"])
                    if row["model_y"]
                    else None
                ),
                registration_default=(
                    row[
                        "registration_default"
                    ]
                    == "true"
                ),
            ),
            pixel_x=float(
                row["pixel_x"]
            ),
            pixel_y=float(
                row["pixel_y"]
            ),
            source_image=row[
                "source_image"
            ],
            source_image_sha256=row[
                "source_image_sha256"
            ],
            image_width_pixels=int(
                row["image_width_pixels"]
            ),
            image_height_pixels=int(
                row["image_height_pixels"]
            ),
        )
        for row in rows
    )

    if observations:
        definitions = tuple(
            item.definition
            for item in observations
        )

        if require_complete:
            validate_figure12_observation_schema(
                definitions
            )
        else:
            sequence = tuple(
                item.sequence_index
                for item in definitions
            )

            if sequence != tuple(
                range(len(sequence))
            ):
                raise ValueError(
                    "Partial pass is not a contiguous schema prefix."
                )

        if len(
            {
                item.pass_id
                for item in observations
            }
        ) != 1:
            raise ValueError(
                "Digitisation file contains multiple pass IDs."
            )

        source_hashes = {
            item.source_image_sha256
            for item in observations
        }

        if len(source_hashes) != 1:
            raise ValueError(
                "Digitisation file contains multiple source hashes."
            )

    return observations


def category_counts(
    schema: Iterable[Figure12Observation],
) -> Counter[str]:
    """Return observation counts by category."""

    return Counter(
        item.category
        for item in schema
    )
