"""Export source-calibrated Figure 14 landmarks.

The selected primary registration is the affine transformation fitted to
the centroid of the three corrected digitisation passes.

The forward transformation maps normalised diagram coordinates into
Cartesian rendered-pixel coordinates. Rendered image y coordinates are
converted from y-down to y-up before fitting.

For each landmark, this module records:

- the repeated-click pixel centroid;
- its position under the selected centroid affine inverse;
- repeated-click uncertainty under the fixed centroid registration;
- pass-to-pass variation after each pass receives its own affine fit;
- residual from the predefined model coordinate, where one exists.

No heptagram candidate is fitted here.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from math import hypot, sqrt
from pathlib import Path
from statistics import fmean
from typing import Sequence

import numpy as np

from .figure14_digitisation import (
    LandmarkDefinition,
    read_landmark_schema_csv,
)
from .figure14_digitisation_qc import (
    DigitisationPass,
    load_digitisation_pass,
)
from .figure14_registration import (
    RegistrationFit,
    RegistrationModel,
    analyze_registration,
    apply_registration_matrix,
    pixel_to_cartesian,
)


REGISTERED_LANDMARK_FIELDS = (
    "sequence_index",
    "landmark_id",
    "category",
    "registration_role",
    "description",
    "pixel_centroid_x",
    "pixel_centroid_y",
    "normalized_x",
    "normalized_y",
    "pass_registered_centroid_x",
    "pass_registered_centroid_y",
    "click_rms_pixels",
    "click_rms_normalized",
    "pass_registered_rms_normalized",
    "model_x",
    "model_y",
    "model_delta_x",
    "model_delta_y",
    "model_residual_normalized",
)

AFFINE_SUMMARY_FIELDS = (
    "selected_model",
    "independent_pass_count",
    "landmark_count",
    "registration_landmark_count",
    "training_rms_pixels",
    "training_maximum_pixels",
    "loo_rms_pixels",
    "loo_maximum_pixels",
    "anisotropy_ratio",
    "linear_determinant",
    "pixels_per_unit_maximum",
    "pixels_per_unit_minimum",
    "mean_pixels_per_unit",
    "units_per_pixel_maximum",
    "overall_click_rms_pixels",
    "overall_click_rms_normalized",
    "overall_pass_registered_rms_normalized",
    "maximum_model_residual_normalized",
)


@dataclass(frozen=True, slots=True)
class RegisteredLandmark:
    """One source-derived Figure 14 landmark."""

    sequence_index: int
    landmark_id: str
    category: str
    registration_role: str
    description: str
    pixel_centroid_x: float
    pixel_centroid_y: float
    normalized_x: float
    normalized_y: float
    pass_registered_centroid_x: float
    pass_registered_centroid_y: float
    click_rms_pixels: float
    click_rms_normalized: float
    pass_registered_rms_normalized: float
    model_x: float | None
    model_y: float | None
    model_delta_x: float | None
    model_delta_y: float | None
    model_residual_normalized: float | None


@dataclass(frozen=True, slots=True)
class AffineCalibrationReport:
    """Selected affine transformation and registered landmarks."""

    selected_fit: RegistrationFit
    forward_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    inverse_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    passes: tuple[DigitisationPass, ...]
    landmarks: tuple[RegisteredLandmark, ...]
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    singular_value_max: float
    singular_value_min: float
    mean_pixels_per_unit: float
    units_per_pixel_maximum: float
    overall_click_rms_pixels: float
    overall_click_rms_normalized: float
    overall_pass_registered_rms_normalized: float
    maximum_model_residual_normalized: float


def _matrix_tuple(
    matrix: np.ndarray,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:
    return tuple(
        tuple(
            float(value)
            for value in row
        )
        for row in matrix
    )  # type: ignore[return-value]


def _rms_distances(
    points: np.ndarray,
    centre: np.ndarray,
) -> float:
    if len(points) == 0:
        return 0.0

    distances = np.linalg.norm(
        points - centre,
        axis=1,
    )

    return sqrt(
        fmean(
            float(value) ** 2
            for value in distances
        )
    )


def _registration_role(
    landmark: LandmarkDefinition,
) -> str:
    if landmark.registration_default:
        return "registration"

    if landmark.category == "moon_centre":
        return "validation"

    if landmark.category == "star_endpoint":
        return "target"

    return "observation"


def _load_and_validate_passes(
    paths: Sequence[str | Path],
) -> tuple[DigitisationPass, ...]:
    if len(paths) < 2:
        raise ValueError(
            "At least two corrected digitisation passes are required."
        )

    passes = tuple(
        load_digitisation_pass(path)
        for path in paths
    )

    reference = passes[0]

    pass_ids = tuple(
        item.pass_id
        for item in passes
    )

    if len(set(pass_ids)) != len(pass_ids):
        raise ValueError(
            "Digitisation pass identifiers must be unique."
        )

    reference_identity = tuple(
        (
            item.sequence_index,
            item.landmark_id,
            item.category,
        )
        for item in reference.observations
    )

    for item in passes[1:]:
        if (
            item.source_image_sha256
            != reference.source_image_sha256
        ):
            raise ValueError(
                "Corrected passes use different source-image hashes."
            )

        if (
            item.image_width_pixels
            != reference.image_width_pixels
            or item.image_height_pixels
            != reference.image_height_pixels
        ):
            raise ValueError(
                "Corrected passes use different image dimensions."
            )

        identity = tuple(
            (
                observation.sequence_index,
                observation.landmark_id,
                observation.category,
            )
            for observation in item.observations
        )

        if identity != reference_identity:
            raise ValueError(
                "Landmark ordering differs between corrected passes."
            )

    return passes


def derive_affine_registered_landmarks(
    *,
    schema_path: str | Path,
    pass_paths: Sequence[str | Path],
) -> AffineCalibrationReport:
    """Derive all Figure 14 landmarks under the selected affine fit."""

    schema = read_landmark_schema_csv(
        schema_path
    )

    passes = _load_and_validate_passes(
        pass_paths
    )

    if len(schema) != len(passes[0].observations):
        raise ValueError(
            "Schema and digitisation landmark counts differ."
        )

    schema_identity = tuple(
        (
            item.sequence_index,
            item.landmark_id,
            item.category,
        )
        for item in schema
    )

    pass_identity = tuple(
        (
            item.sequence_index,
            item.landmark_id,
            item.category,
        )
        for item in passes[0].observations
    )

    if schema_identity != pass_identity:
        raise ValueError(
            "Schema and corrected-pass landmark ordering differ."
        )

    registration_report = analyze_registration(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    selected_fit = next(
        fit
        for fit in registration_report.fits
        if (
            fit.dataset_id == "centroid"
            and fit.model is RegistrationModel.AFFINE
        )
    )

    pass_affine_fits = {
        fit.dataset_id: fit
        for fit in registration_report.fits
        if (
            fit.dataset_id != "centroid"
            and fit.model is RegistrationModel.AFFINE
        )
    }

    expected_pass_ids = {
        item.pass_id
        for item in passes
    }

    if set(pass_affine_fits) != expected_pass_ids:
        raise AssertionError(
            "A pass-specific affine fit is missing."
        )

    forward_matrix_array = np.asarray(
        selected_fit.matrix,
        dtype=float,
    )

    inverse_matrix_array = np.linalg.inv(
        forward_matrix_array
    )

    linear = forward_matrix_array[:2, :2]

    singular_values = np.linalg.svd(
        linear,
        compute_uv=False,
    )

    singular_value_max = float(
        max(singular_values)
    )

    singular_value_min = float(
        min(singular_values)
    )

    if singular_value_min <= 0.0:
        raise ValueError(
            "Selected affine transformation is singular."
        )

    by_pass = tuple(
        {
            observation.landmark_id: observation
            for observation in item.observations
        }
        for item in passes
    )

    pass_inverse_matrices = {
        pass_id: np.linalg.inv(
            np.asarray(
                fit.matrix,
                dtype=float,
            )
        )
        for pass_id, fit in pass_affine_fits.items()
    }

    registered: list[
        RegisteredLandmark
    ] = []

    all_pixel_deviations: list[float] = []
    all_canonical_deviations: list[float] = []
    all_pass_registered_deviations: list[float] = []

    for definition in schema:
        repeated_observations = tuple(
            mapping[definition.landmark_id]
            for mapping in by_pass
        )

        pixel_points = np.asarray(
            [
                (
                    observation.pixel_x,
                    observation.pixel_y,
                )
                for observation in repeated_observations
            ],
            dtype=float,
        )

        pixel_centroid = pixel_points.mean(
            axis=0
        )

        pixel_deviations = np.linalg.norm(
            pixel_points - pixel_centroid,
            axis=1,
        )

        all_pixel_deviations.extend(
            float(value)
            for value in pixel_deviations
        )

        cartesian_points = np.asarray(
            [
                pixel_to_cartesian(
                    observation.pixel_x,
                    observation.pixel_y,
                    passes[0].image_height_pixels,
                )
                for observation in repeated_observations
            ],
            dtype=float,
        )

        canonical_normalized_points = (
            apply_registration_matrix(
                inverse_matrix_array,
                cartesian_points,
            )
        )

        canonical_centroid = (
            canonical_normalized_points.mean(
                axis=0
            )
        )

        canonical_deviations = np.linalg.norm(
            canonical_normalized_points
            - canonical_centroid,
            axis=1,
        )

        all_canonical_deviations.extend(
            float(value)
            for value in canonical_deviations
        )

        pass_registered_points = []

        for digitisation_pass, observation in zip(
            passes,
            repeated_observations,
            strict=True,
        ):
            cartesian_point = np.asarray(
                [
                    pixel_to_cartesian(
                        observation.pixel_x,
                        observation.pixel_y,
                        digitisation_pass.image_height_pixels,
                    )
                ],
                dtype=float,
            )

            normalized_point = (
                apply_registration_matrix(
                    pass_inverse_matrices[
                        digitisation_pass.pass_id
                    ],
                    cartesian_point,
                )[0]
            )

            pass_registered_points.append(
                normalized_point
            )

        pass_registered_array = np.asarray(
            pass_registered_points,
            dtype=float,
        )

        pass_registered_centroid = (
            pass_registered_array.mean(
                axis=0
            )
        )

        pass_registered_deviations = np.linalg.norm(
            pass_registered_array
            - pass_registered_centroid,
            axis=1,
        )

        all_pass_registered_deviations.extend(
            float(value)
            for value in pass_registered_deviations
        )

        if (
            definition.model_x is not None
            and definition.model_y is not None
        ):
            model_delta_x = (
                float(canonical_centroid[0])
                - definition.model_x
            )

            model_delta_y = (
                float(canonical_centroid[1])
                - definition.model_y
            )

            model_residual = hypot(
                model_delta_x,
                model_delta_y,
            )
        else:
            model_delta_x = None
            model_delta_y = None
            model_residual = None

        registered.append(
            RegisteredLandmark(
                sequence_index=(
                    definition.sequence_index
                ),
                landmark_id=definition.landmark_id,
                category=definition.category,
                registration_role=(
                    _registration_role(
                        definition
                    )
                ),
                description=definition.description,
                pixel_centroid_x=float(
                    pixel_centroid[0]
                ),
                pixel_centroid_y=float(
                    pixel_centroid[1]
                ),
                normalized_x=float(
                    canonical_centroid[0]
                ),
                normalized_y=float(
                    canonical_centroid[1]
                ),
                pass_registered_centroid_x=float(
                    pass_registered_centroid[0]
                ),
                pass_registered_centroid_y=float(
                    pass_registered_centroid[1]
                ),
                click_rms_pixels=_rms_distances(
                    pixel_points,
                    pixel_centroid,
                ),
                click_rms_normalized=(
                    _rms_distances(
                        canonical_normalized_points,
                        canonical_centroid,
                    )
                ),
                pass_registered_rms_normalized=(
                    _rms_distances(
                        pass_registered_array,
                        pass_registered_centroid,
                    )
                ),
                model_x=definition.model_x,
                model_y=definition.model_y,
                model_delta_x=model_delta_x,
                model_delta_y=model_delta_y,
                model_residual_normalized=(
                    model_residual
                ),
            )
        )

    model_residuals = tuple(
        item.model_residual_normalized
        for item in registered
        if item.model_residual_normalized is not None
    )

    reference = passes[0]

    return AffineCalibrationReport(
        selected_fit=selected_fit,
        forward_matrix=_matrix_tuple(
            forward_matrix_array
        ),
        inverse_matrix=_matrix_tuple(
            inverse_matrix_array
        ),
        passes=passes,
        landmarks=tuple(registered),
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
        singular_value_max=singular_value_max,
        singular_value_min=singular_value_min,
        mean_pixels_per_unit=fmean(
            (
                singular_value_max,
                singular_value_min,
            )
        ),
        units_per_pixel_maximum=(
            1.0 / singular_value_min
        ),
        overall_click_rms_pixels=sqrt(
            fmean(
                value * value
                for value in all_pixel_deviations
            )
        ),
        overall_click_rms_normalized=sqrt(
            fmean(
                value * value
                for value in all_canonical_deviations
            )
        ),
        overall_pass_registered_rms_normalized=sqrt(
            fmean(
                value * value
                for value in all_pass_registered_deviations
            )
        ),
        maximum_model_residual_normalized=max(
            model_residuals
        ),
    )


def _format_optional_float(
    value: float | None,
) -> str:
    if value is None:
        return ""

    return format(value, ".12f")


def write_registered_landmarks_csv(
    path: str | Path,
    report: AffineCalibrationReport,
) -> Path:
    """Write all 31 calibrated landmark centroids."""

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
            fieldnames=REGISTERED_LANDMARK_FIELDS,
        )

        writer.writeheader()

        for item in report.landmarks:
            writer.writerow(
                {
                    "sequence_index": item.sequence_index,
                    "landmark_id": item.landmark_id,
                    "category": item.category,
                    "registration_role": (
                        item.registration_role
                    ),
                    "description": item.description,
                    "pixel_centroid_x": (
                        _format_optional_float(
                            item.pixel_centroid_x
                        )
                    ),
                    "pixel_centroid_y": (
                        _format_optional_float(
                            item.pixel_centroid_y
                        )
                    ),
                    "normalized_x": (
                        _format_optional_float(
                            item.normalized_x
                        )
                    ),
                    "normalized_y": (
                        _format_optional_float(
                            item.normalized_y
                        )
                    ),
                    "pass_registered_centroid_x": (
                        _format_optional_float(
                            item.pass_registered_centroid_x
                        )
                    ),
                    "pass_registered_centroid_y": (
                        _format_optional_float(
                            item.pass_registered_centroid_y
                        )
                    ),
                    "click_rms_pixels": (
                        _format_optional_float(
                            item.click_rms_pixels
                        )
                    ),
                    "click_rms_normalized": (
                        _format_optional_float(
                            item.click_rms_normalized
                        )
                    ),
                    "pass_registered_rms_normalized": (
                        _format_optional_float(
                            item.pass_registered_rms_normalized
                        )
                    ),
                    "model_x": (
                        _format_optional_float(
                            item.model_x
                        )
                    ),
                    "model_y": (
                        _format_optional_float(
                            item.model_y
                        )
                    ),
                    "model_delta_x": (
                        _format_optional_float(
                            item.model_delta_x
                        )
                    ),
                    "model_delta_y": (
                        _format_optional_float(
                            item.model_delta_y
                        )
                    ),
                    "model_residual_normalized": (
                        _format_optional_float(
                            item.model_residual_normalized
                        )
                    ),
                }
            )

    return output_path


def write_affine_summary_csv(
    path: str | Path,
    report: AffineCalibrationReport,
) -> Path:
    """Write a one-row selected-calibration summary."""

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
            fieldnames=AFFINE_SUMMARY_FIELDS,
        )

        writer.writeheader()

        writer.writerow(
            {
                "selected_model": "affine",
                "independent_pass_count": len(
                    report.passes
                ),
                "landmark_count": len(
                    report.landmarks
                ),
                "registration_landmark_count": len(
                    report.selected_fit.landmark_ids
                ),
                "training_rms_pixels": (
                    _format_optional_float(
                        report.selected_fit.training_rms_pixels
                    )
                ),
                "training_maximum_pixels": (
                    _format_optional_float(
                        report.selected_fit.training_maximum_pixels
                    )
                ),
                "loo_rms_pixels": (
                    _format_optional_float(
                        report.selected_fit.loo_rms_pixels
                    )
                ),
                "loo_maximum_pixels": (
                    _format_optional_float(
                        report.selected_fit.loo_maximum_pixels
                    )
                ),
                "anisotropy_ratio": (
                    _format_optional_float(
                        report.selected_fit.anisotropy_ratio
                    )
                ),
                "linear_determinant": (
                    _format_optional_float(
                        report.selected_fit.linear_determinant
                    )
                ),
                "pixels_per_unit_maximum": (
                    _format_optional_float(
                        report.singular_value_max
                    )
                ),
                "pixels_per_unit_minimum": (
                    _format_optional_float(
                        report.singular_value_min
                    )
                ),
                "mean_pixels_per_unit": (
                    _format_optional_float(
                        report.mean_pixels_per_unit
                    )
                ),
                "units_per_pixel_maximum": (
                    _format_optional_float(
                        report.units_per_pixel_maximum
                    )
                ),
                "overall_click_rms_pixels": (
                    _format_optional_float(
                        report.overall_click_rms_pixels
                    )
                ),
                "overall_click_rms_normalized": (
                    _format_optional_float(
                        report.overall_click_rms_normalized
                    )
                ),
                "overall_pass_registered_rms_normalized": (
                    _format_optional_float(
                        report.overall_pass_registered_rms_normalized
                    )
                ),
                "maximum_model_residual_normalized": (
                    _format_optional_float(
                        report.maximum_model_residual_normalized
                    )
                ),
            }
        )

    return output_path


def write_affine_matrix_json(
    path: str | Path,
    report: AffineCalibrationReport,
) -> Path:
    """Write deterministic affine-calibration metadata and matrices."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "schema_version": 1,
        "selected_model": "affine",
        "selection_status": "primary",
        "selection_basis": {
            "criterion": (
                "Lowest centroid leave-one-landmark-out RMS "
                "with stable performance across all three "
                "independent passes."
            ),
            "centroid_training_rms_pixels": (
                report.selected_fit.training_rms_pixels
            ),
            "centroid_loo_rms_pixels": (
                report.selected_fit.loo_rms_pixels
            ),
            "centroid_loo_maximum_pixels": (
                report.selected_fit.loo_maximum_pixels
            ),
            "anisotropy_ratio": (
                report.selected_fit.anisotropy_ratio
            ),
        },
        "coordinate_systems": {
            "model": (
                "Normalised diagram coordinates in units u, "
                "with positive y upward."
            ),
            "cartesian_pixel": (
                "Rendered pixel coordinates with positive y upward."
            ),
            "rendered_pixel": (
                "Original PNG coordinates with positive y downward."
            ),
        },
        "source_image": {
            "filename": report.source_image,
            "sha256": report.source_image_sha256,
            "width_pixels": report.image_width_pixels,
            "height_pixels": report.image_height_pixels,
        },
        "independent_pass_ids": [
            item.pass_id
            for item in report.passes
        ],
        "forward_model_to_cartesian_pixel": [
            list(row)
            for row in report.forward_matrix
        ],
        "inverse_cartesian_pixel_to_model": [
            list(row)
            for row in report.inverse_matrix
        ],
        "linear_scale_diagnostics": {
            "pixels_per_unit_maximum": (
                report.singular_value_max
            ),
            "pixels_per_unit_minimum": (
                report.singular_value_min
            ),
            "mean_pixels_per_unit": (
                report.mean_pixels_per_unit
            ),
            "units_per_pixel_maximum": (
                report.units_per_pixel_maximum
            ),
        },
        "uncertainty": {
            "overall_click_rms_pixels": (
                report.overall_click_rms_pixels
            ),
            "overall_click_rms_normalized": (
                report.overall_click_rms_normalized
            ),
            "overall_pass_registered_rms_normalized": (
                report.overall_pass_registered_rms_normalized
            ),
        },
    }

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path


def write_affine_calibration_markdown(
    path: str | Path,
    report: AffineCalibrationReport,
) -> Path:
    """Write the selected affine-calibration report."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    by_category: dict[
        str,
        list[RegisteredLandmark],
    ] = {}

    for item in report.landmarks:
        by_category.setdefault(
            item.category,
            [],
        ).append(item)

    lines = [
        "# Figure 14 selected affine calibration",
        "",
        "## Selection",
        "",
        "The affine registration is selected as the primary Figure 14",
        "plate calibration.",
        "",
        f"- Training RMS: {report.selected_fit.training_rms_pixels:.6f} px",
        f"- Leave-one-out RMS: {report.selected_fit.loo_rms_pixels:.6f} px",
        f"- Leave-one-out maximum: {report.selected_fit.loo_maximum_pixels:.6f} px",
        f"- Anisotropy ratio: {report.selected_fit.anisotropy_ratio:.9f}",
        "",
        "The projective model slightly reduced training residual but had",
        "worse leave-one-landmark-out prediction. The similarity model",
        "left materially larger systematic residuals.",
        "",
        "## Scale and uncertainty",
        "",
        f"- Maximum directional scale: {report.singular_value_max:.6f} px/u",
        f"- Minimum directional scale: {report.singular_value_min:.6f} px/u",
        f"- Mean directional scale: {report.mean_pixels_per_unit:.6f} px/u",
        f"- Overall repeated-click RMS: {report.overall_click_rms_pixels:.6f} px",
        (
            "- Overall repeated-click RMS after the fixed affine inverse: "
            f"{report.overall_click_rms_normalized:.9f} u"
        ),
        (
            "- Overall pass-specific registered variation: "
            f"{report.overall_pass_registered_rms_normalized:.9f} u"
        ),
        "",
        "## Landmark categories",
        "",
        "| Category | N | Mean click RMS (px) | Mean click RMS (u) | Mean pass-registered RMS (u) |",
        "|---|---:|---:|---:|---:|",
    ]

    for category, items in sorted(
        by_category.items()
    ):
        lines.append(
            "| "
            f"{category} | "
            f"{len(items)} | "
            f"{fmean(item.click_rms_pixels for item in items):.6f} | "
            f"{fmean(item.click_rms_normalized for item in items):.9f} | "
            f"{fmean(item.pass_registered_rms_normalized for item in items):.9f} |"
        )

    model_ranked = sorted(
        (
            item
            for item in report.landmarks
            if item.model_residual_normalized is not None
        ),
        key=lambda item: (
            item.model_residual_normalized
            if item.model_residual_normalized is not None
            else -1.0
        ),
        reverse=True,
    )

    lines.extend(
        [
            "",
            "## Largest residuals from predefined schema coordinates",
            "",
            "| Rank | Landmark | Role | Residual (u) |",
            "|---:|---|---|---:|",
        ]
    )

    for rank, item in enumerate(
        model_ranked[:10],
        start=1,
    ):
        lines.append(
            "| "
            f"{rank} | "
            f"`{item.landmark_id}` | "
            f"{item.registration_role} | "
            f"{item.model_residual_normalized:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The normalized star endpoints are source observations. They have",
            "not yet been fitted to a regular heptagram, Michell scaffold,",
            "or any Figure-14-specific candidate construction.",
            "",
            "Moon-centre residuals are validation evidence and do not influence",
            "the selected affine registration.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
