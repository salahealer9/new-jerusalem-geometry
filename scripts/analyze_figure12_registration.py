#!/usr/bin/env python3
"""Compare Figure 12 plate-registration models."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure12_registration import (
    analyze_figure12_registration,
    write_figure12_registration_markdown,
    write_figure12_registration_summary_csv,
)


DEFAULT_INPUT_DIRECTORY = Path(
    "data/calibration/figure12/"
    "digitisation/raw"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure12/registration"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare similarity, affine, and projective "
            "registration of Michell's Figure 12 plate."
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
            "ERROR: missing promoted Figure 12 pass(es):"
        )

        for path in missing:
            print(
                f"  {path}"
            )

        return 1

    report = (
        analyze_figure12_registration(
            pass_paths
        )
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        write_figure12_registration_summary_csv(
            args.output_directory
            / "figure12_registration_summary.csv",
            report,
        )
    )

    markdown_path = (
        write_figure12_registration_markdown(
            args.output_directory
            / "figure12_registration_report.md",
            report,
        )
    )

    print(
        "Figure 12 plate-registration comparison"
    )
    print(
        "=" * 39
    )
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

    print(
        "Centroid leave-one-out ranking"
    )
    print(
        "------------------------------"
    )

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
            f"anisotropy={fit.anisotropy_ratio:.9f}  "
            f"perspective={fit.perspective_magnitude:.12g}"
        )

    print()
    print(
        "Independent-pass leave-one-out RMS"
    )
    print(
        "----------------------------------"
    )

    for fit in report.fits:
        if fit.dataset_id == "centroid":
            continue

        print(
            f"{fit.dataset_id:8s} "
            f"{fit.model.value:10s} "
            f"{fit.loo_rms_pixels:.6f} px"
        )

    print()
    print(
        f"Summary CSV:           {summary_path}"
    )
    print(
        f"Markdown report:       {markdown_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
