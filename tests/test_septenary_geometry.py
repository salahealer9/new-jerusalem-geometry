from math import pi

import pytest

from new_jerusalem_geometry import (
    ScaffoldRole,
    build_core_geometry,
    build_michell_28_point_scaffold,
    build_michell_gap_arithmetic,
    michell_heptagon_step_angle,
    michell_scaffold_local_offsets,
    verify_michell_28_point_scaffold,
)


def test_michell_heptagon_step_angle() -> None:
    angle = michell_heptagon_step_angle()

    assert angle * 180.0 / pi == pytest.approx(
        51.47070143243995,
        abs=1.0e-12,
    )


def test_heptagon_step_is_better_than_one_in_1000() -> None:
    angle = michell_heptagon_step_angle()
    exact = 2.0 * pi / 7.0

    relative_error = abs(angle / exact - 1.0)

    assert relative_error == pytest.approx(
        0.0008191945196658335,
        abs=1.0e-15,
    )

    assert relative_error < 1.0e-3


def test_local_offsets() -> None:
    offsets = tuple(
        value * 180.0 / pi
        for value in michell_scaffold_local_offsets()
    )

    assert offsets == pytest.approx(
        (
            0.0,
            12.941402864879908,
            25.587895702680132,
            38.52929856756005,
            51.47070143243995,
            64.41210429731987,
            77.0585971351201,
        ),
        abs=1.0e-12,
    )


def test_scaffold_has_twenty_eight_points() -> None:
    diagram = build_core_geometry()
    scaffold = build_michell_28_point_scaffold(diagram)

    assert len(scaffold.points) == 28
    assert [point.index for point in scaffold.points] == list(
        range(28)
    )


def test_scaffold_role_counts() -> None:
    diagram = build_core_geometry()
    scaffold = build_michell_28_point_scaffold(diagram)

    assert len(scaffold.moon_centre_points) == 12
    assert len(scaffold.inter_moon_gap_points) == 8
    assert (
        len(scaffold.intersection_positioner_points)
        == 8
    )


def test_role_sequence_repeats_in_each_quadrant() -> None:
    diagram = build_core_geometry()
    scaffold = build_michell_28_point_scaffold(diagram)

    expected = (
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTER_MOON_GAP,
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTERSECTION_POSITIONER,
        ScaffoldRole.INTERSECTION_POSITIONER,
        ScaffoldRole.MOON_CENTRE,
        ScaffoldRole.INTER_MOON_GAP,
    )

    for quadrant in range(4):
        actual = tuple(
            point.role
            for point in scaffold.points[
                quadrant * 7 : quadrant * 7 + 7
            ]
        )

        assert actual == expected


def test_gap_arithmetic_equals_forty_four() -> None:
    gaps = build_michell_gap_arithmetic()

    assert gaps.moon_total == pytest.approx(36.0)
    assert gaps.large_gap_total == pytest.approx(
        20.0 / 3.0
    )
    assert gaps.small_gap_total == pytest.approx(
        4.0 / 3.0
    )
    assert gaps.total == pytest.approx(44.0)


def test_scaffold_comparison_with_incidence_model() -> None:
    diagram = build_core_geometry()
    scaffold = build_michell_28_point_scaffold(diagram)

    report = verify_michell_28_point_scaffold(
        diagram,
        scaffold,
    )

    assert report.passed

    assert scaffold.beta_degrees == pytest.approx(
        25.587895702680132,
        abs=1.0e-12,
    )

    assert report.maximum_angular_displacement_degrees \
        == pytest.approx(
            0.3240353431759851,
            abs=1.0e-12,
        )

    assert report.maximum_centre_displacement \
        == pytest.approx(
            0.039588332659837536,
            abs=1.0e-12,
        )

    assert report.mean_centre_displacement \
        == pytest.approx(
            0.026392221773225023,
            abs=1.0e-12,
        )


def test_scaffold_incidence_residual() -> None:
    diagram = build_core_geometry()
    scaffold = build_michell_28_point_scaffold(diagram)

    report = verify_michell_28_point_scaffold(
        diagram,
        scaffold,
    )

    assert report.scaffold_incidence_residual \
        == pytest.approx(
            0.03935445072675403,
            abs=1.0e-12,
        )
