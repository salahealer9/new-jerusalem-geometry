#!/usr/bin/env python3
"""Generate the verified New Jerusalem cardinal core SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_core_geometry,
    verify_core_geometry,
    write_core_svg,
)


DEFAULT_OUTPUT = Path("figures/generated/cardinal_core.svg")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate an SVG of the verified New Jerusalem "
            "cardinal core geometry."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output SVG path. Default: {DEFAULT_OUTPUT}",
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
        help="Verification tolerance. Default: 1e-12.",
    )

    parser.add_argument(
        "--size",
        type=int,
        default=900,
        help="Square SVG canvas size in pixels. Default: 900.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    diagram = build_core_geometry(unit=args.unit)
    report = verify_core_geometry(
        diagram,
        tolerance=args.tolerance,
    )

    if not report.passed:
        print("ERROR: core geometry verification failed.")
        for check in report.checks:
            if not check.passed:
                print(
                    f"FAIL  {check.name}: "
                    f"residual={check.residual:.16g}"
                )
        return 1

    output_path = write_core_svg(
        diagram,
        args.output,
        canvas_size=args.size,
    )

    print("New Jerusalem cardinal core SVG")
    print("=" * 36)
    print("Verification: PASS")
    print(f"Output:       {output_path}")
    print(f"Unit:         {diagram.dimensions.unit:g}")
    print(f"Objects:      {3 + len(diagram.cardinal_moons)}")
    print()
    print("Included:")
    print("  - Earth circle")
    print("  - Earth square")
    print("  - construction circle")
    print("  - four cardinal Moon circles")
    print(f"Canvas:       {args.size} × {args.size} px")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
