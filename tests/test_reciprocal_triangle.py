from __future__ import annotations

from math import pi

import pytest

from new_jerusalem_geometry.core_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.septenary_geometry import (
    MichellTriangleBase,
    build_michell_28_point_scaffold,
    build_michell_fourteenfold_division,
    build_michell_sevenfold_division,
    michell_four_triangle_division_angles,
)


def _sorted_angles(
    angles: tuple[float, ...],
) -> tuple[float, ...]:
    return tuple(
        sorted(
            angle % (2.0 * pi)
            for angle in angles
        )
    )


def test_single_triangle_generates_seven_points() -> None:
    diagram = build_core_geometry()

    division = build_michell_sevenfold_division(
        diagram,
        MichellTriangleBase.SOUTH,
    )

    assert len(division.points) == 7
    assert len(division.angles_radians) == 7

    for point in division.points:
        assert point.distance_to(
            diagram.origin
        ) == pytest.approx(
            diagram.construction_circle.radius,
            abs=1.0e-12,
        )


def test_reciprocal_triangle_is_opposite_rotation() -> None:
    diagram = build_core_geometry()

    south = build_michell_sevenfold_division(
        diagram,
        MichellTriangleBase.SOUTH,
    )

    north = build_michell_sevenfold_division(
        diagram,
        MichellTriangleBase.NORTH,
    )

    rotated = _sorted_angles(
        tuple(
            angle + pi
            for angle in south.angles_radians
        )
    )

    assert _sorted_angles(
        north.angles_radians
    ) == pytest.approx(
        rotated,
        abs=1.0e-12,
    )

    assert (
        MichellTriangleBase.SOUTH.reciprocal
        is MichellTriangleBase.NORTH
    )


def test_reciprocal_pair_generates_fourteen_points() -> None:
    diagram = build_core_geometry()

    division = build_michell_fourteenfold_division(
        diagram
    )

    assert len(division.points) == 14
    assert len(division.angles_radians) == 14

    for point in division.points:
        assert point.distance_to(
            diagram.origin
        ) == pytest.approx(
            diagram.construction_circle.radius,
            abs=1.0e-12,
        )


def test_reciprocal_fourteenfold_angles() -> None:
    diagram = build_core_geometry()

    division = build_michell_fourteenfold_division(
        diagram
    )

    expected_degrees = (
        12.941402864879908,
        38.52929856756005,
        64.41210429731987,
        90.0,
        115.58789570268013,
        141.47070143243995,
        167.0585971351201,
        192.9414028648799,
        218.52929856756005,
        244.41210429731987,
        270.0,
        295.5878957026801,
        321.47070143243995,
        347.0585971351201,
    )

    assert division.angles_degrees \
        == pytest.approx(
            expected_degrees,
            abs=1.0e-12,
        )


def test_four_triangle_union_equals_existing_scaffold() -> None:
    diagram = build_core_geometry()

    triangle_angles = (
        michell_four_triangle_division_angles(
            diagram
        )
    )

    scaffold = build_michell_28_point_scaffold(
        diagram
    )

    scaffold_angles = _sorted_angles(
        tuple(
            point.angle_radians
            for point in scaffold.points
        )
    )

    assert len(triangle_angles) == 28

    assert triangle_angles == pytest.approx(
        scaffold_angles,
        abs=1.0e-12,
    )


def test_fourteenfold_is_approximate_not_regular() -> None:
    diagram = build_core_geometry()

    division = build_michell_fourteenfold_division(
        diagram
    )

    exact_gap = 2.0 * pi / 14.0

    residuals = tuple(
        abs(
            gap - exact_gap
        )
        for gap in division.angular_gaps_radians
    )

    assert max(residuals) > 1.0e-6

    assert min(
        division.angular_gaps_degrees
    ) == pytest.approx(
        25.587895702680132,
        abs=1.0e-12,
    )

    assert max(
        division.angular_gaps_degrees
    ) == pytest.approx(
        25.882805729759816,
        abs=1.0e-12,
    )
