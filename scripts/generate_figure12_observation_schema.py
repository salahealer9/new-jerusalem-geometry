#!/usr/bin/env python3
"""Generate the fixed Figure 12 source-observation schema."""

from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.figure12_digitisation import (
    MOON_OBJECT_IDS,
    WALL_OBJECT_IDS,
    build_figure12_observation_schema,
    category_counts,
    write_figure12_observation_schema_csv,
)


DEFAULT_OUTPUT = Path(
    "data/calibration/figure12/"
    "observation_schema.csv"
)


def main() -> int:
    schema = build_figure12_observation_schema()

    output_path = (
        write_figure12_observation_schema_csv(
            DEFAULT_OUTPUT,
            schema,
        )
    )

    counts = category_counts(schema)

    print(
        "Figure 12 observation schema"
    )
    print(
        "=" * 28
    )
    print(
        f"Output:                    {output_path}"
    )
    print(
        f"Total observations/pass:   {len(schema)}"
    )
    print(
        f"Square corners:             "
        f"{counts['square_corner']}"
    )
    print(
        f"Square-circle junctions:    "
        f"{counts['square_circle_junction']}"
    )
    print(
        f"Moon circumference samples: "
        f"{counts['moon_circumference']}"
    )
    print(
        f"Wall-line samples:          "
        f"{counts['wall_line']}"
    )
    print(
        f"Moon objects:               "
        f"{len(MOON_OBJECT_IDS)}"
    )
    print(
        f"Wall objects:               "
        f"{len(WALL_OBJECT_IDS)}"
    )
    print(
        "Registration observations:  12"
    )
    print(
        "Source-only observations:    108"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
