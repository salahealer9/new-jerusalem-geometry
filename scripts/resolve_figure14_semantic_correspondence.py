#!/usr/bin/env python3
"""Resolve Figure 14 Moon and star landmark correspondences."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_semantic_correspondence import (
    resolve_figure14_semantic_correspondence,
)


DEFAULT_SCHEMA = Path(
    "data/calibration/figure14/landmark_schema.csv"
)

DEFAULT_INPUT_DIRECTORY = Path(
    "data/calibration/figure14/corrected"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/calibration/figure14/"
    "correspondence_resolved"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Resolve Moon-centre and spatial star-endpoint "
            "correspondences without altering coordinate values."
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
            "Junction-corrected pass directory. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Correspondence-resolved output directory. "
            f"Default: {DEFAULT_OUTPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help=(
            "Replace existing resolved files after manual review."
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    result = resolve_figure14_semantic_correspondence(
        schema_path=args.schema,
        input_directory=args.input_directory,
        output_directory=args.output_directory,
        expected_pass_count=3,
        overwrite=args.overwrite,
    )

    print("Figure 14 semantic correspondence")
    print("=" * 37)
    print(f"Resolved passes:          {len(result.files)}")
    print(
        f"Output directory:        "
        f"{result.output_directory}"
    )
    print(f"Manifest:                {result.manifest_path}")
    print(f"Report:                  {result.report_path}")
    print()
    print("Moon correspondence")
    print("-------------------")
    print(
        f"Direction:               "
        f"{result.moon.direction}"
    )
    print(
        f"Shift:                   "
        f"{result.moon.shift}"
    )
    print(
        f"Validation RMS:          "
        f"{result.moon.rms_normalized:.9f} u"
    )
    print(
        f"Validation maximum:      "
        f"{result.moon.maximum_normalized:.9f} u"
    )
    print(
        f"Second-best RMS:         "
        f"{result.moon.second_best_rms_normalized:.9f} u"
    )
    print()
    print("Star endpoint geometry")
    print("----------------------")
    print(
        f"Circle centre:           "
        f"({result.star.circle_centre_x:+.9f}, "
        f"{result.star.circle_centre_y:+.9f}) u"
    )
    print(
        f"Mean radius:             "
        f"{result.star.mean_radius:.9f} u"
    )
    print(
        f"Radial RMS:              "
        f"{result.star.radial_rms:.9f} u"
    )
    print(
        f"Recorded-sequence fit:   "
        f"{result.star.recorded_sequence_notation} "
        f"{result.star.recorded_sequence_direction}"
    )
    print(
        f"Angular RMS:             "
        f"{result.star.recorded_sequence_angular_rms_degrees:.9f}°"
    )
    print(
        f"Angular maximum:         "
        f"{result.star.recorded_sequence_angular_maximum_degrees:.9f}°"
    )
    print()
    print(
        "The recorded-sequence result is retained as "
        "sequence-consistency evidence, not yet as independent "
        "proof of printed-line topology."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
