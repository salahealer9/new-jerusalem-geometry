#!/usr/bin/env python3
"""Generate a three-panel comparison of the oblique Moon models."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    build_oblique_placement,
    verify_core_geometry,
    verify_oblique_placement,
    write_oblique_models_comparison_svg,
)


DEFAULT_OUTPUT = Path(
    "figures/generated/oblique_models_comparison.svg"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a side-by-side SVG comparison of NJG_INC, "
            "NJG_28, and NJG_SVG."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path. Default: {DEFAULT_OUTPUT}",
    )

    parser.add_argument(
        "--unit",
        type=float,
        default=1.0,
        help="Fundamental length unit u. Default: 1.",
    )

    parser.add_argument(
        "--width",
        type=int,
        default=1800,
        help="SVG canvas width in pixels. Default: 1800.",
    )

    parser.add_argument(
        "--height",
        type=int,
        default=720,
        help="SVG canvas height in pixels. Default: 720.",
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

    core_report = verify_core_geometry(
        diagram,
        tolerance=args.tolerance,
    )

    if not core_report.passed:
        print("ERROR: cardinal core verification failed.")
        return 1

    model_reports = {}

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
        model_reports[model] = report

    if not all(report.passed for report in model_reports.values()):
        print("ERROR: an oblique model failed its defining constraints.")
        return 1

    output_path = write_oblique_models_comparison_svg(
        diagram,
        args.output,
        canvas_width=args.width,
        canvas_height=args.height,
    )

    print("New Jerusalem oblique-model comparison SVG")
    print("=" * 47)
    print("Core verification:  PASS")
    print("Model verification: PASS")
    print(f"Output:             {output_path}")
    print(f"Canvas:             {args.width} × {args.height} px")
    print()

    for model in ObliqueModel:
        report = model_reports[model]
        print(
            f"{model.value:7}  "
            f"max incidence residual = "
            f"{report.max_abs_incidence_residual:.15g} u"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
