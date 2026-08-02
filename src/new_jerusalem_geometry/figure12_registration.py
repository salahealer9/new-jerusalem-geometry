"""Plate registration for Michell's Figure 12.

The numerical transformation engine is reused from the already tested
Figure 14 registration implementation.

This module contains only the Figure-12-specific data adapter:

- load the three accepted raw Figure 12 passes;
- select only the twelve predefined registration observations;
- construct one registration dataset per independent pass;
- construct a centroid registration dataset;
- evaluate similarity, affine, and projective models.

Moon-circumference and wall-line observations are deliberately excluded from
all registration fits.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from .figure12_digitisation import (
    Figure12DigitisedObservation,
    read_figure12_digitisation_pass_csv,
)
from .figure14_registration import (
    RegistrationDataset,
    RegistrationFit,
    RegistrationModel,
    RegistrationObservation,
    evaluate_registration,
)


SUMMARY_FIELDS = (
    "dataset_id",
    "model",
    "training_rms_pixels",
    "loo_rms_pixels",
    "loo_maximum_pixels",
    "anisotropy_ratio",
    "perspective_magnitude",
)


@dataclass(frozen=True, slots=True)
class Figure12RegistrationReport:
    """Comparison of Figure 12 registration models."""

    datasets: tuple[RegistrationDataset, ...]
    fits: tuple[RegistrationFit, ...]

    @property
    def centroid_fits(
        self,
    ) -> tuple[RegistrationFit, ...]:
        return tuple(
            fit
            for fit in self.fits
            if fit.dataset_id == "centroid"
        )


def _registration_observations(
    observations: Sequence[
        Figure12DigitisedObservation
    ],
) -> tuple[
    Figure12DigitisedObservation,
    ...,
]:
    selected = tuple(
        item
        for item in observations
        if item.definition.registration_default
    )

    if len(selected) != 12:
        raise ValueError(
            "Expected exactly twelve Figure 12 "
            "registration observations."
        )

    for item in selected:
        definition = item.definition

        if (
            definition.model_x is None
            or definition.model_y is None
        ):
            raise ValueError(
                "Registration observation lacks model "
                f"coordinates: {definition.observation_id}"
            )

    return selected


def _to_registration_observation(
    item: Figure12DigitisedObservation,
) -> RegistrationObservation:
    definition = item.definition

    if (
        definition.model_x is None
        or definition.model_y is None
    ):
        raise ValueError(
            "Registration observation lacks model coordinates."
        )

    return RegistrationObservation(
        sequence_index=definition.sequence_index,
        landmark_id=definition.observation_id,
        category=definition.category,
        model_x=float(definition.model_x),
        model_y=float(definition.model_y),
        pixel_x=float(item.pixel_x),
        pixel_y=float(item.pixel_y),
    )


def build_figure12_registration_datasets(
    pass_paths: Sequence[str | Path],
) -> tuple[RegistrationDataset, ...]:
    """Build three pass datasets plus their centroid dataset."""

    if len(pass_paths) != 3:
        raise ValueError(
            "Exactly three Figure 12 digitisation passes are required."
        )

    loaded: list[
        tuple[
            str,
            tuple[
                Figure12DigitisedObservation,
                ...,
            ],
        ]
    ] = []

    source_hashes: set[str] = set()
    image_dimensions: set[
        tuple[int, int]
    ] = set()

    expected_ids: tuple[str, ...] | None = None
    expected_model_coordinates: (
        tuple[tuple[float, float], ...]
        | None
    ) = None

    for raw_path in pass_paths:
        observations = (
            read_figure12_digitisation_pass_csv(
                raw_path,
                require_complete=True,
            )
        )

        if not observations:
            raise ValueError(
                f"Empty digitisation pass: {raw_path}"
            )

        pass_id = observations[0].pass_id

        selected = _registration_observations(
            observations
        )

        ids = tuple(
            item.definition.observation_id
            for item in selected
        )

        coordinates = tuple(
            (
                float(item.definition.model_x),
                float(item.definition.model_y),
            )
            for item in selected
        )

        if expected_ids is None:
            expected_ids = ids
            expected_model_coordinates = (
                coordinates
            )
        else:
            if ids != expected_ids:
                raise ValueError(
                    "Registration landmark identities differ "
                    "between passes."
                )

            if (
                coordinates
                != expected_model_coordinates
            ):
                raise ValueError(
                    "Registration model coordinates differ "
                    "between passes."
                )

        source_hashes.add(
            observations[0].source_image_sha256
        )

        image_dimensions.add(
            (
                observations[0].image_width_pixels,
                observations[0].image_height_pixels,
            )
        )

        loaded.append(
            (
                pass_id,
                selected,
            )
        )

    if len(source_hashes) != 1:
        raise ValueError(
            "Figure 12 passes use different source images."
        )

    if len(image_dimensions) != 1:
        raise ValueError(
            "Figure 12 passes use different image dimensions."
        )

    image_width, image_height = next(
        iter(image_dimensions)
    )

    datasets: list[
        RegistrationDataset
    ] = []

    for pass_id, selected in loaded:
        datasets.append(
            RegistrationDataset(
                dataset_id=pass_id,
                image_width_pixels=image_width,
                image_height_pixels=image_height,
                observations=tuple(
                    _to_registration_observation(
                        item
                    )
                    for item in selected
                ),
            )
        )

    # ----------------------------------------------------------
    # Centroid dataset
    # ----------------------------------------------------------

    assert expected_ids is not None
    assert expected_model_coordinates is not None

    centroid_observations: list[
        RegistrationObservation
    ] = []

    for landmark_index, landmark_id in enumerate(
        expected_ids
    ):
        source_items = tuple(
            selected[landmark_index]
            for _, selected in loaded
        )

        pixel_x = float(
            np.mean(
                [
                    item.pixel_x
                    for item in source_items
                ]
            )
        )

        pixel_y = float(
            np.mean(
                [
                    item.pixel_y
                    for item in source_items
                ]
            )
        )

        model_x, model_y = (
            expected_model_coordinates[
                landmark_index
            ]
        )

        definition = (
            source_items[0].definition
        )

        centroid_observations.append(
            RegistrationObservation(
                sequence_index=(
                    definition.sequence_index
                ),
                landmark_id=landmark_id,
                category=definition.category,
                model_x=model_x,
                model_y=model_y,
                pixel_x=pixel_x,
                pixel_y=pixel_y,
            )
        )

    datasets.append(
        RegistrationDataset(
            dataset_id="centroid",
            image_width_pixels=image_width,
            image_height_pixels=image_height,
            observations=tuple(
                centroid_observations
            ),
        )
    )

    return tuple(datasets)


def analyze_figure12_registration(
    pass_paths: Sequence[str | Path],
) -> Figure12RegistrationReport:
    """Evaluate all three registration families."""

    datasets = (
        build_figure12_registration_datasets(
            pass_paths
        )
    )

    models = (
        RegistrationModel.SIMILARITY,
        RegistrationModel.AFFINE,
        RegistrationModel.PROJECTIVE,
    )

    fits = tuple(
        evaluate_registration(
            dataset,
            model,
        )
        for dataset in datasets
        for model in models
    )

    return Figure12RegistrationReport(
        datasets=datasets,
        fits=fits,
    )


def _format_float(
    value: float,
) -> str:
    return format(
        value,
        ".17g",
    )


def write_figure12_registration_summary_csv(
    path: str | Path,
    report: Figure12RegistrationReport,
) -> Path:
    """Write deterministic registration-model summary."""

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
            fieldnames=SUMMARY_FIELDS,
        )

        writer.writeheader()

        for fit in report.fits:
            writer.writerow(
                {
                    "dataset_id": fit.dataset_id,
                    "model": fit.model.value,
                    "training_rms_pixels": (
                        _format_float(
                            fit.training_rms_pixels
                        )
                    ),
                    "loo_rms_pixels": (
                        _format_float(
                            fit.loo_rms_pixels
                        )
                    ),
                    "loo_maximum_pixels": (
                        _format_float(
                            fit.loo_maximum_pixels
                        )
                    ),
                    "anisotropy_ratio": (
                        _format_float(
                            fit.anisotropy_ratio
                        )
                    ),
                    "perspective_magnitude": (
                        _format_float(
                            fit.perspective_magnitude
                        )
                    ),
                }
            )

    return output_path


def write_figure12_registration_markdown(
    path: str | Path,
    report: Figure12RegistrationReport,
) -> Path:
    """Write human-readable Figure 12 registration comparison."""

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
        "# Figure 12 plate-registration comparison",
        "",
        "## Evidence boundary",
        "",
        (
            "Only the four Earth-square corners and eight "
            "square/construction-circle junctions are used for "
            "registration."
        ),
        "",
        (
            "Moon-circumference observations and outer-wall "
            "observations do not influence any fitted transformation."
        ),
        "",
        "## Centroid model comparison",
        "",
        (
            "| Rank | Model | Training RMS (px) | "
            "LOO RMS (px) | LOO max (px) | "
            "Anisotropy | Perspective |"
        ),
        (
            "|---:|---|---:|---:|---:|---:|---:|"
        ),
    ]

    for rank, fit in enumerate(
        centroid_ranked,
        start=1,
    ):
        lines.append(
            f"| {rank} | `{fit.model.value}` | "
            f"{fit.training_rms_pixels:.6f} | "
            f"{fit.loo_rms_pixels:.6f} | "
            f"{fit.loo_maximum_pixels:.6f} | "
            f"{fit.anisotropy_ratio:.9f} | "
            f"{fit.perspective_magnitude:.12g} |"
        )

    lines.extend(
        [
            "",
            "## Independent-pass fits",
            "",
            (
                "| Dataset | Model | Training RMS (px) | "
                "LOO RMS (px) | LOO max (px) |"
            ),
            "|---|---|---:|---:|---:|",
        ]
    )

    for fit in report.fits:
        if fit.dataset_id == "centroid":
            continue

        lines.append(
            f"| `{fit.dataset_id}` | "
            f"`{fit.model.value}` | "
            f"{fit.training_rms_pixels:.6f} | "
            f"{fit.loo_rms_pixels:.6f} | "
            f"{fit.loo_maximum_pixels:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Selection boundary",
            "",
            (
                "No registration family is selected merely because "
                "it has the smallest training error."
            ),
            "",
            (
                "Selection must consider leave-one-landmark-out "
                "prediction, maximum prediction error, affine "
                "anisotropy, projective perspective magnitude, "
                "independent-pass stability, and geometric "
                "plausibility."
            ),
            "",
            (
                "No Moon-placement or wall hypothesis is evaluated "
                "at this stage."
            ),
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
