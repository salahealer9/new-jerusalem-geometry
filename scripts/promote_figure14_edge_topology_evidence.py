#!/usr/bin/env python3
"""Promote Figure 14 endpoint-ray topology evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_edge_topology_data import (
    promote_figure14_edge_topology_evidence,
)


DEFAULT_INPUT_DIRECTORY = Path(
    "data/working/figure14/edge_tracing"
)

DEFAULT_OUTPUT_ROOT = Path(
    "data/calibration/figure14/edge_topology"
)

DEFAULT_MATRIX = Path(
    "data/calibration/figure14/derived/"
    "affine_registration_matrix.json"
)

DEFAULT_LANDMARKS = Path(
    "data/calibration/figure14/derived/"
    "registered_landmark_centroids.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Preserve the three Figure 14 edge-tracing passes "
            "and regenerate the tracked topology analysis."
        )
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
        help=(
            "Local trace-pass directory. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=(
            "Tracked topology-evidence root. "
            f"Default: {DEFAULT_OUTPUT_ROOT}"
        ),
    )

    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX,
        help=(
            "Selected affine matrix. "
            f"Default: {DEFAULT_MATRIX}"
        ),
    )

    parser.add_argument(
        "--landmarks",
        type=Path,
        default=DEFAULT_LANDMARKS,
        help=(
            "Registered landmark centroids. "
            f"Default: {DEFAULT_LANDMARKS}"
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Replace existing promoted outputs "
            "after manual review."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    result = (
        promote_figure14_edge_topology_evidence(
            input_directory=(
                args.input_directory
            ),
            output_root=args.output_root,
            matrix_path=args.matrix,
            landmarks_path=args.landmarks,
            expected_pass_count=3,
            expected_selected_step=2,
            require_unanimous=True,
            overwrite=args.overwrite,
        )
    )

    report = result.topology_report

    print("Figure 14 topology-evidence promotion")
    print("=" * 40)
    print(
        f"Promoted raw passes:       "
        f"{len(result.files)}"
    )
    print(
        f"Total ray samples:         "
        f"{2 * len(report.endpoint_results)}"
    )
    print(
        f"Selected topology:         "
        f"{report.selected_notation}"
    )
    print(
        f"Angular RMS:               "
        f"{report.selected_rms_degrees:.9f}°"
    )
    print(
        f"Maximum residual:          "
        f"{report.selected_maximum_degrees:.9f}°"
    )
    print(
        f"Second-best RMS:           "
        f"{report.second_best_rms_degrees:.9f}°"
    )
    print(
        f"RMS margin:                "
        f"{report.rms_margin_degrees:.9f}°"
    )
    print(
        f"Unanimous endpoint/passes: "
        f"{'yes' if report.unanimous_endpoint_passes else 'no'}"
    )
    print()
    print(
        f"Raw directory:             "
        f"{result.raw_directory}"
    )
    print(
        f"Derived directory:         "
        f"{result.derived_directory}"
    )
    print(
        f"Manifest:                  "
        f"{result.manifest_path}"
    )
    print()
    print("Promoted pass hashes")

    for record in result.files:
        print(
            f"  {record.pass_id:8s} "
            f"{record.output_sha256}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
