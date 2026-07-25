#!/usr/bin/env python3
"""Analyse the inferred outer wall of Michell's New Jerusalem."""

from __future__ import annotations

import argparse
from collections import Counter

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_radial_support_wall,
    verify_outer_wall,
)


MICHELL_MEAN_SIDE_FEET = 3264.0
MICHELL_PERIMETER_MY = 14400.0
MICHELL_AREA_SQUARE_FEET = 120_000_000.0
FEET_PER_MY = 2.72


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Construct and verify the inferred radial-support "
            "outer wall."
        )
    )

    parser.add_argument(
        "--unit-feet",
        type=float,
        default=720.0,
        help=(
            "Physical length represented by one normalized unit. "
            "Default: 720 feet."
        ),
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=1.0e-12,
        help="Absolute numerical tolerance.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.unit_feet <= 0.0:
        raise ValueError("--unit-feet must be positive.")

    diagram = build_core_geometry()
    wall = build_radial_support_wall(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    report = verify_outer_wall(
        diagram,
        wall,
        tolerance=args.tolerance,
    )

    side_lengths_feet = tuple(
        length * args.unit_feet
        for length in report.side_lengths
    )

    mean_side_feet = (
        report.mean_side_length * args.unit_feet
    )

    perimeter_feet = report.perimeter * args.unit_feet
    perimeter_my = perimeter_feet / FEET_PER_MY

    area_square_feet = (
        report.area * args.unit_feet**2
    )

    mean_side_difference_percent = (
        100.0
        * (mean_side_feet - MICHELL_MEAN_SIDE_FEET)
        / MICHELL_MEAN_SIDE_FEET
    )

    area_difference_percent = (
        100.0
        * (
            area_square_feet
            - MICHELL_AREA_SQUARE_FEET
        )
        / MICHELL_AREA_SQUARE_FEET
    )

    rounded_classes = Counter(
        round(length, 9)
        for length in report.side_lengths
    )

    print("New Jerusalem inferred outer-wall analysis")
    print("=" * 46)
    print(
        f"Constraint verification: "
        f"{'PASS' if report.passed else 'FAIL'}"
    )
    print(f"Model:                  {wall.model.value}")
    print(f"Wall sides:             {len(wall.lines)}")
    print(f"Wall vertices:          {len(wall.vertices)}")
    print()
    print("Normalized geometry")
    print("-------------------")
    print(f"Perimeter:              {report.perimeter:.15f} u")
    print(
        f"Mean side length:        "
        f"{report.mean_side_length:.15f} u"
    )
    print(f"Area:                   {report.area:.15f} u²")
    print()
    print("Side-length classes")
    print("-------------------")

    for value, count in sorted(rounded_classes.items()):
        print(
            f"{count:2d} sides × {value:.9f} u "
            f"= {value * args.unit_feet:.6f} ft each"
        )

    print()
    print("Comparison with Michell")
    print("-----------------------")
    print(
        f"Computed mean side:      "
        f"{mean_side_feet:.6f} ft"
    )
    print(
        f"Michell mean side:       "
        f"{MICHELL_MEAN_SIDE_FEET:.6f} ft"
    )
    print(
        f"Difference:              "
        f"{mean_side_difference_percent:+.6f}%"
    )
    print()
    print(
        f"Computed perimeter:      "
        f"{perimeter_my:.6f} MY"
    )
    print(
        f"Michell perimeter:       "
        f"{MICHELL_PERIMETER_MY:.6f} MY"
    )
    print()
    print(
        f"Computed area:           "
        f"{area_square_feet:.3f} ft²"
    )
    print(
        f"Michell area:            "
        f"{MICHELL_AREA_SQUARE_FEET:.3f} ft²"
    )
    print(
        f"Difference:              "
        f"{area_difference_percent:+.6f}%"
    )

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
