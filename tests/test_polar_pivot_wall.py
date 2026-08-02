import pytest

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
)
from new_jerusalem_geometry.polar_pivot_wall import (
    POLAR_INDICES,
    build_polar_pivot_tangent_wall,
    wall_normal_angle_degrees,
)


def test_polar_pivot_wall_has_twelve_sides() -> None:
    diagram = build_core_geometry()

    wall = (
        build_polar_pivot_tangent_wall(
            diagram,
            ObliqueModel.INCIDENCE,
        )
    )

    assert len(
        wall.lines
    ) == 12

    assert len(
        wall.vertices
    ) == 12


def test_every_polar_pivot_side_is_tangent() -> None:
    diagram = build_core_geometry()

    wall = (
        build_polar_pivot_tangent_wall(
            diagram
        )
    )

    moons = dict(
        wall.moons
    )

    for line in wall.lines:
        moon = moons[
            line.moon_name
        ]

        assert (
            line.distance_to(
                moon.centre
            )
            == pytest.approx(
                moon.radius,
                abs=1.0e-12,
            )
        )

        assert (
            line.evaluate(
                line.tangency_point
            )
            == pytest.approx(
                0.0,
                abs=1.0e-12,
            )
        )


def test_polar_pivot_angles() -> None:
    diagram = build_core_geometry()

    wall = (
        build_polar_pivot_tangent_wall(
            diagram
        )
    )

    angles = tuple(
        wall_normal_angle_degrees(
            line
        )
        for line in wall.lines
    )

    assert angles == pytest.approx(
        (
            0.0,
            30.571343304605,
            59.428656695395,
            90.0,
            120.571343304605,
            149.428656695395,
            180.0,
            210.571343304605,
            239.428656695395,
            270.0,
            300.571343304605,
            329.428656695395,
        ),
        abs=1.0e-10,
    )


def test_polar_pivot_side_classes() -> None:
    diagram = build_core_geometry()

    wall = (
        build_polar_pivot_tangent_wall(
            diagram
        )
    )

    polar = tuple(
        wall.side_lengths[
            index
        ]
        for index in (
            0,
            3,
            6,
            9,
        )
    )

    oblique = tuple(
        wall.side_lengths[
            index
        ]
        for index
        in range(
            12
        )
        if index
        not in POLAR_INDICES
    )

    assert max(
        polar
    ) - min(
        polar
    ) < 1.0e-12

    assert max(
        oblique
    ) - min(
        oblique
    ) < 1.0e-12

    assert polar[
        0
    ] == pytest.approx(
        4.555136271329,
        abs=1.0e-12,
    )

    assert oblique[
        0
    ] == pytest.approx(
        4.543223126508,
        abs=1.0e-12,
    )

    assert polar[
        0
    ] > oblique[
        0
    ]


def test_polar_pivot_global_dimensions() -> None:
    diagram = build_core_geometry()

    wall = (
        build_polar_pivot_tangent_wall(
            diagram
        )
    )

    assert wall.perimeter == pytest.approx(
        54.566330097384,
        abs=1.0e-11,
    )

    assert wall.area == pytest.approx(
        231.486496089401,
        abs=1.0e-11,
    )

    unit_feet = 720.0

    assert (
        wall.area
        * unit_feet**2
        == pytest.approx(
            120002599.573,
            abs=1.0,
        )
    )

    old_english_perimeter = (
        wall.perimeter
        * unit_feet
        * 11.0
        / 12.0
    )

    assert old_english_perimeter == pytest.approx(
        36013.778,
        abs=0.01,
    )
