from __future__ import annotations

import ast
import hashlib
import json
from math import (
    pi,
    sqrt,
    tau,
)
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.method2_propagation import (
    GAMMA_0_RADIANS,
    IDENTITY_TOLERANCE_RADIANS,
    METHOD2_SOURCE_SHA256,
    PHASE8C_COMMIT,
    PHASE8C_LOCAL_COMPARISON_SHA256,
    PHASE8D_COMMIT,
    PROTOCOL_SHA256,
    STOPPING_STATUS,
    build_method2_propagation,
    method2_propagation_to_json,
    method2_propagation_to_markdown,
)
from new_jerusalem_geometry.sevenfold_dual_method import (
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
    / "v0.8_method2_propagation_protocol.md"
)

PHASE8C_MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "sevenfold_dual_method.py"
)

PHASE8C_JSON = (
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
    / "method2_propagation.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_method2_propagation_result.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _result():
    return build_method2_propagation()


def _payload() -> dict:
    return json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )


def _circular_distance(
    first: float,
    second: float,
) -> float:
    raw = abs(
        (
            first
            % tau
        )
        - (
            second
            % tau
        )
    )

    return min(
        raw,
        tau - raw,
    )


def _angles_match_under_rotation(
    source,
    target,
    rotation: float,
) -> bool:
    used: set[int] = set()

    for source_point in source:
        angle = (
            source_point.angle_radians
            + rotation
        ) % tau

        matches = [
            index
            for index, target_point
            in enumerate(
                target
            )
            if (
                index
                not in used
                and _circular_distance(
                    angle,
                    target_point.angle_radians,
                )
                <= IDENTITY_TOLERANCE_RADIANS
            )
        ]

        if len(
            matches
        ) != 1:
            return False

        used.add(
            matches[
                0
            ]
        )

    return (
        len(
            used
        )
        == len(
            target
        )
    )


def test_frozen_protocol_hash() -> None:
    assert (
        _sha256(
            PROTOCOL
        )
        == PROTOCOL_SHA256
        == "b87b6c54f6084d549236a7f27b336d396a980b1404337f751862a8e5476217c1"
    )


def test_phase8d_commit_is_frozen() -> None:
    assert (
        PHASE8D_COMMIT
        == "11b023e"
    )


def test_phase8c_commit_is_frozen() -> None:
    assert (
        PHASE8C_COMMIT
        == "05e8a89"
    )


def test_frozen_phase8c_method2_source_hash() -> None:
    assert (
        _sha256(
            PHASE8C_MODULE
        )
        == METHOD2_SOURCE_SHA256
        == "33c5fee3a1d198abc1eb73c1ff114829b1dc5a66f0e355605ed25793b33f5c70"
    )


def test_frozen_phase8c_local_comparison_hash() -> None:
    assert (
        _sha256(
            PHASE8C_JSON
        )
        == PHASE8C_LOCAL_COMPARISON_SHA256
        == "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f"
    )


def test_alpha2_is_reused_from_frozen_phase8c_implementation() -> None:
    result = _result()

    assert (
        result.alpha_2_radians
        == method_2_step_from_source_geometry()
    )


def test_global_phase_is_exactly_pi_over_two() -> None:
    result = _result()

    assert (
        result.gamma_0_radians
        == GAMMA_0_RADIANS
        == pi / 2.0
    )


def test_identity_tolerance_is_exactly_registered_value() -> None:
    result = _result()

    assert (
        result.identity_tolerance_radians
        == IDENTITY_TOLERANCE_RADIANS
        == 1.0e-12
    )


def test_local_seven_has_exact_semantic_k_inventory() -> None:
    result = _result()

    points = (
        result.local_seven
        .sorted_points
    )

    assert (
        result.local_seven
        .semantic_count
        == 7
    )

    assert (
        sorted(
            point.local_k
            for point in points
        )
        == list(
            range(
                -3,
                4,
            )
        )
    )

    assert len(
        result.local_seven
        .cyclic_gaps
    ) == 7


def test_twenty_one_semantic_inventory_is_exact() -> None:
    result = _result()

    points = (
        result.twenty_one
        .sorted_points
    )

    assert (
        result.twenty_one
        .semantic_count
        == 21
    )

    inventory = {
        (
            point.carrier_index,
            point.local_k,
        )
        for point in points
    }

    expected = {
        (
            carrier,
            local_k,
        )
        for carrier in range(
            3
        )
        for local_k in range(
            -3,
            4,
        )
    }

    assert inventory == expected


def test_s1_twenty_one_distinctness_is_recomputed() -> None:
    result = _result()

    points = (
        result.twenty_one
        .sorted_points
    )

    collision_count = 0

    for left in range(
        len(
            points
        )
    ):
        for right in range(
            left + 1,
            len(
                points
            ),
        ):
            if (
                _circular_distance(
                    points[
                        left
                    ].angle_radians,
                    points[
                        right
                    ].angle_radians,
                )
                <= IDENTITY_TOLERANCE_RADIANS
            ):
                collision_count += 1

    expected_distinct = (
        collision_count
        == 0
    )

    assert (
        result.twenty_one_structural_checks
        .all_semantic_marks_numerically_distinct
        is expected_distinct
    )

    if expected_distinct:
        assert (
            result.twenty_one
            .numerical_distinct_count
            == 21
        )


def test_s2_twenty_one_rotation_identity_is_recomputed() -> None:
    result = _result()

    points = (
        result.twenty_one
        .sorted_points
    )

    expected = (
        _angles_match_under_rotation(
            points,
            points,
            2.0
            * pi
            / 3.0,
        )
    )

    assert (
        result.twenty_one_structural_checks
        .rotational_identity_2pi_over_3
        is expected
    )


def test_reciprocal_twenty_one_has_exact_inventory() -> None:
    result = _result()

    reciprocal = (
        result.reciprocal_twenty_one
        .sorted_points
    )

    assert (
        result.reciprocal_twenty_one
        .semantic_count
        == 21
    )

    assert {
        point.carrier_index
        for point in reciprocal
    } == {
        1,
        3,
        5,
    }

    assert all(
        point.carrier_family
        == "reciprocal"
        for point in reciprocal
    )


def test_s3_reciprocal_rotation_identity_is_recomputed() -> None:
    result = _result()

    original = (
        result.twenty_one
        .sorted_points
    )

    reciprocal = (
        result.reciprocal_twenty_one
        .sorted_points
    )

    expected = (
        _angles_match_under_rotation(
            original,
            reciprocal,
            pi / 3.0,
        )
    )

    assert (
        result.reciprocal_twenty_one
        .rotated_original_identity_pi_over_3
        is expected
    )


def test_forty_two_semantic_inventory_is_exact() -> None:
    result = _result()

    points = (
        result.forty_two
        .sorted_points
    )

    assert (
        result.forty_two
        .semantic_count
        == 42
    )

    inventory = {
        (
            point.carrier_index,
            point.local_k,
        )
        for point in points
    }

    expected = {
        (
            carrier,
            local_k,
        )
        for carrier in range(
            6
        )
        for local_k in range(
            -3,
            4,
        )
    }

    assert inventory == expected


def test_s1_forty_two_distinctness_is_recomputed() -> None:
    result = _result()

    points = (
        result.forty_two
        .sorted_points
    )

    collision_count = 0

    for left in range(
        len(
            points
        )
    ):
        for right in range(
            left + 1,
            len(
                points
            ),
        ):
            if (
                _circular_distance(
                    points[
                        left
                    ].angle_radians,
                    points[
                        right
                    ].angle_radians,
                )
                <= IDENTITY_TOLERANCE_RADIANS
            ):
                collision_count += 1

    expected_distinct = (
        collision_count
        == 0
    )

    assert (
        result.forty_two_structural_checks
        .all_semantic_marks_numerically_distinct
        is expected_distinct
    )

    if expected_distinct:
        assert (
            result.forty_two
            .numerical_distinct_count
            == 42
        )


def test_s4_union_identity_is_recomputed() -> None:
    result = _result()

    original = (
        result.twenty_one
        .sorted_points
    )

    reciprocal = (
        result.reciprocal_twenty_one
        .sorted_points
    )

    combined = (
        tuple(
            original
        )
        + tuple(
            reciprocal
        )
    )

    expected = (
        _angles_match_under_rotation(
            combined,
            result.forty_two.sorted_points,
            0.0,
        )
    )

    assert (
        result.forty_two_structural_checks
        .union_identity
        is expected
    )


def test_s5_forty_two_rotation_identity_is_recomputed() -> None:
    result = _result()

    points = (
        result.forty_two
        .sorted_points
    )

    expected = (
        _angles_match_under_rotation(
            points,
            points,
            pi / 3.0,
        )
    )

    assert (
        result.forty_two_structural_checks
        .rotational_identity_pi_over_3
        is expected
    )


def _check_gap_metrics(
    point_set,
    expected_count: int,
) -> None:
    gaps = (
        point_set
        .cyclic_gaps
    )

    assert len(
        gaps
    ) == expected_count

    regular = (
        tau
        / expected_count
    )

    assert (
        point_set
        .regular_gap_radians
        == regular
    )

    raw = [
        gap.gap_radians
        for gap in gaps
    ]

    signed = [
        gap.gap_radians
        - regular
        for gap in gaps
    ]

    absolute = [
        abs(
            value
        )
        for value in signed
    ]

    for gap, residual, abs_residual in zip(
        gaps,
        signed,
        absolute,
        strict=True,
    ):
        assert (
            gap.signed_gap_residual_radians
            == residual
        )

        assert (
            gap.absolute_gap_residual_radians
            == abs_residual
        )

    assert (
        point_set.minimum_gap_radians
        == min(
            raw
        )
    )

    assert (
        point_set.maximum_gap_radians
        == max(
            raw
        )
    )

    assert (
        point_set.mean_gap_radians
        == sum(
            raw
        )
        / expected_count
    )

    assert (
        point_set.gap_range_radians
        == max(
            raw
        )
        - min(
            raw
        )
    )

    rms = sqrt(
        sum(
            value
            * value
            for value in signed
        )
        / expected_count
    )

    assert (
        point_set
        .rms_gap_residual_radians
        == rms
    )

    assert (
        point_set
        .maximum_absolute_gap_residual_radians
        == max(
            absolute
        )
    )

    assert (
        point_set
        .normalized_rms_gap_residual
        == rms
        / regular
    )

    assert (
        abs(
            sum(
                raw
            )
            - tau
        )
        <= IDENTITY_TOLERANCE_RADIANS
    )


def test_twenty_one_gap_metrics_are_recomputed() -> None:
    _check_gap_metrics(
        _result().twenty_one,
        21,
    )


def test_forty_two_gap_metrics_are_recomputed() -> None:
    _check_gap_metrics(
        _result().forty_two,
        42,
    )


def test_regularity_classification_uses_only_registered_identity_tolerance() -> None:
    result = _result()

    for point_set in (
        result.twenty_one,
        result.forty_two,
    ):
        expected = (
            point_set
            .maximum_absolute_gap_residual_radians
            <= IDENTITY_TOLERANCE_RADIANS
        )

        assert (
            point_set
            .numerically_regular_at_identity_tolerance
            is expected
        )


def test_registered_rms_ratio_is_recomputed() -> None:
    result = _result()

    denominator = (
        result.twenty_one
        .rms_gap_residual_radians
    )

    if denominator == 0.0:
        assert (
            result.comparison
            .rms_ratio_42_over_21
            is None
        )
    else:
        assert (
            result.comparison
            .rms_ratio_42_over_21
            == (
                result.forty_two
                .rms_gap_residual_radians
                / denominator
            )
        )


def test_registered_max_abs_ratio_is_recomputed() -> None:
    result = _result()

    denominator = (
        result.twenty_one
        .maximum_absolute_gap_residual_radians
    )

    if denominator == 0.0:
        assert (
            result.comparison
            .max_abs_ratio_42_over_21
            is None
        )
    else:
        assert (
            result.comparison
            .max_abs_ratio_42_over_21
            == (
                result.forty_two
                .maximum_absolute_gap_residual_radians
                / denominator
            )
        )


def _expected_order(
    twenty_one: float,
    forty_two: float,
):
    if twenty_one < forty_two:
        return (
            "twenty_one",
            "forty_two",
        )

    if forty_two < twenty_one:
        return (
            "forty_two",
            "twenty_one",
        )

    return "TIE"


def test_registered_orderings_use_raw_metrics() -> None:
    result = _result()

    assert (
        result.comparison.rms_order
        == _expected_order(
            result.twenty_one
            .rms_gap_residual_radians,
            result.forty_two
            .rms_gap_residual_radians,
        )
    )

    assert (
        result.comparison
        .maximum_absolute_residual_order
        == _expected_order(
            result.twenty_one
            .maximum_absolute_gap_residual_radians,
            result.forty_two
            .maximum_absolute_gap_residual_radians,
        )
    )


def test_zero_fit_degrees_of_freedom() -> None:
    dof = (
        _result()
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
        dof.optimized_phase_parameters
        == 0
    )

    assert (
        dof.fitted_deduplication_thresholds
        == 0
    )


def test_stopping_status_is_fixed() -> None:
    assert (
        _result().stopping_status
        == STOPPING_STATUS
        == "METHOD2_7_21_42_PROPAGATION_COMPLETE"
    )


def test_json_is_deterministic() -> None:
    assert (
        method2_propagation_to_json(
            _result()
        )
        == method2_propagation_to_json(
            _result()
        )
    )


def test_markdown_is_deterministic() -> None:
    assert (
        method2_propagation_to_markdown(
            _result()
        )
        == method2_propagation_to_markdown(
            _result()
        )
    )


def test_tracked_json_matches_generation() -> None:
    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == method2_propagation_to_json(
            _result()
        )
    )


def test_tracked_markdown_matches_generation() -> None:
    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == method2_propagation_to_markdown(
            _result()
        )
    )


def test_json_has_required_frozen_provenance() -> None:
    payload = _payload()

    assert (
        payload[
            "protocol_sha256"
        ]
        == PROTOCOL_SHA256
    )

    assert (
        payload[
            "phase8d_commit"
        ]
        == PHASE8D_COMMIT
    )

    assert (
        payload[
            "phase8c_commit"
        ]
        == PHASE8C_COMMIT
    )

    assert (
        payload[
            "phase8c_local_comparison_sha256"
        ]
        == PHASE8C_LOCAL_COMPARISON_SHA256
    )

    assert (
        payload[
            "method2_source_sha256"
        ]
        == METHOD2_SOURCE_SHA256
    )


def test_json_contains_no_absolute_machine_paths() -> None:
    text = JSON_OUT.read_text(
        encoding="utf-8"
    )

    assert "/home/" not in text
    assert "\\Users\\" not in text
    assert str(
        ROOT
    ) not in text


def test_module_import_boundary_is_method2_only() -> None:
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
        "michell_composite",
        "numpy",
        "scipy",
        "optimize",
    )

    for token in forbidden:
        assert token not in joined


def test_module_does_not_import_method1_scaffold_builders() -> None:
    source = MODULE.read_text(
        encoding="utf-8"
    )

    forbidden = (
        "build_michell_28_point_scaffold",
        "build_michell_fourteenfold_division",
        "build_michell_sevenfold_division",
        "michell_four_triangle_division_angles",
    )

    for token in forbidden:
        assert token not in source


def test_no_proximity_deduplication_or_fit_vocabulary_in_payload() -> None:
    text = JSON_OUT.read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "fitted_phase",
        "optimized_gamma",
        "deduplicated_points",
        "p_value",
        "p-value",
        "significance",
        "aggregate_score",
    )

    for token in forbidden:
        assert token not in text


def test_markdown_preserves_interpretation_boundary() -> None:
    text = MARKDOWN_OUT.read_text(
        encoding="utf-8"
    )

    required = (
        "descriptive only",
        "No direction of improvement",
        "does not establish historical intent",
        "Comparison with the Method 1 28-point geometry remains",
        "explicitly deferred",
    )

    for phrase in required:
        assert phrase in text


def test_package_version_is_0_8_0_at_release_closeout() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
