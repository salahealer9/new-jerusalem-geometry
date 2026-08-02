"""Polar-pivot tangent reconstruction of Michell's outer wall.

This is a source-supported project reconstruction motivated by:

- four unchanged polar sides of an initial regular dodecagon;
- eight oblique sides pivoted inward about their polar-side endpoints;
- each pivoted side tangent to its corresponding Moon circle.

The construction is not claimed to be uniquely specified by Michell.

The Moon placement defaults to NJG_INC.
"""

from __future__ import annotations

from math import (
    acos,
    atan2,
    cos,
    hypot,
    pi,
    sin,
)

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .primitives import Point2D
from .wall_geometry import (
    OuterWall,
    WallLine,
    build_ordered_moon_circles,
)


POLAR_INDICES = frozenset(
    {
        0,
        3,
        6,
        9,
    }
)

PIVOT_POLAR_INDEX = {
    1: 0,
    2: 3,
    4: 3,
    5: 6,
    7: 6,
    8: 9,
    10: 9,
    11: 0,
}

POLAR_PIVOT_WALL_IDS = (
    "wall_east",
    "wall_east_north",
    "wall_north_east",
    "wall_north",
    "wall_north_west",
    "wall_west_north",
    "wall_west",
    "wall_west_south",
    "wall_south_west",
    "wall_south",
    "wall_south_east",
    "wall_east_south",
)


def _positive_angle(
    angle: float,
) -> float:
    return (
        angle
        % (
            2.0 * pi
        )
    )


def _angular_distance(
    first: float,
    second: float,
) -> float:
    return abs(
        (
            first
            - second
            + pi
        )
        % (
            2.0 * pi
        )
        - pi
    )


def _normal(
    angle: float,
) -> Point2D:
    return Point2D(
        cos(angle),
        sin(angle),
    )


def _intersection_normal_form(
    first_normal: Point2D,
    first_offset: float,
    second_normal: Point2D,
    second_offset: float,
) -> Point2D:
    determinant = (
        first_normal.x
        * second_normal.y
        - first_normal.y
        * second_normal.x
    )

    if abs(
        determinant
    ) <= 1.0e-15:
        raise ValueError(
            "Wall lines are parallel."
        )

    x = (
        first_offset
        * second_normal.y
        - first_normal.y
        * second_offset
    ) / determinant

    y = (
        first_normal.x
        * second_offset
        - first_offset
        * second_normal.x
    ) / determinant

    return Point2D(
        x,
        y,
    )


def _intersection_lines(
    first: WallLine,
    second: WallLine,
) -> Point2D:
    return _intersection_normal_form(
        first.normal,
        first.offset,
        second.normal,
        second.offset,
    )


def _regular_angle(
    index: int,
) -> float:
    return (
        index
        * pi
        / 6.0
    )


def _tangent_normal_from_pivot(
    *,
    pivot: Point2D,
    centre: Point2D,
    radius: float,
    preferred_angle: float,
) -> Point2D:
    """Return the tangent normal closest to a preferred direction."""

    dx = (
        pivot.x
        - centre.x
    )

    dy = (
        pivot.y
        - centre.y
    )

    distance = hypot(
        dx,
        dy,
    )

    if distance <= radius:
        raise ValueError(
            "No real tangent exists from the pivot to the Moon."
        )

    direction = atan2(
        dy,
        dx,
    )

    tangent_offset = acos(
        radius
        / distance
    )

    candidates = (
        _positive_angle(
            direction
            + tangent_offset
        ),
        _positive_angle(
            direction
            - tangent_offset
        ),
    )

    selected = min(
        candidates,
        key=lambda candidate: (
            _angular_distance(
                candidate,
                preferred_angle,
            )
        ),
    )

    return _normal(
        selected
    )


def build_polar_pivot_tangent_wall(
    diagram: CoreDiagram,
    model: ObliqueModel = ObliqueModel.INCIDENCE,
) -> OuterWall:
    """Construct the source-supported polar-pivot tangent wall."""

    if not isinstance(
        model,
        ObliqueModel,
    ):
        model = ObliqueModel(
            model
        )

    moons = build_ordered_moon_circles(
        diagram,
        model,
    )

    if len(
        moons
    ) != 12:
        raise ValueError(
            "Polar-pivot wall requires exactly twelve Moon circles."
        )

    apothem = (
        diagram.construction_circle.radius
        + diagram.dimensions.moon_radius
    )

    lines: list[
        WallLine
    ] = []

    for index, (
        moon_name,
        moon,
    ) in enumerate(
        moons
    ):
        regular_angle = (
            _regular_angle(
                index
            )
        )

        regular_normal = (
            _normal(
                regular_angle
            )
        )

        if index in POLAR_INDICES:
            normal = (
                regular_normal
            )

            offset = (
                apothem
            )

        else:
            pivot_index = (
                PIVOT_POLAR_INDEX[
                    index
                ]
            )

            pivot = (
                _intersection_normal_form(
                    regular_normal,
                    apothem,
                    _normal(
                        _regular_angle(
                            pivot_index
                        )
                    ),
                    apothem,
                )
            )

            normal = (
                _tangent_normal_from_pivot(
                    pivot=pivot,
                    centre=moon.centre,
                    radius=moon.radius,
                    preferred_angle=(
                        regular_angle
                    ),
                )
            )

            offset = (
                normal.x
                * pivot.x
                + normal.y
                * pivot.y
            )

        tangency_point = Point2D(
            moon.centre.x
            + moon.radius
            * normal.x,
            moon.centre.y
            + moon.radius
            * normal.y,
        )

        tangency_residual = (
            offset
            - normal.x
            * moon.centre.x
            - normal.y
            * moon.centre.y
            - moon.radius
        )

        if abs(
            tangency_residual
        ) > 1.0e-12:
            raise AssertionError(
                "Polar-pivot tangent construction failed "
                f"for {moon_name}: "
                f"{tangency_residual}"
            )

        lines.append(
            WallLine(
                name=(
                    POLAR_PIVOT_WALL_IDS[
                        index
                    ]
                ),
                moon_name=moon_name,
                normal=normal,
                offset=offset,
                tangency_point=(
                    tangency_point
                ),
            )
        )

    vertices = tuple(
        _intersection_lines(
            lines[index],
            lines[
                (
                    index
                    + 1
                )
                % len(
                    lines
                )
            ],
        )
        for index
        in range(
            len(
                lines
            )
        )
    )

    return OuterWall(
        model=model,
        moons=moons,
        lines=tuple(
            lines
        ),
        vertices=vertices,
    )


def wall_normal_angle_degrees(
    line: WallLine,
) -> float:
    """Return an outward wall-normal angle in [0, 360)."""

    return (
        atan2(
            line.normal.y,
            line.normal.x,
        )
        * 180.0
        / pi
    ) % 360.0
