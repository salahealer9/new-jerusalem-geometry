import json
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
from new_jerusalem_geometry.figure14_registered_landmarks import (
    derive_affine_registered_landmarks,
    write_affine_calibration_markdown,
    write_affine_matrix_json,
    write_affine_summary_csv,
    write_registered_landmarks_csv,
)
from new_jerusalem_geometry.figure14_registration import (
    apply_registration_matrix,
    cartesian_to_pixel,
)


TRUE_AFFINE = np.asarray(
    (
        (70.0, 1.4, 760.0),
        (-0.8, 68.0, 900.0),
        (0.0, 0.0, 1.0),
    ),
    dtype=float,
)


def _build_synthetic_dataset(
    tmp_path: Path,
) -> tuple[Path, tuple[Path, ...]]:
    schema = build_figure14_landmark_schema(
        build_core_geometry()
    )

    schema_path = tmp_path / "schema.csv"

    write_landmark_schema_csv(
        schema_path,
        schema,
    )

    source_image = tmp_path / "source.png"
    source_image.write_bytes(
        b"fixed rendered source"
    )

    image_height = 2200

    pass_paths = []

    pass_drifts = (
        (-0.2, 0.1),
        (0.0, 0.0),
        (0.2, -0.1),
    )

    for pass_number, drift in enumerate(
        pass_drifts,
        start=1,
    ):
        points = []

        for landmark in schema:
            if (
                landmark.model_x is not None
                and landmark.model_y is not None
            ):
                normalized = np.asarray(
                    [
                        (
                            landmark.model_x,
                            landmark.model_y,
                        )
                    ],
                    dtype=float,
                )
            else:
                index = (
                    landmark.sequence_index - 24
                )

                normalized = np.asarray(
                    [
                        (
                            -3.0 + index,
                            2.5 - 0.4 * index,
                        )
                    ],
                    dtype=float,
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
            image_width_pixels=1700,
            image_height_pixels=image_height,
        )

        pass_paths.append(pass_path)

    return schema_path, tuple(pass_paths)


def test_affine_calibration_recovers_synthetic_schema(
    tmp_path: Path,
) -> None:
    schema_path, pass_paths = (
        _build_synthetic_dataset(
            tmp_path
        )
    )

    report = derive_affine_registered_landmarks(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    assert len(report.landmarks) == 31
    assert len(report.passes) == 3

    assert (
        report.selected_fit.training_rms_pixels
        < 1.0e-5
    )

    assert (
        report.selected_fit.loo_rms_pixels
        < 1.0e-5
    )

    schema_landmarks = tuple(
        item
        for item in report.landmarks
        if item.model_x is not None
    )

    assert max(
        item.model_residual_normalized
        for item in schema_landmarks
        if item.model_residual_normalized
        is not None
    ) < 1.0e-6


def test_pass_specific_affine_fits_remove_global_drift(
    tmp_path: Path,
) -> None:
    schema_path, pass_paths = (
        _build_synthetic_dataset(
            tmp_path
        )
    )

    report = derive_affine_registered_landmarks(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    assert (
        report.overall_pass_registered_rms_normalized
        < 1.0e-6
    )


def test_registered_roles_are_separated(
    tmp_path: Path,
) -> None:
    schema_path, pass_paths = (
        _build_synthetic_dataset(
            tmp_path
        )
    )

    report = derive_affine_registered_landmarks(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    roles = {
        item.category: item.registration_role
        for item in report.landmarks
    }

    assert roles["square_corner"] == "registration"

    assert (
        roles["square_circle_junction"]
        == "registration"
    )

    assert roles["moon_centre"] == "validation"
    assert roles["star_endpoint"] == "target"


def test_affine_calibration_writers(
    tmp_path: Path,
) -> None:
    schema_path, pass_paths = (
        _build_synthetic_dataset(
            tmp_path
        )
    )

    report = derive_affine_registered_landmarks(
        schema_path=schema_path,
        pass_paths=pass_paths,
    )

    landmark_path = write_registered_landmarks_csv(
        tmp_path / "landmarks.csv",
        report,
    )

    summary_path = write_affine_summary_csv(
        tmp_path / "summary.csv",
        report,
    )

    matrix_path = write_affine_matrix_json(
        tmp_path / "matrix.json",
        report,
    )

    markdown_path = write_affine_calibration_markdown(
        tmp_path / "report.md",
        report,
    )

    assert landmark_path.exists()
    assert summary_path.exists()
    assert matrix_path.exists()
    assert markdown_path.exists()

    payload = json.loads(
        matrix_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["selected_model"] == "affine"

    assert len(
        payload[
            "forward_model_to_cartesian_pixel"
        ]
    ) == 3

    text = markdown_path.read_text(
        encoding="utf-8"
    )

    assert (
        "selected as the primary Figure 14"
        in text
    )

    assert "Interpretation boundary" in text
