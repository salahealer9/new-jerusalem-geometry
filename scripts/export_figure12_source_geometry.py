#!/usr/bin/env python3
"""Export normalized source-derived Figure 12 geometry."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure12_source_geometry import (
    derive_figure12_source_geometry,
    write_figure12_source_geometry,
)


DEFAULT_INPUT_DIRECTORY = Path(
    "data/calibration/figure12/"
    "digitisation/raw"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure12/"
    "source_geometry"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply the selected affine registration and "
            "derive normalized source geometry from Figure 12."
        )
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pass_paths = tuple(
        args.input_directory
        / (
            "figure12_observations_"
            f"pass-{index:02d}.csv"
        )
        for index in (1, 2, 3)
    )

    missing = tuple(
        path
        for path in pass_paths
        if not path.is_file()
    )

    if missing:
        print(
            "ERROR: missing Figure 12 raw calibration pass:"
        )

        for path in missing:
            print(
                f"  {path}"
            )

        return 1

    report = (
        derive_figure12_source_geometry(
            pass_paths
        )
    )

    outputs = (
        write_figure12_source_geometry(
            report,
            args.output_directory,
        )
    )

    print(
        "Figure 12 source-derived normalized geometry"
    )
    print(
        "=" * 43
    )

    print(
        "Selected registration:       centroid affine"
    )

    print(
        f"Scale range:                 "
        f"{report.pixels_per_unit_minimum:.6f} "
        f"to {report.pixels_per_unit_maximum:.6f} px/u"
    )

    print(
        f"Mean scale:                  "
        f"{report.mean_pixels_per_unit:.6f} px/u"
    )

    print(
        f"Moon circles:                "
        f"{len(report.moons)}"
    )

    print(
        f"Wall lines:                  "
        f"{len(report.walls)}"
    )

    print(
        f"Derived wall vertices:       "
        f"{len(report.vertices)}"
    )

    print(
        f"Source wall perimeter:       "
        f"{report.wall_perimeter_u:.9f} u"
    )

    print(
        f"Source wall area:            "
        f"{report.wall_area_u2:.9f} u^2"
    )

    print()
    print("Moon centres")
    print("------------")

    for moon in report.moons:
        print(
            f"{moon.moon_id:22s} "
            f"r0={moon.centre_radius_from_origin_u:.6f} u  "
            f"theta={moon.centre_angle_degrees:9.5f}°  "
            f"moon_r={moon.radius_u:.6f} u  "
            f"pass_RMS={moon.pass_centre_rms_u:.6f} u"
        )

    print()
    print("Wall supports")
    print("-------------")

    for wall in report.walls:
        print(
            f"{wall.wall_id:22s} "
            f"h={wall.support_h_u:.6f} u  "
            f"theta={wall.normal_angle_degrees:9.5f}°  "
            f"fit={wall.line_fit_rms_u:.6f} u"
        )

    print()
    print("Outputs:")

    for path in outputs:
        print(
            f"  {path}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
