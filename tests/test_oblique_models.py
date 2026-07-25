from math import pi

import pytest

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_oblique_placement,
    build_square_construction_intersections,
    verify_oblique_placement,
)


def test_eight_square_circle_intersections() -> None:
    diagram = build_core_geometry()
    intersections = build_square_construction_intersections(
        diagram
    )

    assert len(intersections) == 8
    assert len({item.name for item in intersections}) == 8


def test_intersections_lie_on_circle_and_square_boundary() -> None:
    diagram = build_core_geometry()
    intersections = build_square_construction_intersections(
        diagram
    )

    radius = diagram.construction_circle.radius
    half_side = diagram.earth_square.half_side

    for intersection in intersections:
        point = intersection.point

        assert diagram.origin.distance_to(point) == pytest.approx(
            radius,
            abs=1.0e-12,
        )

        assert max(abs(point.x), abs(point.y)) == pytest.approx(
            half_side,
            abs=1.0e-12,
        )


@pytest.mark.parametrize("model", list(ObliqueModel))
def test_each_model_builds_eight_oblique_moons(
    model: ObliqueModel,
) -> None:
    diagram = build_core_geometry()
    placement = build_oblique_placement(diagram, model)

    assert len(placement.moons) == 8
    assert len({moon.name for moon in placement.moons}) == 8


@pytest.mark.parametrize("model", list(ObliqueModel))
def test_each_model_satisfies_its_defining_constraints(
    model: ObliqueModel,
) -> None:
    diagram = build_core_geometry()
    placement = build_oblique_placement(diagram, model)
    report = verify_oblique_placement(diagram, placement)

    assert report.passed


def test_model_angles_have_expected_order() -> None:
    diagram = build_core_geometry()

    beta_28 = build_oblique_placement(
        diagram,
        ObliqueModel.DIVISION_28,
    ).beta_degrees

    beta_svg = build_oblique_placement(
        diagram,
        ObliqueModel.WIKIMEDIA_SVG,
    ).beta_degrees

    beta_inc = build_oblique_placement(
        diagram,
        ObliqueModel.INCIDENCE,
    ).beta_degrees

    assert beta_28 == pytest.approx(
        360.0 / 14.0,
        abs=1.0e-12,
    )

    assert beta_28 < beta_svg < beta_inc

    assert beta_svg == pytest.approx(
        25.839585585549635,
        abs=1.0e-12,
    )

    assert beta_inc == pytest.approx(
        25.911931045856118,
        abs=1.0e-12,
    )


def test_incidence_model_has_zero_incidence_residual() -> None:
    diagram = build_core_geometry()
    placement = build_oblique_placement(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    assert placement.max_abs_incidence_residual == pytest.approx(
        0.0,
        abs=1.0e-12,
    )


def test_28_fold_model_has_measurable_incidence_residual() -> None:
    diagram = build_core_geometry()
    placement = build_oblique_placement(
        diagram,
        ObliqueModel.DIVISION_28,
    )

    assert placement.max_abs_incidence_residual == pytest.approx(
        0.0240056909272872,
        abs=1.0e-12,
    )


def test_svg_model_has_smaller_but_nonzero_residual() -> None:
    diagram = build_core_geometry()

    svg_placement = build_oblique_placement(
        diagram,
        ObliqueModel.WIKIMEDIA_SVG,
    )

    division_placement = build_oblique_placement(
        diagram,
        ObliqueModel.DIVISION_28,
    )

    assert svg_placement.max_abs_incidence_residual == pytest.approx(
        0.0087874872753280,
        abs=1.0e-12,
    )

    assert (
        0.0
        < svg_placement.max_abs_incidence_residual
        < division_placement.max_abs_incidence_residual
    )


def test_28_fold_angle_is_exact_pi_over_seven() -> None:
    diagram = build_core_geometry()
    placement = build_oblique_placement(
        diagram,
        ObliqueModel.DIVISION_28,
    )

    assert placement.beta_radians == pytest.approx(
        pi / 7.0,
        abs=1.0e-15,
    )
