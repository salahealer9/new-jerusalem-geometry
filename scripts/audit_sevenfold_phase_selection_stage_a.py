"""Run Phase 5F Stage A: grammar-only sevenfold phase selection."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
)
from new_jerusalem_geometry.michell_phase_selection import (
    build_sevenfold_phase_selection_stage_a,
    write_sevenfold_phase_selection_json,
)


ROOT = Path(__file__).resolve().parents[1]

PROTOCOL_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "v0.5_sevenfold_phase_selection_protocol.md"
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

DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_5"
    / "sevenfold_phase_selection.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the grammar-only Phase 5F "
            "sevenfold/scaffold phase-selection audit."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    args = parser.parse_args()

    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    audit = (
        build_sevenfold_phase_selection_stage_a(
            composite,
            protocol_path=(
                PROTOCOL_PATH
            ),
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
        write_sevenfold_phase_selection_json(
            audit,
            args.output,
        )
    )

    stage_a = audit[
        "stage_a"
    ]

    print(path)
    print(
        "Candidates:",
        stage_a[
            "candidate_count"
        ],
    )
    print(
        "Surviving phases:",
        stage_a[
            "surviving_phase_ids"
        ],
    )
    print(
        "Grammar result:",
        stage_a[
            "grammar_selection_result"
        ],
    )
    print(
        "Quarter-turn max residual:",
        stage_a[
            "quarter_turn_orbit"
        ][
            "max_coordinate_residual"
        ],
    )
    print(
        "Role-equivalent:",
        stage_a[
            "role_equivalence"
        ][
            "all_cyclic_role_words_equivalent"
        ],
    )
    print(
        "Metric-equivalent:",
        stage_a[
            "metric_equivalence"
        ][
            "all_phases_metric_equivalent"
        ],
    )
    print(
        "Primary phase:",
        stage_a[
            "primary_reciprocal_correspondence"
        ][
            "primary_phase_id"
        ],
    )
    print(
        "Reciprocal phase:",
        stage_a[
            "primary_reciprocal_correspondence"
        ][
            "reciprocal_phase_id"
        ],
    )
    print(
        "Stage B:",
        audit[
            "stage_b"
        ][
            "status"
        ],
    )


if __name__ == "__main__":
    main()
