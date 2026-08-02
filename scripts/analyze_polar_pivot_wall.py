#!/usr/bin/env python3
"""Analyse the source-supported polar-pivot wall candidate."""

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.polar_pivot_wall import (
    POLAR_INDICES,
    build_polar_pivot_tangent_wall,
    wall_normal_angle_degrees,
)


UNIT_FEET = 720.0

SOURCE_POLAR_FEET = 3280.0
SOURCE_OBLIQUE_FEET = 3270.0
SOURCE_AREA_FEET2 = 120_000_000.0
SOURCE_OLD_ENGLISH_PERIMETER = 36_000.0


def relative_percent(
    value: float,
    target: float,
) -> float:
    return (
        100.0
        * (
            value
            - target
        )
        / target
    )


def main() -> int:
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
        for index
        in (
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

    polar_mean_u = (
        sum(
            polar
        )
        / len(
            polar
        )
    )

    oblique_mean_u = (
        sum(
            oblique
        )
        / len(
            oblique
        )
    )

    polar_feet = (
        polar_mean_u
        * UNIT_FEET
    )

    oblique_feet = (
        oblique_mean_u
        * UNIT_FEET
    )

    area_feet2 = (
        wall.area
        * UNIT_FEET**2
    )

    old_english_perimeter = (
        wall.perimeter
        * UNIT_FEET
        * 11.0
        / 12.0
    )

    print(
        "Polar-pivot tangent wall"
    )

    print(
        "=" * 24
    )

    print()
    print(
        "Wall-normal angles"
    )
    print(
        "------------------"
    )

    for line in wall.lines:
        print(
            f"{line.name:22s} "
            f"{wall_normal_angle_degrees(line):.12f}°"
        )

    print()
    print(
        "Exact geometry"
    )
    print(
        "--------------"
    )

    print(
        f"Polar side:             "
        f"{polar_mean_u:.12f} u"
    )

    print(
        f"Oblique side:           "
        f"{oblique_mean_u:.12f} u"
    )

    print(
        f"Perimeter:              "
        f"{wall.perimeter:.12f} u"
    )

    print(
        f"Area:                   "
        f"{wall.area:.12f} u²"
    )

    print()
    print(
        "Historical comparison"
    )
    print(
        "---------------------"
    )

    print(
        f"Polar side:             "
        f"{polar_feet:.6f} ft  "
        f"target={SOURCE_POLAR_FEET:.0f}  "
        f"error={relative_percent(polar_feet, SOURCE_POLAR_FEET):+.6f}%"
    )

    print(
        f"Oblique side:           "
        f"{oblique_feet:.6f} ft  "
        f"target={SOURCE_OBLIQUE_FEET:.0f}  "
        f"error={relative_percent(oblique_feet, SOURCE_OBLIQUE_FEET):+.6f}%"
    )

    print(
        f"Area:                   "
        f"{area_feet2:,.3f} ft²  "
        f"target={SOURCE_AREA_FEET2:,.0f}  "
        f"error={relative_percent(area_feet2, SOURCE_AREA_FEET2):+.6f}%"
    )

    print(
        f"Old-English perimeter: "
        f"{old_english_perimeter:,.3f} ft  "
        f"target={SOURCE_OLD_ENGLISH_PERIMETER:,.0f}  "
        f"error={relative_percent(old_english_perimeter, SOURCE_OLD_ENGLISH_PERIMETER):+.6f}%"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
