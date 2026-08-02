import math

import pytest

from new_jerusalem_geometry.figure12_wall_model_comparison import (
    RADIAL_SUPPORT,
    REGULAR_DIRECTION_TANGENT,
    predict_wall,
)


def test_regular_direction_tangent_prediction() -> None:
    beta = math.radians(
        25.0
    )

    x = 7.0 * math.cos(
        beta
    )

    y = 7.0 * math.sin(
        beta
    )

    prediction = predict_wall(
        hypothesis=REGULAR_DIRECTION_TANGENT,
        wall_id="wall_east_north",
        moon_id="moon_east_north",
        regular_angle_degrees=30.0,
        moon_x_u=x,
        moon_y_u=y,
        moon_radius_u=1.5,
    )

    expected_h = (
        math.cos(
            math.radians(
                30.0
            )
        )
        * x
        + math.sin(
            math.radians(
                30.0
            )
        )
        * y
        + 1.5
    )

    assert (
        prediction.predicted_angle_degrees
        == pytest.approx(
            30.0
        )
    )

    assert (
        prediction.predicted_support_h_u
        == pytest.approx(
            expected_h
        )
    )


def test_radial_support_prediction() -> None:
    beta = math.radians(
        25.0
    )

    x = 7.0 * math.cos(
        beta
    )

    y = 7.0 * math.sin(
        beta
    )

    prediction = predict_wall(
        hypothesis=RADIAL_SUPPORT,
        wall_id="wall_east_north",
        moon_id="moon_east_north",
        regular_angle_degrees=30.0,
        moon_x_u=x,
        moon_y_u=y,
        moon_radius_u=1.5,
    )

    assert (
        prediction.predicted_angle_degrees
        == pytest.approx(
            25.0
        )
    )

    assert (
        prediction.predicted_support_h_u
        == pytest.approx(
            8.5
        )
    )


def test_hypotheses_are_geometrically_distinct() -> None:
    beta = math.radians(
        25.0
    )

    x = 7.0 * math.cos(
        beta
    )

    y = 7.0 * math.sin(
        beta
    )

    regular = predict_wall(
        hypothesis=REGULAR_DIRECTION_TANGENT,
        wall_id="wall_east_north",
        moon_id="moon_east_north",
        regular_angle_degrees=30.0,
        moon_x_u=x,
        moon_y_u=y,
        moon_radius_u=1.5,
    )

    radial = predict_wall(
        hypothesis=RADIAL_SUPPORT,
        wall_id="wall_east_north",
        moon_id="moon_east_north",
        regular_angle_degrees=30.0,
        moon_x_u=x,
        moon_y_u=y,
        moon_radius_u=1.5,
    )

    assert (
        regular.predicted_angle_degrees
        != pytest.approx(
            radial.predicted_angle_degrees
        )
    )

    assert (
        regular.predicted_support_h_u
        != pytest.approx(
            radial.predicted_support_h_u
        )
    )
