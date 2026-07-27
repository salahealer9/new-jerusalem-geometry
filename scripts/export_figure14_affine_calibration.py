#!/usr/bin/env python3
"""Export the selected Figure 14 affine calibration."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_registered_landmarks import (
    derive_affine_registered_landmarks,
    write_affine_calibration_markdown,
    write_affine_matrix_json,
    write_affine_summary_csv,
    write_registered_landmarks_csv,
)


DEFAULT_SCHEMA = Path(
    "data/calibration/figure14/landmark_schema.csv"
)

DEFAULT_INPUT_DIRECTORY = Path(
    "data/calibration/figure14/"
    "correspondence_resolved"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/calibration/figure14/derived"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export the selected centroid affine calibration "
            "and all 31 registered Figure 14 landmarks."
        )
    )

    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"Landmark schema. Default: {DEFAULT_SCHEMA}",
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
        help=(
            "Correspondence-resolved digitisation directory. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Derived calibration directory. "
            f"Default: {DEFAULT_OUTPUT_DIRECTORY}"
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

    if len(pass_paths) != 3:
        print(
            "ERROR: expected exactly three corrected "
            f"digitisation passes; found {len(pass_paths)}."
        )
        return 1

    report = derive_affine_registered_landmarks(
        schema_path=args.schema,
        pass_paths=pass_paths,
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    landmark_path = write_registered_landmarks_csv(
        args.output_directory
        / "registered_landmark_centroids.csv",
        report,
    )

    summary_path = write_affine_summary_csv(
        args.output_directory
        / "affine_registration_summary.csv",
        report,
    )

    matrix_path = write_affine_matrix_json(
        args.output_directory
        / "affine_registration_matrix.json",
        report,
    )

    report_path = write_affine_calibration_markdown(
        args.output_directory
        / "affine_calibration_report.md",
        report,
    )

    print("Figure 14 selected affine calibration")
    print("=" * 38)
    print("Selected model:              affine")
    print(
        f"Independent passes:          "
        f"{len(report.passes)}"
    )
    print(
        f"Registered landmarks:        "
        f"{len(report.landmarks)}"
    )
    print(
        f"Training RMS:                "
        f"{report.selected_fit.training_rms_pixels:.6f} px"
    )
    print(
        f"Leave-one-out RMS:           "
        f"{report.selected_fit.loo_rms_pixels:.6f} px"
    )
    print(
        f"Leave-one-out maximum:       "
        f"{report.selected_fit.loo_maximum_pixels:.6f} px"
    )
    print(
        f"Anisotropy ratio:            "
        f"{report.selected_fit.anisotropy_ratio:.9f}"
    )
    print(
        f"Scale range:                 "
        f"{report.singular_value_min:.6f}–"
        f"{report.singular_value_max:.6f} px/u"
    )
    print(
        f"Click RMS:                   "
        f"{report.overall_click_rms_pixels:.6f} px"
    )
    print(
        f"Click RMS after registration:"
        f" {report.overall_click_rms_normalized:.9f} u"
    )
    print(
        f"Pass-registered variation:   "
        f"{report.overall_pass_registered_rms_normalized:.9f} u"
    )
    print()
    print("Forward model-to-pixel matrix")

    for row in report.forward_matrix:
        print(
            "  ["
            + ", ".join(
                f"{value:+.12f}"
                for value in row
            )
            + "]"
        )

    print()
    print(f"Landmarks:                   {landmark_path}")
    print(f"Summary:                     {summary_path}")
    print(f"Matrix:                      {matrix_path}")
    print(f"Report:                      {report_path}")

    print()
    print("Registered star endpoints")

    for item in report.landmarks:
        if item.category != "star_endpoint":
            continue

        print(
            f"  {item.landmark_id:38s} "
            f"x={item.normalized_x:+.9f}  "
            f"y={item.normalized_y:+.9f}  "
            f"σ_click={item.click_rms_normalized:.9f} u  "
            f"σ_pass={item.pass_registered_rms_normalized:.9f} u"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
