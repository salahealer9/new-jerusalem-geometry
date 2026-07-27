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
    RegistrationDataset,
    RegistrationModel,
    RegistrationObservation,
    analyze_registration,
    apply_registration_matrix,
    cartesian_to_pixel,
    evaluate_registration,
    fit_registration_matrix,
    pixel_to_cartesian,
    write_registration_markdown,
    write_registration_residuals_csv,
    write_registration_summary_csv,
)


SOURCE_POINTS = np.asarray(
    (
        (-5.0, -4.0),
        (-2.0, 3.0),
        (0.0, 0.0),
        (4.0, -3.0),
        (5.0, 5.0),
        (-4.0, 5.0),
        (3.0, 2.0),
        (-1.0, -5.0),
        (2.0, -1.0),
        (-3.0, 1.0),
        (1.0, 4.0),
        (5.0, 0.0),
    ),
    dtype=float,
)


def test_pixel_cartesian_round_trip() -> None:
    cartesian = pixel_to_cartesian(
        310.25,
        1669.75,
        2327,
    )

    recovered = cartesian_to_pixel(
        cartesian[0],
        cartesian[1],
        2327,
    )

    assert recovered == pytest.approx(
        (310.25, 1669.75),
        abs=1.0e-12,
    )


def test_similarity_fit_is_exact() -> None:
    angle = 0.31
    scale = 42.5

    rotation = np.asarray(
        (
            (
                np.cos(angle),
                -np.sin(angle),
            ),
            (
                np.sin(angle),
                np.cos(angle),
            ),
        )
    )

    target = (
        SOURCE_POINTS
        @ (scale * rotation).T
        + np.asarray((720.0, 980.0))
    )

    matrix = fit_registration_matrix(
        RegistrationModel.SIMILARITY,
        SOURCE_POINTS,
        target,
    )

    predicted = apply_registration_matrix(
        matrix,
        SOURCE_POINTS,
    )

    assert predicted == pytest.approx(
        target,
        abs=1.0e-9,
    )


def test_affine_fit_is_exact() -> None:
    matrix_expected = np.asarray(
        (
            (43.0, 1.7, 720.0),
            (-0.8, 41.0, 980.0),
            (0.0, 0.0, 1.0),
        )
    )

    target = apply_registration_matrix(
        matrix_expected,
        SOURCE_POINTS,
    )

    fitted = fit_registration_matrix(
        RegistrationModel.AFFINE,
        SOURCE_POINTS,
        target,
    )

    predicted = apply_registration_matrix(
        fitted,
        SOURCE_POINTS,
    )

    assert predicted == pytest.approx(
        target,
        abs=1.0e-9,
    )


def test_projective_fit_is_exact() -> None:
    matrix_expected = np.asarray(
        (
            (43.0, 1.7, 720.0),
            (-0.8, 41.0, 980.0),
            (0.0004, -0.0003, 1.0),
        )
    )

    target = apply_registration_matrix(
        matrix_expected,
        SOURCE_POINTS,
    )

    fitted = fit_registration_matrix(
        RegistrationModel.PROJECTIVE,
        SOURCE_POINTS,
        target,
    )

    predicted = apply_registration_matrix(
        fitted,
        SOURCE_POINTS,
    )

    assert predicted == pytest.approx(
        target,
        abs=1.0e-8,
    )


def test_registration_evaluation_and_outputs(
    tmp_path: Path,
) -> None:
    height = 2000

    observations = tuple(
        RegistrationObservation(
            sequence_index=index,
            landmark_id=f"point_{index:02d}",
            category="registration",
            model_x=float(source[0]),
            model_y=float(source[1]),
            pixel_x=float(
                720.0
                + 43.0 * source[0]
                + 1.5 * source[1]
            ),
            pixel_y=float(
                height
                - (
                    980.0
                    - 0.5 * source[0]
                    + 41.0 * source[1]
                )
            ),
        )
        for index, source in enumerate(
            SOURCE_POINTS
        )
    )

    dataset = RegistrationDataset(
        dataset_id="synthetic",
        image_width_pixels=1600,
        image_height_pixels=height,
        observations=observations,
    )

    affine = evaluate_registration(
        dataset,
        RegistrationModel.AFFINE,
    )

    assert affine.training_rms_pixels < 1.0e-9
    assert affine.loo_rms_pixels < 1.0e-8

    diagram = build_core_geometry()
    schema = build_figure14_landmark_schema(
        diagram
    )

    schema_path = tmp_path / "schema.csv"

    write_landmark_schema_csv(
        schema_path,
        schema,
    )

    source_image = tmp_path / "source.png"
    source_image.write_bytes(b"fixed source")

    pass_paths = []

    for pass_number in range(1, 4):
        points = []

        for landmark in schema:
            if (
                landmark.model_x is not None
                and landmark.model_y is not None
            ):
                cartesian_x = (
                    720.0
                    + 43.0 * landmark.model_x
                    + 1.5 * landmark.model_y
                )

                cartesian_y = (
                    980.0
                    - 0.5 * landmark.model_x
                    + 41.0 * landmark.model_y
                )

                pixel_x, pixel_y = cartesian_to_pixel(
                    cartesian_x,
                    cartesian_y,
                    height,
                )
            else:
                pixel_x = 700.0
                pixel_y = 1000.0

            points.append(
                (pixel_x, pixel_y)
            )

        pass_path = (
            tmp_path
            / f"figure14_digitisation_pass-{pass_number:02d}.csv"
        )

        write_digitisation_csv(
            pass_path,
            schema=schema,
            points=points,
            pass_id=f"pass-{pass_number:02d}",
            source_image=source_image,
            image_width_pixels=1600,
            image_height_pixels=height,
        )

        pass_paths.append(pass_path)

    report = analyze_registration(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    assert len(report.datasets) == 4
    assert len(report.fits) == 12

    centroid_affine = next(
        fit
        for fit in report.centroid_fits
        if fit.model is RegistrationModel.AFFINE
    )

    # Coordinates pass through the digitisation CSV format,
    # which stores rendered pixel positions to six decimal places.
    # Sub-micropixel residuals therefore represent numerical zero
    # at the precision of the persisted dataset.
    assert centroid_affine.loo_rms_pixels < 1.0e-6

    summary = write_registration_summary_csv(
        tmp_path / "summary.csv",
        report,
    )

    residuals = write_registration_residuals_csv(
        tmp_path / "residuals.csv",
        report,
    )

    markdown = write_registration_markdown(
        tmp_path / "report.md",
        report,
    )

    assert summary.exists()
    assert residuals.exists()
    assert markdown.exists()

    text = markdown.read_text(
        encoding="utf-8"
    )

    assert "Centroid model ranking" in text
    assert "leave-one-landmark-out" in text
