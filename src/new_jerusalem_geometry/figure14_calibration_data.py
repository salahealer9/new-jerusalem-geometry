"""Promotion and deterministic correction of Figure 14 calibration data.

The three original digitisation passes are preserved byte-for-byte.

A corrected copy of each pass is created by reassigning the coordinates
of the eight square/construction-circle junctions by one cyclic position.
No coordinates are altered numerically, and no other landmark is changed.

The correction was identified after comparison against the independently
digitised square corners. The raw files remain the primary observation
record; the corrected files are an explicitly documented derived dataset.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .figure14_digitisation_qc import (
    DigitisationPass,
    load_digitisation_pass,
)
from .source_preparation import sha256_file


DIGITISATION_GLOB = (
    "figure14_digitisation_pass-*.csv"
)

JUNCTION_IDS = (
    "junction_top_left",
    "junction_top_right",
    "junction_right_upper",
    "junction_right_lower",
    "junction_bottom_right",
    "junction_bottom_left",
    "junction_left_lower",
    "junction_left_upper",
)

# A corrected target landmark receives the coordinates currently
# recorded under the following raw landmark identifier.
JUNCTION_COORDINATE_SOURCE_BY_TARGET = {
    target_id: JUNCTION_IDS[
        (index + 1) % len(JUNCTION_IDS)
    ]
    for index, target_id in enumerate(
        JUNCTION_IDS
    )
}


@dataclass(frozen=True, slots=True)
class CalibrationFileRecord:
    """Hashes and paths for one promoted digitisation pass."""

    pass_id: str
    raw_input_path: Path
    raw_output_path: Path
    corrected_output_path: Path
    raw_sha256: str
    corrected_sha256: str


@dataclass(frozen=True, slots=True)
class CalibrationPromotionResult:
    """Summary of a completed calibration-data promotion."""

    output_root: Path
    raw_directory: Path
    corrected_directory: Path
    manifest_path: Path
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    files: tuple[CalibrationFileRecord, ...]


def _read_csv_table(
    path: str | Path,
) -> tuple[tuple[str, ...], list[dict[str, str]]]:
    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(
                f"CSV has no header: {input_path}"
            )

        fieldnames = tuple(reader.fieldnames)
        rows = [
            dict(row)
            for row in reader
        ]

    if not rows:
        raise ValueError(
            f"CSV has no data rows: {input_path}"
        )

    return fieldnames, rows


def relabel_junction_coordinates(
    rows: Sequence[dict[str, str]],
) -> list[dict[str, str]]:
    """Return rows with the junction coordinates cyclically reassigned.

    The row identities, ordering, metadata, and model coordinates remain
    unchanged. Only ``pixel_x`` and ``pixel_y`` are reassigned for the
    eight junction landmarks.
    """

    copied_rows = [
        dict(row)
        for row in rows
    ]

    by_identifier = {
        row["landmark_id"]: row
        for row in rows
    }

    missing = set(JUNCTION_IDS).difference(
        by_identifier
    )

    if missing:
        raise ValueError(
            "Digitisation pass is missing junction landmarks: "
            + ", ".join(sorted(missing))
        )

    if len(by_identifier) != len(rows):
        raise ValueError(
            "Digitisation landmark identifiers must be unique."
        )

    for corrected_row in copied_rows:
        target_id = corrected_row[
            "landmark_id"
        ]

        source_id = (
            JUNCTION_COORDINATE_SOURCE_BY_TARGET.get(
                target_id
            )
        )

        if source_id is None:
            continue

        source_row = by_identifier[
            source_id
        ]

        corrected_row["pixel_x"] = (
            source_row["pixel_x"]
        )

        corrected_row["pixel_y"] = (
            source_row["pixel_y"]
        )

    return copied_rows


def _write_csv_table(
    path: str | Path,
    *,
    fieldnames: Sequence[str],
    rows: Sequence[dict[str, str]],
) -> Path:
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
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    return output_path


def _check_output_paths(
    paths: Sequence[Path],
    *,
    overwrite: bool,
) -> None:
    existing = [
        path
        for path in paths
        if path.exists()
    ]

    if existing and not overwrite:
        formatted = "\n".join(
            f"  {path}"
            for path in existing
        )

        raise FileExistsError(
            "Calibration outputs already exist:\n"
            f"{formatted}\n"
            "Use overwrite=True only after reviewing them."
        )


def _validate_common_source(
    passes: Sequence[DigitisationPass],
) -> None:
    if not passes:
        raise ValueError(
            "No digitisation passes were supplied."
        )

    pass_ids = [
        item.pass_id
        for item in passes
    ]

    if len(set(pass_ids)) != len(pass_ids):
        raise ValueError(
            "Digitisation pass identifiers must be unique."
        )

    reference = passes[0]

    for item in passes[1:]:
        if item.source_image != reference.source_image:
            raise ValueError(
                "Digitisation passes use different source filenames."
            )

        if (
            item.source_image_sha256
            != reference.source_image_sha256
        ):
            raise ValueError(
                "Digitisation passes use different source-image hashes."
            )

        if (
            item.image_width_pixels
            != reference.image_width_pixels
            or item.image_height_pixels
            != reference.image_height_pixels
        ):
            raise ValueError(
                "Digitisation passes use different image dimensions."
            )

        reference_identity = tuple(
            (
                observation.sequence_index,
                observation.landmark_id,
                observation.category,
            )
            for observation in reference.observations
        )

        item_identity = tuple(
            (
                observation.sequence_index,
                observation.landmark_id,
                observation.category,
            )
            for observation in item.observations
        )

        if item_identity != reference_identity:
            raise ValueError(
                "Landmark ordering differs between digitisation passes."
            )


def promote_figure14_calibration_data(
    *,
    input_directory: str | Path,
    output_root: str | Path,
    expected_pass_count: int = 3,
    overwrite: bool = False,
) -> CalibrationPromotionResult:
    """Preserve raw passes and create corrected committed copies."""

    input_path = Path(input_directory)
    root_path = Path(output_root)

    raw_paths = sorted(
        input_path.glob(
            DIGITISATION_GLOB
        )
    )

    if len(raw_paths) != expected_pass_count:
        raise ValueError(
            f"Expected {expected_pass_count} digitisation passes "
            f"in {input_path}; found {len(raw_paths)}."
        )

    passes = tuple(
        load_digitisation_pass(path)
        for path in raw_paths
    )

    _validate_common_source(
        passes
    )

    raw_directory = (
        root_path / "raw"
    )

    corrected_directory = (
        root_path / "corrected"
    )

    manifest_path = (
        corrected_directory
        / "junction_relabelling_manifest.json"
    )

    planned_outputs = [
        manifest_path,
    ]

    for raw_path in raw_paths:
        planned_outputs.extend(
            (
                raw_directory / raw_path.name,
                corrected_directory / raw_path.name,
            )
        )

    _check_output_paths(
        planned_outputs,
        overwrite=overwrite,
    )

    raw_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    corrected_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    records: list[
        CalibrationFileRecord
    ] = []

    for raw_path, digitisation_pass in zip(
        raw_paths,
        passes,
        strict=True,
    ):
        fieldnames, rows = _read_csv_table(
            raw_path
        )

        corrected_rows = (
            relabel_junction_coordinates(
                rows
            )
        )

        raw_output_path = (
            raw_directory / raw_path.name
        )

        corrected_output_path = (
            corrected_directory
            / raw_path.name
        )

        # Preserve the raw observation file exactly.
        raw_output_path.write_bytes(
            raw_path.read_bytes()
        )

        _write_csv_table(
            corrected_output_path,
            fieldnames=fieldnames,
            rows=corrected_rows,
        )

        # Validate the generated corrected pass using the same
        # parser used by all later analyses.
        corrected_pass = load_digitisation_pass(
            corrected_output_path
        )

        if (
            corrected_pass.pass_id
            != digitisation_pass.pass_id
        ):
            raise AssertionError(
                "Corrected pass identifier changed unexpectedly."
            )

        raw_digest = sha256_file(
            raw_path
        )

        copied_raw_digest = sha256_file(
            raw_output_path
        )

        if copied_raw_digest != raw_digest:
            raise AssertionError(
                "Promoted raw pass does not match its source bytes."
            )

        records.append(
            CalibrationFileRecord(
                pass_id=digitisation_pass.pass_id,
                raw_input_path=raw_path,
                raw_output_path=raw_output_path,
                corrected_output_path=(
                    corrected_output_path
                ),
                raw_sha256=raw_digest,
                corrected_sha256=sha256_file(
                    corrected_output_path
                ),
            )
        )

    reference = passes[0]

    manifest = {
        "schema_version": 1,
        "correction_id": (
            "figure14-junction-cyclic-shift-plus-one"
        ),
        "correction_type": (
            "coordinate_reassignment"
        ),
        "raw_files_modified": False,
        "reason": (
            "The eight square/construction-circle junctions "
            "were digitised consistently across all three passes "
            "using a landmark sequence displaced backward by one "
            "cyclic position. Registration against the independently "
            "digitised square corners identified the unique corrected "
            "cyclic correspondence."
        ),
        "coordinate_mapping_semantics": (
            "Each target landmark receives pixel_x and pixel_y "
            "from the named raw source landmark. All other fields "
            "remain attached to the target landmark."
        ),
        "coordinate_mapping": [
            {
                "target_landmark_id": target_id,
                "raw_coordinate_source_landmark_id": (
                    JUNCTION_COORDINATE_SOURCE_BY_TARGET[
                        target_id
                    ]
                ),
            }
            for target_id in JUNCTION_IDS
        ],
        "source_image": {
            "filename": reference.source_image,
            "sha256": (
                reference.source_image_sha256
            ),
            "width_pixels": (
                reference.image_width_pixels
            ),
            "height_pixels": (
                reference.image_height_pixels
            ),
        },
        "passes": [
            {
                "pass_id": record.pass_id,
                "raw_filename": (
                    record.raw_output_path.name
                ),
                "raw_sha256": record.raw_sha256,
                "corrected_filename": (
                    record.corrected_output_path.name
                ),
                "corrected_sha256": (
                    record.corrected_sha256
                ),
            }
            for record in records
        ],
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return CalibrationPromotionResult(
        output_root=root_path,
        raw_directory=raw_directory,
        corrected_directory=(
            corrected_directory
        ),
        manifest_path=manifest_path,
        source_image=reference.source_image,
        source_image_sha256=(
            reference.source_image_sha256
        ),
        image_width_pixels=(
            reference.image_width_pixels
        ),
        image_height_pixels=(
            reference.image_height_pixels
        ),
        files=tuple(records),
    )
