#!/usr/bin/env python3
"""Generate the deterministic v0.6 Phase 6D evidential audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry.prediction_status_audit import (
    DEFAULT_OUTPUT_RELATIVE_PATH,
    DEFAULT_PHASE6C_RELATIVE_PATH,
    DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH,
    DEFAULT_REGISTRY_RELATIVE_PATH,
    write_prediction_status_audit,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the v0.6 prediction-status and "
            "development-leakage audit."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / DEFAULT_OUTPUT_RELATIVE_PATH
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    payload = write_prediction_status_audit(
        registry_path=(
            ROOT
            / DEFAULT_REGISTRY_RELATIVE_PATH
        ),
        phase6c_path=(
            ROOT
            / DEFAULT_PHASE6C_RELATIVE_PATH
        ),
        protocol_path=(
            ROOT
            / DEFAULT_PHASE6D_PROTOCOL_RELATIVE_PATH
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
