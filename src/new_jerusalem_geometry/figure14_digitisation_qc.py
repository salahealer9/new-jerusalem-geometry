"""Quality control for repeated Figure 14 digitisation passes.

This module measures manual digitisation uncertainty before any geometric
registration or candidate fitting is attempted.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from math import hypot, sqrt
from pathlib import Path
from statistics import fmean, median
from typing import Sequence


LANDMARK_QC_FIELDNAMES = (
    "sequence_index",
    "landmark_id",
    "category",
    "description",
    "centroid_x",
    "centroid_y",
    "rms_dispersion_pixels",
    "maximum_deviation_pixels",
    "maximum_pairwise_separation_pixels",
    "spread_x_pixels",
    "spread_y_pixels",
    "robust_z_max_pairwise",
    "review_flag",
)

PASS_QC_FIELDNAMES = (
    "pass_id",
    "landmark_count",
    "mean_dx_pixels",
    "mean_dy_pixels",
    "drift_magnitude_pixels",
    "rms_residual_pixels",
    "drift_corrected_rms_pixels",
    "maximum_residual_pixels",
)

CATEGORY_QC_FIELDNAMES = (
    "category",
    "landmark_count",
    "mean_rms_dispersion_pixels",
    "median_rms_dispersion_pixels",
    "maximum_rms_dispersion_pixels",
    "mean_max_pairwise_pixels",
    "maximum_pairwise_pixels",
    "review_flag_count",
)


@dataclass(frozen=True, slots=True)
class DigitisedObservation:
    """One landmark observation from one independent pass."""

    pass_id: str
    sequence_index: int
    landmark_id: str
    category: str
    description: str
    pixel_x: float
    pixel_y: float


@dataclass(frozen=True, slots=True)
class DigitisationPass:
    """One complete independent digitisation pass."""

    path: Path
    pass_id: str
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    observations: tuple[DigitisedObservation, ...]


@dataclass(frozen=True, slots=True)
class LandmarkQC:
    """Repeated-click statistics for one landmark."""

    sequence_index: int
    landmark_id: str
    category: str
    description: str
    centroid_x: float
    centroid_y: float
    rms_dispersion_pixels: float
    maximum_deviation_pixels: float
    maximum_pairwise_separation_pixels: float
    spread_x_pixels: float
    spread_y_pixels: float
    robust_z_max_pairwise: float
    review_flag: bool


@dataclass(frozen=True, slots=True)
class PassQC:
    """Global displacement and residual statistics for one pass."""

    pass_id: str
    landmark_count: int
    mean_dx_pixels: float
    mean_dy_pixels: float
    drift_magnitude_pixels: float
    rms_residual_pixels: float
    drift_corrected_rms_pixels: float
    maximum_residual_pixels: float


@dataclass(frozen=True, slots=True)
class CategoryQC:
    """Aggregated uncertainty statistics for one landmark category."""

    category: str
    landmark_count: int
    mean_rms_dispersion_pixels: float
    median_rms_dispersion_pixels: float
    maximum_rms_dispersion_pixels: float
    mean_max_pairwise_pixels: float
    maximum_pairwise_pixels: float
    review_flag_count: int


@dataclass(frozen=True, slots=True)
class DigitisationQCReport:
    """Complete repeated-digitisation quality-control report."""

    passes: tuple[DigitisationPass, ...]
    landmarks: tuple[LandmarkQC, ...]
    pass_statistics: tuple[PassQC, ...]
    category_statistics: tuple[CategoryQC, ...]
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    overall_rms_dispersion_pixels: float
    median_landmark_rms_pixels: float
    maximum_pairwise_separation_pixels: float
    review_flag_count: int
    absolute_review_threshold_pixels: float
    robust_z_review_threshold: float


def _root_mean_square(values: Sequence[float]) -> float:
    if not values:
        return 0.0

    return sqrt(
        fmean(value * value for value in values)
    )


def _median_absolute_deviation(
    values: Sequence[float],
) -> float:
    if not values:
        return 0.0

    centre = median(values)

    return median(
        abs(value - centre)
        for value in values
    )


def load_digitisation_pass(
    path: str | Path,
) -> DigitisationPass:
    """Load and validate one digitisation-pass CSV."""

    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise ValueError(
            f"Digitisation pass is empty: {input_path}"
        )

    required_fields = {
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
    }

    missing = required_fields.difference(rows[0])

    if missing:
        raise ValueError(
            "Digitisation CSV is missing fields: "
            + ", ".join(sorted(missing))
        )

    pass_ids = {
        row["pass_id"]
        for row in rows
    }

    source_images = {
        row["source_image"]
        for row in rows
    }

    source_hashes = {
        row["source_image_sha256"]
        for row in rows
    }

    image_sizes = {
        (
            int(row["image_width_pixels"]),
            int(row["image_height_pixels"]),
        )
        for row in rows
    }

    if len(pass_ids) != 1:
        raise ValueError(
            f"Inconsistent pass IDs in {input_path}."
        )

    if len(source_images) != 1:
        raise ValueError(
            f"Inconsistent source images in {input_path}."
        )

    if len(source_hashes) != 1:
        raise ValueError(
            f"Inconsistent source hashes in {input_path}."
        )

    if len(image_sizes) != 1:
        raise ValueError(
            f"Inconsistent image dimensions in {input_path}."
        )

    observations = tuple(
        DigitisedObservation(
            pass_id=row["pass_id"],
            sequence_index=int(
                row["sequence_index"]
            ),
            landmark_id=row["landmark_id"],
            category=row["category"],
            description=row["description"],
            pixel_x=float(row["pixel_x"]),
            pixel_y=float(row["pixel_y"]),
        )
        for row in rows
    )

    expected_indices = tuple(
        range(len(observations))
    )

    observed_indices = tuple(
        observation.sequence_index
        for observation in observations
    )

    if observed_indices != expected_indices:
        raise ValueError(
            "Digitisation sequence indices must be contiguous "
            f"and begin at zero: {input_path}"
        )

    identifiers = tuple(
        observation.landmark_id
        for observation in observations
    )

    if len(set(identifiers)) != len(identifiers):
        raise ValueError(
            f"Duplicate landmark identifiers in {input_path}."
        )

    width, height = next(iter(image_sizes))

    for observation in observations:
        if not 0.0 <= observation.pixel_x <= width:
            raise ValueError(
                f"x coordinate outside image in {input_path}: "
                f"{observation.landmark_id}"
            )

        if not 0.0 <= observation.pixel_y <= height:
            raise ValueError(
                f"y coordinate outside image in {input_path}: "
                f"{observation.landmark_id}"
            )

    return DigitisationPass(
        path=input_path,
        pass_id=next(iter(pass_ids)),
        source_image=next(iter(source_images)),
        source_image_sha256=next(iter(source_hashes)),
        image_width_pixels=width,
        image_height_pixels=height,
        observations=observations,
    )


def analyze_digitisation_passes(
    paths: Sequence[str | Path],
    *,
    absolute_review_threshold_pixels: float = 5.0,
    robust_z_review_threshold: float = 3.5,
) -> DigitisationQCReport:
    """Analyse repeated Figure 14 digitisation passes."""

    if len(paths) < 2:
        raise ValueError(
            "At least two digitisation passes are required."
        )

    if absolute_review_threshold_pixels <= 0.0:
        raise ValueError(
            "Absolute review threshold must be positive."
        )

    if robust_z_review_threshold <= 0.0:
        raise ValueError(
            "Robust-z review threshold must be positive."
        )

    passes = tuple(
        load_digitisation_pass(path)
        for path in paths
    )

    pass_ids = tuple(
        item.pass_id
        for item in passes
    )

    if len(set(pass_ids)) != len(pass_ids):
        raise ValueError(
            "Digitisation pass identifiers must be unique."
        )

    reference = passes[0]

    for item in passes[1:]:
        if item.source_image != reference.source_image:
            raise ValueError(
                "All passes must use the same source image."
            )

        if (
            item.source_image_sha256
            != reference.source_image_sha256
        ):
            raise ValueError(
                "All passes must use the same source-image hash."
            )

        if (
            item.image_width_pixels
            != reference.image_width_pixels
            or item.image_height_pixels
            != reference.image_height_pixels
        ):
            raise ValueError(
                "All passes must use the same image dimensions."
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
                "Landmark ordering differs between passes."
            )

    provisional: list[dict[str, object]] = []

    for sequence_index in range(
        len(reference.observations)
    ):
        observations = tuple(
            item.observations[sequence_index]
            for item in passes
        )

        xs = tuple(
            observation.pixel_x
            for observation in observations
        )

        ys = tuple(
            observation.pixel_y
            for observation in observations
        )

        centroid_x = fmean(xs)
        centroid_y = fmean(ys)

        deviations = tuple(
            hypot(
                observation.pixel_x - centroid_x,
                observation.pixel_y - centroid_y,
            )
            for observation in observations
        )

        pairwise = tuple(
            hypot(
                first.pixel_x - second.pixel_x,
                first.pixel_y - second.pixel_y,
            )
            for first, second in combinations(
                observations,
                2,
            )
        )

        reference_observation = observations[0]

        provisional.append(
            {
                "sequence_index": sequence_index,
                "landmark_id": (
                    reference_observation.landmark_id
                ),
                "category": (
                    reference_observation.category
                ),
                "description": (
                    reference_observation.description
                ),
                "centroid_x": centroid_x,
                "centroid_y": centroid_y,
                "rms_dispersion_pixels": (
                    _root_mean_square(deviations)
                ),
                "maximum_deviation_pixels": max(
                    deviations
                ),
                "maximum_pairwise_separation_pixels": max(
                    pairwise
                ),
                "spread_x_pixels": max(xs) - min(xs),
                "spread_y_pixels": max(ys) - min(ys),
            }
        )

    pairwise_values = tuple(
        float(
            item[
                "maximum_pairwise_separation_pixels"
            ]
        )
        for item in provisional
    )

    pairwise_median = median(pairwise_values)
    pairwise_mad = _median_absolute_deviation(
        pairwise_values
    )

    landmarks: list[LandmarkQC] = []

    for item in provisional:
        max_pairwise = float(
            item[
                "maximum_pairwise_separation_pixels"
            ]
        )

        if pairwise_mad > 0.0:
            robust_z = (
                0.6744897501960817
                * (max_pairwise - pairwise_median)
                / pairwise_mad
            )
        else:
            robust_z = 0.0

        review_flag = (
            max_pairwise
            > absolute_review_threshold_pixels
            or robust_z
            > robust_z_review_threshold
        )

        landmarks.append(
            LandmarkQC(
                sequence_index=int(
                    item["sequence_index"]
                ),
                landmark_id=str(
                    item["landmark_id"]
                ),
                category=str(
                    item["category"]
                ),
                description=str(
                    item["description"]
                ),
                centroid_x=float(
                    item["centroid_x"]
                ),
                centroid_y=float(
                    item["centroid_y"]
                ),
                rms_dispersion_pixels=float(
                    item["rms_dispersion_pixels"]
                ),
                maximum_deviation_pixels=float(
                    item["maximum_deviation_pixels"]
                ),
                maximum_pairwise_separation_pixels=(
                    max_pairwise
                ),
                spread_x_pixels=float(
                    item["spread_x_pixels"]
                ),
                spread_y_pixels=float(
                    item["spread_y_pixels"]
                ),
                robust_z_max_pairwise=robust_z,
                review_flag=review_flag,
            )
        )

    landmark_tuple = tuple(landmarks)

    pass_statistics: list[PassQC] = []

    for pass_index, item in enumerate(passes):
        offsets = tuple(
            (
                observation.pixel_x
                - landmark_tuple[index].centroid_x,
                observation.pixel_y
                - landmark_tuple[index].centroid_y,
            )
            for index, observation in enumerate(
                item.observations
            )
        )

        mean_dx = fmean(
            offset[0]
            for offset in offsets
        )

        mean_dy = fmean(
            offset[1]
            for offset in offsets
        )

        residuals = tuple(
            hypot(dx, dy)
            for dx, dy in offsets
        )

        drift_corrected = tuple(
            hypot(
                dx - mean_dx,
                dy - mean_dy,
            )
            for dx, dy in offsets
        )

        pass_statistics.append(
            PassQC(
                pass_id=item.pass_id,
                landmark_count=len(offsets),
                mean_dx_pixels=mean_dx,
                mean_dy_pixels=mean_dy,
                drift_magnitude_pixels=hypot(
                    mean_dx,
                    mean_dy,
                ),
                rms_residual_pixels=(
                    _root_mean_square(residuals)
                ),
                drift_corrected_rms_pixels=(
                    _root_mean_square(
                        drift_corrected
                    )
                ),
                maximum_residual_pixels=max(
                    residuals
                ),
            )
        )

    by_category: dict[
        str,
        list[LandmarkQC],
    ] = defaultdict(list)

    for landmark in landmark_tuple:
        by_category[landmark.category].append(
            landmark
        )

    category_statistics = tuple(
        CategoryQC(
            category=category,
            landmark_count=len(items),
            mean_rms_dispersion_pixels=fmean(
                item.rms_dispersion_pixels
                for item in items
            ),
            median_rms_dispersion_pixels=median(
                item.rms_dispersion_pixels
                for item in items
            ),
            maximum_rms_dispersion_pixels=max(
                item.rms_dispersion_pixels
                for item in items
            ),
            mean_max_pairwise_pixels=fmean(
                item.maximum_pairwise_separation_pixels
                for item in items
            ),
            maximum_pairwise_pixels=max(
                item.maximum_pairwise_separation_pixels
                for item in items
            ),
            review_flag_count=sum(
                item.review_flag
                for item in items
            ),
        )
        for category, items in sorted(
            by_category.items()
        )
    )

    all_deviations = tuple(
        hypot(
            observation.pixel_x
            - landmark_tuple[index].centroid_x,
            observation.pixel_y
            - landmark_tuple[index].centroid_y,
        )
        for item in passes
        for index, observation in enumerate(
            item.observations
        )
    )

    return DigitisationQCReport(
        passes=passes,
        landmarks=landmark_tuple,
        pass_statistics=tuple(pass_statistics),
        category_statistics=category_statistics,
        source_image=reference.source_image,
        source_image_sha256=(
            reference.source_image_sha256
        ),
        image_width_pixels=reference.image_width_pixels,
        image_height_pixels=reference.image_height_pixels,
        overall_rms_dispersion_pixels=(
            _root_mean_square(all_deviations)
        ),
        median_landmark_rms_pixels=median(
            landmark.rms_dispersion_pixels
            for landmark in landmark_tuple
        ),
        maximum_pairwise_separation_pixels=max(
            landmark.maximum_pairwise_separation_pixels
            for landmark in landmark_tuple
        ),
        review_flag_count=sum(
            landmark.review_flag
            for landmark in landmark_tuple
        ),
        absolute_review_threshold_pixels=(
            absolute_review_threshold_pixels
        ),
        robust_z_review_threshold=(
            robust_z_review_threshold
        ),
    )


def _format_float(value: float) -> str:
    return format(value, ".9f")


def write_landmark_qc_csv(
    path: str | Path,
    report: DigitisationQCReport,
) -> Path:
    """Write per-landmark uncertainty statistics."""

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
            fieldnames=LANDMARK_QC_FIELDNAMES,
        )

        writer.writeheader()

        for item in report.landmarks:
            writer.writerow(
                {
                    "sequence_index": item.sequence_index,
                    "landmark_id": item.landmark_id,
                    "category": item.category,
                    "description": item.description,
                    "centroid_x": _format_float(
                        item.centroid_x
                    ),
                    "centroid_y": _format_float(
                        item.centroid_y
                    ),
                    "rms_dispersion_pixels": _format_float(
                        item.rms_dispersion_pixels
                    ),
                    "maximum_deviation_pixels": _format_float(
                        item.maximum_deviation_pixels
                    ),
                    "maximum_pairwise_separation_pixels": (
                        _format_float(
                            item.maximum_pairwise_separation_pixels
                        )
                    ),
                    "spread_x_pixels": _format_float(
                        item.spread_x_pixels
                    ),
                    "spread_y_pixels": _format_float(
                        item.spread_y_pixels
                    ),
                    "robust_z_max_pairwise": _format_float(
                        item.robust_z_max_pairwise
                    ),
                    "review_flag": (
                        "true"
                        if item.review_flag
                        else "false"
                    ),
                }
            )

    return output_path


def write_pass_qc_csv(
    path: str | Path,
    report: DigitisationQCReport,
) -> Path:
    """Write per-pass drift and residual statistics."""

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
            fieldnames=PASS_QC_FIELDNAMES,
        )

        writer.writeheader()

        for item in report.pass_statistics:
            writer.writerow(
                {
                    "pass_id": item.pass_id,
                    "landmark_count": item.landmark_count,
                    "mean_dx_pixels": _format_float(
                        item.mean_dx_pixels
                    ),
                    "mean_dy_pixels": _format_float(
                        item.mean_dy_pixels
                    ),
                    "drift_magnitude_pixels": _format_float(
                        item.drift_magnitude_pixels
                    ),
                    "rms_residual_pixels": _format_float(
                        item.rms_residual_pixels
                    ),
                    "drift_corrected_rms_pixels": _format_float(
                        item.drift_corrected_rms_pixels
                    ),
                    "maximum_residual_pixels": _format_float(
                        item.maximum_residual_pixels
                    ),
                }
            )

    return output_path


def write_category_qc_csv(
    path: str | Path,
    report: DigitisationQCReport,
) -> Path:
    """Write uncertainty summaries by landmark category."""

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
            fieldnames=CATEGORY_QC_FIELDNAMES,
        )

        writer.writeheader()

        for item in report.category_statistics:
            writer.writerow(
                {
                    "category": item.category,
                    "landmark_count": item.landmark_count,
                    "mean_rms_dispersion_pixels": _format_float(
                        item.mean_rms_dispersion_pixels
                    ),
                    "median_rms_dispersion_pixels": _format_float(
                        item.median_rms_dispersion_pixels
                    ),
                    "maximum_rms_dispersion_pixels": _format_float(
                        item.maximum_rms_dispersion_pixels
                    ),
                    "mean_max_pairwise_pixels": _format_float(
                        item.mean_max_pairwise_pixels
                    ),
                    "maximum_pairwise_pixels": _format_float(
                        item.maximum_pairwise_pixels
                    ),
                    "review_flag_count": (
                        item.review_flag_count
                    ),
                }
            )

    return output_path


def write_qc_markdown(
    path: str | Path,
    report: DigitisationQCReport,
) -> Path:
    """Write a human-readable repeated-digitisation QC report."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ranked = sorted(
        report.landmarks,
        key=lambda item: (
            item.maximum_pairwise_separation_pixels
        ),
        reverse=True,
    )

    status = (
        "REVIEW"
        if report.review_flag_count
        else "PASS"
    )

    lines = [
        "# Figure 14 digitisation quality control",
        "",
        f"Status: **{status}**",
        "",
        "## Dataset",
        "",
        f"- Independent passes: {len(report.passes)}",
        f"- Landmarks per pass: {len(report.landmarks)}",
        (
            f"- Total measured points: "
            f"{len(report.passes) * len(report.landmarks)}"
        ),
        f"- Source image: `{report.source_image}`",
        (
            f"- Source SHA-256: "
            f"`{report.source_image_sha256}`"
        ),
        (
            f"- Image dimensions: "
            f"{report.image_width_pixels} × "
            f"{report.image_height_pixels} pixels"
        ),
        "",
        "## Overall uncertainty",
        "",
        (
            f"- Overall RMS click dispersion: "
            f"{report.overall_rms_dispersion_pixels:.6f} px"
        ),
        (
            f"- Median landmark RMS dispersion: "
            f"{report.median_landmark_rms_pixels:.6f} px"
        ),
        (
            f"- Maximum pairwise separation: "
            f"{report.maximum_pairwise_separation_pixels:.6f} px"
        ),
        (
            f"- Review-flagged landmarks: "
            f"{report.review_flag_count}"
        ),
        "",
        "A review flag is diagnostic rather than a rejection. It is set when",
        "either:",
        "",
        (
            f"- maximum pairwise separation exceeds "
            f"{report.absolute_review_threshold_pixels:.3f} px; or"
        ),
        (
            f"- robust z-score exceeds "
            f"{report.robust_z_review_threshold:.3f}."
        ),
        "",
        "## Pass-level statistics",
        "",
        "| Pass | Mean dx (px) | Mean dy (px) | Drift (px) | RMS (px) | Drift-corrected RMS (px) | Maximum (px) |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]

    for item in report.pass_statistics:
        lines.append(
            "| "
            f"{item.pass_id} | "
            f"{item.mean_dx_pixels:.6f} | "
            f"{item.mean_dy_pixels:.6f} | "
            f"{item.drift_magnitude_pixels:.6f} | "
            f"{item.rms_residual_pixels:.6f} | "
            f"{item.drift_corrected_rms_pixels:.6f} | "
            f"{item.maximum_residual_pixels:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Category-level statistics",
            "",
            "| Category | N | Mean RMS (px) | Median RMS (px) | Maximum RMS (px) | Maximum pairwise (px) | Flags |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for item in report.category_statistics:
        lines.append(
            "| "
            f"{item.category} | "
            f"{item.landmark_count} | "
            f"{item.mean_rms_dispersion_pixels:.6f} | "
            f"{item.median_rms_dispersion_pixels:.6f} | "
            f"{item.maximum_rms_dispersion_pixels:.6f} | "
            f"{item.maximum_pairwise_pixels:.6f} | "
            f"{item.review_flag_count} |"
        )

    lines.extend(
        [
            "",
            "## Largest repeated-click separations",
            "",
            "| Rank | Landmark | Category | RMS (px) | Maximum pairwise (px) | Robust z | Review |",
            "|---:|---|---|---:|---:|---:|:---:|",
        ]
    )

    for rank, item in enumerate(
        ranked[:10],
        start=1,
    ):
        lines.append(
            "| "
            f"{rank} | "
            f"`{item.landmark_id}` | "
            f"{item.category} | "
            f"{item.rms_dispersion_pixels:.6f} | "
            f"{item.maximum_pairwise_separation_pixels:.6f} | "
            f"{item.robust_z_max_pairwise:.6f} | "
            f"{'yes' if item.review_flag else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "These statistics measure repeated manual clicking only. They do not",
            "yet include printed-line thickness, scan distortion, registration",
            "uncertainty, or disagreement between the historical plate and any",
            "candidate geometric model.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
