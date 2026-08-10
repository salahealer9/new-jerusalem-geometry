from __future__ import annotations

import hashlib
import json
from pathlib import Path

import new_jerusalem_geometry as njg

from new_jerusalem_geometry.exact_heptagon_synthesis import (
    FIXED_PHASE_DEGREES,
    PHASE9D_COMMIT,
    PHASE9E_PROTOCOL_SHA256,
    STOPPING_STATUS,
    build_exact_heptagon_synthesis,
    synthesis_to_json,
    synthesis_to_markdown,
    synthesis_to_svg,
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
    / "v0.9_exact_heptagon_synthesis_protocol.md"
)

PHASE9D_RESULT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "one_trisection_heptagon.json"
)

PHASE9D_MARKDOWN = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_one_trisection_heptagon_result.md"
)

PLATE_INPUT = (
    ROOT
    / "data"
    / "calibration"
    / "figure14"
    / "derived"
    / "star_endpoint_geometry.csv"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_heptagon_synthesis.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_exact_heptagon_synthesis.md"
)

SVG_OUT = (
    ROOT
    / "figures"
    / "generated"
    / "v0.9_exact_heptagon_synthesis.svg"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _synthesis():
    return build_exact_heptagon_synthesis(
        root=ROOT
    )


def test_protocol_hash_is_frozen() -> None:
    assert (
        _sha256(
            PROTOCOL
        )
        == PHASE9E_PROTOCOL_SHA256
        == "8d256b7cf8eeab7903fc88386b8f16333a938993937d07f990dd98dddbc6d8b1"
    )


def test_phase9d_commit_is_bound() -> None:
    assert (
        PHASE9D_COMMIT
        == "fb111056291a478884fb2e2b340fa4bb8930a98b"
    )


def test_phase9d_result_hashes_remain_frozen() -> None:
    assert (
        _sha256(
            PHASE9D_RESULT
        )
        == "f82d8fc9307ac12cb9541f24c090500d6ac7784bb11eb673eb89c9f2cb433dad"
    )

    assert (
        _sha256(
            PHASE9D_MARKDOWN
        )
        == "87fecdcb9758d26e4d576523a541a0b1d9a17524dfe54b6e80509cbfead39471"
    )


def test_fixed_north_orientation_has_no_fit() -> None:
    synthesis = _synthesis()

    assert (
        synthesis.fixed_orientation_degrees
        == FIXED_PHASE_DEGREES
        == 90.0
    )

    assert (
        synthesis.orientation_fit_applied
        is False
    )

    dof = (
        synthesis.degrees_of_freedom
    )

    assert (
        dof.rotational_fit_parameters
        == 0
    )
    assert (
        dof.phase_optimization_parameters
        == 0
    )
    assert (
        dof.endpoint_permutation_searches
        == 0
    )
    assert (
        dof.wall_nearest_neighbor_searches
        == 0
    )
    assert (
        dof.fitted_parameters_total
        == 0
    )


def test_exact_vertices_are_north_anchored_counterclockwise() -> None:
    synthesis = _synthesis()

    expected = tuple(
        (
            90.0
            + index
            * (
                360.0
                / 7.0
            )
        )
        % 360.0
        for index in range(
            7
        )
    )

    assert len(
        synthesis.exact_vertices
    ) == 7

    for actual, target in zip(
        synthesis.exact_vertex_angles_degrees,
        expected,
        strict=True,
    ):
        delta = (
            (
                actual
                - target
                + 180.0
            )
            % 360.0
            - 180.0
        )

        assert abs(
            delta
        ) < 1.0e-12


def test_step_comparison_contains_exact_method1_method2_only() -> None:
    rows = (
        _synthesis()
        .step_comparisons
    )

    assert tuple(
        row.method_id
        for row in rows
    ) == (
        "EXACT_ONE_TRISECTION",
        "MICHELL_METHOD_1",
        "MICHELL_METHOD_2",
    )

    assert (
        rows[
            0
        ].absolute_residual_degrees
        == 0.0
    )

    assert (
        rows[
            1
        ].signed_residual_degrees
        > 0.0
    )

    assert (
        rows[
            2
        ].signed_residual_degrees
        < 0.0
    )


def test_scaffold_comparison_is_fixed_index_by_index() -> None:
    synthesis = _synthesis()

    rows = (
        synthesis
        .scaffold_vertex_comparisons
    )

    assert len(
        rows
    ) == 7

    assert tuple(
        row.vertex_index
        for row in rows
    ) == tuple(
        range(
            7
        )
    )

    assert tuple(
        row.endpoint_id
        for row in rows
    ) == tuple(
        f"scaffold_vertex_{index}"
        for index in range(
            7
        )
    )

    assert (
        synthesis.scaffold_aggregate.vertex_count
        == 7
    )


def test_plate_comparison_uses_frozen_semantic_sequence() -> None:
    synthesis = _synthesis()

    rows = (
        synthesis
        .figure14_plate_comparisons
    )

    assert len(
        rows
    ) == 7

    expected_ids = (
        "star_endpoint_00_top",
        "star_endpoint_01_upper_left",
        "star_endpoint_02_lower_left",
        "star_endpoint_03_bottom_left",
        "star_endpoint_04_bottom_right",
        "star_endpoint_05_lower_right",
        "star_endpoint_06_upper_right",
    )

    assert tuple(
        row.endpoint_id
        for row in rows
    ) == expected_ids

    assert (
        synthesis.figure14_plate_input_sha256
        == _sha256(
            PLATE_INPUT
        )
    )


def test_plate_radial_and_angular_components_are_kept_separate() -> None:
    rows = (
        _synthesis()
        .figure14_plate_comparisons
    )

    assert any(
        abs(
            row.radial_residual_u
        )
        > 0.0
        for row in rows
    )

    assert any(
        row.absolute_angular_residual_degrees
        > 0.0
        for row in rows
    )


def test_wall_is_context_only() -> None:
    context = (
        _synthesis()
        .context
    )

    assert (
        context.wall_vertex_count
        == 12
    )

    assert (
        context.incidence_moon_count
        == 12
    )

    assert (
        context.square_circle_junction_count
        == 8
    )

    assert (
        context.wall_comparison_performed
        is False
    )

    assert (
        "No nearest-neighbour"
        in context.note
    )


def test_synthesis_is_source_consistency_not_validation_claim() -> None:
    synthesis = _synthesis()

    assert (
        synthesis.interpretation_status
        == "SOURCE_CONSISTENCY_SYNTHESIS_NO_REFIT"
    )

    required = (
        "not independent validation",
        "no phase fitting",
    )

    normalized = " ".join(
        (
            synthesis.scaffold_aggregate.interpretation
            + " "
            + synthesis.figure14_plate_aggregate.interpretation
        ).split()
    )

    for phrase in required:
        assert phrase in normalized


def test_stopping_status_is_fixed() -> None:
    assert (
        _synthesis()
        .stopping_status
        == STOPPING_STATUS
        == "EXACT_HEPTAGON_SYNTHESIS_COMPLETE"
    )


def test_json_is_deterministic() -> None:
    first = (
        synthesis_to_json(
            _synthesis()
        )
    )

    second = (
        synthesis_to_json(
            _synthesis()
        )
    )

    assert first == second


def test_markdown_is_deterministic() -> None:
    first = (
        synthesis_to_markdown(
            _synthesis()
        )
    )

    second = (
        synthesis_to_markdown(
            _synthesis()
        )
    )

    assert first == second


def test_svg_is_deterministic_and_transparent() -> None:
    first = (
        synthesis_to_svg(
            _synthesis()
        )
    )

    second = (
        synthesis_to_svg(
            _synthesis()
        )
    )

    assert first == second

    assert (
        "<svg"
        in first
    )

    assert (
        "background-color"
        not in first
    )

    assert (
        'id="background"'
        not in first
    )

    assert (
        "no rotational fitting"
        in first
    )


def test_tracked_outputs_match_generation() -> None:
    synthesis = _synthesis()

    assert (
        JSON_OUT.read_text(
            encoding="utf-8"
        )
        == synthesis_to_json(
            synthesis
        )
    )

    assert (
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        )
        == synthesis_to_markdown(
            synthesis
        )
    )

    assert (
        SVG_OUT.read_text(
            encoding="utf-8"
        )
        == synthesis_to_svg(
            synthesis
        )
    )


def test_markdown_preserves_interpretation_boundary() -> None:
    text = " ".join(
        MARKDOWN_OUT.read_text(
            encoding="utf-8"
        ).split()
    )

    required = (
        "no new construction search",
        "No phase is fitted",
        "not statistically independent validation",
        "wall sevenfold comparison = none",
        "No historical knowledge or intention",
    )

    for phrase in required:
        assert phrase in text


def test_json_contains_complete_comparison_tables() -> None:
    payload = json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )

    assert len(
        payload[
            "scaffold_vertex_comparisons"
        ]
    ) == 7

    assert len(
        payload[
            "figure14_plate_comparisons"
        ]
    ) == 7

    assert len(
        payload[
            "step_comparisons"
        ]
    ) == 3


def test_package_version_remains_0_8_0() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
