#!/usr/bin/env python3
"""Generate the deterministic v0.6 Phase 6E residual report."""

from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.historical_residuals import (
    DEFAULT_CSV_OUTPUT_RELATIVE_PATH,
    DEFAULT_JSON_OUTPUT_RELATIVE_PATH,
    DEFAULT_MARKDOWN_OUTPUT_RELATIVE_PATH,
    DEFAULT_PHASE6C_RELATIVE_PATH,
    DEFAULT_PHASE6D_RELATIVE_PATH,
    DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH,
    DEFAULT_REGISTRY_RELATIVE_PATH,
    DEFAULT_UNIT_MANIFEST_RELATIVE_PATH,
    write_historical_residual_outputs,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]


def main() -> None:
    json_path = (
        ROOT
        / DEFAULT_JSON_OUTPUT_RELATIVE_PATH
    )

    csv_path = (
        ROOT
        / DEFAULT_CSV_OUTPUT_RELATIVE_PATH
    )

    markdown_path = (
        ROOT
        / DEFAULT_MARKDOWN_OUTPUT_RELATIVE_PATH
    )

    outputs = write_historical_residual_outputs(
        registry_path=(
            ROOT
            / DEFAULT_REGISTRY_RELATIVE_PATH
        ),
        unit_manifest_path=(
            ROOT
            / DEFAULT_UNIT_MANIFEST_RELATIVE_PATH
        ),
        phase6c_path=(
            ROOT
            / DEFAULT_PHASE6C_RELATIVE_PATH
        ),
        phase6d_path=(
            ROOT
            / DEFAULT_PHASE6D_RELATIVE_PATH
        ),
        protocol_path=(
            ROOT
            / DEFAULT_PHASE6E_PROTOCOL_RELATIVE_PATH
        ),
        json_path=json_path,
        csv_path=csv_path,
        markdown_path=markdown_path,
    )

    for path, payload in zip(
        (
            json_path,
            csv_path,
            markdown_path,
        ),
        outputs,
    ):
        print(
            path
        )

        print(
            "bytes:",
            len(
                payload
            ),
        )


if __name__ == "__main__":
    main()
