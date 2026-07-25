import pytest

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_ordered_moon_circles,
    build_radial_support_wall,
    verify_outer_wall,
)


def test_wall_uses_twelve_ordered_moons() -> None:
    diagram = build_core_geometry()

    moons = build_ordered_moon_circles(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    assert len(moons) == 12
    assert len({name for name, _ in moons}) == 12


def test_wall_contains_twelve_lines_and_vertices() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)

    assert len(wall.lines) == 12
    assert len(wall.vertices) == 12


def test_wall_constraints_pass() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)
    report = verify_outer_wall(diagram, wall)

    assert report.passed
    assert all(check.passed for check in report.checks)


def test_every_wall_side_is_tangent_to_its_moon() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)

    moons = dict(wall.moons)

    for line in wall.lines:
        moon = moons[line.moon_name]

        assert line.distance_to(
            moon.centre
        ) == pytest.approx(
            moon.radius,
            abs=1.0e-12,
        )


def test_wall_has_two_side_length_classes() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)

    short_length = 3.91100001373699
    long_length = 4.89690680337037

    short_count = sum(
        length == pytest.approx(
            short_length,
            abs=1.0e-12,
        )
        for length in wall.side_lengths
    )

    long_count = sum(
        length == pytest.approx(
            long_length,
            abs=1.0e-12,
        )
        for length in wall.side_lengths
    )

    assert short_count == 4
    assert long_count == 8


def test_wall_perimeter_and_area() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)

    assert wall.perimeter == pytest.approx(
        54.81925448191095,
        abs=1.0e-12,
    )

    assert wall.mean_side_length == pytest.approx(
        4.568271206825913,
        abs=1.0e-12,
    )

    assert wall.area == pytest.approx(
        232.98183154812156,
        abs=1.0e-10,
    )


def test_wall_is_close_to_michell_dimensions() -> None:
    diagram = build_core_geometry()
    wall = build_radial_support_wall(diagram)

    unit_feet = 720.0

    mean_side_feet = (
        wall.mean_side_length * unit_feet
    )

    area_square_feet = (
        wall.area * unit_feet**2
    )

    assert mean_side_feet == pytest.approx(
        3289.155268914657,
        abs=1.0e-9,
    )

    assert area_square_feet == pytest.approx(
        120_777_781.47454622,
        abs=1.0e-5,
    )

    assert abs(
        mean_side_feet - 3264.0
    ) / 3264.0 < 0.01

    assert abs(
        area_square_feet - 120_000_000.0
    ) / 120_000_000.0 < 0.01
