"""Generate the canonical NJG_MICHELL provenance manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
)
from new_jerusalem_geometry.michell_provenance import (
    build_michell_composite_provenance,
    write_michell_composite_provenance_json,
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "provenance"
    / "njg_michell_v0_5"
    / "njg_michell_provenance.json"
)

NODES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

DEPENDENCIES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

CLAIMS_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the deterministic "
            "NJG_MICHELL provenance manifest."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--unit",
        type=float,
        default=1.0,
    )

    args = parser.parse_args()

    composite = build_michell_composite(
        unit=args.unit
    )

    provenance = (
        build_michell_composite_provenance(
            composite,
            construction_nodes_path=(
                NODES_PATH
            ),
            construction_dependencies_path=(
                DEPENDENCIES_PATH
            ),
            claim_matrix_path=(
                CLAIMS_PATH
            ),
        )
    )

    path = (
        write_michell_composite_provenance_json(
            provenance,
            args.output,
        )
    )

    print(path)
    print(
        "Objects:",
        provenance.object_count,
    )
    print(
        "Grammar nodes:",
        len(
            provenance
            .grammar_snapshot
            .nodes
        ),
    )
    print(
        "Dependencies:",
        len(
            provenance
            .grammar_snapshot
            .dependencies
        ),
    )
    print(
        "Claims:",
        len(
            provenance
            .grammar_snapshot
            .claims
        ),
    )


if __name__ == "__main__":
    main()
