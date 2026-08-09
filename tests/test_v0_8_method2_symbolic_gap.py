from __future__ import annotations

import ast
from fractions import Fraction
import hashlib
import json
from math import (
    pi,
    sqrt,
)
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.method2_symbolic_gap import (
    IDENTITY_TOLERANCE_RADIANS,
    PHASE8C_LOCAL_COMPARISON_SHA256,
    PHASE8E_COMMIT,
    PHASE8E_PROPAGATION_JSON_SHA256,
    SPECIFICATION_SHA256,
    STOPPING_STATUS,
    build_method2_symbolic_gap_audit,
    method2_symbolic_gap_audit_to_json,
    method2_symbolic_gap_audit_to_markdown,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

SPECIFICATION = (
    ROOT
    / "docs"
    / "specification"
    / "v0.8_method2_symbolic_gap_audit.md"
)

PROPAGATION_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

LOCAL_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
)

MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "method2_symbolic_gap.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_symbolic_gap_audit.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_method2_symbolic_gap_audit_result.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _propagation() -> dict:
    return json.loads(
        PROPAGATION_JSON.read_text(
            encoding="utf-8"
        )
    )


def _local() -> dict:
    return json.loads(
        LOCAL_JSON.read_text(
            encoding="utf-8"
        )
    )


def _audit():
    return build_method2_symbolic_gap_audit(
        _propagation(),
        _local(),
    )


def test_specification_hash_is_frozen() -> None:
    assert (
        _sha256(
            SPECIFICATION
        )
        == SPECIFICATION_SHA256
        == "d1fe38b9c2cd6cacae504510fa5392630467c11629766bd5cb5f74db9c14c9f8"
    )


def test_phase8e_commit_is_frozen() -> None:
    assert (
        PHASE8E_COMMIT
        == "058a934"
    )


def test_frozen_input_hashes() -> None:
    assert (
        _sha256(
            PROPAGATION_JSON
        )
        == PHASE8E_PROPAGATION_JSON_SHA256
        == "5af0b893ef9f18f5bb6c04e013f12298d816f426a2a248eccbd9230ab5ad4a43"
    )

    assert (
        _sha256(
            LOCAL_JSON
        )
        == PHASE8C_LOCAL_COMPARISON_SHA256
        == "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f"
    )


def test_evidential_status_is_explicitly_post_result() -> None:
    audit = _audit()

    assert (
        audit.evidential_status
        == "post-result explanatory derivation"
    )

    specification = SPECIFICATION.read_text(
        encoding="utf-8"
    )

    assert (
        "not preregistered predictions"
        in specification
    )


def test_delta_definition() -> None:
    audit = _audit()

    expected = (
        2.0
        * pi
        / 7.0
        - audit.alpha_radians
    )

    assert (
        audit.delta_radians
        == expected
    )

    assert (
        audit.delta_radians
        > 0.0
    )


def test_twenty_one_signature_classes_are_exactly_disclosed_candidates() -> None:
    audit = _audit()

    rows = {
        (
            row.a_pi_over_3,
            row.b_alpha,
        ): (
            row.count,
            row.delta_residual_coefficient,
        )
        for row
        in audit.twenty_one.signature_classes
    }

    assert rows == {
        (
            2,
            -2,
        ): (
            15,
            2,
        ),
        (
            -4,
            5,
        ): (
            6,
            -5,
        ),
    }


def test_forty_two_signature_classes_are_exactly_disclosed_candidates() -> None:
    audit = _audit()

    rows = {
        (
            row.a_pi_over_3,
            row.b_alpha,
        ): (
            row.count,
            row.delta_residual_coefficient,
        )
        for row
        in audit.forty_two.signature_classes
    }

    assert rows == {
        (
            1,
            -1,
        ): (
            36,
            1,
        ),
        (
            -5,
            6,
        ): (
            6,
            -6,
        ),
    }


def test_exact_rational_regular_gap_identities() -> None:
    twenty_one = (
        (
            2,
            -2,
        ),
        (
            -4,
            5,
        ),
    )

    forty_two = (
        (
            1,
            -1,
        ),
        (
            -5,
            6,
        ),
    )

    for a, b in twenty_one:
        assert (
            Fraction(
                a,
                3,
            )
            + Fraction(
                2
                * b,
                7,
            )
            == Fraction(
                2,
                21,
            )
        )

    for a, b in forty_two:
        assert (
            Fraction(
                a,
                3,
            )
            + Fraction(
                2
                * b,
                7,
            )
            == Fraction(
                1,
                21,
            )
        )


def test_cyclic_patterns_are_exactly_disclosed_candidates() -> None:
    audit = _audit()

    assert (
        audit.twenty_one
        .cyclic_class_pattern
        == "LLLSLLS"
        * 3
    )

    assert (
        audit.forty_two
        .cyclic_class_pattern
        == "LLLLLLS"
        * 6
    )


def test_weighted_residual_coefficients_close_exactly() -> None:
    audit = _audit()

    assert (
        audit.twenty_one
        .weighted_delta_residual_coefficient_sum
        == 0
    )

    assert (
        audit.forty_two
        .weighted_delta_residual_coefficient_sum
        == 0
    )

    assert (
        15
        * 2
        + 6
        * (
            -5
        )
        == 0
    )

    assert (
        36
        * 1
        + 6
        * (
            -6
        )
        == 0
    )


def test_rms_coefficients_are_exact() -> None:
    audit = _audit()

    assert (
        audit.twenty_one
        .rms_squared_delta_coefficient
        == 10
    )

    assert (
        audit.forty_two
        .rms_squared_delta_coefficient
        == 6
    )

    assert (
        audit.twenty_one
        .rms_delta_coefficient_symbolic
        == "sqrt(10)"
    )

    assert (
        audit.forty_two
        .rms_delta_coefficient_symbolic
        == "sqrt(6)"
    )


def test_max_and_range_coefficients_are_exact() -> None:
    audit = _audit()

    assert (
        audit.twenty_one
        .maximum_absolute_delta_coefficient
        == 5
    )

    assert (
        audit.forty_two
        .maximum_absolute_delta_coefficient
        == 6
    )

    assert (
        audit.twenty_one
        .gap_range_delta_coefficient
        == 7
    )

    assert (
        audit.forty_two
        .gap_range_delta_coefficient
        == 7
    )


def test_derived_metrics_reproduce_frozen_phase8e() -> None:
    audit = _audit()

    errors = (
        audit.twenty_one
        .rms_identity_absolute_error_radians,
        audit.twenty_one
        .max_identity_absolute_error_radians,
        audit.twenty_one
        .range_identity_absolute_error_radians,
        audit.forty_two
        .rms_identity_absolute_error_radians,
        audit.forty_two
        .max_identity_absolute_error_radians,
        audit.forty_two
        .range_identity_absolute_error_radians,
    )

    assert all(
        error
        <= IDENTITY_TOLERANCE_RADIANS
        for error in errors
    )


def test_exact_cross_relation_predictions() -> None:
    audit = _audit()

    cross = (
        audit.cross_relations
    )

    assert (
        cross.raw_rms_ratio_symbolic
        == "sqrt(3/5)"
    )

    assert (
        cross.raw_rms_ratio_predicted
        == sqrt(
            3.0
            / 5.0
        )
    )

    assert (
        cross.max_abs_ratio_symbolic
        == "6/5"
    )

    assert (
        cross.max_abs_ratio_predicted
        == 6.0
        / 5.0
    )

    assert (
        cross.gap_range_ratio_symbolic
        == "1"
    )

    assert (
        cross.gap_range_ratio_predicted
        == 1.0
    )

    assert (
        cross.normalized_rms_ratio_symbolic
        == "2*sqrt(3/5)"
    )

    assert (
        cross.normalized_rms_ratio_predicted
        == 2.0
        * sqrt(
            3.0
            / 5.0
        )
    )


def test_cross_relations_reproduce_frozen_phase8e() -> None:
    audit = _audit()

    cross = (
        audit.cross_relations
    )

    errors = (
        cross.raw_rms_ratio_absolute_error,
        cross.max_abs_ratio_absolute_error,
        cross.gap_range_ratio_absolute_error,
        cross.normalized_rms_ratio_absolute_error,
        cross.twenty_one_range_vs_closure_absolute_error_radians,
        cross.forty_two_range_vs_closure_absolute_error_radians,
    )

    assert all(
        error
        <= IDENTITY_TOLERANCE_RADIANS
        for error in errors
    )


def test_common_range_equals_seven_delta() -> None:
    audit = _audit()

    predicted = (
        7.0
        * audit.delta_radians
    )

    assert (
        abs(
            audit.twenty_one
            .predicted_gap_range_radians
            - predicted
        )
        <= IDENTITY_TOLERANCE_RADIANS
    )

    assert (
        abs(
            audit.forty_two
            .predicted_gap_range_radians
            - predicted
        )
        <= IDENTITY_TOLERANCE_RADIANS
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
        dof.scale_parameters
        == 0
    )

    assert (
        dof.gap_clustering_thresholds
        == 0
    )

    assert (
        dof.optimized_symbolic_coefficients
        == 0
    )

    assert (
        dof.candidate_class_selection_after_specification
        == 0
    )


def test_stopping_status_is_fixed() -> None:
    assert (
        _audit().stopping_status
        == STOPPING_STATUS
        == "METHOD2_SYMBOLIC_GAP_AUDIT_COMPLETE"
    )


def test_json_is_deterministic() -> None:
    assert (
        method2_symbolic_gap_audit_to_json(
            _audit()
        )
        == method2_symbolic_gap_audit_to_json(
            _audit()
        )
    )


def test_markdown_is_deterministic() -> None:
    assert (
        method2_symbolic_gap_audit_to_markdown(
            _audit()
        )
        == method2_symbolic_gap_audit_to_markdown(
            _audit()
        )
    )


def test_tracked_json_matches_generation() -> None:
    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == method2_symbolic_gap_audit_to_json(
            _audit()
        )
    )


def test_tracked_markdown_matches_generation() -> None:
    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == method2_symbolic_gap_audit_to_markdown(
            _audit()
        )
    )


def test_json_has_no_absolute_machine_paths() -> None:
    text = JSON_OUT.read_text(
        encoding="utf-8"
    )

    assert "/home/" not in text
    assert "\\Users\\" not in text
    assert str(
        ROOT
    ) not in text


def test_module_has_no_fit_or_plate_imports() -> None:
    tree = ast.parse(
        MODULE.read_text(
            encoding="utf-8"
        )
    )

    imports: list[str] = []

    for node in ast.walk(
        tree
    ):
        if isinstance(
            node,
            ast.Import,
        ):
            imports.extend(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.ImportFrom,
        ):
            imports.append(
                node.module
                or ""
            )

    joined = " ".join(
        imports
    ).lower()

    forbidden = (
        "figure14",
        "calibration",
        "registration",
        "numpy",
        "scipy",
        "optimize",
    )

    for token in forbidden:
        assert token not in joined


def test_markdown_preserves_post_result_boundary() -> None:
    text = MARKDOWN_OUT.read_text(
        encoding="utf-8"
    )

    required = (
        "post-result explanatory derivation",
        "not preregistered predictions",
        "mechanically derived symbolic identity",
        "does not show that Michell stated",
        "independent historical or empirical evidence",
    )

    for phrase in required:
        assert phrase in text


def test_package_version_remains_0_7_0() -> None:
    assert (
        njg.__version__
        == "0.7.0"
    )
