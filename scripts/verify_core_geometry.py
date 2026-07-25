#!/usr/bin/env python3
"""Verify the normalized New Jerusalem core geometry."""

from __future__ import annotations

import argparse
import json

from new_jerusalem_geometry import (
    build_core_geometry,
    verify_core_geometry,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify the New Jerusalem core geometry."
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
        help="Absolute numerical tolerance.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the report as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    diagram = build_core_geometry(unit=args.unit)
    report = verify_core_geometry(
        diagram,
        tolerance=args.tolerance,
    )

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print("New Jerusalem core verification")
        print("=" * 36)

        for check in report.checks:
            status = "PASS" if check.passed else "FAIL"
            print(
                f"{status:4}  {check.name}: "
                f"residual={check.residual:.16g}"
            )

        print()
        print(f"Square perimeter:          {report.square_perimeter:.15g}")
        print(
            "Construction circumference:"
            f" {report.construction_circumference:.15g}"
        )
        print(
            f"Perimeter discrepancy:     "
            f"{report.perimeter_discrepancy:.15g}"
        )
        print(
            f"Relative discrepancy:      "
            f"{100.0 * report.relative_perimeter_discrepancy:.9f}%"
        )
        print()
        print(f"Overall: {'PASS' if report.passed else 'FAIL'}")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
