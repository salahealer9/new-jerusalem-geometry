from __future__ import annotations

import ast
import hashlib
import json
from math import (
    acos,
    pi,
)
from pathlib import Path

import pytest

import new_jerusalem_geometry as njg
from new_jerusalem_geometry.core_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.septenary_geometry import (
    MichellTriangleBase,
    build_michell_sevenfold_division,
)
from new_jerusalem_geometry.sevenfold_dual_method import (
    METHOD2_IDENTITY_TOLERANCE_RADIANS,
    PHASE8A_COMMIT,
    PHASE8A_SOURCE_AUDIT_SHA256,
    PROTOCOL_SHA256,
    STOPPING_STATUS,
    build_dual_method_comparison,
    dual_method_comparison_to_json,
    dual_method_comparison_to_markdown,
    method_2_step_from_source_geometry,
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
    / "v0.8_dual_method_numerical_comparison_protocol.md"
)

SOURCE_AUDIT = (
    ROOT
    / "docs"
    / "sources"
    / "v0.8_sevenfold_dual_method_source_audit.md"
)

METHOD1_SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "septenary_geometry.py"
)

MODULE_SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "sevenfold_dual_method.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_dual_method_comparison_result.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _canonical_result():
    return build_dual_method_comparison(
        method1_source_sha256=(
            _sha256(
                METHOD1_SOURCE
            )
        ),
    )


def _tracked_payload() -> dict:
    return json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )


def test_frozen_protocol_hash() -> None:
    assert (
        _sha256(
            PROTOCOL
        )
        == PROTOCOL_SHA256
        == "6e4c4e6a5c87280f3ff67d3e21997c681aec22b5cfbe39be713b5627507d2a99"
    )


def test_frozen_phase8a_source_audit_hash() -> None:
    assert (
        _sha256(
            SOURCE_AUDIT
        )
        == PHASE8A_SOURCE_AUDIT_SHA256
        == "48a7892bb7be5ebd1b0cfdc2e66f0de7a4f380b6926d7a1799c6693e7dd441b4"
    )


def test_method1_source_hash_is_bound_by_protocol() -> None:
    method1_sha = _sha256(
        METHOD1_SOURCE
    )

    assert method1_sha in PROTOCOL.read_text(
        encoding="utf-8"
    )


def test_phase8a_commit_is_frozen() -> None:
    assert (
        PHASE8A_COMMIT
        == "d30a384"
    )


def test_exact_reference_is_two_pi_over_seven() -> None:
    result = _canonical_result()

    assert (
        result.alpha_exact_radians
        == 2.0 * pi / 7.0
    )


def test_method1_is_read_from_frozen_existing_builder() -> None:
    result = _canonical_result()

    diagram = build_core_geometry(
        unit=1.0
    )

    existing = (
        build_michell_sevenfold_division(
            diagram,
            MichellTriangleBase.SOUTH,
        )
    )

    assert (
        result.method_1.alpha_radians
        == existing.step_radians
    )


def test_method2_source_geometry_matches_acos_five_eighths() -> None:
    derived = (
        method_2_step_from_source_geometry()
    )

    identity = acos(
        5.0
        / 8.0
    )

    assert (
        abs(
            derived
            - identity
        )
        <= METHOD2_IDENTITY_TOLERANCE_RADIANS
    )


@pytest.mark.parametrize(
    "name",
    [
        "method_1",
        "method_2",
    ],
)
def test_primary_residual_formulas(
    name: str,
) -> None:
    result = _canonical_result()

    method = getattr(
        result,
        name,
    )

    signed = (
        method.alpha_radians
        - result.alpha_exact_radians
    )

    assert (
        method.signed_residual_radians
        == signed
    )

    assert (
        method.absolute_residual_radians
        == abs(
            signed
        )
    )

    assert (
        method.relative_residual
        == signed
        / result.alpha_exact_radians
    )

    assert (
        method.percent_residual
        == 100.0
        * method.relative_residual
    )

    assert (
        method.absolute_percent_residual
        == abs(
            method.percent_residual
        )
    )

    assert (
        method.seven_step_closure_radians
        == 7.0
        * method.alpha_radians
        - 2.0
        * pi
    )


def test_r1_bracketing_is_recomputed_from_raw_angles() -> None:
    result = _canonical_result()

    expected = (
        result.method_2.alpha_radians
        < result.alpha_exact_radians
        < result.method_1.alpha_radians
    )

    assert (
        result.relationships.bracketing
        is expected
    )


def test_r2_opposite_signed_errors_is_recomputed() -> None:
    result = _canonical_result()

    first = (
        result.method_1
        .signed_residual_radians
    )

    second = (
        result.method_2
        .signed_residual_radians
    )

    expected = (
        first != 0.0
        and second != 0.0
        and (
            first > 0.0
        )
        != (
            second > 0.0
        )
    )

    assert (
        result.relationships
        .opposite_signed_errors
        is expected
    )


def test_r3_accuracy_order_uses_raw_absolute_residuals() -> None:
    result = _canonical_result()

    first = (
        result.method_1
        .absolute_residual_radians
    )

    second = (
        result.method_2
        .absolute_residual_radians
    )

    if first < second:
        expected = (
            "method_1",
            "method_2",
        )
    elif second < first:
        expected = (
            "method_2",
            "method_1",
        )
    else:
        expected = "TIE"

    assert (
        result.relationships
        .absolute_accuracy_order
        == expected
    )


def test_r4_absolute_error_ratio_formula() -> None:
    result = _canonical_result()

    denominator = (
        result.method_1
        .absolute_residual_radians
    )

    if denominator == 0.0:
        assert (
            result.relationships
            .absolute_error_ratio
            is None
        )
    else:
        assert (
            result.relationships
            .absolute_error_ratio
            == (
                result.method_2
                .absolute_residual_radians
                / denominator
            )
        )


def test_r5_midpoint_formulas() -> None:
    result = _canonical_result()

    midpoint = (
        result.method_1.alpha_radians
        + result.method_2.alpha_radians
    ) / 2.0

    signed = (
        midpoint
        - result.alpha_exact_radians
    )

    assert (
        result.exploratory
        .arithmetic_midpoint_radians
        == midpoint
    )

    assert (
        result.exploratory
        .midpoint_signed_residual_radians
        == signed
    )

    assert (
        result.exploratory
        .midpoint_absolute_residual_radians
        == abs(
            signed
        )
    )


def test_zero_fit_degrees_of_freedom() -> None:
    dof = (
        _canonical_result()
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
        dof.target_based_candidate_choices
        == 0
    )

    assert (
        dof.optimized_combination_weights
        == 0
    )


def test_method2_identity_is_implementation_check_only() -> None:
    checks = (
        _canonical_result()
        .implementation_checks
    )

    assert (
        checks.method_2_identity_pass
        is True
    )

    assert (
        checks.method_2_identity_absolute_error_radians
        <= checks.method_2_identity_tolerance_radians
        == METHOD2_IDENTITY_TOLERANCE_RADIANS
    )


def test_stopping_status_is_fixed() -> None:
    result = _canonical_result()

    assert (
        result.stopping_status
        == STOPPING_STATUS
        == "DUAL_METHOD_LOCAL_COMPARISON_COMPLETE"
    )


def test_canonical_json_is_deterministic() -> None:
    first = dual_method_comparison_to_json(
        _canonical_result()
    )

    second = dual_method_comparison_to_json(
        _canonical_result()
    )

    assert first == second


def test_canonical_markdown_is_deterministic() -> None:
    first = dual_method_comparison_to_markdown(
        _canonical_result()
    )

    second = dual_method_comparison_to_markdown(
        _canonical_result()
    )

    assert first == second


def test_tracked_json_matches_canonical_generation() -> None:
    expected = dual_method_comparison_to_json(
        _canonical_result()
    )

    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == expected
    )


def test_tracked_markdown_matches_canonical_generation() -> None:
    expected = (
        dual_method_comparison_to_markdown(
            _canonical_result()
        )
    )

    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == expected
    )


def test_json_records_required_provenance() -> None:
    payload = _tracked_payload()

    assert (
        payload[
            "protocol_sha256"
        ]
        == PROTOCOL_SHA256
    )

    assert (
        payload[
            "phase8a_commit"
        ]
        == PHASE8A_COMMIT
    )

    assert (
        payload[
            "phase8a_source_audit_sha256"
        ]
        == PHASE8A_SOURCE_AUDIT_SHA256
    )

    assert (
        payload[
            "method1_source_sha256"
        ]
        == _sha256(
            METHOD1_SOURCE
        )
    )


def test_json_has_no_absolute_repository_paths() -> None:
    text = JSON_OUT.read_text(
        encoding="utf-8"
    )

    assert "/home/" not in text
    assert "\\Users\\" not in text
    assert str(
        ROOT
    ) not in text


def test_markdown_preserves_exploratory_boundary() -> None:
    text = MARKDOWN_OUT.read_text(
        encoding="utf-8"
    )

    required = (
        "explicitly exploratory arithmetic quantity",
        "not a Michell construction",
        "not a tuned correction",
        "evidence",
        "intended to compensate",
    )

    for phrase in required:
        assert phrase in text


def test_module_import_boundary_excludes_plate_and_fit_modules() -> None:
    tree = ast.parse(
        MODULE_SOURCE.read_text(
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

        if isinstance(
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
        "scipy",
        "numpy",
        "optimize",
    )

    for token in forbidden:
        assert token not in joined


def test_module_does_not_import_28_point_scaffold_builder() -> None:
    source = MODULE_SOURCE.read_text(
        encoding="utf-8"
    )

    assert (
        "build_michell_28_point_scaffold"
        not in source
    )

    assert (
        "build_michell_fourteenfold_division"
        not in source
    )


def test_no_aggregate_statistics_or_significance_fields() -> None:
    payload_text = JSON_OUT.read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "p_value",
        "p-value",
        "significance",
        "goodness_of_fit",
        "aggregate_score",
        "chi_square",
    )

    for token in forbidden:
        assert token not in payload_text


def test_package_version_remains_0_7_0() -> None:
    assert (
        njg.__version__
        == "0.7.0"
    )
