from __future__ import annotations

from math import cos, pi, sin

import numpy as np
import pytest

from new_jerusalem_geometry.figure12_digitisation_qc import (
    fit_circle,
    fit_line,
)


def test_circle_fit_recovers_exact_circle() -> None:
    centre_x = 123.5
    centre_y = 456.25
    radius = 80.0

    points = np.asarray(
        [
            (
                centre_x
                + radius * cos(
                    2.0 * pi * index / 6.0
                ),
                centre_y
                + radius * sin(
                    2.0 * pi * index / 6.0
                ),
            )
            for index in range(6)
        ],
        dtype=float,
    )

    (
        fitted_x,
        fitted_y,
        fitted_radius,
        radial_rms,
    ) = fit_circle(points)

    assert fitted_x == pytest.approx(
        centre_x,
        abs=1.0e-10,
    )

    assert fitted_y == pytest.approx(
        centre_y,
        abs=1.0e-10,
    )

    assert fitted_radius == pytest.approx(
        radius,
        abs=1.0e-10,
    )

    assert radial_rms < 1.0e-10


def test_line_fit_recovers_exact_line() -> None:
    points = np.asarray(
        (
            (10.0, 25.0),
            (50.0, 45.0),
            (90.0, 65.0),
        ),
        dtype=float,
    )

    (
        normal_x,
        normal_y,
        offset,
        _,
        _,
        fit_rms,
    ) = fit_line(points)

    residuals = (
        points
        @ np.asarray(
            (
                normal_x,
                normal_y,
            )
        )
        + offset
    )

    assert np.max(
        np.abs(residuals)
    ) < 1.0e-10

    assert fit_rms < 1.0e-10


def test_circle_fit_rejects_collinear_points() -> None:
    points = np.asarray(
        (
            (0.0, 0.0),
            (1.0, 1.0),
            (2.0, 2.0),
            (3.0, 3.0),
        ),
        dtype=float,
    )

    with pytest.raises(
        ValueError,
        match="degenerate",
    ):
        fit_circle(points)
