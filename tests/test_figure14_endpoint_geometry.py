import json
from math import cos, pi, sin
from pathlib import Path

import pytest

from new_jerusalem_geometry.figure14_endpoint_geometry import (
    TOPOLOGY_IDENTIFIABILITY_STATEMENT,
    analyze_star_endpoint_points,
    fit_canonical_origin_radius7,
    fit_free_regular_seven_vertices,
    fit_origin_radius7_with_free_phase,
    write_endpoint_geometry_csv,
    write_endpoint_geometry_json,
    write_endpoint_geometry_markdown,
)


def _regular_points(
    *,
    centre_x: float,
    centre_y: float,
    radius: float,
    phase: float,
) -> tuple[tuple[float, float], ...]:
    return tuple(
        (
            centre_x
            + radius
            * cos(
                phase
                + index
                * 2.0
                * pi
                / 7.0
            ),
            centre_y
            + radius
            * sin(
                phase
                + index
                * 2.0
                * pi
                / 7.0
            ),
        )
        for index in range(7)
    )


def test_free_regular_fit_recovers_exact_geometry() -> None:
    points = _regular_points(
        centre_x=0.25,
        centre_y=-0.40,
        radius=7.15,
        phase=1.17,
    )

    fit = fit_free_regular_seven_vertices(
        points
    )

    assert fit.centre_x == pytest.approx(
        0.25,
        abs=1.0e-12,
    )

    assert fit.centre_y == pytest.approx(
        -0.40,
        abs=1.0e-12,
    )

    assert fit.radius == pytest.approx(
        7.15,
        abs=1.0e-12,
    )

    assert fit.rms_residual < 1.0e-12
    assert fit.maximum_residual < 1.0e-12


def test_origin_radius7_fit_recovers_phase() -> None:
    phase = 1.31

    points = _regular_points(
        centre_x=0.0,
        centre_y=0.0,
        radius=7.0,
        phase=phase,
    )

    fit = fit_origin_radius7_with_free_phase(
        points
    )

    assert fit.phase_degrees == pytest.approx(
        phase * 180.0 / pi,
        abs=1.0e-12,
    )

    assert fit.rms_residual < 1.0e-12


def test_canonical_fit_is_exact_for_top_vertex() -> None:
    points = _regular_points(
        centre_x=0.0,
        centre_y=0.0,
        radius=7.0,
        phase=pi / 2.0,
    )

    fit = fit_canonical_origin_radius7(
        points
    )

    assert fit.phase_degrees == pytest.approx(
        90.0,
        abs=1.0e-12,
    )

    assert fit.rms_residual < 1.0e-12
    assert fit.angular_rms_degrees < 1.0e-12


def test_endpoint_report_preserves_topology_boundary() -> None:
    points = _regular_points(
        centre_x=0.0,
        centre_y=0.0,
        radius=7.0,
        phase=pi / 2.0,
    )

    report = analyze_star_endpoint_points(
        points=points,
        mean_pixels_per_unit=70.0,
        registration_loo_rms_pixels=2.5,
    )

    assert (
        report.topology_identifiability_statement
        == TOPOLOGY_IDENTIFIABILITY_STATEMENT
    )

    assert "{7/2}" in (
        report.topology_identifiability_statement
    )

    assert "{7/3}" in (
        report.topology_identifiability_statement
    )

    assert (
        report.free_fit_rms_fraction_of_registration_loo
        < 1.0e-10
    )


def test_endpoint_geometry_writers(
    tmp_path: Path,
) -> None:
    points = _regular_points(
        centre_x=0.01,
        centre_y=-0.02,
        radius=7.01,
        phase=pi / 2.0 + 0.002,
    )

    report = analyze_star_endpoint_points(
        points=points,
        click_rms_normalized=(
            0.005,
        ) * 7,
        pass_registered_rms_normalized=(
            0.006,
        ) * 7,
        mean_pixels_per_unit=71.5,
        registration_loo_rms_pixels=2.55,
    )

    csv_path = write_endpoint_geometry_csv(
        tmp_path / "endpoints.csv",
        report,
    )

    json_path = write_endpoint_geometry_json(
        tmp_path / "summary.json",
        report,
    )

    markdown_path = (
        write_endpoint_geometry_markdown(
            tmp_path / "report.md",
            report,
        )
    )

    assert csv_path.exists()
    assert json_path.exists()
    assert markdown_path.exists()

    payload = json.loads(
        json_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["endpoint_count"] == 7

    assert (
        payload["topology_identifiability"][
            "vertex_set_distinguishes_7_2_from_7_3"
        ]
        is False
    )

    text = markdown_path.read_text(
        encoding="utf-8"
    )

    assert "Regular seven-vertex fits" in text
    assert "Topology boundary" in text
    assert "cannot by itself establish" in text
