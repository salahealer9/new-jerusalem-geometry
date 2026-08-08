#!/usr/bin/env python3
"""Generate the deterministic v0.6 Phase 6B unit-system manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.metrology import (
    DEFAULT_REGISTRY_RELATIVE_PATH,
    write_unit_manifest,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "metrology"
    / "njg_michell_v0_6"
    / "unit_system.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the deterministic v0.6 formal unit-system manifest."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    registry_path = (
        ROOT
        / DEFAULT_REGISTRY_RELATIVE_PATH
    )

    payload = write_unit_manifest(
        registry_path=registry_path,
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
