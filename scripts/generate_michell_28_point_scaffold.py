#!/usr/bin/env python3
"""Generate Michell's 28-point scaffold comparison SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_core_geometry,
    build_michell_28_point_scaffold,
    verify_core_geometry,
    verify_michell_28_point_scaffold,
    write_michell_28_point_scaffold_svg,
)


DEFAULT_OUTPUT = Path(
    "figures/generated/michell_28_point_scaffold.svg"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an SVG comparing Michell's approximate "
            "28-point scaffold with NJG_INC."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path. Default: {DEFAULT_OUTPUT}",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1400,
        help="SVG canvas width in pixels. Default: 1400.",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=900,
        help="SVG canvas height in pixels. Default: 900.",
    )

    parser.add_argument(
        "--displacement-magnification",
        type=float,
        default=40.0,
        help=(
            "Magnification used in the displacement inset. "
            "Default: 40."
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

    diagram = build_core_geometry()

    core_report = verify_core_geometry(
        diagram,
        tolerance=args.tolerance,
    )

    if not core_report.passed:
        print("ERROR: cardinal core verification failed.")
        return 1

    scaffold = build_michell_28_point_scaffold(
        diagram
    )

    scaffold_report = verify_michell_28_point_scaffold(
        diagram,
        scaffold,
        tolerance=args.tolerance,
    )

    if not scaffold_report.passed:
        print("ERROR: scaffold verification failed.")
        return 1

    output_path = write_michell_28_point_scaffold_svg(
        diagram,
        args.output,
        scaffold,
        canvas_width=args.width,
        canvas_height=args.height,
        displacement_magnification=(
            args.displacement_magnification
        ),
    )

    print("Michell 28-point scaffold comparison SVG")
    print("=" * 45)
    print("Core verification:      PASS")
    print("Scaffold verification:  PASS")
    print(f"Output:                 {output_path}")
    print(
        f"Canvas:                 "
        f"{args.width} × {args.height} px"
    )
    print(f"Scaffold points:        {len(scaffold.points)}")
    print(
        f"Role counts:            "
        f"{scaffold_report.moon_centre_count} + "
        f"{scaffold_report.inter_moon_gap_count} + "
        f"{scaffold_report.intersection_positioner_count}"
    )
    print(
        f"Max centre displacement:"
        f" {scaffold_report.maximum_centre_displacement:.15f} u"
    )
    print(
        f"Displacement inset:     "
        f"{args.displacement_magnification:g}×"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
