"""Landmark schema and records for Figure 14 source calibration.

The landmark schema separates:

- registration geometry with known model coordinates;
- Moon-circle centres used as structural validation landmarks;
- seven visually observed heptagram endpoints with no assumed model
  coordinates.

No transformation fitting is performed in this module.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from math import atan2, pi, sqrt, tau
from pathlib import Path
from typing import Sequence

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .source_preparation import sha256_file
from .wall_geometry import build_ordered_moon_circles


SCHEMA_FIELDNAMES = (
    "sequence_index",
    "landmark_id",
    "category",
    "description",
    "model_x",
    "model_y",
    "registration_default",
)

DIGITISATION_FIELDNAMES = (
    "schema_version",
    "pass_id",
    "source_image",
    "source_image_sha256",
    "image_width_pixels",
    "image_height_pixels",
    "sequence_index",
    "landmark_id",
    "category",
    "description",
    "pixel_x",
    "pixel_y",
    "model_x",
    "model_y",
    "registration_default",
)


@dataclass(frozen=True, slots=True)
class LandmarkDefinition:
    """One landmark requested during source digitisation."""

    sequence_index: int
    landmark_id: str
    category: str
    description: str
    model_x: float | None
    model_y: float | None
    registration_default: bool


def _format_optional_float(
    value: float | None,
) -> str:
    if value is None:
        return ""

    if abs(value) < 1.0e-15:
        return "0"

    # Seventeen significant digits guarantee an exact
    # round trip for an IEEE-754 binary64 Python float.
    return format(value, ".17g")


def _parse_optional_float(
    value: str,
) -> float | None:
    stripped = value.strip()

    if not stripped:
        return None

    return float(stripped)


def _append_landmark(
    landmarks: list[LandmarkDefinition],
    *,
    landmark_id: str,
    category: str,
    description: str,
    model_x: float | None,
    model_y: float | None,
    registration_default: bool,
) -> None:
    landmarks.append(
        LandmarkDefinition(
            sequence_index=len(landmarks),
            landmark_id=landmark_id,
            category=category,
            description=description,
            model_x=model_x,
            model_y=model_y,
            registration_default=registration_default,
        )
    )


def build_figure14_landmark_schema(
    diagram: CoreDiagram,
) -> tuple[LandmarkDefinition, ...]:
    """Build the fixed thirty-one-landmark Figure 14 schema.

    Registration geometry contains:

    - four Earth-square corners;
    - eight Earth-square/construction-circle junctions.

    Structural validation geometry contains:

    - twelve Moon-circle centres.

    The seven apparent heptagram endpoints deliberately have no model
    coordinates at the digitisation stage.
    """

    landmarks: list[LandmarkDefinition] = []

    half_side = diagram.earth_square.half_side
    radius = diagram.construction_circle.radius

    junction_offset = sqrt(
        radius * radius
        - half_side * half_side
    )

    square_corners = (
        (
            "square_corner_top_left",
            -half_side,
            half_side,
            "Top-left corner of the Earth square.",
        ),
        (
            "square_corner_top_right",
            half_side,
            half_side,
            "Top-right corner of the Earth square.",
        ),
        (
            "square_corner_bottom_right",
            half_side,
            -half_side,
            "Bottom-right corner of the Earth square.",
        ),
        (
            "square_corner_bottom_left",
            -half_side,
            -half_side,
            "Bottom-left corner of the Earth square.",
        ),
    )

    for landmark_id, x, y, description in square_corners:
        _append_landmark(
            landmarks,
            landmark_id=landmark_id,
            category="square_corner",
            description=description,
            model_x=x,
            model_y=y,
            registration_default=True,
        )

    junctions = (
        (
            "junction_top_left",
            -junction_offset,
            half_side,
            "Left junction on the top side of the Earth square.",
        ),
        (
            "junction_top_right",
            junction_offset,
            half_side,
            "Right junction on the top side of the Earth square.",
        ),
        (
            "junction_right_upper",
            half_side,
            junction_offset,
            "Upper junction on the right side of the Earth square.",
        ),
        (
            "junction_right_lower",
            half_side,
            -junction_offset,
            "Lower junction on the right side of the Earth square.",
        ),
        (
            "junction_bottom_right",
            junction_offset,
            -half_side,
            "Right junction on the bottom side of the Earth square.",
        ),
        (
            "junction_bottom_left",
            -junction_offset,
            -half_side,
            "Left junction on the bottom side of the Earth square.",
        ),
        (
            "junction_left_lower",
            -half_side,
            -junction_offset,
            "Lower junction on the left side of the Earth square.",
        ),
        (
            "junction_left_upper",
            -half_side,
            junction_offset,
            "Upper junction on the left side of the Earth square.",
        ),
    )

    for landmark_id, x, y, description in junctions:
        _append_landmark(
            landmarks,
            landmark_id=landmark_id,
            category="square_circle_junction",
            description=description,
            model_x=x,
            model_y=y,
            registration_default=True,
        )

    incidence_moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    moon_centres = [
        moon.centre
        for _, moon in incidence_moons
    ]

    def phase_from_top(point: object) -> float:
        angle = atan2(point.y, point.x)

        return (
            angle
            - pi / 2.0
        ) % tau

    moon_centres.sort(
        key=phase_from_top
    )

    for moon_index, centre in enumerate(moon_centres):
        angle = atan2(
            centre.y,
            centre.x,
        )

        if angle < 0.0:
            angle += tau

        angle_degrees = angle * 180.0 / pi

        _append_landmark(
            landmarks,
            landmark_id=(
                f"moon_centre_{moon_index:02d}"
            ),
            category="moon_centre",
            description=(
                "Centre of Moon circle "
                f"{moon_index:02d}, ordered counter-clockwise "
                f"from the top; model angle "
                f"{angle_degrees:.6f} degrees."
            ),
            model_x=centre.x,
            model_y=centre.y,
            registration_default=False,
        )

    star_endpoints = (
        (
            "star_endpoint_00_top",
            "Apparent upper heptagram endpoint.",
        ),
        (
            "star_endpoint_01_upper_left",
            (
                "Apparent upper-left heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
        (
            "star_endpoint_02_lower_left",
            (
                "Apparent lower-left side heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
        (
            "star_endpoint_03_bottom_left",
            (
                "Apparent bottom-left heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
        (
            "star_endpoint_04_bottom_right",
            (
                "Apparent bottom-right heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
        (
            "star_endpoint_05_lower_right",
            (
                "Apparent lower-right side heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
        (
            "star_endpoint_06_upper_right",
            (
                "Apparent upper-right heptagram endpoint, "
                "ordered counter-clockwise from the top."
            ),
        ),
    )

    for landmark_id, description in star_endpoints:
        _append_landmark(
            landmarks,
            landmark_id=landmark_id,
            category="star_endpoint",
            description=description,
            model_x=None,
            model_y=None,
            registration_default=False,
        )

    if len(landmarks) != 31:
        raise AssertionError(
            "Figure 14 schema must contain exactly 31 landmarks."
        )

    return tuple(landmarks)


def write_landmark_schema_csv(
    path: str | Path,
    schema: Sequence[LandmarkDefinition],
) -> Path:
    """Write the deterministic landmark-schema CSV."""

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

        for landmark in schema:
            writer.writerow(
                {
                    "sequence_index": (
                        landmark.sequence_index
                    ),
                    "landmark_id": landmark.landmark_id,
                    "category": landmark.category,
                    "description": landmark.description,
                    "model_x": _format_optional_float(
                        landmark.model_x
                    ),
                    "model_y": _format_optional_float(
                        landmark.model_y
                    ),
                    "registration_default": (
                        "true"
                        if landmark.registration_default
                        else "false"
                    ),
                }
            )

    return output_path


def read_landmark_schema_csv(
    path: str | Path,
) -> tuple[LandmarkDefinition, ...]:
    """Read and validate a landmark-schema CSV."""

    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    schema = tuple(
        LandmarkDefinition(
            sequence_index=int(
                row["sequence_index"]
            ),
            landmark_id=row["landmark_id"],
            category=row["category"],
            description=row["description"],
            model_x=_parse_optional_float(
                row["model_x"]
            ),
            model_y=_parse_optional_float(
                row["model_y"]
            ),
            registration_default=(
                row["registration_default"]
                .strip()
                .lower()
                == "true"
            ),
        )
        for row in rows
    )

    expected_indices = tuple(
        range(len(schema))
    )

    observed_indices = tuple(
        landmark.sequence_index
        for landmark in schema
    )

    if observed_indices != expected_indices:
        raise ValueError(
            "Landmark sequence indices must be contiguous "
            "and begin at zero."
        )

    identifiers = tuple(
        landmark.landmark_id
        for landmark in schema
    )

    if len(set(identifiers)) != len(identifiers):
        raise ValueError(
            "Landmark identifiers must be unique."
        )

    return schema


def write_digitisation_csv(
    path: str | Path,
    *,
    schema: Sequence[LandmarkDefinition],
    points: Sequence[tuple[float, float]],
    pass_id: str,
    source_image: str | Path,
    image_width_pixels: int,
    image_height_pixels: int,
) -> Path:
    """Write one complete independent digitisation pass."""

    if len(points) != len(schema):
        raise ValueError(
            "Digitised point count must equal schema length: "
            f"{len(points)} != {len(schema)}."
        )

    if not pass_id.strip():
        raise ValueError(
            "pass_id must not be empty."
        )

    if image_width_pixels <= 0 or image_height_pixels <= 0:
        raise ValueError(
            "Image dimensions must be positive."
        )

    source_path = Path(source_image)

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Source image not found: {source_path}"
        )

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_digest = sha256_file(
        source_path
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=DIGITISATION_FIELDNAMES,
        )

        writer.writeheader()

        for landmark, point in zip(
            schema,
            points,
            strict=True,
        ):
            pixel_x, pixel_y = point

            writer.writerow(
                {
                    "schema_version": 1,
                    "pass_id": pass_id,
                    "source_image": source_path.name,
                    "source_image_sha256": source_digest,
                    "image_width_pixels": (
                        image_width_pixels
                    ),
                    "image_height_pixels": (
                        image_height_pixels
                    ),
                    "sequence_index": (
                        landmark.sequence_index
                    ),
                    "landmark_id": landmark.landmark_id,
                    "category": landmark.category,
                    "description": landmark.description,
                    "pixel_x": format(
                        float(pixel_x),
                        ".6f",
                    ),
                    "pixel_y": format(
                        float(pixel_y),
                        ".6f",
                    ),
                    "model_x": _format_optional_float(
                        landmark.model_x
                    ),
                    "model_y": _format_optional_float(
                        landmark.model_y
                    ),
                    "registration_default": (
                        "true"
                        if landmark.registration_default
                        else "false"
                    ),
                }
            )

    return output_path
