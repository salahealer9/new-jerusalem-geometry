"""Resolve Figure 14 Moon-centre and star-endpoint correspondences.

The junction-corrected digitisation passes preserve two remaining semantic
mismatches:

- Moon centres were recorded in a reversed cyclic sequence;
- star endpoints were recorded in a sequence that does not match their
  spatial endpoint labels.

This module derives those mappings from the affine-calibrated observations,
creates a new correspondence-resolved layer, and preserves the preceding
layers unchanged.

Only ``pixel_x`` and ``pixel_y`` are reassigned. No numerical coordinate is
edited, averaged, discarded, or replaced.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from math import atan2, degrees, hypot, pi, sqrt, tau
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from .figure14_registered_landmarks import (
    AffineCalibrationReport,
    derive_affine_registered_landmarks,
)
from .figure14_digitisation_qc import (
    load_digitisation_pass,
)
from .source_preparation import sha256_file


DIGITISATION_GLOB = (
    "figure14_digitisation_pass-*.csv"
)

MOON_IDS = tuple(
    f"moon_centre_{index:02d}"
    for index in range(12)
)

STAR_IDS = (
    "star_endpoint_00_top",
    "star_endpoint_01_upper_left",
    "star_endpoint_02_lower_left",
    "star_endpoint_03_bottom_left",
    "star_endpoint_04_bottom_right",
    "star_endpoint_05_lower_right",
    "star_endpoint_06_upper_right",
)


EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET = {
    "moon_centre_00": "moon_centre_01",
    "moon_centre_01": "moon_centre_00",
    "moon_centre_02": "moon_centre_11",
    "moon_centre_03": "moon_centre_10",
    "moon_centre_04": "moon_centre_09",
    "moon_centre_05": "moon_centre_08",
    "moon_centre_06": "moon_centre_07",
    "moon_centre_07": "moon_centre_06",
    "moon_centre_08": "moon_centre_05",
    "moon_centre_09": "moon_centre_04",
    "moon_centre_10": "moon_centre_03",
    "moon_centre_11": "moon_centre_02",
}


EXPECTED_STAR_COORDINATE_SOURCE_BY_TARGET = {
    "star_endpoint_00_top":
        "star_endpoint_00_top",
    "star_endpoint_01_upper_left":
        "star_endpoint_03_bottom_left",
    "star_endpoint_02_lower_left":
        "star_endpoint_06_upper_right",
    "star_endpoint_03_bottom_left":
        "star_endpoint_02_lower_left",
    "star_endpoint_04_bottom_right":
        "star_endpoint_05_lower_right",
    "star_endpoint_05_lower_right":
        "star_endpoint_01_upper_left",
    "star_endpoint_06_upper_right":
        "star_endpoint_04_bottom_right",
}


@dataclass(frozen=True, slots=True)
class MoonCorrespondence:
    """Best cyclic correspondence for the twelve Moon centres."""

    direction: str
    shift: int
    rms_normalized: float
    maximum_normalized: float
    second_best_rms_normalized: float
    mapping: tuple[tuple[str, str], ...]
    residuals_by_target: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class StarCorrespondence:
    """Spatial mapping and recorded-sequence diagnostics for star endpoints."""

    circle_centre_x: float
    circle_centre_y: float
    circle_centre_displacement: float
    fitted_radius: float
    mean_radius: float
    radial_rms: float
    radial_standard_deviation: float
    radius_minimum: float
    radius_maximum: float
    recorded_sequence_step_size: int
    recorded_sequence_notation: str
    recorded_sequence_direction: str
    recorded_sequence_phase_degrees: float
    recorded_sequence_angular_rms_degrees: float
    recorded_sequence_angular_maximum_degrees: float
    second_best_angular_rms_degrees: float
    spatial_mapping: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class ResolvedFileRecord:
    """One input/output pair in the correspondence-resolved layer."""

    pass_id: str
    input_path: Path
    output_path: Path
    input_sha256: str
    output_sha256: str


@dataclass(frozen=True, slots=True)
class SemanticResolutionResult:
    """Complete Figure 14 semantic correspondence resolution."""

    output_directory: Path
    manifest_path: Path
    report_path: Path
    moon: MoonCorrespondence
    star: StarCorrespondence
    files: tuple[ResolvedFileRecord, ...]
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int


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


def _wrap_angles(
    angles: np.ndarray,
) -> np.ndarray:
    return (
        angles + pi
    ) % tau - pi


def infer_moon_correspondence(
    report: AffineCalibrationReport,
) -> MoonCorrespondence:
    """Find the best cyclic or reversed cyclic Moon correspondence."""

    moons = tuple(
        item
        for item in report.landmarks
        if item.category == "moon_centre"
    )

    if tuple(
        item.landmark_id
        for item in moons
    ) != MOON_IDS:
        raise ValueError(
            "Moon landmarks do not match the fixed schema order."
        )

    model = np.asarray(
        [
            (
                item.model_x,
                item.model_y,
            )
            for item in moons
        ],
        dtype=float,
    )

    observed = np.asarray(
        [
            (
                item.normalized_x,
                item.normalized_y,
            )
            for item in moons
        ],
        dtype=float,
    )

    if not np.all(np.isfinite(model)):
        raise ValueError(
            "Moon schema coordinates must be finite."
        )

    candidates: list[
        tuple[
            float,
            float,
            str,
            int,
            np.ndarray,
            np.ndarray,
        ]
    ] = []

    for direction_name, direction in (
        ("forward", 1),
        ("reversed", -1),
    ):
        for shift in range(len(moons)):
            source_indices = np.asarray(
                [
                    (
                        shift
                        + direction * target_index
                    )
                    % len(moons)
                    for target_index in range(
                        len(moons)
                    )
                ],
                dtype=int,
            )

            assigned = observed[
                source_indices
            ]

            residuals = np.linalg.norm(
                assigned - model,
                axis=1,
            )

            rms = sqrt(
                float(
                    np.mean(
                        residuals * residuals
                    )
                )
            )

            candidates.append(
                (
                    rms,
                    float(np.max(residuals)),
                    direction_name,
                    shift,
                    source_indices,
                    residuals,
                )
            )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    best = candidates[0]
    second = candidates[1]

    (
        rms,
        maximum,
        direction_name,
        shift,
        source_indices,
        residuals,
    ) = best

    mapping = tuple(
        (
            moons[target_index].landmark_id,
            moons[int(source_index)].landmark_id,
        )
        for target_index, source_index in enumerate(
            source_indices
        )
    )

    residuals_by_target = tuple(
        (
            moons[index].landmark_id,
            float(residuals[index]),
        )
        for index in range(len(moons))
    )

    return MoonCorrespondence(
        direction=direction_name,
        shift=shift,
        rms_normalized=rms,
        maximum_normalized=maximum,
        second_best_rms_normalized=second[0],
        mapping=mapping,
        residuals_by_target=residuals_by_target,
    )


def analyze_star_correspondence(
    report: AffineCalibrationReport,
) -> StarCorrespondence:
    """Resolve spatial endpoint identities and analyse row-sequence geometry."""

    stars = tuple(
        item
        for item in report.landmarks
        if item.category == "star_endpoint"
    )

    if tuple(
        item.landmark_id
        for item in stars
    ) != STAR_IDS:
        raise ValueError(
            "Star landmarks do not match the fixed schema order."
        )

    points = np.asarray(
        [
            (
                item.normalized_x,
                item.normalized_y,
            )
            for item in stars
        ],
        dtype=float,
    )

    x = points[:, 0]
    y = points[:, 1]

    design = np.column_stack(
        (
            2.0 * x,
            2.0 * y,
            np.ones(len(stars)),
        )
    )

    right_hand_side = (
        x * x + y * y
    )

    solution, _, rank, _ = np.linalg.lstsq(
        design,
        right_hand_side,
        rcond=None,
    )

    if rank < 3:
        raise ValueError(
            "Star endpoints are degenerate for circle fitting."
        )

    centre_x = float(solution[0])
    centre_y = float(solution[1])
    constant = float(solution[2])

    radius_squared = (
        constant
        + centre_x * centre_x
        + centre_y * centre_y
    )

    if radius_squared <= 0.0:
        raise ValueError(
            "Star circle fit produced a non-positive radius."
        )

    fitted_radius = sqrt(
        radius_squared
    )

    centred = (
        points
        - np.asarray(
            (centre_x, centre_y)
        )
    )

    radii = np.linalg.norm(
        centred,
        axis=1,
    )

    angles = np.arctan2(
        centred[:, 1],
        centred[:, 0],
    )

    candidates: list[
        tuple[
            float,
            float,
            int,
            str,
            float,
        ]
    ] = []

    for step_size in (1, 2, 3):
        for direction_name, direction in (
            ("counter-clockwise", 1),
            ("clockwise", -1),
        ):
            step = (
                direction
                * tau
                * step_size
                / len(stars)
            )

            phase_samples = (
                angles
                - np.arange(len(stars))
                * step
            )

            phase = atan2(
                float(
                    np.mean(
                        np.sin(
                            phase_samples
                        )
                    )
                ),
                float(
                    np.mean(
                        np.cos(
                            phase_samples
                        )
                    )
                ),
            )

            predicted = (
                phase
                + np.arange(len(stars))
                * step
            )

            residuals = _wrap_angles(
                angles - predicted
            )

            angular_rms = degrees(
                sqrt(
                    float(
                        np.mean(
                            residuals * residuals
                        )
                    )
                )
            )

            angular_maximum = degrees(
                float(
                    np.max(
                        np.abs(residuals)
                    )
                )
            )

            candidates.append(
                (
                    angular_rms,
                    angular_maximum,
                    step_size,
                    direction_name,
                    phase,
                )
            )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1],
        )
    )

    best = candidates[0]
    second = candidates[1]

    (
        angular_rms,
        angular_maximum,
        step_size,
        direction_name,
        phase,
    ) = best

    notation = {
        1: "perimeter",
        2: "{7/2}",
        3: "{7/3}",
    }[step_size]

    # Anchor the spatial ordering to the actually observed
    # uppermost endpoint rather than to the exact angle pi/2.
    #
    # Using (angle - pi/2) % tau is numerically fragile: an
    # endpoint infinitesimally below pi/2 after CSV rounding or
    # affine inversion is wrapped to almost 2*pi and placed last.
    top_index = int(
        np.argmax(points[:, 1])
    )

    top_angle = float(
        angles[top_index]
    )

    angular_offset_from_top = (
        angles - top_angle
    ) % tau

    spatial_order = np.argsort(
        angular_offset_from_top,
        kind="stable",
    )

    spatial_mapping = tuple(
        (
            target_id,
            stars[int(source_index)].landmark_id,
        )
        for target_id, source_index in zip(
            STAR_IDS,
            spatial_order,
            strict=True,
        )
    )

    radial_residuals = (
        radii - fitted_radius
    )

    return StarCorrespondence(
        circle_centre_x=centre_x,
        circle_centre_y=centre_y,
        circle_centre_displacement=hypot(
            centre_x,
            centre_y,
        ),
        fitted_radius=fitted_radius,
        mean_radius=float(
            np.mean(radii)
        ),
        radial_rms=sqrt(
            float(
                np.mean(
                    radial_residuals
                    * radial_residuals
                )
            )
        ),
        radial_standard_deviation=float(
            np.std(radii)
        ),
        radius_minimum=float(
            np.min(radii)
        ),
        radius_maximum=float(
            np.max(radii)
        ),
        recorded_sequence_step_size=step_size,
        recorded_sequence_notation=notation,
        recorded_sequence_direction=direction_name,
        recorded_sequence_phase_degrees=degrees(
            phase
        ),
        recorded_sequence_angular_rms_degrees=(
            angular_rms
        ),
        recorded_sequence_angular_maximum_degrees=(
            angular_maximum
        ),
        second_best_angular_rms_degrees=second[0],
        spatial_mapping=spatial_mapping,
    )


def reassign_semantic_coordinates(
    rows: Sequence[dict[str, str]],
    mapping: Mapping[str, str],
) -> list[dict[str, str]]:
    """Apply a target-to-source coordinate mapping to CSV rows."""

    copied_rows = [
        dict(row)
        for row in rows
    ]

    by_identifier = {
        row["landmark_id"]: row
        for row in rows
    }

    if len(by_identifier) != len(rows):
        raise ValueError(
            "Digitisation landmark identifiers must be unique."
        )

    missing_targets = set(mapping).difference(
        by_identifier
    )

    missing_sources = set(
        mapping.values()
    ).difference(
        by_identifier
    )

    if missing_targets:
        raise ValueError(
            "Missing target landmarks: "
            + ", ".join(
                sorted(missing_targets)
            )
        )

    if missing_sources:
        raise ValueError(
            "Missing source landmarks: "
            + ", ".join(
                sorted(missing_sources)
            )
        )

    if len(set(mapping.values())) != len(mapping):
        raise ValueError(
            "Coordinate-source landmarks must be unique."
        )

    for corrected_row in copied_rows:
        target_id = corrected_row[
            "landmark_id"
        ]

        source_id = mapping.get(
            target_id
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


def _write_semantic_report(
    path: str | Path,
    *,
    moon: MoonCorrespondence,
    star: StarCorrespondence,
    files: Sequence[ResolvedFileRecord],
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# Figure 14 semantic correspondence resolution",
        "",
        "## Data layers",
        "",
        "The original digitisation files and the junction-corrected files",
        "remain unchanged. This layer reassigns only coordinate pairs to",
        "their resolved Moon-centre and spatial star-endpoint identities.",
        "",
        f"- Resolved passes: {len(files)}",
        "- Numerical coordinate values changed: no",
        "- Registration landmarks changed: no",
        "",
        "## Moon-centre correspondence",
        "",
        f"- Best cyclic direction: `{moon.direction}`",
        f"- Best cyclic shift: {moon.shift}",
        f"- Validation RMS after correspondence: {moon.rms_normalized:.9f} u",
        f"- Maximum validation residual: {moon.maximum_normalized:.9f} u",
        f"- Second-best cyclic RMS: {moon.second_best_rms_normalized:.9f} u",
        "",
        "| Target Moon identity | Coordinate source | Residual (u) |",
        "|---|---|---:|",
    ]

    residual_by_target = dict(
        moon.residuals_by_target
    )

    for target_id, source_id in moon.mapping:
        lines.append(
            "| "
            f"`{target_id}` | "
            f"`{source_id}` | "
            f"{residual_by_target[target_id]:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Star endpoint circle",
            "",
            (
                f"- Fitted centre: "
                f"({star.circle_centre_x:+.9f}, "
                f"{star.circle_centre_y:+.9f}) u"
            ),
            (
                f"- Centre displacement: "
                f"{star.circle_centre_displacement:.9f} u"
            ),
            f"- Mean radius: {star.mean_radius:.9f} u",
            f"- Radial RMS: {star.radial_rms:.9f} u",
            (
                f"- Radius range: "
                f"{star.radius_minimum:.9f}–"
                f"{star.radius_maximum:.9f} u"
            ),
            "",
            "## Star spatial correspondence",
            "",
            "| Spatial endpoint identity | Coordinate source |",
            "|---|---|",
        ]
    )

    for target_id, source_id in star.spatial_mapping:
        lines.append(
            f"| `{target_id}` | `{source_id}` |"
        )

    lines.extend(
        [
            "",
            "## Recorded endpoint sequence",
            "",
            (
                f"- Best regular-step consistency: "
                f"{star.recorded_sequence_notation} "
                f"{star.recorded_sequence_direction}"
            ),
            (
                f"- Angular RMS: "
                f"{star.recorded_sequence_angular_rms_degrees:.9f}°"
            ),
            (
                f"- Maximum angular residual: "
                f"{star.recorded_sequence_angular_maximum_degrees:.9f}°"
            ),
            (
                f"- Second-best candidate RMS: "
                f"{star.second_best_angular_rms_degrees:.9f}°"
            ),
            "",
            "### Interpretation boundary",
            "",
            "The recorded row sequence is strongly consistent with a clockwise",
            r"`{7/2}` step pattern. This is preserved as sequence-consistency",
            "evidence. It is not, by itself, treated as independent proof of",
            "the printed line topology because the digitiser originally used",
            "spatial endpoint descriptions rather than an explicit instruction",
            "to trace the connected star line.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path


def resolve_figure14_semantic_correspondence(
    *,
    schema_path: str | Path,
    input_directory: str | Path,
    output_directory: str | Path,
    expected_pass_count: int = 3,
    overwrite: bool = False,
    enforce_expected_mapping: bool = True,
) -> SemanticResolutionResult:
    """Create the correspondence-resolved Figure 14 calibration layer."""

    input_path = Path(input_directory)
    output_path = Path(output_directory)

    pass_paths = sorted(
        input_path.glob(
            DIGITISATION_GLOB
        )
    )

    if len(pass_paths) != expected_pass_count:
        raise ValueError(
            f"Expected {expected_pass_count} digitisation passes "
            f"in {input_path}; found {len(pass_paths)}."
        )

    calibration = derive_affine_registered_landmarks(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    moon = infer_moon_correspondence(
        calibration
    )

    star = analyze_star_correspondence(
        calibration
    )

    moon_mapping = dict(
        moon.mapping
    )

    star_mapping = dict(
        star.spatial_mapping
    )

    if enforce_expected_mapping:
        if (
            moon_mapping
            != EXPECTED_MOON_COORDINATE_SOURCE_BY_TARGET
        ):
            raise ValueError(
                "Derived Moon correspondence differs from "
                "the reviewed expected mapping."
            )

        if (
            star_mapping
            != EXPECTED_STAR_COORDINATE_SOURCE_BY_TARGET
        ):
            raise ValueError(
                "Derived star correspondence differs from "
                "the reviewed expected mapping."
            )

        if not (
            star.recorded_sequence_step_size == 2
            and star.recorded_sequence_direction
            == "clockwise"
        ):
            raise ValueError(
                "Recorded endpoint sequence is no longer best "
                "described by a clockwise {7/2} step."
            )

    combined_mapping = {
        **moon_mapping,
        **star_mapping,
    }

    manifest_path = (
        output_path
        / "semantic_correspondence_manifest.json"
    )

    report_path = (
        output_path
        / "semantic_correspondence_report.md"
    )

    planned_outputs = [
        output_path / path.name
        for path in pass_paths
    ] + [
        manifest_path,
        report_path,
    ]

    existing = [
        path
        for path in planned_outputs
        if path.exists()
    ]

    if existing and not overwrite:
        formatted = "\n".join(
            f"  {path}"
            for path in existing
        )

        raise FileExistsError(
            "Semantic-resolution outputs already exist:\n"
            f"{formatted}\n"
            "Use overwrite=True only after reviewing them."
        )

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    registration_categories = {
        "square_corner",
        "square_circle_junction",
    }

    file_records: list[
        ResolvedFileRecord
    ] = []

    for source_path in pass_paths:
        fieldnames, rows = _read_csv_table(
            source_path
        )

        resolved_rows = reassign_semantic_coordinates(
            rows,
            combined_mapping,
        )

        original_by_id = {
            row["landmark_id"]: row
            for row in rows
        }

        resolved_by_id = {
            row["landmark_id"]: row
            for row in resolved_rows
        }

        for landmark_id, original_row in (
            original_by_id.items()
        ):
            if (
                original_row["category"]
                not in registration_categories
            ):
                continue

            resolved_row = resolved_by_id[
                landmark_id
            ]

            if (
                resolved_row["pixel_x"]
                != original_row["pixel_x"]
                or resolved_row["pixel_y"]
                != original_row["pixel_y"]
            ):
                raise AssertionError(
                    "A registration landmark changed during "
                    "semantic correspondence resolution."
                )

        destination_path = (
            output_path / source_path.name
        )

        _write_csv_table(
            destination_path,
            fieldnames=fieldnames,
            rows=resolved_rows,
        )

        resolved_pass = load_digitisation_pass(
            destination_path
        )

        source_pass = load_digitisation_pass(
            source_path
        )

        if resolved_pass.pass_id != source_pass.pass_id:
            raise AssertionError(
                "Pass identifier changed during resolution."
            )

        file_records.append(
            ResolvedFileRecord(
                pass_id=source_pass.pass_id,
                input_path=source_path,
                output_path=destination_path,
                input_sha256=sha256_file(
                    source_path
                ),
                output_sha256=sha256_file(
                    destination_path
                ),
            )
        )

    reference = calibration.passes[0]

    manifest = {
        "schema_version": 1,
        "resolution_id": (
            "figure14-moon-star-semantic-correspondence-v1"
        ),
        "input_layer": "junction-corrected",
        "output_layer": "correspondence-resolved",
        "coordinate_only_reassignment": True,
        "numerical_coordinate_values_modified": False,
        "registration_landmarks_modified": False,
        "preceding_layers_modified": False,
        "source_image": {
            "filename": calibration.source_image,
            "sha256": calibration.source_image_sha256,
            "width_pixels": (
                calibration.image_width_pixels
            ),
            "height_pixels": (
                calibration.image_height_pixels
            ),
        },
        "registration_reference": {
            "model": "affine",
            "centroid_training_rms_pixels": (
                calibration.selected_fit.training_rms_pixels
            ),
            "centroid_loo_rms_pixels": (
                calibration.selected_fit.loo_rms_pixels
            ),
            "centroid_loo_maximum_pixels": (
                calibration.selected_fit.loo_maximum_pixels
            ),
            "anisotropy_ratio": (
                calibration.selected_fit.anisotropy_ratio
            ),
        },
        "moon_correspondence": {
            "search_space": (
                "All twelve forward cyclic shifts and all "
                "twelve reversed cyclic shifts."
            ),
            "best_direction": moon.direction,
            "best_shift": moon.shift,
            "rms_normalized": (
                moon.rms_normalized
            ),
            "maximum_normalized": (
                moon.maximum_normalized
            ),
            "second_best_rms_normalized": (
                moon.second_best_rms_normalized
            ),
            "coordinate_mapping": [
                {
                    "target_landmark_id": target_id,
                    "input_coordinate_source_landmark_id": (
                        source_id
                    ),
                    "residual_normalized": dict(
                        moon.residuals_by_target
                    )[target_id],
                }
                for target_id, source_id in moon.mapping
            ],
        },
        "star_correspondence": {
            "circle": {
                "centre_x": star.circle_centre_x,
                "centre_y": star.circle_centre_y,
                "centre_displacement": (
                    star.circle_centre_displacement
                ),
                "fitted_radius": star.fitted_radius,
                "mean_radius": star.mean_radius,
                "radial_rms": star.radial_rms,
                "radial_standard_deviation": (
                    star.radial_standard_deviation
                ),
                "radius_minimum": (
                    star.radius_minimum
                ),
                "radius_maximum": (
                    star.radius_maximum
                ),
            },
            "spatial_coordinate_mapping": [
                {
                    "target_landmark_id": target_id,
                    "input_coordinate_source_landmark_id": (
                        source_id
                    ),
                }
                for target_id, source_id
                in star.spatial_mapping
            ],
            "recorded_sequence_consistency": {
                "status": (
                    "sequence-consistency evidence; "
                    "not independent topology proof"
                ),
                "best_step_size": (
                    star.recorded_sequence_step_size
                ),
                "best_notation": (
                    star.recorded_sequence_notation
                ),
                "best_direction": (
                    star.recorded_sequence_direction
                ),
                "phase_degrees": (
                    star.recorded_sequence_phase_degrees
                ),
                "angular_rms_degrees": (
                    star.recorded_sequence_angular_rms_degrees
                ),
                "angular_maximum_degrees": (
                    star.recorded_sequence_angular_maximum_degrees
                ),
                "second_best_angular_rms_degrees": (
                    star.second_best_angular_rms_degrees
                ),
                "interpretation_boundary": (
                    "The digitiser used spatial endpoint descriptions "
                    "rather than an explicit connected-line tracing "
                    "instruction."
                ),
            },
        },
        "passes": [
            {
                "pass_id": record.pass_id,
                "input_filename": (
                    record.input_path.name
                ),
                "input_sha256": (
                    record.input_sha256
                ),
                "output_filename": (
                    record.output_path.name
                ),
                "output_sha256": (
                    record.output_sha256
                ),
            }
            for record in file_records
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

    _write_semantic_report(
        report_path,
        moon=moon,
        star=star,
        files=file_records,
    )

    return SemanticResolutionResult(
        output_directory=output_path,
        manifest_path=manifest_path,
        report_path=report_path,
        moon=moon,
        star=star,
        files=tuple(file_records),
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
    )
