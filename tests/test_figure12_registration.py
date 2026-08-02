from __future__ import annotations

from pathlib import Path

import pytest

from new_jerusalem_geometry.figure12_digitisation import (
    Figure12DigitisedObservation,
    build_figure12_observation_schema,
    write_figure12_digitisation_pass_csv,
)
from new_jerusalem_geometry.figure12_registration import (
    analyze_figure12_registration,
    build_figure12_registration_datasets,
)
from new_jerusalem_geometry.figure14_registration import (
    RegistrationModel,
    cartesian_to_pixel,
)


def _synthetic_passes(
    tmp_path: Path,
) -> tuple[Path, ...]:
    schema = (
        build_figure12_observation_schema()
    )

    width = 1512
    height = 2327

    paths: list[Path] = []

    for pass_number in range(1, 4):
        observations = []

        for definition in schema:
            if definition.registration_default:
                assert (
                    definition.model_x
                    is not None
                )
                assert (
                    definition.model_y
                    is not None
                )

                x = definition.model_x
                y = definition.model_y

                # Deliberately affine rather than exact
                # similarity geometry.
                cartesian_x = (
                    760.0
                    + 70.0 * x
                    + 1.25 * y
                )

                cartesian_y = (
                    900.0
                    - 0.75 * x
                    + 72.0 * y
                )

                pixel_x, pixel_y = (
                    cartesian_to_pixel(
                        cartesian_x,
                        cartesian_y,
                        height,
                    )
                )

            else:
                # Source-only observations do not participate
                # in registration.
                pixel_x = 500.0
                pixel_y = 1000.0

            observations.append(
                Figure12DigitisedObservation(
                    pass_id=(
                        f"pass-{pass_number:02d}"
                    ),
                    definition=definition,
                    pixel_x=float(pixel_x),
                    pixel_y=float(pixel_y),
                    source_image="source.png",
                    source_image_sha256=(
                        "a" * 64
                    ),
                    image_width_pixels=width,
                    image_height_pixels=height,
                )
            )

        path = (
            tmp_path
            / (
                "figure12_observations_"
                f"pass-{pass_number:02d}.csv"
            )
        )

        write_figure12_digitisation_pass_csv(
            path,
            observations,
        )

        paths.append(path)

    return tuple(paths)


def test_builds_three_passes_plus_centroid(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    datasets = (
        build_figure12_registration_datasets(
            paths
        )
    )

    assert tuple(
        dataset.dataset_id
        for dataset in datasets
    ) == (
        "pass-01",
        "pass-02",
        "pass-03",
        "centroid",
    )

    assert all(
        len(dataset.observations) == 12
        for dataset in datasets
    )


def test_source_only_observations_do_not_enter_registration(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    datasets = (
        build_figure12_registration_datasets(
            paths
        )
    )

    categories = {
        observation.category
        for dataset in datasets
        for observation in dataset.observations
    }

    assert categories == {
        "square_corner",
        "square_circle_junction",
    }


def test_exact_affine_registration_is_recovered(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    report = (
        analyze_figure12_registration(
            paths
        )
    )

    assert len(report.fits) == 12

    affine = next(
        fit
        for fit in report.centroid_fits
        if fit.model
        is RegistrationModel.AFFINE
    )

    assert (
        affine.training_rms_pixels
        < 1.0e-8
    )

    assert (
        affine.loo_rms_pixels
        < 1.0e-7
    )


def test_centroid_contains_three_models(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    report = (
        analyze_figure12_registration(
            paths
        )
    )

    assert {
        fit.model
        for fit in report.centroid_fits
    } == {
        RegistrationModel.SIMILARITY,
        RegistrationModel.AFFINE,
        RegistrationModel.PROJECTIVE,
    }
