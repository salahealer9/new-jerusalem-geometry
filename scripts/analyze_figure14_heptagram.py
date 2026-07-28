#!/usr/bin/env python3
"""Analyse candidate reconstructions of Michell's Figure 14."""

from __future__ import annotations

from math import pi
from statistics import mean, pstdev

from new_jerusalem_geometry import (
    build_core_geometry,
    build_figure14_aligned_heptagram,
    build_figure14_anchor_set,
    build_regular_heptagram,
    build_scaffold_heptagram,
    verify_figure14_heptagrams,
)


def degrees(value: float) -> float:
    return value * 180.0 / pi


def edge_coefficient_of_variation(
    lengths: tuple[float, ...],
) -> float:
    return pstdev(lengths) / mean(lengths)


def print_fit(label: str, fit: object) -> None:
    print(label)
    print(
        f"  maximum residual:       "
        f"{fit.maximum_point_residual:.15f} u"
    )
    print(
        f"  RMS residual:           "
        f"{fit.rms_point_residual:.15f} u"
    )
    print(
        f"  maximum stated residual:"
        f" {fit.maximum_stated_point_residual:.15f} u"
    )
    print(
        f"  RMS stated residual:    "
        f"{fit.rms_stated_point_residual:.15f} u"
    )
    print(
        f"  maximum angular error:  "
        f"{fit.maximum_angular_residual_degrees:.12f}°"
    )
    print(
        f"  RMS angular error:      "
        f"{fit.rms_angular_residual_degrees:.12f}°"
    )


def main() -> int:
    diagram = build_core_geometry()

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
    )

    print("Michell Figure 14 heptagram analysis")
    print("=" * 41)
    print(
        f"Verification:             "
        f"{'PASS' if report.passed else 'FAIL'}"
    )
    print("Family:                   {7/2}")
    print(
        f"Traversal:                "
        f"{regular.traversal_indices()}"
    )
    print(
        f"Anchor roles:             "
        f"{report.moon_centre_count} Moon centres + "
        f"{report.junction_count} junctions + "
        f"{report.gap_count} inferred gaps"
    )
    print(
        f"Evidence:                 "
        f"{report.stated_anchor_count} text/plate + "
        f"{report.inferred_anchor_count} plate inference"
    )

    print()
    print("Figure 14 anchor angles")
    print("-----------------------")

    for anchor in anchors:
        print(
            f"{anchor.index}: "
            f"{anchor.angle_degrees:16.12f}°  "
            f"{anchor.role.value:24s}  "
            f"{anchor.name}"
        )

    print()
    print("Successive angular steps")
    print("------------------------")

    for index, step in enumerate(
        report.anchor_step_angles_radians
    ):
        print(
            f"{index} → {(index + 1) % 7}: "
            f"{degrees(step):.12f}°"
        )

    print()
    print("Candidate fits")
    print("--------------")
    print_fit("Exact regular {7/2}", report.regular_fit)
    print()
    print_fit(
        "Michell 28-point {7/2}",
        report.scaffold_fit,
    )
    print()
    print_fit(
        "Figure-14-aligned {7/2}",
        report.aligned_fit,
    )

    print()
    print("Heptagram edge variation")
    print("-------------------------")
    regular_cv = edge_coefficient_of_variation(
        report.regular_edge_lengths
    )
    scaffold_cv = edge_coefficient_of_variation(
        report.scaffold_edge_lengths
    )
    aligned_cv = edge_coefficient_of_variation(
        report.aligned_edge_lengths
    )

    print(
        f"Exact regular CV:         {regular_cv:.12f}"
    )
    print(
        f"Michell scaffold CV:      {scaffold_cv:.12f}"
    )
    print(
        f"Figure-14-aligned CV:     {aligned_cv:.12f}"
    )

    print()
    print("Fit comparison")
    print("--------------")
    print(
        "The regular candidate has the lower RMS residual."
    )
    print(
        "The Michell scaffold candidate has the lower "
        "maximum residual."
    )
    print(
        "Neither approximate construction strictly dominates."
    )

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
