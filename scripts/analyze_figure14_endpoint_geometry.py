#!/usr/bin/env python3
"""Analyse source-derived Figure 14 star endpoint geometry."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_endpoint_geometry import (
    derive_figure14_star_endpoint_geometry,
    write_endpoint_geometry_csv,
    write_endpoint_geometry_json,
    write_endpoint_geometry_markdown,
)
from new_jerusalem_geometry.figure14_registered_landmarks import (
    derive_affine_registered_landmarks,
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
            "Audit the regularity, radius, centre, and phase "
            "of the seven source-derived Figure 14 endpoints."
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
            "Correspondence-resolved pass directory. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Derived output directory. "
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
            "ERROR: expected exactly three "
            f"correspondence-resolved passes; found {len(pass_paths)}."
        )
        return 1

    calibration = (
        derive_affine_registered_landmarks(
            schema_path=args.schema,
            pass_paths=pass_paths,
        )
    )

    report = (
        derive_figure14_star_endpoint_geometry(
            calibration
        )
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_path = write_endpoint_geometry_csv(
        args.output_directory
        / "star_endpoint_geometry.csv",
        report,
    )

    json_path = write_endpoint_geometry_json(
        args.output_directory
        / "star_endpoint_geometry.json",
        report,
    )

    markdown_path = (
        write_endpoint_geometry_markdown(
            args.output_directory
            / "star_endpoint_geometry_report.md",
            report,
        )
    )

    print("Figure 14 source-derived endpoint geometry")
    print("=" * 42)
    print()
    print("Free regular seven-vertex fit")
    print("-----------------------------")
    print(
        f"Centre:             "
        f"({report.free_fit.centre_x:+.9f}, "
        f"{report.free_fit.centre_y:+.9f}) u"
    )
    print(
        f"Centre displacement:"
        f" {(report.free_fit.centre_x ** 2 + report.free_fit.centre_y ** 2) ** 0.5:.9f} u"
    )
    print(
        f"Radius:             "
        f"{report.free_fit.radius:.9f} u"
    )
    print(
        f"Phase:              "
        f"{report.free_fit.phase_degrees:.9f}°"
    )
    print(
        f"RMS residual:       "
        f"{report.free_fit.rms_residual:.9f} u"
    )
    print(
        f"Maximum residual:   "
        f"{report.free_fit.maximum_residual:.9f} u"
    )
    print(
        f"Angular RMS:        "
        f"{report.free_fit.angular_rms_degrees:.9f}°"
    )
    print()
    print("Origin, radius-7 fit")
    print("--------------------")
    print(
        f"Best phase:         "
        f"{report.fixed_radius7_fit.phase_degrees:.9f}°"
    )
    print(
        f"RMS residual:       "
        f"{report.fixed_radius7_fit.rms_residual:.9f} u"
    )
    print(
        f"Maximum residual:   "
        f"{report.fixed_radius7_fit.maximum_residual:.9f} u"
    )
    print()
    print("Canonical top-vertex fit")
    print("------------------------")
    print(
        f"RMS residual:       "
        f"{report.canonical_fit.rms_residual:.9f} u"
    )
    print(
        f"Maximum residual:   "
        f"{report.canonical_fit.maximum_residual:.9f} u"
    )
    print()
    print("Calibration comparison")
    print("----------------------")
    print(
        f"Registration LOO:   "
        f"{report.registration_loo_equivalent_normalized:.9f} u"
    )
    print(
        f"Free-fit fraction:  "
        f"{report.free_fit_rms_fraction_of_registration_loo:.6f}"
    )
    print(
        f"Radius-7 fraction:  "
        f"{report.fixed_radius7_rms_fraction_of_registration_loo:.6f}"
    )
    print(
        f"Canonical fraction: "
        f"{report.canonical_rms_fraction_of_registration_loo:.6f}"
    )
    print()
    print(f"Endpoint CSV:       {csv_path}")
    print(f"Summary JSON:       {json_path}")
    print(f"Markdown report:    {markdown_path}")
    print()
    print("Topology boundary")
    print("-----------------")
    print(
        report.topology_identifiability_statement
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
