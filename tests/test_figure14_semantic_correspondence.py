import csv
import json
from math import cos, pi, sin
from pathlib import Path

import numpy as np
import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.figure14_digitisation import (
    build_figure14_landmark_schema,
    write_digitisation_csv,
    write_landmark_schema_csv,
)
from new_jerusalem_geometry.figure14_registration import (
    apply_registration_matrix,
    cartesian_to_pixel,
)
from new_jerusalem_geometry.figure14_semantic_correspondence import (
    EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET,
    EXPECTED_STAR_COORDINATE_SOURCE_BY_TARGET,
    resolve_figure14_semantic_correspondence,
)


TRUE_AFFINE = np.asarray(
    (
        (70.0, 1.2, 760.0),
        (-0.7, 68.5, 910.0),
        (0.0, 0.0, 1.0),
    ),
    dtype=float,
)


def _read_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def _make_semantically_permuted_dataset(
    tmp_path: Path,
) -> tuple[
    Path,
    Path,
    tuple[Path, ...],
]:
    schema = build_figure14_landmark_schema(
        build_core_geometry()
    )

    schema_by_id = {
        item.landmark_id: item
        for item in schema
    }

    schema_path = (
        tmp_path / "landmark_schema.csv"
    )

    write_landmark_schema_csv(
        schema_path,
        schema,
    )

    input_directory = (
        tmp_path / "corrected"
    )

    input_directory.mkdir()

    source_image = (
        tmp_path / "source.png"
    )

    source_image.write_bytes(
        b"fixed source image"
    )

    # Each source Moon row contains the model coordinate of the
    # target that will later receive that source coordinate.
    moon_target_by_source = {
        source_id: target_id
        for target_id, source_id in (
            EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET.items()
        )
    }

    pass_paths = []
    image_height = 2200

    for pass_number, drift in enumerate(
        (
            (-0.15, 0.10),
            (0.00, 0.00),
            (0.15, -0.10),
        ),
        start=1,
    ):
        points = []

        for landmark in schema:
            if landmark.category in {
                "square_corner",
                "square_circle_junction",
            }:
                normalized = np.asarray(
                    [
                        (
                            landmark.model_x,
                            landmark.model_y,
                        )
                    ],
                    dtype=float,
                )

            elif landmark.category == "moon_centre":
                target_id = moon_target_by_source[
                    landmark.landmark_id
                ]

                target = schema_by_id[
                    target_id
                ]

                normalized = np.asarray(
                    [
                        (
                            target.model_x,
                            target.model_y,
                        )
                    ],
                    dtype=float,
                )

            elif landmark.category == "star_endpoint":
                star_index = (
                    landmark.sequence_index - 24
                )

                angle = (
                    pi / 2.0
                    - star_index
                    * 4.0
                    * pi
                    / 7.0
                )

                normalized = np.asarray(
                    [
                        (
                            7.0 * cos(angle),
                            7.0 * sin(angle),
                        )
                    ],
                    dtype=float,
                )

            else:
                raise AssertionError(
                    f"Unexpected category: {landmark.category}"
                )

            cartesian = apply_registration_matrix(
                TRUE_AFFINE,
                normalized,
            )[0]

            cartesian = (
                cartesian
                + np.asarray(drift)
            )

            pixel_x, pixel_y = cartesian_to_pixel(
                float(cartesian[0]),
                float(cartesian[1]),
                image_height,
            )

            points.append(
                (
                    pixel_x,
                    pixel_y,
                )
            )

        pass_path = (
            input_directory
            / (
                "figure14_digitisation_"
                f"pass-{pass_number:02d}.csv"
            )
        )

        write_digitisation_csv(
            pass_path,
            schema=schema,
            points=points,
            pass_id=f"pass-{pass_number:02d}",
            source_image=source_image,
            image_width_pixels=1700,
            image_height_pixels=image_height,
        )

        pass_paths.append(pass_path)

    return (
        schema_path,
        input_directory,
        tuple(pass_paths),
    )


def test_semantic_resolution_recovers_expected_mappings(
    tmp_path: Path,
) -> None:
    schema_path, input_directory, _ = (
        _make_semantically_permuted_dataset(
            tmp_path
        )
    )

    result = resolve_figure14_semantic_correspondence(
        schema_path=schema_path,
        input_directory=input_directory,
        output_directory=tmp_path / "resolved",
    )

    assert dict(result.moon.mapping) == (
        EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET
    )

    assert dict(
        result.star.spatial_mapping
    ) == (
        EXPECTED_STAR_COORDINATE_SOURCE_BY_TARGET
    )

    assert result.moon.direction == "reversed"
    assert result.moon.shift == 1

    assert (
        result.star.recorded_sequence_notation
        == "{7/2}"
    )

    assert (
        result.star.recorded_sequence_direction
        == "clockwise"
    )

    assert (
        result.star.recorded_sequence_angular_rms_degrees
        < 1.0e-5
    )


def test_resolution_changes_only_moon_and_star_coordinates(
    tmp_path: Path,
) -> None:
    schema_path, input_directory, pass_paths = (
        _make_semantically_permuted_dataset(
            tmp_path
        )
    )

    result = resolve_figure14_semantic_correspondence(
        schema_path=schema_path,
        input_directory=input_directory,
        output_directory=tmp_path / "resolved",
    )

    input_rows = _read_rows(
        pass_paths[0]
    )

    output_rows = _read_rows(
        result.files[0].output_path
    )

    input_by_id = {
        row["landmark_id"]: row
        for row in input_rows
    }

    output_by_id = {
        row["landmark_id"]: row
        for row in output_rows
    }

    for landmark_id, input_row in (
        input_by_id.items()
    ):
        output_row = output_by_id[
            landmark_id
        ]

        if input_row["category"] in {
            "square_corner",
            "square_circle_junction",
        }:
            assert (
                output_row["pixel_x"]
                == input_row["pixel_x"]
            )

            assert (
                output_row["pixel_y"]
                == input_row["pixel_y"]
            )

    moon_target = "moon_centre_00"
    moon_source = (
        EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET[
            moon_target
        ]
    )

    assert (
        output_by_id[moon_target]["pixel_x"]
        == input_by_id[moon_source]["pixel_x"]
    )

    star_target = (
        "star_endpoint_01_upper_left"
    )

    star_source = (
        EXPECTED_STAR_COORDINATE_SOURCE_BY_TARGET[
            star_target
        ]
    )

    assert (
        output_by_id[star_target]["pixel_y"]
        == input_by_id[star_source]["pixel_y"]
    )


def test_semantic_manifest_preserves_interpretation_boundary(
    tmp_path: Path,
) -> None:
    schema_path, input_directory, _ = (
        _make_semantically_permuted_dataset(
            tmp_path
        )
    )

    result = resolve_figure14_semantic_correspondence(
        schema_path=schema_path,
        input_directory=input_directory,
        output_directory=tmp_path / "resolved",
    )

    payload = json.loads(
        result.manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["registration_landmarks_modified"]
        is False
    )

    assert (
        payload[
            "numerical_coordinate_values_modified"
        ]
        is False
    )

    sequence = payload[
        "star_correspondence"
    ]["recorded_sequence_consistency"]

    assert sequence["best_notation"] == "{7/2}"
    assert sequence["best_direction"] == "clockwise"

    assert (
        "not independent topology proof"
        in sequence["status"]
    )

    report_text = result.report_path.read_text(
        encoding="utf-8"
    )

    assert "Interpretation boundary" in report_text
    assert "not, by itself" in report_text


def test_semantic_resolution_refuses_silent_overwrite(
    tmp_path: Path,
) -> None:
    schema_path, input_directory, _ = (
        _make_semantically_permuted_dataset(
            tmp_path
        )
    )

    output_directory = (
        tmp_path / "resolved"
    )

    resolve_figure14_semantic_correspondence(
        schema_path=schema_path,
        input_directory=input_directory,
        output_directory=output_directory,
    )

    with pytest.raises(
        FileExistsError,
        match="already exist",
    ):
        resolve_figure14_semantic_correspondence(
            schema_path=schema_path,
            input_directory=input_directory,
            output_directory=output_directory,
        )
