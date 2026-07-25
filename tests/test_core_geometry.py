from math import isclose, pi

import pytest

from new_jerusalem_geometry import (
    CoreDimensions,
    build_core_geometry,
    verify_core_geometry,
)


def test_core_dimensions() -> None:
    dimensions = CoreDimensions(unit=1.0)

    assert dimensions.earth_diameter == pytest.approx(11.0)
    assert dimensions.earth_radius == pytest.approx(5.5)
    assert dimensions.moon_diameter == pytest.approx(3.0)
    assert dimensions.moon_radius == pytest.approx(1.5)
    assert dimensions.construction_radius == pytest.approx(7.0)
    assert dimensions.earth_square_side == pytest.approx(11.0)


def test_geometry_is_scale_invariant() -> None:
    diagram = build_core_geometry(unit=720.0)
    dimensions = diagram.dimensions

    assert dimensions.earth_diameter == pytest.approx(7920.0)
    assert dimensions.moon_diameter == pytest.approx(2160.0)
    assert dimensions.construction_radius == pytest.approx(5040.0)


def test_all_core_constraints_pass() -> None:
    diagram = build_core_geometry()
    report = verify_core_geometry(diagram)

    assert report.passed
    assert all(check.passed for check in report.checks)


def test_cardinal_moon_count_and_names() -> None:
    diagram = build_core_geometry()

    assert len(diagram.cardinal_moons) == 4
    assert tuple(name for name, _ in diagram.cardinal_moons) == (
        "east",
        "north",
        "west",
        "south",
    )


def test_squared_circle_relation_is_approximate() -> None:
    diagram = build_core_geometry()
    report = verify_core_geometry(diagram)

    assert report.square_perimeter == pytest.approx(44.0)
    assert report.construction_circumference == pytest.approx(14.0 * pi)
    assert report.perimeter_discrepancy > 0.0

    assert report.perimeter_discrepancy == pytest.approx(
        44.0 - 14.0 * pi
    )

    assert isclose(
        100.0 * report.relative_perimeter_discrepancy,
        0.0402337494,
        rel_tol=0.0,
        abs_tol=1.0e-9,
    )


@pytest.mark.parametrize("invalid_unit", [0.0, -1.0])
def test_unit_must_be_positive(invalid_unit: float) -> None:
    with pytest.raises(ValueError):
        CoreDimensions(unit=invalid_unit)
