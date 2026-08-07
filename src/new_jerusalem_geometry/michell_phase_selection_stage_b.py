"""Frozen Figure 14 source-consistency comparison for Phase 5F Stage B.

Stage B consumes the already committed Stage A artifact and the already
promoted affine-registered Figure 14 endpoint coordinates.

No registration or geometric fitting is performed here.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from math import hypot, isclose, sqrt
from pathlib import Path
from statistics import fmean
from typing import Any

from .michell_composite import MichellComposite


STAGE_B_SCHEMA_VERSION = "1.0"

HISTORICAL_STAGE_A_SHA256 = (
    "48a96dc7e160365cafc9114d7586ce94"
    "b070ebbe0403d759e71e8795c28d6d7d"
)

HISTORICAL_STAGE_A_COMMIT = "a84949a"

FROZEN_STAGE_A_SHA256 = (
    "6bfb543d5fbb98cbd383a242eac109d1"
    "ff0f7a96a68410d370ed294ec119613b"
)

STAGE_A_NOT_RUN = {
    "status": "NOT_RUN",
    "reason": (
        "Stage A must be recorded before "
        "Figure 14 source-coordinate comparison."
    ),
    "independent_validation": False,
    "feeds_back_into_builder": False,
}

ORIENTATIONS = (
    "forward",
    "reverse",
)

CYCLIC_SHIFTS = tuple(
    range(7)
)

CORRESPONDENCE_COUNT = (
    len(ORIENTATIONS)
    * len(CYCLIC_SHIFTS)
)

RTOL = 1.0e-12
ATOL = 1.0e-12


def _canonical_json_text(
    value: dict[str, Any],
) -> str:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


def _sha256_bytes(
    value: bytes,
) -> str:
    return hashlib.sha256(
        value
    ).hexdigest()


def _sha256_path(
    path: str | Path,
) -> str:
    return _sha256_bytes(
        Path(path).read_bytes()
    )


def _repository_relative_path(
    path: str | Path,
) -> str:
    """Return a stable repository-relative path when possible."""

    resolved = Path(
        path
    ).resolve()

    repository_root = (
        Path(__file__)
        .resolve()
        .parents[2]
    )

    try:
        return (
            resolved
            .relative_to(
                repository_root
            )
            .as_posix()
        )
    except ValueError:
        return str(
            resolved
        )


def _frozen_stage_a_input(
    path: str | Path,
) -> tuple[
    dict[str, Any],
    str,
]:
    """Load/reconstruct the exact frozen Stage A document.

    First execution reads the committed Stage A artifact whose Stage B status
    is NOT_RUN.

    Later executions may receive the completed Stage B artifact.  In that
    case the frozen Stage A input is reconstructed purely by restoring the
    exact registered NOT_RUN placeholder.  Stage A geometry is never
    recomputed.
    """

    path = Path(path)

    raw = path.read_bytes()

    document = json.loads(
        raw.decode(
            "utf-8"
        )
    )

    status = document[
        "stage_b"
    ][
        "status"
    ]

    if status == "NOT_RUN":
        canonical = (
            _canonical_json_text(
                document
            ).encode(
                "utf-8"
            )
        )

        if raw != canonical:
            raise ValueError(
                "Frozen Stage A artifact is not "
                "canonical deterministic JSON."
            )

        frozen = document
        frozen_hash = (
            _sha256_bytes(
                raw
            )
        )

    elif status == "COMPLETE":
        expected_hash = (
            document[
                "stage_b"
            ][
                "stage_a_input_sha256"
            ]
        )

        frozen = copy.deepcopy(
            document
        )

        frozen[
            "stage_b"
        ] = copy.deepcopy(
            STAGE_A_NOT_RUN
        )

        canonical = (
            _canonical_json_text(
                frozen
            ).encode(
                "utf-8"
            )
        )

        frozen_hash = (
            _sha256_bytes(
                canonical
            )
        )

        if (
            frozen_hash
            != expected_hash
        ):
            raise ValueError(
                "Completed Stage B artifact does not "
                "reconstruct its recorded frozen "
                "Stage A input hash."
            )

    else:
        raise ValueError(
            "Unsupported Stage B status in "
            "phase-selection artifact: "
            f"{status!r}"
        )

    if (
        frozen_hash
        != FROZEN_STAGE_A_SHA256
    ):
        raise ValueError(
            "Stage B input is not the exact "
            "portable Phase 5F Stage A artifact. "
            f"Expected {FROZEN_STAGE_A_SHA256}, "
            f"got {frozen_hash}."
        )

    if (
        frozen[
            "stage_a"
        ][
            "grammar_selection_result"
        ]
        != "GRAMMAR_UNDERDETERMINED"
    ):
        raise ValueError(
            "Stage B requires the frozen Stage A "
            "GRAMMAR_UNDERDETERMINED result."
        )

    if (
        frozen[
            "stage_a"
        ][
            "surviving_phase_ids"
        ]
        != [
            0,
            1,
            2,
            3,
        ]
    ):
        raise ValueError(
            "Stage B requires all four registered "
            "Stage A phases to survive."
        )

    return (
        frozen,
        frozen_hash,
    )


def _load_source_endpoints(
    *,
    registered_landmarks_path: str | Path,
    endpoint_geometry_path: str | Path,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
]:
    """Load the frozen seven affine-registered source endpoints.

    Only the promoted ``normalized_x`` / ``normalized_y`` columns are used
    as source coordinates.  No matrix is applied here.
    """

    endpoint_geometry = (
        json.loads(
            Path(
                endpoint_geometry_path
            ).read_text(
                encoding="utf-8"
            )
        )
    )

    endpoint_order = (
        endpoint_geometry[
            "endpoint_order"
        ]
    )

    if len(
        endpoint_order
    ) != 7:
        raise ValueError(
            "Expected exactly seven Figure 14 "
            "source endpoint IDs."
        )

    if len(
        set(
            endpoint_order
        )
    ) != 7:
        raise ValueError(
            "Figure 14 endpoint order contains "
            "duplicate IDs."
        )

    with Path(
        registered_landmarks_path
    ).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    star_rows = {
        row[
            "landmark_id"
        ]: row
        for row in rows
        if (
            row[
                "category"
            ]
            == "star_endpoint"
        )
    }

    if (
        set(
            star_rows
        )
        != set(
            endpoint_order
        )
    ):
        raise ValueError(
            "Promoted registered star endpoints "
            "do not match endpoint_geometry.json "
            "endpoint_order."
        )

    endpoints = []

    for source_index, endpoint_id in enumerate(
        endpoint_order
    ):
        row = star_rows[
            endpoint_id
        ]

        if (
            row[
                "registration_role"
            ]
            != "target"
        ):
            raise ValueError(
                "Figure 14 star endpoint is not "
                "classified as a registration target: "
                f"{endpoint_id}"
            )

        # The source endpoint rows are observations, not model anchors.
        if (
            row[
                "model_x"
            ].strip()
            or row[
                "model_y"
            ].strip()
        ):
            raise ValueError(
                "Figure 14 source endpoint unexpectedly "
                "contains model coordinates: "
                f"{endpoint_id}"
            )

        x = float(
            row[
                "normalized_x"
            ]
        )

        y = float(
            row[
                "normalized_y"
            ]
        )

        endpoints.append(
            {
                "source_index": (
                    source_index
                ),
                "endpoint_id": (
                    endpoint_id
                ),
                "x": x,
                "y": y,
            }
        )

    registration_scale = (
        endpoint_geometry[
            "registration_scale"
        ]
    )

    loo_rms_pixels = float(
        registration_scale[
            "loo_rms_pixels"
        ]
    )

    mean_pixels_per_unit = float(
        registration_scale[
            "mean_pixels_per_unit"
        ]
    )

    loo_equivalent = float(
        registration_scale[
            "loo_rms_equivalent_normalized"
        ]
    )

    if not (
        loo_rms_pixels > 0.0
        and mean_pixels_per_unit
        > 0.0
        and loo_equivalent
        > 0.0
    ):
        raise ValueError(
            "Invalid Figure 14 registration "
            "uncertainty scale."
        )

    independently_derived = (
        loo_rms_pixels
        / mean_pixels_per_unit
    )

    if not isclose(
        independently_derived,
        loo_equivalent,
        rel_tol=RTOL,
        abs_tol=ATOL,
    ):
        raise ValueError(
            "Figure 14 registration LOO "
            "normalized equivalent is inconsistent "
            "with pixels / mean pixels-per-unit."
        )

    return (
        endpoints,
        {
            "loo_rms_pixels": (
                loo_rms_pixels
            ),
            "mean_pixels_per_unit": (
                mean_pixels_per_unit
            ),
            "loo_rms_equivalent_normalized": (
                loo_equivalent
            ),
        },
    )


def _load_affine_binding(
    affine_matrix_path: str | Path,
) -> dict[str, Any]:
    """Read registration metadata only.

    The affine matrix is never applied by Stage B.
    """

    path = Path(
        affine_matrix_path
    )

    document = json.loads(
        path.read_text(
            encoding="utf-8"
        )
    )

    selected_model = (
        document[
            "selected_model"
        ]
    )

    if selected_model != "affine":
        raise ValueError(
            "Stage B requires the already selected "
            "Figure 14 affine registration."
        )

    return {
        "selected_model": (
            selected_model
        ),
        "sha256": (
            _sha256_path(
                path
            )
        ),
        "applied_in_stage_b": (
            False
        ),
        "purpose": (
            "provenance_binding_only"
        ),
    }


def _candidate_index_sequence(
    indices: list[int],
    *,
    orientation: str,
    shift: int,
) -> list[int]:
    if len(
        indices
    ) != 7:
        raise ValueError(
            "Each phase must contain seven scaffold indices."
        )

    if orientation == "forward":
        return [
            indices[
                (
                    shift + offset
                )
                % 7
            ]
            for offset in range(7)
        ]

    if orientation == "reverse":
        return [
            indices[
                (
                    shift - offset
                )
                % 7
            ]
            for offset in range(7)
        ]

    raise ValueError(
        "Unknown correspondence orientation: "
        f"{orientation!r}"
    )


def _comparison(
    composite: MichellComposite,
    source_endpoints: list[
        dict[str, Any]
    ],
    indices: list[int],
    *,
    orientation: str,
    shift: int,
) -> dict[str, Any]:
    candidate_indices = (
        _candidate_index_sequence(
            indices,
            orientation=orientation,
            shift=shift,
        )
    )

    residuals = []

    for source, scaffold_index in zip(
        source_endpoints,
        candidate_indices,
        strict=True,
    ):
        point = (
            composite
            .scaffold
            .points[
                scaffold_index
            ]
            .point
        )

        residuals.append(
            hypot(
                point.x
                - source[
                    "x"
                ],
                point.y
                - source[
                    "y"
                ],
            )
        )

    rms = sqrt(
        fmean(
            residual
            * residual
            for residual in residuals
        )
    )

    return {
        "orientation": (
            orientation
        ),
        "cyclic_shift": (
            shift
        ),
        "candidate_scaffold_indices": (
            candidate_indices
        ),
        "rms_residual": (
            rms
        ),
        "mean_residual": (
            fmean(
                residuals
            )
        ),
        "max_residual": (
            max(
                residuals
            )
        ),
        "point_residuals": (
            residuals
        ),
    }


def _best_correspondence(
    comparisons: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:
    orientation_rank = {
        "forward": 0,
        "reverse": 1,
    }

    return min(
        comparisons,
        key=lambda item: (
            item[
                "rms_residual"
            ],
            orientation_rank[
                item[
                    "orientation"
                ]
            ],
            item[
                "cyclic_shift"
            ],
        ),
    )


def _best_point_pairs(
    composite: MichellComposite,
    source_endpoints: list[
        dict[str, Any]
    ],
    best: dict[str, Any],
) -> list[dict[str, Any]]:
    result = []

    for source, scaffold_index, residual in zip(
        source_endpoints,
        best[
            "candidate_scaffold_indices"
        ],
        best[
            "point_residuals"
        ],
        strict=True,
    ):
        point = (
            composite
            .scaffold
            .points[
                scaffold_index
            ]
            .point
        )

        result.append(
            {
                "source_index": (
                    source[
                        "source_index"
                    ]
                ),
                "endpoint_id": (
                    source[
                        "endpoint_id"
                    ]
                ),
                "scaffold_index": (
                    scaffold_index
                ),
                "source_point": {
                    "x": (
                        source[
                            "x"
                        ]
                    ),
                    "y": (
                        source[
                            "y"
                        ]
                    ),
                },
                "candidate_point": {
                    "x": point.x,
                    "y": point.y,
                },
                "residual": (
                    residual
                ),
            }
        )

    return result


def _phase_result(
    composite: MichellComposite,
    source_endpoints: list[
        dict[str, Any]
    ],
    *,
    phase_record: dict[
        str,
        Any,
    ],
    registration_loo_u: float,
) -> dict[str, Any]:
    phase_id = int(
        phase_record[
            "phase_id"
        ]
    )

    indices = [
        int(value)
        for value in phase_record[
            "scaffold_indices"
        ]
    ]

    comparisons = [
        _comparison(
            composite,
            source_endpoints,
            indices,
            orientation=orientation,
            shift=shift,
        )
        for orientation
        in ORIENTATIONS
        for shift
        in CYCLIC_SHIFTS
    ]

    if len(
        comparisons
    ) != CORRESPONDENCE_COUNT:
        raise AssertionError(
            "Stage B correspondence count "
            "does not equal registered 14."
        )

    best = (
        _best_correspondence(
            comparisons
        )
    )

    return {
        "phase_id": (
            phase_id
        ),
        "scaffold_indices": (
            indices
        ),
        "comparison_count": (
            len(
                comparisons
            )
        ),
        "all_correspondences": (
            comparisons
        ),
        "best_correspondence": {
            "orientation": (
                best[
                    "orientation"
                ]
            ),
            "cyclic_shift": (
                best[
                    "cyclic_shift"
                ]
            ),
            "candidate_scaffold_indices": (
                best[
                    "candidate_scaffold_indices"
                ]
            ),
        },
        "rms_residual": (
            best[
                "rms_residual"
            ]
        ),
        "mean_residual": (
            best[
                "mean_residual"
            ]
        ),
        "max_residual": (
            best[
                "max_residual"
            ]
        ),
        "rms_fraction_of_registration_loo": (
            best[
                "rms_residual"
            ]
            / registration_loo_u
        ),
        "best_point_pairs": (
            _best_point_pairs(
                composite,
                source_endpoints,
                best,
            )
        ),
    }


def build_sevenfold_phase_selection_stage_b(
    composite: MichellComposite,
    *,
    stage_a_artifact_path: str | Path,
    registered_landmarks_path: str | Path,
    endpoint_geometry_path: str | Path,
    affine_matrix_path: str | Path,
) -> dict[str, Any]:
    """Complete Stage B without recomputing Stage A or fitting geometry."""

    if not isclose(
        composite.unit,
        1.0,
        rel_tol=RTOL,
        abs_tol=ATOL,
    ):
        raise ValueError(
            "Phase 5F Stage B is registered at unit=1.0."
        )

    (
        frozen_stage_a,
        frozen_stage_a_hash,
    ) = _frozen_stage_a_input(
        stage_a_artifact_path
    )

    (
        source_endpoints,
        registration_scale,
    ) = _load_source_endpoints(
        registered_landmarks_path=(
            registered_landmarks_path
        ),
        endpoint_geometry_path=(
            endpoint_geometry_path
        ),
    )

    affine_binding = (
        _load_affine_binding(
            affine_matrix_path
        )
    )

    stage_a_phases = (
        frozen_stage_a[
            "stage_a"
        ][
            "phases"
        ]
    )

    if [
        int(
            item[
                "phase_id"
            ]
        )
        for item in stage_a_phases
    ] != [
        0,
        1,
        2,
        3,
    ]:
        raise ValueError(
            "Frozen Stage A phase records are "
            "not ordered 0,1,2,3."
        )

    phase_results = [
        _phase_result(
            composite,
            source_endpoints,
            phase_record=(
                phase_record
            ),
            registration_loo_u=(
                registration_scale[
                    "loo_rms_equivalent_normalized"
                ]
            ),
        )
        for phase_record
        in stage_a_phases
    ]

    ranked = sorted(
        phase_results,
        key=lambda item: (
            item[
                "rms_residual"
            ],
            item[
                "phase_id"
            ],
        ),
    )

    rank_by_phase = {
        item[
            "phase_id"
        ]: rank
        for rank, item
        in enumerate(
            ranked,
            start=1,
        )
    }

    for item in phase_results:
        item[
            "rank"
        ] = rank_by_phase[
            item[
                "phase_id"
            ]
        ]

    winner = ranked[0]

    runner_up = ranked[1]

    winner_margin = (
        runner_up[
            "rms_residual"
        ]
        - winner[
            "rms_residual"
        ]
    )

    final = copy.deepcopy(
        frozen_stage_a
    )

    final[
        "stage_b"
    ] = {
        "status": "COMPLETE",
        "schema_version": (
            STAGE_B_SCHEMA_VERSION
        ),
        "stage_a_input_sha256": (
            frozen_stage_a_hash
        ),
        "historical_stage_a_input_sha256": (
            HISTORICAL_STAGE_A_SHA256
        ),
        "historical_stage_a_commit": (
            HISTORICAL_STAGE_A_COMMIT
        ),
        "portability_normalization": {
            "field": "protocol.protocol_path",
            "change": (
                "machine_absolute_to_repository_relative"
            ),
            "scientific_values_changed": False,
        },
        "stage_a_result_preserved": (
            frozen_stage_a[
                "stage_a"
            ][
                "grammar_selection_result"
            ]
        ),
        "comparison_rule": {
            "source_coordinate_fields": [
                "normalized_x",
                "normalized_y",
            ],
            "source_endpoint_order": (
                "promoted endpoint_order from "
                "star_endpoint_geometry.json"
            ),
            "cyclic_shift_count": 7,
            "orientations": list(
                ORIENTATIONS
            ),
            "correspondence_count_per_phase": (
                CORRESPONDENCE_COUNT
            ),
            "selection_metric": (
                "minimum Euclidean RMS residual"
            ),
            "tie_break_rule": (
                "minimum raw RMS; exact ties use "
                "forward before reverse, then "
                "lower cyclic shift"
            ),
            "continuous_fit_parameters": 0,
            "candidate_translation_fit": False,
            "candidate_rotation_fit": False,
            "candidate_scale_fit": False,
            "candidate_phase_fit": False,
            "candidate_centre_fit": False,
            "candidate_radius_fit": False,
            "registration_refit": False,
        },
        "source_bindings": {
            "registered_landmarks": {
                "path": (
                    _repository_relative_path(
                        registered_landmarks_path
                    )
                ),
                "sha256": (
                    _sha256_path(
                        registered_landmarks_path
                    )
                ),
            },
            "endpoint_geometry": {
                "path": (
                    _repository_relative_path(
                        endpoint_geometry_path
                    )
                ),
                "sha256": (
                    _sha256_path(
                        endpoint_geometry_path
                    )
                ),
            },
            "affine_registration_matrix": {
                "path": (
                    _repository_relative_path(
                        affine_matrix_path
                    )
                ),
                **affine_binding,
            },
        },
        "registration_scale": (
            registration_scale
        ),
        "source_endpoints": (
            source_endpoints
        ),
        "phase_results": (
            phase_results
        ),
        "ranking_phase_ids": [
            item[
                "phase_id"
            ]
            for item in ranked
        ],
        "winner": {
            "phase_id": (
                winner[
                    "phase_id"
                ]
            ),
            "rms_residual": (
                winner[
                    "rms_residual"
                ]
            ),
            "mean_residual": (
                winner[
                    "mean_residual"
                ]
            ),
            "max_residual": (
                winner[
                    "max_residual"
                ]
            ),
            "rms_fraction_of_registration_loo": (
                winner[
                    "rms_fraction_of_registration_loo"
                ]
            ),
            "best_correspondence": (
                winner[
                    "best_correspondence"
                ]
            ),
        },
        "runner_up": {
            "phase_id": (
                runner_up[
                    "phase_id"
                ]
            ),
            "rms_residual": (
                runner_up[
                    "rms_residual"
                ]
            ),
        },
        "winner_rms_margin_to_runner_up": (
            winner_margin
        ),
        "winner_margin_fraction_of_registration_loo": (
            winner_margin
            / registration_scale[
                "loo_rms_equivalent_normalized"
            ]
        ),
        "interpretation": {
            "comparison_type": (
                "descriptive_source_consistency"
            ),
            "independent_validation": False,
            "grammar_selection_changed": False,
            "stage_a_remains_grammar_underdetermined": (
                True
            ),
            "feeds_back_into_builder": False,
        },
        "independent_validation": False,
        "feeds_back_into_builder": False,
    }

    return final


def sevenfold_phase_selection_stage_b_to_json(
    audit: dict[str, Any],
) -> str:
    """Serialize the completed Phase 5F artifact deterministically."""

    return _canonical_json_text(
        audit
    )


def write_sevenfold_phase_selection_stage_b_json(
    audit: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Atomically write the completed Stage B artifact."""

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary = path.with_suffix(
        path.suffix
        + ".tmp"
    )

    temporary.write_text(
        sevenfold_phase_selection_stage_b_to_json(
            audit
        ),
        encoding="utf-8",
    )

    temporary.replace(
        path
    )

    return path
