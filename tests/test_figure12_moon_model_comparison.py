import pytest

from new_jerusalem_geometry.figure12_digitisation import (
    MOON_OBJECT_IDS,
)
from new_jerusalem_geometry.figure12_moon_model_comparison import (
    CANDIDATE_ORDER,
    _compare_centres,
    build_candidate_centres,
)


def test_candidate_betas_are_ordered() -> None:
    # Use the east-north oblique Moon so its angle is beta itself.
    def east_north_beta(candidate):
        return next(
            item.angle_degrees
            for item in build_candidate_centres(
                candidate
            )
            if item.moon_id
            == "moon_east_north"
        )

    values = [
        east_north_beta(
            candidate
        )
        for candidate
        in CANDIDATE_ORDER
    ]

    assert (
        values[0]
        < values[1]
        < values[2]
        < values[3]
    )


def test_candidate_contains_all_twelve_moons() -> None:
    for candidate in CANDIDATE_ORDER:
        centres = (
            build_candidate_centres(
                candidate
            )
        )

        assert len(
            centres
        ) == 12

        assert {
            item.moon_id
            for item in centres
        } == set(
            MOON_OBJECT_IDS
        )


def test_exact_candidate_has_zero_residual() -> None:
    candidate = "NJG_SVG"

    expected = (
        build_candidate_centres(
            candidate
        )
    )

    observed = {
        item.moon_id: (
            item.x_u,
            item.y_u,
        )
        for item in expected
    }

    fit, residuals = (
        _compare_centres(
            observed,
            candidate,
        )
    )

    assert (
        fit.all_rms_u
        < 1.0e-12
    )

    assert (
        fit.oblique_rms_u
        < 1.0e-12
    )

    assert max(
        row.distance_u
        for row in residuals
    ) < 1.0e-12
