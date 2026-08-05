from __future__ import annotations

import inspect
from pathlib import Path
import subprocess

import pytest

from new_jerusalem_geometry.forward_validation import (
    EXPECTED_VALIDATION_INPUT_SHA256,
    FIGURE12_POLAR_WALL_IDS,
    FIGURE14_ENDPOINT_ORDER,
    FIGURE14_INFERRED_ENDPOINTS,
    FIGURE14_SOURCE_SUPPORTED_ENDPOINTS,
    FROZEN_PREDICTOR_COMMIT,
    FROZEN_PREDICTOR_PATHS,
    analyze_forward_validation,
    verify_validation_input_hashes,
)
from new_jerusalem_geometry.heptagram_geometry import (
    build_regular_heptagram,
)
from new_jerusalem_geometry.michell_composite import (
    build_michell_composite,
)


ROOT = Path(__file__).resolve().parents[1]


def test_validation_inputs_match_preregistered_hashes() -> None:
    hashes = dict(
        verify_validation_input_hashes(
            ROOT
        )
    )

    assert (
        hashes
        == EXPECTED_VALIDATION_INPUT_SHA256
    )


def test_frozen_predictor_sources_remain_unchanged() -> None:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            FROZEN_PREDICTOR_COMMIT,
            "--",
            *FROZEN_PREDICTOR_PATHS,
        ],
        cwd=ROOT,
        check=False,
    )

    assert result.returncode == 0


def test_figure12_uses_fixed_semantic_correspondence() -> None:
    report = analyze_forward_validation(
        ROOT
    )

    figure12 = report.figure12

    assert figure12.wall_side_count == 12
    assert figure12.polar_side_count == 4
    assert figure12.oblique_side_count == 8

    assert {
        row.wall_id
        for row in figure12.line_residuals
    } == {
        row.wall_id
        for row in figure12.side_residuals
    }

    assert {
        row.wall_id
        for row in figure12.line_residuals
    } == set(
        (
            "wall_east",
            "wall_east_north",
            "wall_north_east",
            "wall_north",
            "wall_north_west",
            "wall_west_north",
            "wall_west",
            "wall_west_south",
            "wall_south_west",
            "wall_south",
            "wall_south_east",
            "wall_east_south",
        )
    )

    assert {
        row.wall_id
        for row in figure12.line_residuals
        if (
            row.wall_id
            in FIGURE12_POLAR_WALL_IDS
        )
    } == set(
        FIGURE12_POLAR_WALL_IDS
    )

    assert len(
        figure12.vertex_residuals
    ) == 12


def test_figure14_uses_fixed_endpoint_order_and_evidence_partition() -> None:
    report = analyze_forward_validation(
        ROOT
    )

    figure14 = report.figure14

    scaffold = (
        figure14.scaffold_candidate
    )

    assert tuple(
        row.landmark_id
        for row in scaffold.vertex_residuals
    ) == FIGURE14_ENDPOINT_ORDER

    assert (
        figure14.endpoint_count
        == 7
    )

    assert (
        figure14.source_supported_endpoint_count
        == 5
    )

    assert (
        figure14.inferred_endpoint_count
        == 2
    )

    assert {
        row.landmark_id
        for row in scaffold.vertex_residuals
        if (
            row.evidence_class
            == "source_text_and_plate"
        )
    } == set(
        FIGURE14_SOURCE_SUPPORTED_ENDPOINTS
    )

    assert {
        row.landmark_id
        for row in scaffold.vertex_residuals
        if (
            row.evidence_class
            == "plate_inference"
        )
    } == set(
        FIGURE14_INFERRED_ENDPOINTS
    )


def test_figure14_predictions_are_unmodified_frozen_vertices() -> None:
    report = analyze_forward_validation(
        ROOT
    )

    composite = (
        build_michell_composite()
    )

    scaffold_rows = (
        report
        .figure14
        .scaffold_candidate
        .vertex_residuals
    )

    for row, vertex in zip(
        scaffold_rows,
        composite
        .scaffold_heptagram_candidate
        .vertices,
        strict=True,
    ):
        assert (
            row.predicted_x_u
            == pytest.approx(
                vertex.x,
                abs=1.0e-15,
            )
        )

        assert (
            row.predicted_y_u
            == pytest.approx(
                vertex.y,
                abs=1.0e-15,
            )
        )

    canonical = (
        build_regular_heptagram(
            composite.core,
            family=(
                composite
                .scaffold_heptagram_candidate
                .family
            ),
        )
    )

    canonical_rows = (
        report
        .figure14
        .canonical_regular
        .vertex_residuals
    )

    for row, vertex in zip(
        canonical_rows,
        canonical.vertices,
        strict=True,
    ):
        assert (
            row.predicted_x_u
            == pytest.approx(
                vertex.x,
                abs=1.0e-15,
            )
        )

        assert (
            row.predicted_y_u
            == pytest.approx(
                vertex.y,
                abs=1.0e-15,
            )
        )


def test_validation_api_exposes_no_geometric_fit_parameters() -> None:
    signature = inspect.signature(
        analyze_forward_validation
    )

    assert tuple(
        signature.parameters
    ) == (
        "repo_root",
    )


def test_forward_validation_is_deterministic() -> None:
    first = analyze_forward_validation(
        ROOT
    )

    second = analyze_forward_validation(
        ROOT
    )

    assert first == second


def test_frozen_figure12_forward_validation_metrics() -> None:
    report = analyze_forward_validation(
        ROOT
    )

    result = report.figure12

    assert result.angle_rms_degrees == pytest.approx(
        1.019835793,
        abs=1.0e-9,
    )

    assert result.angle_maximum_degrees == pytest.approx(
        2.062522195,
        abs=1.0e-9,
    )

    assert result.support_rms_u == pytest.approx(
        0.038999406,
        abs=1.0e-9,
    )

    assert result.support_maximum_u == pytest.approx(
        0.072467862,
        abs=1.0e-9,
    )

    assert result.vertex_rms_u == pytest.approx(
        0.100021612,
        abs=1.0e-9,
    )

    assert result.vertex_maximum_u == pytest.approx(
        0.162698870,
        abs=1.0e-9,
    )

    assert result.side_length_rms_u == pytest.approx(
        0.142495117,
        abs=1.0e-9,
    )

    assert result.predicted_perimeter_u == pytest.approx(
        54.566330097384,
        abs=1.0e-12,
    )

    assert result.source_perimeter_u == pytest.approx(
        54.77399703826629,
        abs=1.0e-12,
    )

    assert result.perimeter_relative_residual == pytest.approx(
        -0.00379134,
        abs=1.0e-8,
    )

    assert result.predicted_area_u2 == pytest.approx(
        231.486496089401,
        abs=1.0e-12,
    )

    assert result.source_area_u2 == pytest.approx(
        233.14023443980977,
        abs=1.0e-12,
    )

    assert result.area_relative_residual == pytest.approx(
        -0.00709332,
        abs=1.0e-8,
    )


def test_frozen_figure14_forward_validation_metrics() -> None:
    report = analyze_forward_validation(
        ROOT
    )

    scaffold = (
        report.figure14.scaffold_candidate
    )

    canonical = (
        report.figure14.canonical_regular
    )

    assert scaffold.point_rms_u == pytest.approx(
        0.031023606,
        abs=1.0e-9,
    )

    assert canonical.point_rms_u == pytest.approx(
        0.031953847,
        abs=1.0e-9,
    )

    assert scaffold.point_maximum_u == pytest.approx(
        0.049325681,
        abs=1.0e-9,
    )

    assert canonical.point_maximum_u == pytest.approx(
        0.059258803,
        abs=1.0e-9,
    )

    assert scaffold.angular_rms_degrees == pytest.approx(
        0.215205853,
        abs=1.0e-9,
    )

    assert canonical.angular_rms_degrees == pytest.approx(
        0.224058789,
        abs=1.0e-9,
    )

    assert scaffold.radial_rms_u == pytest.approx(
        canonical.radial_rms_u,
        abs=1.0e-12,
    )

    assert scaffold.point_rms_fraction_of_registration_loo == pytest.approx(
        0.871259992,
        abs=1.0e-9,
    )

    assert canonical.point_rms_fraction_of_registration_loo == pytest.approx(
        0.897384694,
        abs=1.0e-9,
    )

    assert scaffold.source_supported_point_rms_u == pytest.approx(
        0.023288890,
        abs=1.0e-9,
    )

    assert canonical.source_supported_point_rms_u == pytest.approx(
        0.023451831,
        abs=1.0e-9,
    )

    assert scaffold.inferred_point_rms_u == pytest.approx(
        0.044863052,
        abs=1.0e-9,
    )

    assert canonical.inferred_point_rms_u == pytest.approx(
        0.046890280,
        abs=1.0e-9,
    )

    assert (
        report.figure14.scaffold_minus_canonical_point_rms_u
        == pytest.approx(
            -0.000930242,
            abs=1.0e-9,
        )
    )

    assert (
        report.figure14.scaffold_minus_canonical_point_maximum_u
        == pytest.approx(
            -0.009933122,
            abs=1.0e-9,
        )
    )
