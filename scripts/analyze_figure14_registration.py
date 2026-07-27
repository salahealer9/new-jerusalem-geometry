#!/usr/bin/env python3
"""Fit and compare Figure 14 plate-registration models."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_registration import (
    analyze_registration,
    write_registration_markdown,
    write_registration_residuals_csv,
    write_registration_summary_csv,
)


DEFAULT_SCHEMA = Path(
    "data/calibration/figure14/landmark_schema.csv"
)

DEFAULT_INPUT_DIRECTORY = Path(
    "data/working/figure14"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure14/registration"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare similarity, affine, and projective "
            "registration of Michell's Figure 14 plate."
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
            "Directory containing digitisation passes. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Directory for local registration outputs. "
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

    if len(pass_paths) < 2:
        print(
            "ERROR: at least two digitisation passes are required."
        )
        return 1

    if not args.schema.is_file():
        print(
            f"ERROR: schema not found: {args.schema}"
        )
        return 1

    report = analyze_registration(
        schema_path=args.schema,
        pass_paths=pass_paths,
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = write_registration_summary_csv(
        args.output_directory
        / "figure14_registration_summary.csv",
        report,
    )

    residual_path = write_registration_residuals_csv(
        args.output_directory
        / "figure14_registration_residuals.csv",
        report,
    )

    report_path = write_registration_markdown(
        args.output_directory
        / "figure14_registration_report.md",
        report,
    )

    print("Figure 14 plate-registration comparison")
    print("=" * 40)
    print(
        f"Datasets:              "
        f"{len(report.datasets)}"
    )
    print(
        f"Models per dataset:    "
        f"{len(report.centroid_fits)}"
    )
    print(
        f"Total fitted models:   "
        f"{len(report.fits)}"
    )
    print()

    print("Centroid leave-one-out ranking")
    print("------------------------------")

    ranked = sorted(
        report.centroid_fits,
        key=lambda fit: fit.loo_rms_pixels,
    )

    for rank, fit in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{rank}. {fit.model.value:10s} "
            f"train={fit.training_rms_pixels:.6f} px  "
            f"LOO={fit.loo_rms_pixels:.6f} px  "
            f"max={fit.loo_maximum_pixels:.6f} px  "
            f"anisotropy={fit.anisotropy_ratio:.9f}"
        )

    print()
    print("Independent-pass leave-one-out RMS")
    print("----------------------------------")

    for fit in report.fits:
        if fit.dataset_id == "centroid":
            continue

        print(
            f"{fit.dataset_id:8s} "
            f"{fit.model.value:10s} "
            f"{fit.loo_rms_pixels:.6f} px"
        )

    print()
    print(f"Summary CSV:           {summary_path}")
    print(f"Residual CSV:          {residual_path}")
    print(f"Markdown report:       {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
