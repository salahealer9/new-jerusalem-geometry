#!/usr/bin/env python3
"""Generate the inferred Michell outer-wall SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_radial_support_wall,
    verify_core_geometry,
    verify_outer_wall,
    write_michell_outer_wall_svg,
)


DEFAULT_OUTPUT = Path(
    "figures/generated/michell_outer_wall.svg"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an SVG of the exact-incidence Moon circles "
            "and inferred radial-support wall."
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
        default=1200,
        help="SVG canvas width in pixels. Default: 1200.",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=900,
        help="SVG canvas height in pixels. Default: 900.",
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
        help="Absolute verification tolerance.",
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

    wall = build_radial_support_wall(
        diagram,
        ObliqueModel.INCIDENCE,
    )

    wall_report = verify_outer_wall(
        diagram,
        wall,
        tolerance=args.tolerance,
    )

    if not wall_report.passed:
        print("ERROR: outer-wall verification failed.")
        return 1

    output_path = write_michell_outer_wall_svg(
        diagram,
        args.output,
        wall,
        canvas_width=args.width,
        canvas_height=args.height,
        unit_feet=args.unit_feet,
    )

    print("New Jerusalem inferred Michell wall SVG")
    print("=" * 43)
    print("Core verification:  PASS")
    print("Wall verification:  PASS")
    print(f"Output:             {output_path}")
    print(f"Canvas:             {args.width} × {args.height} px")
    print(f"Wall sides:         {len(wall.lines)}")
    print(f"Mean side:          {wall_report.mean_side_length:.15f} u")
    print(f"Area:               {wall_report.area:.15f} u²")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
