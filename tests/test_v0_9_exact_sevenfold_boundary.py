from __future__ import annotations

import hashlib
import inspect
import json
from math import comb
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.exact_sevenfold_boundary import (
    EUCLIDEAN_EXCLUDED,
    NO_NATIVE_EXACT,
    PHASE9A_COMMIT,
    PROTOCOL_SHA256,
    REGISTRY_SPEC_SHA256,
    STOPPING_STATUS,
    build_exact_sevenfold_boundary_audit,
    build_native_candidate_registry,
    build_target_injection_exclusions,
    build_target_polynomial_audit,
    exact_sevenfold_boundary_to_json,
    exact_sevenfold_boundary_to_markdown,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

PROTOCOL = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_exact_sevenfold_constructibility_protocol.md"
)

PROTOCOL_TEST = (
    ROOT
    / "tests"
    / "test_v0_9_exact_sevenfold_constructibility_protocol.py"
)

REGISTRY_SPEC = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_native_incidence_registry.md"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_sevenfold_boundary.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_exact_sevenfold_boundary_result.md"
)

FROZEN_V08 = {
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "septenary_geometry.py"
    ): (
        "419d38ac8b5a4d0201e6e0cb4ed05a8d"
        "776386286119885463fa95fae374fa6c"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "sevenfold_dual_method.py"
    ): (
        "33c5fee3a1d198abc1eb73c1ff114829b"
        "1dc5a66f0e355605ed25793b33f5c70"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "method2_propagation.py"
    ): (
        "8b28ee957a7ee210ee35dfe80f66bd642"
        "07e5c146da23623d859d6cc7d491a9d"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "method2_symbolic_gap.py"
    ): (
        "2f81fce15e6863a877e28c0ad0ffb1a9"
        "5a35c6186cfb5b42313d58077b1bdb2c"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_nodes.csv"
    ): (
        "5c13a735882ebb27c4e1b942bea605cf7"
        "6d76f996c486ca049325d7246735bc7"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_dependencies.csv"
    ): (
        "cdb8f7fc881851e2c52ba84fec5f2f80"
        "c51e45193c47eef4f11f6e42512657a5"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_grammar.md"
    ): (
        "3f2d7a4cb879565509be05dbc71f6cc8"
        "b5d8d57c54a7f7324393c9f71fe25110"
    ),
}


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _audit():
    return build_exact_sevenfold_boundary_audit()


def test_phase9a_boundary_is_frozen() -> None:
    assert (
        PHASE9A_COMMIT
        == "d986a18a3985bf55b620a41678380231e71c7c38"
    )

    assert (
        _sha256(
            PROTOCOL
        )
        == PROTOCOL_SHA256
        == "ac50f47c4a57000a831958b4e47381533768ed8cebe1d40d309e5c66e3aa2d22"
    )

    assert (
        _sha256(
            PROTOCOL_TEST
        )
        == "585fcb788ffff46b1041182e935f0abb145b36757bcd3c0f8f43da0fb47a551c"
    )


def test_registry_specification_hash_is_frozen() -> None:
    assert (
        _sha256(
            REGISTRY_SPEC
        )
        == REGISTRY_SPEC_SHA256
        == "e26b1725d44ce2454324b97d4b63d11ee8e371cfabef64c1f2da3bb7835cfc35"
    )


def test_frozen_v08_surfaces_remain_unchanged() -> None:
    for path, digest in FROZEN_V08.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_target_cubic_is_derived_exactly() -> None:
    audit = (
        build_target_polynomial_audit()
    )

    assert (
        audit.polynomial_coefficients_low_to_high
        == (
            -1,
            -2,
            1,
            1,
        )
    )

    assert (
        audit.polynomial_text
        == "y^3 + y^2 - 2*y - 1"
    )

    assert (
        audit.cosine_polynomial_coefficients_low_to_high
        == (
            -1,
            -4,
            4,
            8,
        )
    )

    assert (
        audit.cosine_polynomial_text
        == "8*c^3 + 4*c^2 - 4*c - 1"
    )


def test_target_cubic_is_irreducible_over_q() -> None:
    audit = (
        build_target_polynomial_audit()
    )

    assert (
        audit.rational_root_candidates
        == (
            -1,
            1,
        )
    )

    assert (
        audit.rational_root_values
        == (
            1,
            -1,
        )
    )

    assert (
        audit.irreducible_over_q
        is True
    )

    assert (
        audit.algebraic_degree
        == 3
    )

    assert (
        audit.degree_is_power_of_two
        is False
    )


def test_euclidean_closure_is_excluded() -> None:
    audit = _audit()

    assert (
        audit.euclidean_closure_status
        == EUCLIDEAN_EXCLUDED
        == "EUCLIDEAN_EXACT_SEVENFOLD_EXCLUDED"
    )


def test_all_n0_seed_lineages_are_verified() -> None:
    audit = _audit()

    expected = {
        "CORE_DIMENSIONS",
        "EARTH_CIRCLE",
        "EARTH_SQUARE",
        "CONSTRUCTION_CIRCLE",
        "CARDINAL_MOONS",
        "SQUARE_CIRCLE_INTERSECTIONS",
        "NJG_INC_MOONS",
        "MOON_GROUPS_4X3",
        "SEPTENARY_METHOD_1",
        "RECIPROCAL_TRIANGLE_14",
        "SCAFFOLD_28",
        "SEPTENARY_METHOD_2",
        "METHOD2_21",
        "METHOD2_42",
    }

    assert {
        row.node_id
        for row in audit.n0_seed_lineage_checks
    } == expected

    assert all(
        row.verified_constructible
        for row in audit.n0_seed_lineage_checks
    )


def test_n1_lineage_is_verified_but_not_censused() -> None:
    audit = _audit()

    assert {
        row.node_id
        for row in audit.n1_seed_lineage_checks
    } == {
        "REGULAR_DODECAGON_BASELINE",
        "POLAR_PIVOT_WALL",
    }

    assert all(
        row.verified_constructible
        for row in audit.n1_seed_lineage_checks
    )

    assert all(
        not row.census_enabled
        for row in audit.n1_seed_lineage_checks
    )


def test_target_injection_exclusion_registry_is_exactly_frozen() -> None:
    rows = (
        build_target_injection_exclusions()
    )

    assert len(
        rows
    ) == 7

    assert {
        row.exclusion_id
        for row in rows
    } == {
        "X01",
        "X02",
        "X03",
        "X04",
        "X05",
        "X06",
        "X07",
    }

    names = {
        row.object_name
        for row in rows
    }

    required = {
        "ObliqueModel.DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "free regular seven-vertex fits",
        "exact_heptagon_step_radians",
        "exact_heptagonal_step_radians",
        "direct 2*pi/7 reference objects",
    }

    assert names == required


def test_native_registry_scope_is_frozen_before_target_comparison() -> None:
    candidates = (
        build_native_candidate_registry()
    )

    radial = [
        row
        for row in candidates
        if row.feature_type
        == "radial_direction"
    ]

    separations = [
        row
        for row in candidates
        if row.feature_type
        == "pairwise_radial_separation"
    ]

    lines = [
        row
        for row in candidates
        if row.feature_type
        == "native_line_direction"
    ]

    assert len(
        radial
    ) == 98

    assert len(
        separations
    ) == comb(
        98,
        2,
    ) == 4753

    assert len(
        lines
    ) == 22

    assert len(
        candidates
    ) == 4873


def test_native_registry_generation_does_not_inject_target() -> None:
    source = inspect.getsource(
        build_native_candidate_registry
    )

    forbidden = (
        "2.0 * pi / 7.0",
        "pi / 7",
        "DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "exact_heptagon_step_radians",
        "exact_heptagonal_step_radians",
    )

    for token in forbidden:
        assert token not in source

    candidates = (
        build_native_candidate_registry()
    )

    assert all(
        not row.target_injected
        for row in candidates
    )

    assert all(
        row.constructible_lineage
        for row in candidates
    )


def test_candidate_ids_are_unique() -> None:
    candidates = (
        build_native_candidate_registry()
    )

    ids = [
        row.candidate_id
        for row in candidates
    ]

    assert len(
        ids
    ) == len(
        set(
            ids
        )
    )


def test_symmetry_reduction_is_deliberately_disabled() -> None:
    census = (
        _audit()
        .census
    )

    assert (
        census.candidate_count_semantic
        == 4873
    )

    assert (
        census.candidate_count_symmetry_reduced
        == 4873
    )

    assert (
        "no numerical symmetry clustering"
        in census.symmetry_reduction_mode
    )


def test_exact_native_candidate_count_uses_theorem_not_tolerance() -> None:
    census = (
        _audit()
        .census
    )

    assert (
        census.exact_classification_method
        == (
            "constructibility_degree_obstruction; "
            "no numerical tolerance"
        )
    )

    assert (
        census.exact_candidate_count
        == 0
    )

    assert (
        census.native_incidence_status
        == NO_NATIVE_EXACT
        == "NO_NATIVE_EXACT_SEVENFOLD"
    )


def test_closest_candidate_is_descriptive_and_nonzero() -> None:
    census = (
        _audit()
        .census
    )

    assert (
        census.closest_descriptive_candidate_id
    )

    assert (
        census.closest_descriptive_residual_radians
        > 0.0
    )

    assert (
        census.closest_descriptive_residual_degrees
        > 0.0
    )


def test_question_c_remains_deferred() -> None:
    audit = _audit()

    assert (
        audit.question_c_status
        == "DEFERRED_UNTIL_PHASE_9B_FREEZE"
    )


def test_zero_fit_degrees_of_freedom() -> None:
    dof = (
        _audit()
        .degrees_of_freedom
    )

    assert (
        dof.continuous_fitted_parameters
        == 0
    )
    assert (
        dof.scale_fitted_parameters
        == 0
    )
    assert (
        dof.phase_optimized_parameters
        == 0
    )
    assert (
        dof.target_based_candidate_choices
        == 0
    )
    assert (
        dof.numerical_acceptance_tolerances
        == 0
    )
    assert (
        dof.post_hoc_seed_additions
        == 0
    )
    assert (
        dof.non_euclidean_operations
        == 0
    )


def test_stopping_status_is_outcome_independent() -> None:
    assert (
        _audit().stopping_status
        == STOPPING_STATUS
        == "EXACT_SEVENFOLD_BOUNDARY_AUDIT_COMPLETE"
    )


def test_json_is_deterministic() -> None:
    assert (
        exact_sevenfold_boundary_to_json(
            _audit()
        )
        == exact_sevenfold_boundary_to_json(
            _audit()
        )
    )


def test_markdown_is_deterministic() -> None:
    assert (
        exact_sevenfold_boundary_to_markdown(
            _audit()
        )
        == exact_sevenfold_boundary_to_markdown(
            _audit()
        )
    )


def test_tracked_json_matches_generation() -> None:
    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == exact_sevenfold_boundary_to_json(
            _audit()
        )
    )


def test_tracked_markdown_matches_generation() -> None:
    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == exact_sevenfold_boundary_to_markdown(
            _audit()
        )
    )


def test_markdown_preserves_interpretation_boundary() -> None:
    text = MARKDOWN_OUT.read_text(
        encoding="utf-8"
    )

    normalized = " ".join(
        text.split()
    )

    required = (
        "theorem-level constructibility result",
        "not a finite-search failure",
        "nearest value is not promoted",
        "No neusis, marked-ruler, origami, or conic extension",
        "does not establish",
        "metaphysical significance",
    )

    for phrase in required:
        assert phrase in normalized


def test_json_has_full_semantic_registry() -> None:
    payload = json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )

    assert len(
        payload[
            "native_candidates"
        ]
    ) == 4873


def test_package_version_remains_0_8_0() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
