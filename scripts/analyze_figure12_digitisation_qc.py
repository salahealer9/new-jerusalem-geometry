#!/usr/bin/env python3
"""Analyse repeatability of the three Figure 12 digitisation passes."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure12_digitisation_qc import (
    analyze_figure12_digitisation_qc,
    write_figure12_digitisation_qc,
)


DEFAULT_INPUT = Path(
    "data/working/figure12/digitisation"
)

DEFAULT_OUTPUT = Path(
    "data/working/figure12/qc"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run source-only repeatability QC on the three "
            "Figure 12 digitisation passes."
        )
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT,
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pass_paths = tuple(
        args.input_directory
        / f"figure12_observations_pass-0{index}.csv"
        for index in (1, 2, 3)
    )

    report = (
        analyze_figure12_digitisation_qc(
            pass_paths
        )
    )

    outputs = (
        write_figure12_digitisation_qc(
            report,
            args.output_directory,
        )
    )

    print(
        "Figure 12 digitisation QC"
    )
    print(
        "=" * 27
    )

    print(
        f"Registration max RMS:       "
        f"{report.maximum_registration_rms_pixels:.6f} px"
    )

    print(
        f"Registration max pairwise:  "
        f"{report.maximum_registration_pairwise_pixels:.6f} px"
    )

    print(
        f"Moon-centre max RMS:        "
        f"{report.maximum_moon_centre_rms_pixels:.6f} px"
    )

    print(
        f"Moon-centre max pairwise:   "
        f"{report.maximum_moon_centre_pairwise_pixels:.6f} px"
    )

    print(
        f"Moon-circle max fit RMS:    "
        f"{report.maximum_moon_radial_fit_rms_pixels:.6f} px"
    )

    print(
        f"Wall max angle pairwise:    "
        f"{report.maximum_wall_angle_pairwise_degrees:.6f}°"
    )

    print(
        f"Wall max offset pairwise:   "
        f"{report.maximum_wall_offset_pairwise_pixels:.6f} px"
    )

    print(
        f"Wall max fit RMS:           "
        f"{report.maximum_wall_fit_rms_pixels:.6f} px"
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
