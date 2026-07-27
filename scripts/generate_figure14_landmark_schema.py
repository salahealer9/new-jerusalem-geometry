#!/usr/bin/env python3
"""Generate the fixed Figure 14 landmark schema."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.figure14_digitisation import (
    build_figure14_landmark_schema,
    write_landmark_schema_csv,
)


DEFAULT_OUTPUT = Path(
    "data/calibration/figure14/landmark_schema.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the fixed thirty-one-landmark "
            "Figure 14 digitisation schema."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path. Default: {DEFAULT_OUTPUT}",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    diagram = build_core_geometry()

    schema = build_figure14_landmark_schema(
        diagram
    )

    output_path = write_landmark_schema_csv(
        args.output,
        schema,
    )

    category_counts: dict[str, int] = {}

    for landmark in schema:
        category_counts[landmark.category] = (
            category_counts.get(
                landmark.category,
                0,
            )
            + 1
        )

    print("Figure 14 landmark schema")
    print("=" * 27)
    print(f"Output:                  {output_path}")
    print(f"Total landmarks:         {len(schema)}")
    print(
        "Square corners:          "
        f"{category_counts.get('square_corner', 0)}"
    )
    print(
        "Square-circle junctions: "
        f"{category_counts.get('square_circle_junction', 0)}"
    )
    print(
        "Moon centres:            "
        f"{category_counts.get('moon_centre', 0)}"
    )
    print(
        "Star endpoints:          "
        f"{category_counts.get('star_endpoint', 0)}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
