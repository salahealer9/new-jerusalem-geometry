#!/usr/bin/env python3

from math import pi

from new_jerusalem_geometry.core_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.septenary_geometry import (
    MichellTriangleBase,
    build_michell_28_point_scaffold,
    build_michell_fourteenfold_division,
    michell_four_triangle_division_angles,
)


def main() -> None:
    diagram = build_core_geometry()

    division = build_michell_fourteenfold_division(
        diagram,
        MichellTriangleBase.SOUTH,
    )

    print(
        "Michell reciprocal-triangle fourteenfold division"
    )
    print(
        "================================================="
    )
    print()

    print(
        "Primary triangle base:   "
        f"{division.primary.base_side.value}"
    )
    print(
        "Reciprocal base:         "
        f"{division.reciprocal.base_side.value}"
    )
    print(
        "Method-1 alpha:          "
        f"{division.primary.step_radians * 180.0 / pi:.12f}°"
    )
    print(
        "Division points:         "
        f"{len(division.points)}"
    )

    print()
    print("Fourteen angular positions")
    print("--------------------------")

    for index, angle in enumerate(
        division.angles_degrees
    ):
        print(
            f"{index:02d}: {angle:18.12f}°"
        )

    gaps = division.angular_gaps_degrees

    print()
    print("Angular-gap diagnostics")
    print("-----------------------")
    print(
        "Exact 360/14 gap:        "
        f"{360.0 / 14.0:.12f}°"
    )
    print(
        "Minimum approximate gap: "
        f"{min(gaps):.12f}°"
    )
    print(
        "Maximum approximate gap: "
        f"{max(gaps):.12f}°"
    )

    triangle_angles = (
        michell_four_triangle_division_angles(
            diagram
        )
    )

    scaffold = build_michell_28_point_scaffold(
        diagram
    )

    scaffold_angles = tuple(
        sorted(
            point.angle_radians
            for point in scaffold.points
        )
    )

    maximum_difference = max(
        abs(first - second)
        for first, second in zip(
            triangle_angles,
            scaffold_angles,
            strict=True,
        )
    )

    print()
    print("Four-triangle closure")
    print("---------------------")
    print(
        "Triangle-generated marks:"
        f" {len(triangle_angles)}"
    )
    print(
        "Existing scaffold marks: "
        f"{len(scaffold_angles)}"
    )
    print(
        "Maximum angular mismatch: "
        f"{maximum_difference:.3e} rad"
    )
    print(
        "Same 28-point set:        "
        f"{maximum_difference < 1.0e-12}"
    )


if __name__ == "__main__":
    main()
