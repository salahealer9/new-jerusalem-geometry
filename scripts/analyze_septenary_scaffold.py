#!/usr/bin/env python3
"""Analyse Michell's approximate twenty-eight-point scaffold."""

from __future__ import annotations

from math import pi

from new_jerusalem_geometry import (
    build_core_geometry,
    build_michell_28_point_scaffold,
    build_michell_gap_arithmetic,
    verify_michell_28_point_scaffold,
)


def degrees(value: float) -> float:
    return value * 180.0 / pi


def main() -> int:
    diagram = build_core_geometry()

    scaffold = build_michell_28_point_scaffold(
        diagram
    )

    report = verify_michell_28_point_scaffold(
        diagram,
        scaffold,
    )

    gaps = build_michell_gap_arithmetic()

    print("Michell approximate 28-point scaffold")
    print("=" * 43)
    print(
        f"Verification:             "
        f"{'PASS' if report.passed else 'FAIL'}"
    )
    print(f"Scaffold points:          {len(scaffold.points)}")
    print(
        f"Role counts:              "
        f"{report.moon_centre_count} Moon centres + "
        f"{report.inter_moon_gap_count} gaps + "
        f"{report.intersection_positioner_count} "
        "intersection positioners"
    )
    print()
    print("Septenary approximation")
    print("------------------------")
    print(
        f"Michell step alpha:       "
        f"{scaffold.heptagon_step_degrees:.12f}°"
    )
    print(
        f"Exact 360/7 step:         "
        f"{degrees(report.exact_heptagon_step_radians):.12f}°"
    )
    step_difference = (
        scaffold.heptagon_step_radians
        - report.exact_heptagon_step_radians
    )

    print(
        f"Angular difference:       "
        f"{degrees(step_difference):+.12f}°"
    )
    print(
        f"Relative error:           "
        f"{100.0 * report.relative_heptagon_step_error:.9f}%"
    )
    print()
    print("Oblique Moon placement")
    print("----------------------")
    print(
        f"Scaffold beta:            "
        f"{degrees(report.scaffold_beta_radians):.12f}°"
    )
    print(
        f"NJG_INC beta:             "
        f"{degrees(report.incidence_beta_radians):.12f}°"
    )
    beta_difference = (
        report.scaffold_beta_radians
        - report.incidence_beta_radians
    )

    print(
        f"Angular difference:       "
        f"{degrees(beta_difference):+.12f}°"
    )
    print(
        f"Max centre displacement:  "
        f"{report.maximum_centre_displacement:.15f} u"
    )
    print(
        f"Mean centre displacement: "
        f"{report.mean_centre_displacement:.15f} u"
    )
    print(
        f"Max angular displacement: "
        f"{report.maximum_angular_displacement_degrees:.12f}°"
    )
    print(
        f"Square-circle incidence "
        f"residual: {report.scaffold_incidence_residual:.15f} u"
    )
    print()
    print("Figure 28 gap arithmetic")
    print("------------------------")
    print(
        f"Moon arcs:                "
        f"{gaps.moon_count} × {gaps.moon_diameter:.12f} "
        f"= {gaps.moon_total:.12f}"
    )
    print(
        f"Large gaps:               "
        f"{gaps.large_gap_count} × {gaps.large_gap:.12f} "
        f"= {gaps.large_gap_total:.12f}"
    )
    print(
        f"Small gaps:               "
        f"{gaps.small_gap_count} × {gaps.small_gap:.12f} "
        f"= {gaps.small_gap_total:.12f}"
    )
    print(
        f"Total:                    "
        f"{gaps.total:.12f}"
    )

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
