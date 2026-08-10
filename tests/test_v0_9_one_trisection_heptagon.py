from __future__ import annotations

import hashlib
import inspect
import json
from fractions import Fraction
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.one_trisection_heptagon import (
    PHASE9C_COMMIT,
    PHASE9C_PROTOCOL_SHA256,
    PHASE9C_PROTOCOL_TEST_SHA256,
    STOPPING_STATUS_CONFIRMED,
    build_one_trisection_audit,
    build_one_trisection_heptagon,
    derive_depressed_cubic_coefficients,
    derive_target_cubic_coefficients,
    one_trisection_audit_to_json,
    one_trisection_audit_to_markdown,
    verify_builder_target_injection_boundary,
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
    / "v0.9_one_trisection_heptagon_protocol.md"
)

PROTOCOL_TEST = (
    ROOT
    / "tests"
    / "test_v0_9_one_trisection_heptagon_protocol.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "one_trisection_heptagon.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_one_trisection_heptagon_result.md"
)

FROZEN_PHASE9B = {
    (
        ROOT
        / "docs"
        / "specification"
        / "v0.9_native_incidence_registry.md"
    ): (
        "e26b1725d44ce2454324b97d4b63d11e"
        "e8e371cfabef64c1f2da3bb7835cfc35"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "exact_sevenfold_boundary.py"
    ): (
        "81be21198b4ec7d1efea59b7512a7d4d"
        "8fa91fd00427ab54b8ce153c10abf7a9"
    ),
    (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_9"
        / "exact_sevenfold_boundary.json"
    ): (
        "cc150e2c92efdebe130f86f2c03998336"
        "883abb985513e8e634977682c84442f"
    ),
    (
        ROOT
        / "docs"
        / "geometry"
        / "v0.9_exact_sevenfold_boundary_result.md"
    ): (
        "90e6067f21ef9d11f891ca786110f360"
        "3394ce1439c868c48588f54691f5dab5"
    ),
}


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _audit():
    return build_one_trisection_audit()


def test_phase9c_boundary_is_frozen() -> None:
    assert (
        PHASE9C_COMMIT
        == "83dba523f9097b162e5dde45ebd68089cbc3972a"
    )

    assert (
        _sha256(
            PROTOCOL
        )
        == PHASE9C_PROTOCOL_SHA256
        == "d125a37b1764c6dee558b36279dc45cfa10b2df6627d76ebecfba6b727fe629c"
    )

    assert (
        _sha256(
            PROTOCOL_TEST
        )
        == PHASE9C_PROTOCOL_TEST_SHA256
        == "766f7c6e6e4802907c9005f6a019e3dfc90b0d3875e2585d18418947f68f0248"
    )


def test_phase9b_results_remain_frozen() -> None:
    for path, digest in FROZEN_PHASE9B.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_depressed_cubic_is_exact_fraction_arithmetic() -> None:
    assert (
        derive_depressed_cubic_coefficients()
        == (
            Fraction(
                -7,
                27,
            ),
            Fraction(
                -7,
                3,
            ),
            Fraction(
                0,
                1,
            ),
            Fraction(
                1,
                1,
            ),
        )
    )


def test_target_cubic_shift_is_exact_fraction_arithmetic() -> None:
    assert (
        derive_target_cubic_coefficients()
        == (
            Fraction(
                -1,
                1,
            ),
            Fraction(
                -2,
                1,
            ),
            Fraction(
                1,
                1,
            ),
            Fraction(
                1,
                1,
            ),
        )
    )


def test_builder_uses_exactly_one_trisection() -> None:
    construction = (
        build_one_trisection_heptagon()
    )

    assert (
        construction.cubic.trisection_call_count
        == 1
    )


def test_builder_target_injection_boundary() -> None:
    assert (
        verify_builder_target_injection_boundary()
        is True
    )

    source = inspect.getsource(
        build_one_trisection_heptagon
    )

    forbidden = (
        "2*pi/7",
        "2.0 * pi / 7.0",
        "pi/7",
        "DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "separation/021-078",
    )

    for token in forbidden:
        assert token not in source


def test_all_registered_criteria_pass() -> None:
    audit = _audit()

    assert len(
        audit.criteria
    ) == 14

    assert [
        criterion.criterion_id
        for criterion in audit.criteria
    ] == [
        f"C{index}"
        for index in range(
            1,
            15,
        )
    ]

    assert all(
        criterion.passed
        for criterion in audit.criteria
    )


def test_exact_target_identification_is_theorem_based() -> None:
    audit = _audit()

    assert (
        audit.exact_target_identification
        is True
    )

    c10 = next(
        criterion
        for criterion in audit.criteria
        if criterion.criterion_id
        == "C10"
    )

    assert (
        c10.proof_kind
        == "same exact cubic plus unique registered interval"
    )


def test_exact_heptagon_has_seven_vertices_and_sides() -> None:
    construction = (
        _audit()
        .construction
    )

    assert len(
        construction.heptagon.vertices
    ) == 7

    assert len(
        construction.heptagon.side_lengths
    ) == 7


def test_numerical_diagnostics_are_machine_scale_only() -> None:
    audit = _audit()

    # These are implementation diagnostics only, not exactness thresholds.
    assert abs(
        audit.target_numeric_residual
    ) < 1.0e-12

    assert abs(
        audit.target_angle_residual_radians
    ) < 1.0e-12

    assert (
        audit.max_radius_residual
        < 1.0e-12
    )

    assert (
        audit.side_length_range
        < 1.0e-12
    )

    assert (
        audit.seven_step_closure_residual
        < 1.0e-12
    )


def test_stopping_status_is_confirmed_only_after_all_criteria() -> None:
    audit = _audit()

    assert all(
        criterion.passed
        for criterion in audit.criteria
    )

    assert (
        audit.stopping_status
        == STOPPING_STATUS_CONFIRMED
        == "ONE_TRISECTION_EXACT_HEPTAGON_CONFIRMED"
    )


def test_minimality_statement_is_narrow() -> None:
    audit = _audit()

    assert (
        audit.minimality_status
        == "MINIMUM_ONE_CUBIC_CAPABLE_OPERATION_WITHIN_FROZEN_MODEL"
    )

    assert (
        audit.non_euclidean_operation_count
        == 1
    )

    assert (
        audit.non_euclidean_operation_type
        == "TRISECT_ANGLE"
    )


def test_zero_search_degrees_of_freedom() -> None:
    dof = (
        _audit()
        .degrees_of_freedom
    )

    assert dof == {
        "continuous_fitted_parameters": 0,
        "scale_fitted_parameters": 0,
        "angle_search_parameters": 0,
        "anchor_search_parameters": 0,
        "root_branch_choices_after_result": 0,
        "target_based_candidate_choices": 0,
        "numerical_exactness_tolerances": 0,
        "post_hoc_candidate_substitutions": 0,
    }


def test_json_is_deterministic() -> None:
    assert (
        one_trisection_audit_to_json(
            _audit()
        )
        == one_trisection_audit_to_json(
            _audit()
        )
    )


def test_markdown_is_deterministic() -> None:
    assert (
        one_trisection_audit_to_markdown(
            _audit()
        )
        == one_trisection_audit_to_markdown(
            _audit()
        )
    )


def test_tracked_json_matches_generation() -> None:
    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == one_trisection_audit_to_json(
            _audit()
        )
    )


def test_tracked_markdown_matches_generation() -> None:
    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == one_trisection_audit_to_markdown(
            _audit()
        )
    )


def test_markdown_interpretation_boundary() -> None:
    text = " ".join(
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        ).split()
    )

    required = (
        "single candidate frozen in the Phase 9C protocol",
        "No alternative cubic-capable construction was searched",
        "numerical residuals are diagnostics, not the exactness proof",
        "minimum in the number of cubic-capable operations",
        "not a claim that angle trisection is uniquely simplest",
        "does not establish that Michell or Sommerville knew this construction",
    )

    for phrase in required:
        assert phrase in text


def test_json_contains_all_criteria() -> None:
    payload = json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )

    assert len(
        payload[
            "criteria"
        ]
    ) == 14


def test_package_version_remains_0_8_0() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
