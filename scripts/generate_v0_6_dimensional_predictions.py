#!/usr/bin/env python3
"""Generate the frozen v0.6 Phase 6C dimensional predictions."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.dimensional_predictions import (
    DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH,
    DEFAULT_PHASE6C_OUTPUT_RELATIVE_PATH,
    DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH,
    write_frozen_dimensional_predictions,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate frozen v0.6 dimensional predictions "
            "without historical target comparison."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / DEFAULT_PHASE6C_OUTPUT_RELATIVE_PATH
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    payload = write_frozen_dimensional_predictions(
        unit_manifest_path=(
            ROOT
            / DEFAULT_PHASE6B_UNIT_MANIFEST_RELATIVE_PATH
        ),
        geometry_export_path=(
            ROOT
            / DEFAULT_V0_5_GEOMETRY_RELATIVE_PATH
        ),
        output_path=args.output,
    )

    print(
        args.output
    )
    print(
        "bytes:",
        len(
            payload
        ),
    )


if __name__ == "__main__":
    main()
