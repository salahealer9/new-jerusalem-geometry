"""Grammar-only sevenfold/scaffold phase-selection audit.

Phase 5F Stage A enumerates the four seven-point residue classes of the
28-point Michell scaffold without consulting Figure 14 calibration
coordinates.

The module consumes an already constructed ``MichellComposite``. It does
not construct the composite and does not import calibration modules.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from math import hypot, isclose, pi
from pathlib import Path
from typing import Any

from .michell_composite import MichellComposite


PHASE_AUDIT_SCHEMA_NAME = "njg_michell_sevenfold_phase_selection"
PHASE_AUDIT_SCHEMA_VERSION = "1.0"

REGISTERED_PHASES: dict[int, tuple[int, ...]] = {
    0: (0, 4, 8, 12, 16, 20, 24),
    1: (1, 5, 9, 13, 17, 21, 25),
    2: (2, 6, 10, 14, 18, 22, 26),
    3: (3, 7, 11, 15, 19, 23, 27),
}

STEP2_EDGE_PAIRS: tuple[tuple[int, int], ...] = (
    (0, 2),
    (2, 4),
    (4, 6),
    (6, 1),
    (1, 3),
    (3, 5),
    (5, 0),
)

REGISTERED_QUARTER_TURN_ORBIT: dict[int, int] = {
    0: 3,
    3: 2,
    2: 1,
    1: 0,
}

RTOL = 1.0e-12
ATOL = 1.0e-12

SOURCE_GROUNDED_STATUSES = {
    "stated_exact",
    "stated_approximate",
    "conventional_exact",
}

CARDINAL_TERMS = (
    "north",
    "south",
    "east",
    "west",
    "cardinal",
)


def _read_csv(
    path: str | Path,
) -> list[dict[str, str]]:
    with Path(path).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def _sha256(
    path: str | Path,
) -> str:
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()



def _repository_relative_path(
    path: str | Path,
) -> str:
    """Return a stable repository-relative path for repository inputs."""

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

def _close(
    a: float,
    b: float,
) -> bool:
    return isclose(
        a,
        b,
        rel_tol=RTOL,
        abs_tol=ATOL,
    )


def _point_distance(
    a: object,
    b: object,
) -> float:
    return hypot(
        getattr(a, "x")
        - getattr(b, "x"),
        getattr(a, "y")
        - getattr(b, "y"),
    )


def _canonical_cyclic_word(
    word: tuple[str, ...],
) -> tuple[str, ...]:
    rotations = tuple(
        word[index:]
        + word[:index]
        for index in range(
            len(word)
        )
    )

    return min(rotations)


def _angular_gaps(
    angles: tuple[float, ...],
) -> tuple[float, ...]:
    ordered = tuple(
        sorted(
            angle % (2.0 * pi)
            for angle in angles
        )
    )

    result = []

    for index, angle in enumerate(
        ordered
    ):
        next_angle = ordered[
            (index + 1)
            % len(ordered)
        ]

        if index == (
            len(ordered) - 1
        ):
            next_angle += (
                2.0 * pi
            )

        result.append(
            next_angle - angle
        )

    return tuple(result)


def _edge_lengths(
    vertices: tuple[object, ...],
) -> tuple[float, ...]:
    return tuple(
        _point_distance(
            vertices[start],
            vertices[end],
        )
        for start, end
        in STEP2_EDGE_PAIRS
    )


def _match_scaffold_index(
    point: object,
    composite: MichellComposite,
) -> int:
    matches = [
        scaffold_point.index
        for scaffold_point
        in composite.scaffold.points
        if (
            _close(
                scaffold_point.point.x,
                getattr(
                    point,
                    "x",
                ),
            )
            and _close(
                scaffold_point.point.y,
                getattr(
                    point,
                    "y",
                ),
            )
        )
    ]

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one scaffold "
            "match for generated point; "
            f"got {matches!r}."
        )

    return matches[0]


def _phase_for_index_set(
    indices: set[int],
) -> int:
    matches = [
        phase_id
        for phase_id, phase_indices
        in REGISTERED_PHASES.items()
        if set(
            phase_indices
        ) == indices
    ]

    if len(matches) != 1:
        raise ValueError(
            "Index set does not resolve to "
            "exactly one registered phase: "
            f"{sorted(indices)!r}"
        )

    return matches[0]


def _phase_candidate(
    composite: MichellComposite,
    phase_id: int,
) -> dict[str, Any]:
    indices = (
        REGISTERED_PHASES[
            phase_id
        ]
    )

    scaffold_points = tuple(
        composite.scaffold.points[
            index
        ]
        for index in indices
    )

    vertices = tuple(
        item.point
        for item in scaffold_points
    )

    roles = tuple(
        item.role.value
        for item in scaffold_points
    )

    role_counts = Counter(
        roles
    )

    radii = tuple(
        hypot(
            point.x,
            point.y,
        )
        for point in vertices
    )

    radius_residuals = tuple(
        radius
        - composite.scaffold.radius
        for radius in radii
    )

    max_radius_residual = max(
        abs(value)
        for value in radius_residuals
    )

    unique_points = {
        (
            point.x,
            point.y,
        )
        for point in vertices
    }

    edge_lengths = (
        _edge_lengths(
            vertices
        )
    )

    angular_gaps = (
        _angular_gaps(
            tuple(
                item.angle_radians
                for item
                in scaffold_points
            )
        )
    )

    quarter_turned_indices = {
        (
            index + 7
        )
        % 28
        for index in indices
    }

    quarter_turn_target = (
        _phase_for_index_set(
            quarter_turned_indices
        )
    )

    source_role_criterion_pass = (
        role_counts[
            "moon_centre"
        ]
        == 3
        and role_counts[
            "intersection_positioner"
        ]
        == 2
    )

    inferred_gap_completion_count = (
        role_counts[
            "inter_moon_gap"
        ]
    )

    candidate_valid = (
        len(indices) == 7
        and len(
            set(indices)
        ) == 7
        and len(
            unique_points
        ) == 7
        and max_radius_residual
        <= ATOL
        and source_role_criterion_pass
    )

    return {
        "phase_id": phase_id,
        "scaffold_indices": list(
            indices
        ),
        "unique_index_count": len(
            set(indices)
        ),
        "unique_point_count": len(
            unique_points
        ),
        "role_counts": {
            role: role_counts[
                role
            ]
            for role in (
                "moon_centre",
                "intersection_positioner",
                "inter_moon_gap",
            )
        },
        "cyclic_role_sequence": list(
            roles
        ),
        "canonical_cyclic_role_sequence": list(
            _canonical_cyclic_word(
                roles
            )
        ),
        "source_stated_role_criterion": {
            "required_moon_centres": 3,
            "required_intersection_positions": 2,
            "passes": (
                source_role_criterion_pass
            ),
        },
        "project_inferred_gap_completion": {
            "inter_moon_gap_count": (
                inferred_gap_completion_count
            ),
            "status": (
                "project_inference"
            ),
        },
        "radius_check": {
            "expected_radius": (
                composite
                .scaffold
                .radius
            ),
            "max_abs_residual": (
                max_radius_residual
            ),
            "passes": (
                max_radius_residual
                <= ATOL
            ),
        },
        "step2_edge_pairs": [
            [start, end]
            for start, end
            in STEP2_EDGE_PAIRS
        ],
        "edge_lengths": list(
            edge_lengths
        ),
        "sorted_edge_lengths": list(
            sorted(
                edge_lengths
            )
        ),
        "star_edge_perimeter": sum(
            edge_lengths
        ),
        "angular_gaps": list(
            angular_gaps
        ),
        "sorted_angular_gaps": list(
            sorted(
                angular_gaps
            )
        ),
        "quarter_turn_target_phase": (
            quarter_turn_target
        ),
        "candidate_valid": (
            candidate_valid
        ),
    }


def _quarter_turn_audit(
    composite: MichellComposite,
) -> dict[str, Any]:
    maximum_residual = 0.0
    role_mismatches = []

    for point in (
        composite.scaffold.points
    ):
        target_index = (
            point.index + 7
        ) % 28

        target = (
            composite
            .scaffold
            .points[
                target_index
            ]
        )

        rotated_x = (
            -point.point.y
        )

        rotated_y = (
            point.point.x
        )

        residual = hypot(
            target.point.x
            - rotated_x,
            target.point.y
            - rotated_y,
        )

        maximum_residual = max(
            maximum_residual,
            residual,
        )

        if (
            target.role
            != point.role
        ):
            role_mismatches.append(
                {
                    "index": point.index,
                    "target_index": (
                        target_index
                    ),
                    "source_role": (
                        point.role.value
                    ),
                    "target_role": (
                        target.role.value
                    ),
                }
            )

    observed_orbit = {}

    for phase_id, indices in (
        REGISTERED_PHASES.items()
    ):
        target_indices = {
            (
                index + 7
            )
            % 28
            for index in indices
        }

        observed_orbit[
            str(phase_id)
        ] = _phase_for_index_set(
            target_indices
        )

    expected_orbit = {
        str(key): value
        for key, value
        in REGISTERED_QUARTER_TURN_ORBIT.items()
    }

    return {
        "index_action": (
            "(index + 7) mod 28"
        ),
        "observed_phase_orbit": (
            observed_orbit
        ),
        "expected_phase_orbit": (
            expected_orbit
        ),
        "max_coordinate_residual": (
            maximum_residual
        ),
        "coordinate_rotation_passes": (
            maximum_residual
            <= ATOL
        ),
        "role_mismatches": (
            role_mismatches
        ),
        "role_rotation_passes": (
            not role_mismatches
        ),
        "orbit_passes": (
            observed_orbit
            == expected_orbit
        ),
    }


def _metric_equivalence(
    phases: list[
        dict[str, Any]
    ],
) -> dict[str, Any]:
    reference = phases[0]

    reference_edges = (
        reference[
            "sorted_edge_lengths"
        ]
    )

    reference_gaps = (
        reference[
            "sorted_angular_gaps"
        ]
    )

    reference_perimeter = (
        reference[
            "star_edge_perimeter"
        ]
    )

    per_phase = []
    all_equivalent = True

    for candidate in phases:
        edge_residual = max(
            abs(
                actual - expected
            )
            for actual, expected
            in zip(
                candidate[
                    "sorted_edge_lengths"
                ],
                reference_edges,
                strict=True,
            )
        )

        gap_residual = max(
            abs(
                actual - expected
            )
            for actual, expected
            in zip(
                candidate[
                    "sorted_angular_gaps"
                ],
                reference_gaps,
                strict=True,
            )
        )

        perimeter_residual = abs(
            candidate[
                "star_edge_perimeter"
            ]
            - reference_perimeter
        )

        equivalent = (
            edge_residual
            <= ATOL
            and gap_residual
            <= ATOL
            and perimeter_residual
            <= ATOL
        )

        all_equivalent = (
            all_equivalent
            and equivalent
        )

        per_phase.append(
            {
                "phase_id": (
                    candidate[
                        "phase_id"
                    ]
                ),
                "max_sorted_edge_length_residual": (
                    edge_residual
                ),
                "max_sorted_angular_gap_residual": (
                    gap_residual
                ),
                "star_edge_perimeter_residual": (
                    perimeter_residual
                ),
                "equivalent_to_phase_0": (
                    equivalent
                ),
            }
        )

    return {
        "reference_phase_id": 0,
        "all_phases_metric_equivalent": (
            all_equivalent
        ),
        "comparisons": per_phase,
    }


def _primary_reciprocal_correspondence(
    composite: MichellComposite,
) -> dict[str, Any]:
    primary_indices = {
        _match_scaffold_index(
            point,
            composite,
        )
        for point
        in composite
        .fourteenfold
        .primary
        .points
    }

    reciprocal_indices = {
        _match_scaffold_index(
            point,
            composite,
        )
        for point
        in composite
        .fourteenfold
        .reciprocal
        .points
    }

    return {
        "primary_scaffold_indices": (
            sorted(
                primary_indices
            )
        ),
        "primary_phase_id": (
            _phase_for_index_set(
                primary_indices
            )
        ),
        "reciprocal_scaffold_indices": (
            sorted(
                reciprocal_indices
            )
        ),
        "reciprocal_phase_id": (
            _phase_for_index_set(
                reciprocal_indices
            )
        ),
        "selection_status": (
            "descriptive_only"
        ),
    }


def _existing_candidate_state(
    composite: MichellComposite,
) -> dict[str, Any]:
    indices = tuple(
        _match_scaffold_index(
            vertex,
            composite,
        )
        for vertex
        in composite
        .scaffold_heptagram_candidate
        .vertices
    )

    return {
        "ordered_scaffold_indices": list(
            indices
        ),
        "phase_id": (
            _phase_for_index_set(
                set(indices)
            )
        ),
        "cyclic_origin_scaffold_index": (
            indices[0]
        ),
        "used_as_selection_evidence": (
            False
        ),
    }


def _grammar_boundary_audit(
    node_rows: list[
        dict[str, str]
    ],
    dependency_rows: list[
        dict[str, str]
    ],
) -> dict[str, Any]:
    nodes = {
        row["node_id"]: row
        for row in node_rows
    }

    dependencies = {
        row["edge_id"]: row
        for row in dependency_rows
    }

    candidate_node = nodes[
        "FIG14_SCAFFOLD_VERTICES"
    ]

    dep_022 = dependencies[
        "DEP-022"
    ]

    dep_024 = dependencies[
        "DEP-024"
    ]

    if (
        candidate_node[
            "node_type"
        ]
        != "project_candidate"
    ):
        raise ValueError(
            "FIG14_SCAFFOLD_VERTICES is no longer "
            "classified project_candidate; "
            "manual Phase 5F review required."
        )

    if (
        dep_022[
            "evidence_status"
        ]
        != "implementation_only"
    ):
        raise ValueError(
            "DEP-022 evidence status changed; "
            "manual Phase 5F review required."
        )

    if (
        dep_024[
            "evidence_status"
        ]
        != "hypothesis_to_test"
    ):
        raise ValueError(
            "DEP-024 evidence status changed; "
            "manual Phase 5F review required."
        )

    touching_edges = tuple(
        dict(row)
        for row in dependency_rows
        if (
            row[
                "parent_node"
            ]
            == "FIG14_SCAFFOLD_VERTICES"
            or row[
                "child_node"
            ]
            == "FIG14_SCAFFOLD_VERTICES"
        )
    )

    return {
        "candidate_node": dict(
            candidate_node
        ),
        "touching_edges": list(
            touching_edges
        ),
        "excluded_existing_phase_evidence": {
            "DEP-022": (
                dep_022[
                    "evidence_status"
                ]
            ),
            "DEP-024": (
                dep_024[
                    "evidence_status"
                ]
            ),
        },
        "existing_phase_node_is_admissible_selection_evidence": (
            False
        ),
    }


def _source_orientation_scan(
    claim_rows: list[
        dict[str, str]
    ],
) -> dict[str, Any]:
    admissible_star_claims = [
        row
        for row in claim_rows
        if (
            row[
                "claim_id"
            ].startswith(
                "STAR-"
            )
            and row[
                "source_status"
            ]
            in SOURCE_GROUNDED_STATUSES
        )
    ]

    matched = []

    for row in admissible_star_claims:
        text = " ".join(
            (
                row.get(
                    "claim",
                    "",
                ),
                row.get(
                    "mathematical_implication",
                    "",
                ),
                row.get(
                    "notes",
                    "",
                ),
            )
        ).lower()

        words = {
            token.strip(
                ".,;:()[]{}\"'"
            )
            for token
            in text.split()
        }

        terms = [
            term
            for term in CARDINAL_TERMS
            if term in words
        ]

        if terms:
            matched.append(
                {
                    "claim_id": (
                        row[
                            "claim_id"
                        ]
                    ),
                    "matched_terms": (
                        terms
                    ),
                }
            )

    if matched:
        raise ValueError(
            "A source-grounded STAR claim contains "
            "named cardinal-orientation language. "
            "Stage A requires manual review before "
            "a selection result is recorded: "
            f"{matched!r}"
        )

    return {
        "admissible_source_claim_ids": [
            row["claim_id"]
            for row
            in admissible_star_claims
        ],
        "searched_terms": list(
            CARDINAL_TERMS
        ),
        "named_cardinal_matches": (
            matched
        ),
        "named_cardinal_orientation_condition_present": (
            False
        ),
        "note": (
            "This scan establishes absence of an explicit "
            "named-cardinal condition in the audited "
            "source-grounded STAR claim records. "
            "It does not infer orientation from source-plate geometry."
        ),
    }


def build_sevenfold_phase_selection_stage_a(
    composite: MichellComposite,
    *,
    protocol_path: str | Path,
    construction_nodes_path: str | Path,
    construction_dependencies_path: str | Path,
    claim_matrix_path: str | Path,
) -> dict[str, Any]:
    """Build the deterministic grammar-only Phase 5F Stage A audit."""

    if not _close(
        composite.unit,
        1.0,
    ):
        raise ValueError(
            "Phase 5F Stage A is registered at unit=1.0."
        )

    node_rows = _read_csv(
        construction_nodes_path
    )

    dependency_rows = _read_csv(
        construction_dependencies_path
    )

    claim_rows = _read_csv(
        claim_matrix_path
    )

    phases = [
        _phase_candidate(
            composite,
            phase_id,
        )
        for phase_id in range(4)
    ]

    quarter_turn = (
        _quarter_turn_audit(
            composite
        )
    )

    metric_equivalence = (
        _metric_equivalence(
            phases
        )
    )

    canonical_role_words = {
        tuple(
            candidate[
                "canonical_cyclic_role_sequence"
            ]
        )
        for candidate in phases
    }

    role_equivalence = {
        "all_role_counts_equal": (
            len(
                {
                    tuple(
                        sorted(
                            candidate[
                                "role_counts"
                            ].items()
                        )
                    )
                    for candidate
                    in phases
                }
            )
            == 1
        ),
        "all_cyclic_role_words_equivalent": (
            len(
                canonical_role_words
            )
            == 1
        ),
        "canonical_cyclic_role_sequence": (
            list(
                next(
                    iter(
                        canonical_role_words
                    )
                )
            )
        ),
    }

    grammar_boundary = (
        _grammar_boundary_audit(
            node_rows,
            dependency_rows,
        )
    )

    orientation_scan = (
        _source_orientation_scan(
            claim_rows
        )
    )

    correspondence = (
        _primary_reciprocal_correspondence(
            composite
        )
    )

    existing_candidate = (
        _existing_candidate_state(
            composite
        )
    )

    surviving_phase_ids = [
        candidate[
            "phase_id"
        ]
        for candidate in phases
        if (
            candidate[
                "candidate_valid"
            ]
        )
    ]

    if not surviving_phase_ids:
        selection_result = (
            "GRAMMAR_INCONSISTENT"
        )

        discriminating_condition = (
            "No registered phase satisfies "
            "the admissible Stage A validity criteria."
        )

    elif len(
        surviving_phase_ids
    ) == 1:
        selection_result = (
            "UNIQUE_GRAMMAR_SELECTION"
        )

        discriminating_condition = (
            "Exactly one registered phase satisfies "
            "the admissible Stage A validity criteria."
        )

    else:
        selection_result = (
            "GRAMMAR_UNDERDETERMINED"
        )

        discriminating_condition = None

    if (
        selection_result
        == "GRAMMAR_UNDERDETERMINED"
        and (
            not quarter_turn[
                "coordinate_rotation_passes"
            ]
            or not quarter_turn[
                "role_rotation_passes"
            ]
            or not quarter_turn[
                "orbit_passes"
            ]
            or not role_equivalence[
                "all_role_counts_equal"
            ]
            or not role_equivalence[
                "all_cyclic_role_words_equivalent"
            ]
            or not metric_equivalence[
                "all_phases_metric_equivalent"
            ]
        )
    ):
        raise ValueError(
            "Multiple phases survive but the registered "
            "symmetry/equivalence expectations do not all pass. "
            "Manual Stage A review is required."
        )

    return {
        "schema_name": (
            PHASE_AUDIT_SCHEMA_NAME
        ),
        "schema_version": (
            PHASE_AUDIT_SCHEMA_VERSION
        ),
        "model_name": (
            composite.model_name
        ),
        "protocol": {
            "phase": "5F",
            "stage": "A",
            "unit": composite.unit,
            "registered_phase_indices": {
                str(phase_id): list(
                    indices
                )
                for phase_id, indices
                in REGISTERED_PHASES.items()
            },
            "registered_step2_edge_pairs": [
                [start, end]
                for start, end
                in STEP2_EDGE_PAIRS
            ],
            "registered_rtol": RTOL,
            "registered_atol": ATOL,
            "protocol_path": (
                _repository_relative_path(
                    protocol_path
                )
            ),
            "protocol_sha256": (
                _sha256(
                    protocol_path
                )
            ),
            "construction_nodes_sha256": (
                _sha256(
                    construction_nodes_path
                )
            ),
            "construction_dependencies_sha256": (
                _sha256(
                    construction_dependencies_path
                )
            ),
            "claim_matrix_sha256": (
                _sha256(
                    claim_matrix_path
                )
            ),
        },
        "stage_a": {
            "candidate_count": (
                len(phases)
            ),
            "phases": phases,
            "quarter_turn_orbit": (
                quarter_turn
            ),
            "role_equivalence": (
                role_equivalence
            ),
            "metric_equivalence": (
                metric_equivalence
            ),
            "primary_reciprocal_correspondence": (
                correspondence
            ),
            "existing_candidate_state": (
                existing_candidate
            ),
            "grammar_boundary": (
                grammar_boundary
            ),
            "source_orientation_scan": (
                orientation_scan
            ),
            "grammar_selection_result": (
                selection_result
            ),
            "surviving_phase_ids": (
                surviving_phase_ids
            ),
            "discriminating_grammar_condition": (
                discriminating_condition
            ),
            "feeds_back_into_builder": False,
        },
        "stage_b": {
            "status": "NOT_RUN",
            "reason": (
                "Stage A must be recorded before "
                "Figure 14 source-coordinate comparison."
            ),
            "independent_validation": False,
            "feeds_back_into_builder": False,
        },
    }


def sevenfold_phase_selection_to_json(
    audit: dict[str, Any],
) -> str:
    """Serialize the phase-selection audit deterministically."""

    return (
        json.dumps(
            audit,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


def write_sevenfold_phase_selection_json(
    audit: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write deterministic Phase 5F audit JSON."""

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        sevenfold_phase_selection_to_json(
            audit
        ),
        encoding="utf-8",
    )

    return path
