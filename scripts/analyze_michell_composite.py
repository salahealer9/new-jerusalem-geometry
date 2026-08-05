#!/usr/bin/env python3

from math import pi

from new_jerusalem_geometry.michell_composite import (
    build_michell_composite,
)


def main() -> None:
    composite = build_michell_composite()

    print(
        "NJG_MICHELL forward composite"
    )
    print(
        "============================="
    )

    print()
    print("Core")
    print("----")
    print(
        f"Model:                     "
        f"{composite.model_name}"
    )
    print(
        f"Unit:                      "
        f"{composite.unit:.12f}"
    )
    print(
        f"Earth radius:              "
        f"{composite.core.dimensions.earth_radius:.12f} u"
    )
    print(
        f"Moon radius:               "
        f"{composite.core.dimensions.moon_radius:.12f} u"
    )
    print(
        f"Construction radius:       "
        f"{composite.core.dimensions.construction_radius:.12f} u"
    )

    print()
    print("Moon system")
    print("-----------")

    for group in composite.moon_groups:
        print(
            f"{group.direction:5s}: "
            + " | ".join(
                group.member_names
            )
        )

    print(
        f"Total Moon circles:        "
        f"{composite.moon_count}"
    )

    wall = composite.wall_reconstruction

    print()
    print("Polar-pivot wall")
    print("----------------")
    print(
        f"Moon model:                "
        f"{wall.model.value}"
    )
    print(
        f"Wall sides:                "
        f"{len(wall.lines)}"
    )
    print(
        f"Perimeter:                 "
        f"{wall.perimeter:.12f} u"
    )
    print(
        f"Area:                      "
        f"{wall.area:.12f} u^2"
    )

    print()
    print("Septenary chain")
    print("----------------")
    print(
        f"Sevenfold marks:           "
        f"{len(composite.sevenfold.points)}"
    )
    print(
        f"Method-1 alpha:            "
        f"{composite.sevenfold.step_radians * 180.0 / pi:.12f}°"
    )
    print(
        f"Fourteenfold marks:        "
        f"{len(composite.fourteenfold.points)}"
    )
    print(
        f"Four-triangle marks:       "
        f"{len(composite.four_triangle_angles_radians)}"
    )
    print(
        f"Role-labelled scaffold:    "
        f"{len(composite.scaffold.points)}"
    )
    print(
        f"28-set maximum mismatch:   "
        f"{composite.four_triangle_scaffold_max_mismatch_radians:.3e} rad"
    )

    star = (
        composite.scaffold_heptagram_candidate
    )

    print()
    print("Forward Figure 14 candidate")
    print("---------------------------")
    print(
        f"Candidate vertices:        "
        f"{len(star.vertices)}"
    )
    print(
        f"Heptagram family:          "
        f"{{7/{star.family.value}}}"
    )
    print(
        "Traversal:                 "
        + ", ".join(
            str(index)
            for index in star.traversal_indices()
        )
    )

    print()
    print("Provenance boundary")
    print("-------------------")
    print(
        "Caller-supplied geometry:  unit only"
    )
    print(
        "Plate calibration inputs:  none"
    )
    print(
        "Figure 14 status:           scaffold-derived candidate"
    )


if __name__ == "__main__":
    main()
