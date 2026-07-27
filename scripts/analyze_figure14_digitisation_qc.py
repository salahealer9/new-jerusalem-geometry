#!/usr/bin/env python3
"""Analyse repeated Figure 14 landmark digitisation passes."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_digitisation_qc import (
    analyze_digitisation_passes,
    write_category_qc_csv,
    write_landmark_qc_csv,
    write_pass_qc_csv,
    write_qc_markdown,
)


DEFAULT_INPUT_DIRECTORY = Path(
    "data/working/figure14"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure14/qc"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Measure repeated-click uncertainty across "
            "independent Figure 14 digitisation passes."
        )
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
        help=(
            "Directory containing pass CSVs. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Directory for local QC outputs. "
            f"Default: {DEFAULT_OUTPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--absolute-review-threshold",
        type=float,
        default=5.0,
        help=(
            "Flag a landmark when maximum pairwise separation "
            "exceeds this number of pixels. Default: 5."
        ),
    )

    parser.add_argument(
        "--robust-z-review-threshold",
        type=float,
        default=3.5,
        help=(
            "Flag a landmark when its robust z-score exceeds "
            "this value. Default: 3.5."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pass_paths = sorted(
        args.input_directory.glob(
            "figure14_digitisation_pass-*.csv"
        )
    )

    if len(pass_paths) < 2:
        print(
            "ERROR: expected at least two digitisation passes "
            f"in {args.input_directory}."
        )
        return 1

    report = analyze_digitisation_passes(
        pass_paths,
        absolute_review_threshold_pixels=(
            args.absolute_review_threshold
        ),
        robust_z_review_threshold=(
            args.robust_z_review_threshold
        ),
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    landmark_path = write_landmark_qc_csv(
        args.output_directory
        / "figure14_landmark_qc.csv",
        report,
    )

    pass_path = write_pass_qc_csv(
        args.output_directory
        / "figure14_pass_qc.csv",
        report,
    )

    category_path = write_category_qc_csv(
        args.output_directory
        / "figure14_category_qc.csv",
        report,
    )

    report_path = write_qc_markdown(
        args.output_directory
        / "figure14_digitisation_qc.md",
        report,
    )

    status = (
        "REVIEW"
        if report.review_flag_count
        else "PASS"
    )

    print("Figure 14 repeated-digitisation QC")
    print("=" * 38)
    print(f"Status:                    {status}")
    print(
        f"Independent passes:        "
        f"{len(report.passes)}"
    )
    print(
        f"Landmarks per pass:        "
        f"{len(report.landmarks)}"
    )
    print(
        f"Total measured points:     "
        f"{len(report.passes) * len(report.landmarks)}"
    )
    print(
        f"Overall RMS dispersion:    "
        f"{report.overall_rms_dispersion_pixels:.6f} px"
    )
    print(
        f"Median landmark RMS:       "
        f"{report.median_landmark_rms_pixels:.6f} px"
    )
    print(
        f"Maximum pairwise separation:"
        f" {report.maximum_pairwise_separation_pixels:.6f} px"
    )
    print(
        f"Review-flagged landmarks:  "
        f"{report.review_flag_count}"
    )
    print()
    print(f"Landmark CSV:              {landmark_path}")
    print(f"Pass CSV:                  {pass_path}")
    print(f"Category CSV:              {category_path}")
    print(f"Markdown report:           {report_path}")
    print()
    print("Pass-level drift")

    for item in report.pass_statistics:
        print(
            f"  {item.pass_id:8s} "
            f"dx={item.mean_dx_pixels:+.6f} px  "
            f"dy={item.mean_dy_pixels:+.6f} px  "
            f"|d|={item.drift_magnitude_pixels:.6f} px  "
            f"RMS={item.rms_residual_pixels:.6f} px"
        )

    print()
    print("Largest pairwise separations")

    ranked = sorted(
        report.landmarks,
        key=lambda item: (
            item.maximum_pairwise_separation_pixels
        ),
        reverse=True,
    )

    for item in ranked[:10]:
        marker = (
            "REVIEW"
            if item.review_flag
            else "ok"
        )

        print(
            f"  {item.landmark_id:38s} "
            f"{item.maximum_pairwise_separation_pixels:9.6f} px  "
            f"z={item.robust_z_max_pairwise:8.3f}  "
            f"{marker}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
