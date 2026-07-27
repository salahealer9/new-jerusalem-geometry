"""Plate-registration models for Michell's Figure 14.

Registration is fitted from normalised project coordinates to rendered
source-image coordinates using the twelve default registration landmarks:

- four Earth-square corners;
- eight square/construction-circle junctions.

Rendered pixel y coordinates increase downward. Internally they are converted
to Cartesian pixel coordinates with y increasing upward before fitting.

Three transformation families are supported:

- similarity;
- affine;
- projective homography.

Model comparison includes leave-one-landmark-out prediction errors.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import Enum
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


REGISTRATION_SUMMARY_FIELDS = (
    "dataset_id",
    "model",
    "parameter_count",
    "landmark_count",
    "training_rms_pixels",
    "training_maximum_pixels",
    "loo_rms_pixels",
    "loo_maximum_pixels",
    "linear_determinant",
    "singular_value_max",
    "singular_value_min",
    "anisotropy_ratio",
    "perspective_magnitude",
    "denominator_minimum",
    "denominator_maximum",
)

REGISTRATION_RESIDUAL_FIELDS = (
    "dataset_id",
    "model",
    "sequence_index",
    "landmark_id",
    "category",
    "training_residual_pixels",
    "loo_residual_pixels",
)


class RegistrationModel(str, Enum):
    """Supported source-plate registration families."""

    SIMILARITY = "similarity"
    AFFINE = "affine"
    PROJECTIVE = "projective"


@dataclass(frozen=True, slots=True)
class RegistrationObservation:
    """One registration landmark in model and rendered-pixel space."""

    sequence_index: int
    landmark_id: str
    category: str
    model_x: float
    model_y: float
    pixel_x: float
    pixel_y: float


@dataclass(frozen=True, slots=True)
class RegistrationDataset:
    """One registration dataset: an independent pass or centroid."""

    dataset_id: str
    image_width_pixels: int
    image_height_pixels: int
    observations: tuple[RegistrationObservation, ...]


@dataclass(frozen=True, slots=True)
class RegistrationFit:
    """One fitted registration model and its diagnostics."""

    dataset_id: str
    model: RegistrationModel
    parameter_count: int
    matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    landmark_ids: tuple[str, ...]
    training_residuals_pixels: tuple[float, ...]
    loo_residuals_pixels: tuple[float, ...]
    training_rms_pixels: float
    training_maximum_pixels: float
    loo_rms_pixels: float
    loo_maximum_pixels: float
    linear_determinant: float
    singular_value_max: float
    singular_value_min: float
    anisotropy_ratio: float
    perspective_magnitude: float
    denominator_minimum: float
    denominator_maximum: float


@dataclass(frozen=True, slots=True)
class RegistrationReport:
    """All fitted models across the pass and centroid datasets."""

    datasets: tuple[RegistrationDataset, ...]
    fits: tuple[RegistrationFit, ...]

    @property
    def centroid_fits(self) -> tuple[RegistrationFit, ...]:
        return tuple(
            fit
            for fit in self.fits
            if fit.dataset_id == "centroid"
        )


def _rms(values: Sequence[float]) -> float:
    if not values:
        return 0.0

    return sqrt(
        fmean(value * value for value in values)
    )


def pixel_to_cartesian(
    pixel_x: float,
    pixel_y: float,
    image_height_pixels: int,
) -> tuple[float, float]:
    """Convert rendered y-down pixels to Cartesian y-up pixels."""

    return (
        float(pixel_x),
        float(image_height_pixels) - float(pixel_y),
    )


def cartesian_to_pixel(
    cartesian_x: float,
    cartesian_y: float,
    image_height_pixels: int,
) -> tuple[float, float]:
    """Convert Cartesian y-up pixels to rendered y-down pixels."""

    return (
        float(cartesian_x),
        float(image_height_pixels) - float(cartesian_y),
    )


def _as_points(
    values: Sequence[Sequence[float]],
) -> np.ndarray:
    array = np.asarray(
        values,
        dtype=float,
    )

    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(
            "Point coordinates must have shape (n, 2)."
        )

    if not np.all(np.isfinite(array)):
        raise ValueError(
            "Point coordinates must be finite."
        )

    return array


def apply_registration_matrix(
    matrix: Sequence[Sequence[float]],
    points: Sequence[Sequence[float]],
) -> np.ndarray:
    """Apply a homogeneous transformation to two-dimensional points."""

    transform = np.asarray(
        matrix,
        dtype=float,
    )

    if transform.shape != (3, 3):
        raise ValueError(
            "Registration matrix must have shape (3, 3)."
        )

    source = _as_points(points)

    homogeneous = np.column_stack(
        (
            source,
            np.ones(len(source)),
        )
    )

    mapped = (
        transform
        @ homogeneous.T
    ).T

    denominators = mapped[:, 2]

    if np.any(
        np.abs(denominators) < 1.0e-12
    ):
        raise ValueError(
            "Transformation maps a point to infinity."
        )

    return (
        mapped[:, :2]
        / denominators[:, None]
    )


def _fit_similarity(
    source: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """Fit a direct uniform-scale similarity transformation."""

    if len(source) < 2:
        raise ValueError(
            "Similarity fitting requires at least two points."
        )

    source_centre = source.mean(axis=0)
    target_centre = target.mean(axis=0)

    source_centred = source - source_centre
    target_centred = target - target_centre

    source_energy = float(
        np.sum(source_centred * source_centred)
    )

    if source_energy <= 0.0:
        raise ValueError(
            "Similarity source points are degenerate."
        )

    covariance = (
        source_centred.T
        @ target_centred
    )

    left, singular_values, right_transpose = (
        np.linalg.svd(covariance)
    )

    correction = np.eye(2)

    rotation_candidate = (
        right_transpose.T
        @ left.T
    )

    if np.linalg.det(rotation_candidate) < 0.0:
        correction[-1, -1] = -1.0

    rotation = (
        right_transpose.T
        @ correction
        @ left.T
    )

    scale = float(
        np.sum(
            singular_values
            * np.diag(correction)
        )
        / source_energy
    )

    linear = scale * rotation

    translation = (
        target_centre
        - linear @ source_centre
    )

    matrix = np.eye(3)
    matrix[:2, :2] = linear
    matrix[:2, 2] = translation

    return matrix


def _fit_affine(
    source: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """Fit a full two-dimensional affine transformation."""

    if len(source) < 3:
        raise ValueError(
            "Affine fitting requires at least three points."
        )

    design = np.column_stack(
        (
            source,
            np.ones(len(source)),
        )
    )

    coefficients, _, rank, _ = np.linalg.lstsq(
        design,
        target,
        rcond=None,
    )

    if rank < 3:
        raise ValueError(
            "Affine source points are degenerate."
        )

    matrix = np.array(
        (
            (
                coefficients[0, 0],
                coefficients[1, 0],
                coefficients[2, 0],
            ),
            (
                coefficients[0, 1],
                coefficients[1, 1],
                coefficients[2, 1],
            ),
            (0.0, 0.0, 1.0),
        ),
        dtype=float,
    )

    return matrix


def _normalisation_matrix(
    points: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return Hartley-normalised points and their transformation."""

    centre = points.mean(axis=0)
    centred = points - centre

    mean_distance = float(
        np.mean(
            np.linalg.norm(
                centred,
                axis=1,
            )
        )
    )

    if mean_distance <= 0.0:
        raise ValueError(
            "Projective points are degenerate."
        )

    scale = sqrt(2.0) / mean_distance

    matrix = np.array(
        (
            (
                scale,
                0.0,
                -scale * centre[0],
            ),
            (
                0.0,
                scale,
                -scale * centre[1],
            ),
            (0.0, 0.0, 1.0),
        ),
        dtype=float,
    )

    homogeneous = np.column_stack(
        (
            points,
            np.ones(len(points)),
        )
    )

    normalised_homogeneous = (
        matrix
        @ homogeneous.T
    ).T

    return (
        normalised_homogeneous[:, :2],
        matrix,
    )


def _fit_projective(
    source: np.ndarray,
    target: np.ndarray,
) -> np.ndarray:
    """Fit a projective homography using normalised DLT."""

    if len(source) < 4:
        raise ValueError(
            "Projective fitting requires at least four points."
        )

    source_normalised, source_transform = (
        _normalisation_matrix(source)
    )

    target_normalised, target_transform = (
        _normalisation_matrix(target)
    )

    rows: list[list[float]] = []

    for (
        source_point,
        target_point,
    ) in zip(
        source_normalised,
        target_normalised,
        strict=True,
    ):
        x, y = source_point
        u, v = target_point

        rows.append(
            [
                -x,
                -y,
                -1.0,
                0.0,
                0.0,
                0.0,
                u * x,
                u * y,
                u,
            ]
        )

        rows.append(
            [
                0.0,
                0.0,
                0.0,
                -x,
                -y,
                -1.0,
                v * x,
                v * y,
                v,
            ]
        )

    design = np.asarray(
        rows,
        dtype=float,
    )

    _, _, right_transpose = np.linalg.svd(
        design
    )

    normalised_homography = (
        right_transpose[-1]
        .reshape(3, 3)
    )

    homography = (
        np.linalg.inv(target_transform)
        @ normalised_homography
        @ source_transform
    )

    if abs(homography[2, 2]) > 1.0e-15:
        homography = (
            homography
            / homography[2, 2]
        )
    else:
        norm = np.linalg.norm(homography)

        if norm <= 0.0:
            raise ValueError(
                "Projective fit produced a zero matrix."
            )

        homography = homography / norm

    return homography


def fit_registration_matrix(
    model: RegistrationModel,
    source_points: Sequence[Sequence[float]],
    target_points: Sequence[Sequence[float]],
) -> np.ndarray:
    """Fit one supported registration model."""

    source = _as_points(source_points)
    target = _as_points(target_points)

    if len(source) != len(target):
        raise ValueError(
            "Source and target point counts must agree."
        )

    if model is RegistrationModel.SIMILARITY:
        return _fit_similarity(
            source,
            target,
        )

    if model is RegistrationModel.AFFINE:
        return _fit_affine(
            source,
            target,
        )

    if model is RegistrationModel.PROJECTIVE:
        return _fit_projective(
            source,
            target,
        )

    raise ValueError(
        f"Unsupported registration model: {model}"
    )


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


def evaluate_registration(
    dataset: RegistrationDataset,
    model: RegistrationModel,
) -> RegistrationFit:
    """Fit and cross-validate one registration model."""

    source = np.asarray(
        [
            (
                observation.model_x,
                observation.model_y,
            )
            for observation in dataset.observations
        ],
        dtype=float,
    )

    target = np.asarray(
        [
            pixel_to_cartesian(
                observation.pixel_x,
                observation.pixel_y,
                dataset.image_height_pixels,
            )
            for observation in dataset.observations
        ],
        dtype=float,
    )

    matrix = fit_registration_matrix(
        model,
        source,
        target,
    )

    predicted = apply_registration_matrix(
        matrix,
        source,
    )

    training_residuals = np.linalg.norm(
        predicted - target,
        axis=1,
    )

    loo_residuals: list[float] = []

    for withheld_index in range(len(source)):
        mask = np.ones(
            len(source),
            dtype=bool,
        )

        mask[withheld_index] = False

        withheld_matrix = fit_registration_matrix(
            model,
            source[mask],
            target[mask],
        )

        withheld_prediction = (
            apply_registration_matrix(
                withheld_matrix,
                source[
                    withheld_index : withheld_index + 1
                ],
            )[0]
        )

        loo_residuals.append(
            float(
                np.linalg.norm(
                    withheld_prediction
                    - target[withheld_index]
                )
            )
        )

    linear = matrix[:2, :2]

    singular_values = np.linalg.svd(
        linear,
        compute_uv=False,
    )

    singular_max = float(
        max(singular_values)
    )

    singular_min = float(
        min(singular_values)
    )

    if singular_min <= 0.0:
        anisotropy_ratio = float("inf")
    else:
        anisotropy_ratio = (
            singular_max / singular_min
        )

    homogeneous_source = np.column_stack(
        (
            source,
            np.ones(len(source)),
        )
    )

    raw_mapped = (
        matrix
        @ homogeneous_source.T
    ).T

    denominators = raw_mapped[:, 2]

    parameter_count = {
        RegistrationModel.SIMILARITY: 4,
        RegistrationModel.AFFINE: 6,
        RegistrationModel.PROJECTIVE: 8,
    }[model]

    training_tuple = tuple(
        float(value)
        for value in training_residuals
    )

    loo_tuple = tuple(loo_residuals)

    return RegistrationFit(
        dataset_id=dataset.dataset_id,
        model=model,
        parameter_count=parameter_count,
        matrix=_matrix_tuple(matrix),
        landmark_ids=tuple(
            observation.landmark_id
            for observation in dataset.observations
        ),
        training_residuals_pixels=training_tuple,
        loo_residuals_pixels=loo_tuple,
        training_rms_pixels=_rms(training_tuple),
        training_maximum_pixels=max(
            training_tuple
        ),
        loo_rms_pixels=_rms(loo_tuple),
        loo_maximum_pixels=max(loo_tuple),
        linear_determinant=float(
            np.linalg.det(linear)
        ),
        singular_value_max=singular_max,
        singular_value_min=singular_min,
        anisotropy_ratio=anisotropy_ratio,
        perspective_magnitude=hypot(
            float(matrix[2, 0]),
            float(matrix[2, 1]),
        ),
        denominator_minimum=float(
            np.min(denominators)
        ),
        denominator_maximum=float(
            np.max(denominators)
        ),
    )


def build_registration_datasets(
    *,
    schema_path: str | Path,
    pass_paths: Sequence[str | Path],
) -> tuple[RegistrationDataset, ...]:
    """Build pass-specific and centroid registration datasets."""

    if len(pass_paths) < 2:
        raise ValueError(
            "At least two digitisation passes are required."
        )

    schema = read_landmark_schema_csv(
        schema_path
    )

    registration_definitions = tuple(
        landmark
        for landmark in schema
        if landmark.registration_default
    )

    if len(registration_definitions) != 12:
        raise ValueError(
            "Expected exactly twelve default registration landmarks."
        )

    passes = tuple(
        load_digitisation_pass(path)
        for path in pass_paths
    )

    reference = passes[0]

    for item in passes[1:]:
        if (
            item.source_image_sha256
            != reference.source_image_sha256
        ):
            raise ValueError(
                "Registration passes use different source images."
            )

        if (
            item.image_width_pixels
            != reference.image_width_pixels
            or item.image_height_pixels
            != reference.image_height_pixels
        ):
            raise ValueError(
                "Registration passes use different image dimensions."
            )

    datasets: list[RegistrationDataset] = []

    for digitisation_pass in passes:
        by_identifier = {
            observation.landmark_id: observation
            for observation in digitisation_pass.observations
        }

        observations: list[
            RegistrationObservation
        ] = []

        for definition in registration_definitions:
            source = by_identifier.get(
                definition.landmark_id
            )

            if source is None:
                raise ValueError(
                    "Pass is missing registration landmark "
                    f"{definition.landmark_id}."
                )

            if (
                definition.model_x is None
                or definition.model_y is None
            ):
                raise ValueError(
                    "Registration landmark lacks model coordinates: "
                    f"{definition.landmark_id}."
                )

            observations.append(
                RegistrationObservation(
                    sequence_index=(
                        definition.sequence_index
                    ),
                    landmark_id=(
                        definition.landmark_id
                    ),
                    category=definition.category,
                    model_x=definition.model_x,
                    model_y=definition.model_y,
                    pixel_x=source.pixel_x,
                    pixel_y=source.pixel_y,
                )
            )

        datasets.append(
            RegistrationDataset(
                dataset_id=digitisation_pass.pass_id,
                image_width_pixels=(
                    digitisation_pass.image_width_pixels
                ),
                image_height_pixels=(
                    digitisation_pass.image_height_pixels
                ),
                observations=tuple(observations),
            )
        )

    centroid_observations: list[
        RegistrationObservation
    ] = []

    pass_maps = tuple(
        {
            observation.landmark_id: observation
            for observation in item.observations
        }
        for item in passes
    )

    for definition in registration_definitions:
        repeated = tuple(
            mapping[definition.landmark_id]
            for mapping in pass_maps
        )

        if (
            definition.model_x is None
            or definition.model_y is None
        ):
            raise ValueError(
                "Registration landmark lacks model coordinates."
            )

        centroid_observations.append(
            RegistrationObservation(
                sequence_index=definition.sequence_index,
                landmark_id=definition.landmark_id,
                category=definition.category,
                model_x=definition.model_x,
                model_y=definition.model_y,
                pixel_x=fmean(
                    item.pixel_x
                    for item in repeated
                ),
                pixel_y=fmean(
                    item.pixel_y
                    for item in repeated
                ),
            )
        )

    datasets.append(
        RegistrationDataset(
            dataset_id="centroid",
            image_width_pixels=(
                reference.image_width_pixels
            ),
            image_height_pixels=(
                reference.image_height_pixels
            ),
            observations=tuple(
                centroid_observations
            ),
        )
    )

    return tuple(datasets)


def analyze_registration(
    *,
    schema_path: str | Path,
    pass_paths: Sequence[str | Path],
) -> RegistrationReport:
    """Fit all registration models to all available datasets."""

    datasets = build_registration_datasets(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    fits = tuple(
        evaluate_registration(
            dataset,
            model,
        )
        for dataset in datasets
        for model in RegistrationModel
    )

    return RegistrationReport(
        datasets=datasets,
        fits=fits,
    )


def _format_float(value: float) -> str:
    return format(value, ".12f")


def write_registration_summary_csv(
    path: str | Path,
    report: RegistrationReport,
) -> Path:
    """Write one summary row per dataset and model."""

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
            fieldnames=REGISTRATION_SUMMARY_FIELDS,
        )

        writer.writeheader()

        for fit in report.fits:
            writer.writerow(
                {
                    "dataset_id": fit.dataset_id,
                    "model": fit.model.value,
                    "parameter_count": fit.parameter_count,
                    "landmark_count": len(
                        fit.landmark_ids
                    ),
                    "training_rms_pixels": _format_float(
                        fit.training_rms_pixels
                    ),
                    "training_maximum_pixels": _format_float(
                        fit.training_maximum_pixels
                    ),
                    "loo_rms_pixels": _format_float(
                        fit.loo_rms_pixels
                    ),
                    "loo_maximum_pixels": _format_float(
                        fit.loo_maximum_pixels
                    ),
                    "linear_determinant": _format_float(
                        fit.linear_determinant
                    ),
                    "singular_value_max": _format_float(
                        fit.singular_value_max
                    ),
                    "singular_value_min": _format_float(
                        fit.singular_value_min
                    ),
                    "anisotropy_ratio": _format_float(
                        fit.anisotropy_ratio
                    ),
                    "perspective_magnitude": _format_float(
                        fit.perspective_magnitude
                    ),
                    "denominator_minimum": _format_float(
                        fit.denominator_minimum
                    ),
                    "denominator_maximum": _format_float(
                        fit.denominator_maximum
                    ),
                }
            )

    return output_path


def write_registration_residuals_csv(
    path: str | Path,
    report: RegistrationReport,
) -> Path:
    """Write per-landmark training and cross-validation residuals."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataset_by_id = {
        dataset.dataset_id: dataset
        for dataset in report.datasets
    }

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=REGISTRATION_RESIDUAL_FIELDS,
        )

        writer.writeheader()

        for fit in report.fits:
            dataset = dataset_by_id[
                fit.dataset_id
            ]

            for (
                observation,
                training_residual,
                loo_residual,
            ) in zip(
                dataset.observations,
                fit.training_residuals_pixels,
                fit.loo_residuals_pixels,
                strict=True,
            ):
                writer.writerow(
                    {
                        "dataset_id": fit.dataset_id,
                        "model": fit.model.value,
                        "sequence_index": (
                            observation.sequence_index
                        ),
                        "landmark_id": (
                            observation.landmark_id
                        ),
                        "category": observation.category,
                        "training_residual_pixels": (
                            _format_float(
                                training_residual
                            )
                        ),
                        "loo_residual_pixels": (
                            _format_float(
                                loo_residual
                            )
                        ),
                    }
                )

    return output_path


def write_registration_markdown(
    path: str | Path,
    report: RegistrationReport,
) -> Path:
    """Write a human-readable model-comparison report."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    centroid_ranked = sorted(
        report.centroid_fits,
        key=lambda fit: fit.loo_rms_pixels,
    )

    lines = [
        "# Figure 14 plate-registration comparison",
        "",
        "## Registration evidence",
        "",
        "- Four Earth-square corners",
        "- Eight square/construction-circle junctions",
        "- Twelve landmarks in total",
        "- Three independent digitisation passes",
        "- One repeated-pass centroid dataset",
        "",
        "Rendered pixel coordinates were converted from y-down image",
        "coordinates to y-up Cartesian coordinates before fitting.",
        "",
        "## Centroid model ranking",
        "",
        "| Rank | Model | Parameters | Training RMS (px) | LOO RMS (px) | LOO maximum (px) | Anisotropy | Perspective magnitude |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    for rank, fit in enumerate(
        centroid_ranked,
        start=1,
    ):
        lines.append(
            "| "
            f"{rank} | "
            f"{fit.model.value} | "
            f"{fit.parameter_count} | "
            f"{fit.training_rms_pixels:.6f} | "
            f"{fit.loo_rms_pixels:.6f} | "
            f"{fit.loo_maximum_pixels:.6f} | "
            f"{fit.anisotropy_ratio:.9f} | "
            f"{fit.perspective_magnitude:.12g} |"
        )

    lines.extend(
        [
            "",
            "## All fitted datasets",
            "",
            "| Dataset | Model | Training RMS (px) | LOO RMS (px) | LOO maximum (px) | Anisotropy |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )

    for fit in report.fits:
        lines.append(
            "| "
            f"{fit.dataset_id} | "
            f"{fit.model.value} | "
            f"{fit.training_rms_pixels:.6f} | "
            f"{fit.loo_rms_pixels:.6f} | "
            f"{fit.loo_maximum_pixels:.6f} | "
            f"{fit.anisotropy_ratio:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Selection boundary",
            "",
            "Training residual alone must not determine the selected model.",
            "The preferred model must balance:",
            "",
            "- leave-one-landmark-out prediction;",
            "- stability across independent passes;",
            "- transformation complexity;",
            "- geometric plausibility;",
            "- absence of excessive anisotropy or perspective distortion.",
            "",
            "No star endpoint or Moon-centre observation is used to fit these",
            "transformations.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
