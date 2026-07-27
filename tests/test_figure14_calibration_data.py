import csv
import json
from pathlib import Path

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.figure14_calibration_data import (
    JUNCTION_COORDINATE_SOURCE_BY_TARGET,
    JUNCTION_IDS,
    promote_figure14_calibration_data,
    relabel_junction_coordinates,
)
from new_jerusalem_geometry.figure14_digitisation import (
    build_figure14_landmark_schema,
    write_digitisation_csv,
)
from new_jerusalem_geometry.source_preparation import (
    sha256_file,
)


def _make_passes(
    tmp_path: Path,
) -> tuple[
    Path,
    tuple[object, ...],
]:
    input_directory = (
        tmp_path / "working"
    )

    input_directory.mkdir()

    schema = build_figure14_landmark_schema(
        build_core_geometry()
    )

    source_image = (
        tmp_path / "source.png"
    )

    source_image.write_bytes(
        b"fixed rendered source"
    )

    for pass_number in range(1, 4):
        points = tuple(
            (
                100.0
                + 10.0 * landmark.sequence_index
                + pass_number / 10.0,
                200.0
                + 20.0 * landmark.sequence_index
                + pass_number / 10.0,
            )
            for landmark in schema
        )

        write_digitisation_csv(
            input_directory
            / (
                "figure14_digitisation_"
                f"pass-{pass_number:02d}.csv"
            ),
            schema=schema,
            points=points,
            pass_id=f"pass-{pass_number:02d}",
            source_image=source_image,
            image_width_pixels=2000,
            image_height_pixels=3000,
        )

    return input_directory, schema


def _read_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(csv.DictReader(handle))


def test_junction_coordinate_mapping_is_one_step_cyclic() -> None:
    assert len(
        JUNCTION_COORDINATE_SOURCE_BY_TARGET
    ) == 8

    for index, target_id in enumerate(
        JUNCTION_IDS
    ):
        assert (
            JUNCTION_COORDINATE_SOURCE_BY_TARGET[
                target_id
            ]
            == JUNCTION_IDS[
                (index + 1) % len(JUNCTION_IDS)
            ]
        )


def test_relabelling_changes_only_junction_coordinates() -> None:
    rows = [
        {
            "landmark_id": landmark_id,
            "pixel_x": str(index + 0.25),
            "pixel_y": str(index + 0.75),
            "description": f"row {index}",
        }
        for index, landmark_id in enumerate(
            (
                "square_corner_top_left",
                *JUNCTION_IDS,
                "star_endpoint_00_top",
            )
        )
    ]

    corrected = relabel_junction_coordinates(
        rows
    )

    raw_by_id = {
        row["landmark_id"]: row
        for row in rows
    }

    corrected_by_id = {
        row["landmark_id"]: row
        for row in corrected
    }

    assert (
        corrected_by_id[
            "square_corner_top_left"
        ]
        == raw_by_id[
            "square_corner_top_left"
        ]
    )

    assert (
        corrected_by_id[
            "star_endpoint_00_top"
        ]
        == raw_by_id[
            "star_endpoint_00_top"
        ]
    )

    for target_id, source_id in (
        JUNCTION_COORDINATE_SOURCE_BY_TARGET.items()
    ):
        corrected_row = corrected_by_id[
            target_id
        ]

        source_row = raw_by_id[
            source_id
        ]

        assert (
            corrected_row["pixel_x"]
            == source_row["pixel_x"]
        )

        assert (
            corrected_row["pixel_y"]
            == source_row["pixel_y"]
        )

        assert (
            corrected_row["description"]
            == raw_by_id[target_id]["description"]
        )


def test_promotion_preserves_raw_bytes_and_writes_manifest(
    tmp_path: Path,
) -> None:
    input_directory, _ = _make_passes(
        tmp_path
    )

    output_root = (
        tmp_path / "calibration"
    )

    result = promote_figure14_calibration_data(
        input_directory=input_directory,
        output_root=output_root,
    )

    assert len(result.files) == 3
    assert result.manifest_path.exists()

    for record in result.files:
        assert (
            record.raw_output_path.read_bytes()
            == record.raw_input_path.read_bytes()
        )

        assert (
            sha256_file(record.raw_output_path)
            == record.raw_sha256
        )

        assert (
            sha256_file(
                record.corrected_output_path
            )
            == record.corrected_sha256
        )

        raw_rows = _read_rows(
            record.raw_output_path
        )

        corrected_rows = _read_rows(
            record.corrected_output_path
        )

        raw_by_id = {
            row["landmark_id"]: row
            for row in raw_rows
        }

        corrected_by_id = {
            row["landmark_id"]: row
            for row in corrected_rows
        }

        assert (
            corrected_by_id[
                "junction_top_left"
            ]["pixel_x"]
            == raw_by_id[
                "junction_top_right"
            ]["pixel_x"]
        )

    manifest = json.loads(
        result.manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert manifest["raw_files_modified"] is False
    assert (
        manifest["correction_id"]
        == "figure14-junction-cyclic-shift-plus-one"
    )

    assert len(manifest["passes"]) == 3
    assert len(
        manifest["coordinate_mapping"]
    ) == 8


def test_promotion_refuses_silent_overwrite(
    tmp_path: Path,
) -> None:
    input_directory, _ = _make_passes(
        tmp_path
    )

    output_root = (
        tmp_path / "calibration"
    )

    promote_figure14_calibration_data(
        input_directory=input_directory,
        output_root=output_root,
    )

    with pytest.raises(
        FileExistsError,
        match="already exist",
    ):
        promote_figure14_calibration_data(
            input_directory=input_directory,
            output_root=output_root,
        )
