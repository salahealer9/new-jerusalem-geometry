#!/usr/bin/env python3
"""Promote Figure 14 digitisation passes into tracked calibration data."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_calibration_data import (
    JUNCTION_COORDINATE_SOURCE_BY_TARGET,
    promote_figure14_calibration_data,
)


DEFAULT_INPUT_DIRECTORY = Path(
    "data/working/figure14"
)

DEFAULT_OUTPUT_ROOT = Path(
    "data/calibration/figure14"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preserve the three raw Figure 14 digitisation "
            "passes and create deterministically corrected copies."
        )
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
        help=(
            "Directory containing the original pass CSVs. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Tracked calibration-data root. "
            f"Default: {DEFAULT_OUTPUT_ROOT}"
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Replace existing promoted files after manual review."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    result = promote_figure14_calibration_data(
        input_directory=args.input_directory,
        output_root=args.output_root,
        expected_pass_count=3,
        overwrite=args.overwrite,
    )

    print("Figure 14 calibration-data promotion")
    print("=" * 38)
    print(f"Raw directory:       {result.raw_directory}")
    print(
        f"Corrected directory: "
        f"{result.corrected_directory}"
    )
    print(f"Manifest:            {result.manifest_path}")
    print(f"Passes:              {len(result.files)}")
    print(
        f"Source dimensions:   "
        f"{result.image_width_pixels} × "
        f"{result.image_height_pixels}"
    )
    print(
        f"Source SHA-256:       "
        f"{result.source_image_sha256}"
    )
    print()
    print("Coordinate reassignment")

    for target_id, source_id in (
        JUNCTION_COORDINATE_SOURCE_BY_TARGET.items()
    ):
        print(
            f"  {target_id:28s} <- {source_id}"
        )

    print()
    print("Promoted files")

    for record in result.files:
        print(
            f"  {record.pass_id}:"
        )
        print(
            f"    raw       "
            f"{record.raw_output_path}"
        )
        print(
            f"    SHA-256   "
            f"{record.raw_sha256}"
        )
        print(
            f"    corrected "
            f"{record.corrected_output_path}"
        )
        print(
            f"    SHA-256   "
            f"{record.corrected_sha256}"
        )

    print()
    print(
        "The original working CSVs were not modified."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
