from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path

import numpy as np
import pytest

from new_jerusalem_geometry.figure12_digitisation import (
    Figure12DigitisedObservation,
    MOON_OBJECT_IDS,
    WALL_OBJECT_IDS,
    build_figure12_observation_schema,
    write_figure12_digitisation_pass_csv,
)
from new_jerusalem_geometry.figure12_source_geometry import (
    derive_figure12_source_geometry,
    write_figure12_source_geometry,
)
from new_jerusalem_geometry.figure14_registration import (
    apply_registration_matrix,
    cartesian_to_pixel,
)


def _model_point_for_source_observation(
    *,
    category: str,
    object_id: str,
    sample_index: int,
) -> tuple[float, float]:
    if category == "moon_circumference":
        moon_index = (
            MOON_OBJECT_IDS.index(
                object_id
            )
        )

        centre_angle = (
            pi / 2.0
            - moon_index
            * 2.0
            * pi
            / 12.0
        )

        centre = np.asarray(
            (
                7.0 * cos(
                    centre_angle
                ),
                7.0 * sin(
                    centre_angle
                ),
            ),
            dtype=float,
        )

        sample_angle = (
            2.0
            * pi
            * (
                sample_index - 1
            )
            / 6.0
        )

        point = (
            centre
            + 1.5
            * np.asarray(
                (
                    cos(sample_angle),
                    sin(sample_angle),
                )
            )
        )

        return (
            float(point[0]),
            float(point[1]),
        )

    if category == "wall_line":
        wall_index = (
            WALL_OBJECT_IDS.index(
                object_id
            )
        )

        normal_angle = (
            3.0 * pi / 4.0
            - wall_index
            * 2.0
            * pi
            / 12.0
        )

        normal = np.asarray(
            (
                cos(normal_angle),
                sin(normal_angle),
            ),
            dtype=float,
        )

        tangent = np.asarray(
            (
                -normal[1],
                normal[0],
            ),
            dtype=float,
        )

        offsets = (
            -1.2,
            0.0,
            1.2,
        )

        point = (
            8.5 * normal
            + offsets[
                sample_index - 1
            ]
            * tangent
        )

        return (
            float(point[0]),
            float(point[1]),
        )

    raise ValueError(
        f"Unexpected source-only category: {category}"
    )


def _synthetic_passes(
    tmp_path: Path,
) -> tuple[Path, ...]:
    schema = (
        build_figure12_observation_schema()
    )

    height = 2327
    width = 1512

    forward = np.asarray(
        (
            (
                70.0,
                1.25,
                760.0,
            ),
            (
                -0.75,
                72.0,
                900.0,
            ),
            (
                0.0,
                0.0,
                1.0,
            ),
        ),
        dtype=float,
    )

    paths: list[
        Path
    ] = []

    for pass_number in range(
        1,
        4,
    ):
        observations: list[
            Figure12DigitisedObservation
        ] = []

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

                model_point = (
                    definition.model_x,
                    definition.model_y,
                )

            else:
                model_point = (
                    _model_point_for_source_observation(
                        category=definition.category,
                        object_id=definition.object_id,
                        sample_index=definition.sample_index,
                    )
                )

            cartesian = (
                apply_registration_matrix(
                    forward,
                    np.asarray(
                        [
                            model_point
                        ],
                        dtype=float,
                    ),
                )[0]
            )

            pixel_x, pixel_y = (
                cartesian_to_pixel(
                    float(
                        cartesian[0]
                    ),
                    float(
                        cartesian[1]
                    ),
                    height,
                )
            )

            observations.append(
                Figure12DigitisedObservation(
                    pass_id=(
                        f"pass-{pass_number:02d}"
                    ),
                    definition=definition,
                    pixel_x=pixel_x,
                    pixel_y=pixel_y,
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

        paths.append(
            path
        )

    return tuple(
        paths
    )


def test_recovers_source_moon_geometry(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    report = (
        derive_figure12_source_geometry(
            paths
        )
    )

    assert len(
        report.moons
    ) == 12

    for moon in report.moons:
        assert (
            moon.centre_radius_from_origin_u
            == pytest.approx(
                7.0,
                abs=1.0e-8,
            )
        )

        assert (
            moon.radius_u
            == pytest.approx(
                1.5,
                abs=1.0e-8,
            )
        )

        assert (
            moon.radial_fit_rms_u
            < 1.0e-8
        )


def test_recovers_source_wall_supports(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    report = (
        derive_figure12_source_geometry(
            paths
        )
    )

    assert len(
        report.walls
    ) == 12

    assert len(
        report.vertices
    ) == 12

    assert len(
        report.sides
    ) == 12

    for wall in report.walls:
        assert (
            wall.support_h_u
            == pytest.approx(
                8.5,
                abs=1.0e-8,
            )
        )

        assert (
            wall.line_fit_rms_u
            < 1.0e-8
        )


def test_source_geometry_outputs_are_written(
    tmp_path: Path,
) -> None:
    paths = _synthetic_passes(
        tmp_path
    )

    report = (
        derive_figure12_source_geometry(
            paths
        )
    )

    outputs = (
        write_figure12_source_geometry(
            report,
            tmp_path
            / "derived",
        )
    )

    assert len(
        outputs
    ) == 9

    assert all(
        path.is_file()
        for path in outputs
    )

    report_text = (
        tmp_path
        / "derived"
        / "figure12_source_geometry_report.md"
    ).read_text(
        encoding="utf-8",
    )

    assert (
        "No NJG Moon-placement candidate"
        in report_text
    )

    assert (
        "source-plate measurements"
        in report_text
    )
