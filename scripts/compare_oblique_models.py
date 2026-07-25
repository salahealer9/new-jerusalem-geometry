#!/usr/bin/env python3
"""Compare the three oblique Moon-circle placement models."""

from __future__ import annotations

import argparse
from math import degrees, pi

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_oblique_placement,
    square_intersection_angle,
    verify_oblique_placement,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the NJG_INC, NJG_28, and NJG_SVG "
            "oblique Moon placements."
        )
    )

    parser.add_argument(
        "--unit",
        type=float,
        default=1.0,
        help="Fundamental length unit u. Default: 1.",
    )

    parser.add_argument(
        "--tolerance",
        type=float,
        default=1.0e-12,
        help="Absolute verification tolerance.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    diagram = build_core_geometry(unit=args.unit)

    theta = square_intersection_angle(diagram)

    print("New Jerusalem oblique-model comparison")
    print("=" * 44)
    print(
        "Square-circle intersection angle: "
        f"{degrees(theta):.12f}°"
    )
    print()

    overall_pass = True

    for model in ObliqueModel:
        placement = build_oblique_placement(
            diagram,
            model,
        )

        report = verify_oblique_placement(
            diagram,
            placement,
            tolerance=args.tolerance,
        )

        deviation_from_28 = degrees(
            placement.beta_radians - pi / 7.0
        )

        print(model.value)
        print("-" * len(model.value))
        print(
            f"Oblique angle beta:       "
            f"{placement.beta_degrees:.12f}°"
        )
        print(
            f"Deviation from pi/7:      "
            f"{deviation_from_28:+.12f}°"
        )
        print(
            f"Max incidence residual:   "
            f"{report.max_abs_incidence_residual:.15g}"
        )
        print(
            f"Normalised residual:      "
            f"{report.max_abs_incidence_residual / args.unit:.15g} u"
        )
        print(
            f"Defining constraints:     "
            f"{'PASS' if report.passed else 'FAIL'}"
        )
        print()

        overall_pass = overall_pass and report.passed

    print(f"Overall defining constraints: {'PASS' if overall_pass else 'FAIL'}")

    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
