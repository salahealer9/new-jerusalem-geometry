#!/usr/bin/env python3
"""Analyse independent Figure 14 near-endpoint ray traces."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.figure14_edge_tracing import (
    analyze_edge_trace_passes,
    load_edge_trace_reference,
    write_edge_topology_details_csv,
    write_edge_topology_json,
    write_edge_topology_markdown,
)


DEFAULT_MATRIX = Path(
    "data/calibration/figure14/derived/"
    "affine_registration_matrix.json"
)

DEFAULT_LANDMARKS = Path(
    "data/calibration/figure14/derived/"
    "registered_landmark_centroids.csv"
)

DEFAULT_INPUT_DIRECTORY = Path(
    "data/working/figure14/edge_tracing"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure14/edge_tracing/analysis"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare perimeter, {7/2}, and {7/3} topology "
            "using near-endpoint printed-stroke directions."
        )
    )

    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX,
        help=f"Affine matrix JSON. Default: {DEFAULT_MATRIX}",
    )

    parser.add_argument(
        "--landmarks",
        type=Path,
        default=DEFAULT_LANDMARKS,
        help=(
            "Registered landmarks CSV. "
            f"Default: {DEFAULT_LANDMARKS}"
        ),
    )

    parser.add_argument(
        "--input-directory",
        type=Path,
        default=DEFAULT_INPUT_DIRECTORY,
        help=(
            "Directory containing edge-trace passes. "
            f"Default: {DEFAULT_INPUT_DIRECTORY}"
        ),
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Local analysis output directory. "
            f"Default: {DEFAULT_OUTPUT_DIRECTORY}"
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    pass_paths = sorted(
        args.input_directory.glob(
            "figure14_edge_trace_pass-*.csv"
        )
    )

    if len(pass_paths) != 3:
        print(
            "ERROR: expected exactly three edge-tracing "
            f"passes; found {len(pass_paths)}."
        )
        return 1

    reference = load_edge_trace_reference(
        matrix_path=args.matrix,
        landmarks_path=args.landmarks,
    )

    report = analyze_edge_trace_passes(
        reference=reference,
        pass_paths=pass_paths,
    )

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    details_path = (
        write_edge_topology_details_csv(
            args.output_directory
            / "edge_topology_details.csv",
            report,
        )
    )

    json_path = write_edge_topology_json(
        args.output_directory
        / "edge_topology_summary.json",
        report,
    )

    markdown_path = (
        write_edge_topology_markdown(
            args.output_directory
            / "edge_topology_report.md",
            report,
        )
    )

    print("Figure 14 near-endpoint topology audit")
    print("=" * 40)
    print(
        f"Independent passes:       "
        f"{len(report.passes)}"
    )
    print(
        f"Endpoint/pass tests:      "
        f"{len(report.endpoint_results)}"
    )
    print(
        f"Total ray samples:        "
        f"{2 * len(report.endpoint_results)}"
    )
    print()
    print("Candidate ranking")
    print("-----------------")

    ranked = sorted(
        report.candidate_summaries,
        key=lambda item: (
            item.rms_degrees,
            item.maximum_degrees,
        ),
    )

    for rank, item in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{rank}. {item.notation:9s} "
            f"step={item.step}  "
            f"RMS={item.rms_degrees:.6f}°  "
            f"max={item.maximum_degrees:.6f}°  "
            f"wins={item.endpoint_pass_wins}/"
            f"{item.endpoint_pass_count}"
        )

    print()
    print("Selected topology")
    print("-----------------")
    print(
        f"Connection:               "
        f"{report.selected_notation}"
    )
    print(
        f"Angular RMS:              "
        f"{report.selected_rms_degrees:.6f}°"
    )
    print(
        f"Maximum residual:         "
        f"{report.selected_maximum_degrees:.6f}°"
    )
    print(
        f"Second-best RMS:          "
        f"{report.second_best_rms_degrees:.6f}°"
    )
    print(
        f"RMS margin:               "
        f"{report.rms_margin_degrees:.6f}°"
    )
    print(
        f"Unanimous endpoint/passes:"
        f" {'yes' if report.unanimous_endpoint_passes else 'no'}"
    )
    print()
    print(f"Details CSV:              {details_path}")
    print(f"Summary JSON:             {json_path}")
    print(f"Markdown report:          {markdown_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
