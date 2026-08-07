"""Run Phase 5F Stage B against frozen Figure 14 source coordinates."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
)
from new_jerusalem_geometry.michell_phase_selection_stage_b import (
    build_sevenfold_phase_selection_stage_b,
    write_sevenfold_phase_selection_stage_b_json,
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_5"
    / "sevenfold_phase_selection.json"
)

REGISTERED_LANDMARKS = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "registered_landmark_centroids.csv"
)

ENDPOINT_GEOMETRY = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "star_endpoint_geometry.json"
)

AFFINE_MATRIX = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "affine_registration_matrix.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Complete Phase 5F Stage B using the "
            "already promoted Figure 14 source coordinates."
        )
    )

    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help=(
            "Frozen Stage A artifact to consume "
            "and completed Stage B artifact to write."
        ),
    )

    args = parser.parse_args()

    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    audit = (
        build_sevenfold_phase_selection_stage_b(
            composite,
            stage_a_artifact_path=(
                args.artifact
            ),
            registered_landmarks_path=(
                REGISTERED_LANDMARKS
            ),
            endpoint_geometry_path=(
                ENDPOINT_GEOMETRY
            ),
            affine_matrix_path=(
                AFFINE_MATRIX
            ),
        )
    )

    output_path = (
        write_sevenfold_phase_selection_stage_b_json(
            audit,
            args.artifact,
        )
    )

    stage_b = audit[
        "stage_b"
    ]

    print(output_path)

    print(
        "Stage A input SHA256:",
        stage_b[
            "stage_a_input_sha256"
        ],
    )

    print(
        "Stage A result:",
        stage_b[
            "stage_a_result_preserved"
        ],
    )

    print(
        "Stage B status:",
        stage_b[
            "status"
        ],
    )

    print(
        "Correspondences per phase:",
        stage_b[
            "comparison_rule"
        ][
            "correspondence_count_per_phase"
        ],
    )

    print()

    print(
        "phase,rank,rms,mean,max,"
        "rms_over_registration_loo,"
        "orientation,shift"
    )

    for phase in sorted(
        stage_b[
            "phase_results"
        ],
        key=lambda item: (
            item[
                "rank"
            ]
        ),
    ):
        best = phase[
            "best_correspondence"
        ]

        print(
            f"{phase['phase_id']},"
            f"{phase['rank']},"
            f"{phase['rms_residual']:.17g},"
            f"{phase['mean_residual']:.17g},"
            f"{phase['max_residual']:.17g},"
            f"{phase['rms_fraction_of_registration_loo']:.17g},"
            f"{best['orientation']},"
            f"{best['cyclic_shift']}"
        )

    print()

    print(
        "Ranking:",
        stage_b[
            "ranking_phase_ids"
        ],
    )

    print(
        "Winner phase:",
        stage_b[
            "winner"
        ][
            "phase_id"
        ],
    )

    print(
        "Winner RMS:",
        f"{stage_b['winner']['rms_residual']:.17g}",
    )

    print(
        "Runner-up phase:",
        stage_b[
            "runner_up"
        ][
            "phase_id"
        ],
    )

    print(
        "RMS margin:",
        f"{stage_b['winner_rms_margin_to_runner_up']:.17g}",
    )

    print(
        "Margin / registration LOO:",
        f"{stage_b['winner_margin_fraction_of_registration_loo']:.17g}",
    )

    print(
        "Independent validation:",
        stage_b[
            "independent_validation"
        ],
    )

    print(
        "Feeds back into builder:",
        stage_b[
            "feeds_back_into_builder"
        ],
    )


if __name__ == "__main__":
    main()
