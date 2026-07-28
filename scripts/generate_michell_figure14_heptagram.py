#!/usr/bin/env python3
"""Generate the Michell Figure 14 heptagram comparison SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_core_geometry,
    build_figure14_aligned_heptagram,
    build_figure14_anchor_set,
    build_regular_heptagram,
    build_scaffold_heptagram,
    verify_core_geometry,
    verify_figure14_heptagrams,
    write_michell_figure14_heptagram_svg,
)


DEFAULT_OUTPUT = Path(
    "figures/generated/michell_figure14_heptagram.svg"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a three-panel comparison of candidate "
            "reconstructions of Michell's Figure 14 heptagram."
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
        default=1600,
        help="SVG canvas width in pixels. Default: 1600.",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=920,
        help="SVG canvas height in pixels. Default: 920.",
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

    anchors = build_figure14_anchor_set(diagram)
    regular = build_regular_heptagram(diagram)
    scaffold = build_scaffold_heptagram(diagram)
    aligned = build_figure14_aligned_heptagram(
        diagram
    )

    report = verify_figure14_heptagrams(
        diagram,
        anchors,
        regular,
        scaffold,
        aligned,
        tolerance=args.tolerance,
    )

    if not report.passed:
        print("ERROR: Figure 14 verification failed.")
        return 1

    output_path = write_michell_figure14_heptagram_svg(
        diagram,
        args.output,
        canvas_width=args.width,
        canvas_height=args.height,
    )

    print("Michell Figure 14 heptagram comparison SVG")
    print("=" * 48)
    print("Core verification:       PASS")
    print("Figure 14 verification:  PASS")
    print(f"Output:                  {output_path}")
    print(
        f"Canvas:                  "
        f"{args.width} × {args.height} px"
    )
    print("Heptagram family:        {7/2}")
    print(
        f"Endpoint evidence:       "
        f"{report.stated_anchor_count} stated + "
        f"{report.inferred_anchor_count} inferred"
    )
    print(
        f"Regular maximum residual:"
        f" {report.regular_fit.maximum_point_residual:.15f} u"
    )
    print(
        f"Scaffold maximum residual:"
        f" {report.scaffold_fit.maximum_point_residual:.15f} u"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
