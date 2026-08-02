from pathlib import Path
from xml.etree import ElementTree

import pytest

from new_jerusalem_geometry.figure12_wall_evidence_svg import (
    CANDIDATE_ORDER,
    POLAR_PIVOT_TANGENT,
    RADIAL_SUPPORT,
    REGULAR_DIRECTION_TANGENT,
    analyze_figure12_wall_evidence,
    figure12_wall_evidence_to_svg,
    write_figure12_wall_evidence_json,
    write_figure12_wall_evidence_svg,
)


SVG = {
    "svg": "http://www.w3.org/2000/svg"
}


RAW = Path(
    "data/calibration/figure12/digitisation/raw"
)


PASS_PATHS = tuple(
    RAW
    / (
        "figure12_observations_"
        f"pass-{index:02d}.csv"
    )
    for index in (
        1,
        2,
        3,
    )
)


def _report():
    return (
        analyze_figure12_wall_evidence(
            PASS_PATHS
        )
    )


def _root():
    return ElementTree.fromstring(
        figure12_wall_evidence_to_svg(
            _report()
        )
    )


def test_figure12_wall_evidence_metrics() -> None:
    report = _report()

    fits = {
        fit.candidate: fit
        for fit
        in report.fits
    }

    assert (
        fits[
            POLAR_PIVOT_TANGENT
        ].angle_rms_degrees
        == pytest.approx(
            1.019835793,
            abs=1.0e-9,
        )
    )

    assert (
        fits[
            REGULAR_DIRECTION_TANGENT
        ].angle_rms_degrees
        == pytest.approx(
            1.458881984,
            abs=1.0e-9,
        )
    )

    assert (
        fits[
            RADIAL_SUPPORT
        ].angle_rms_degrees
        == pytest.approx(
            4.755395950,
            abs=1.0e-9,
        )
    )

    assert (
        fits[
            POLAR_PIVOT_TANGENT
        ].support_rms_u
        == pytest.approx(
            0.038999406,
            abs=1.0e-9,
        )
    )

    assert (
        fits[
            REGULAR_DIRECTION_TANGENT
        ].support_rms_u
        == pytest.approx(
            0.036819219,
            abs=1.0e-9,
        )
    )

    assert (
        fits[
            RADIAL_SUPPORT
        ].support_rms_u
        == pytest.approx(
            0.032822024,
            abs=1.0e-9,
        )
    )


def test_figure12_wall_evidence_svg_is_deterministic() -> None:
    report = _report()

    assert (
        figure12_wall_evidence_to_svg(
            report
        )
        == figure12_wall_evidence_to_svg(
            report
        )
    )


def test_figure12_wall_evidence_svg_structure() -> None:
    root = _root()

    assert (
        root.tag
        == "{http://www.w3.org/2000/svg}svg"
    )

    assert (
        root.attrib["width"]
        == "1800"
    )

    assert (
        root.attrib["height"]
        == "900"
    )

    panels = [
        root.find(
            f".//svg:g[@id='panel-{index}']",
            SVG,
        )
        for index in (
            1,
            2,
            3,
        )
    ]

    assert all(
        panel is not None
        for panel in panels
    )

    assert tuple(
        panel.attrib[
            "data-candidate"
        ]
        for panel in panels
        if panel is not None
    ) == CANDIDATE_ORDER


def test_each_panel_contains_source_and_candidate_wall() -> None:
    root = _root()

    source_walls = root.findall(
        ".//svg:polygon[@class='source-wall']",
        SVG,
    )

    candidate_walls = root.findall(
        ".//svg:polygon[@class='candidate-wall']",
        SVG,
    )

    assert len(
        source_walls
    ) == 3

    assert len(
        candidate_walls
    ) == 3

    for polygon in (
        source_walls
        + candidate_walls
    ):
        assert len(
            polygon.attrib[
                "points"
            ].split()
        ) == 12


def test_figure12_wall_evidence_file_writers(
    tmp_path: Path,
) -> None:
    report = _report()

    svg_path = (
        write_figure12_wall_evidence_svg(
            report,
            tmp_path
            / "nested"
            / "comparison.svg",
        )
    )

    json_path = (
        write_figure12_wall_evidence_json(
            report,
            tmp_path
            / "nested"
            / "comparison.json",
        )
    )

    assert svg_path.exists()
    assert json_path.exists()

    assert (
        "POLAR_PIVOT_TANGENT"
        in svg_path.read_text(
            encoding="utf-8"
        )
    )

    assert (
        "POLAR_PIVOT_TANGENT"
        in json_path.read_text(
            encoding="utf-8"
        )
    )


def test_source_wall_is_drawn_above_candidate_wall() -> None:
    root = _root()

    for index in (
        1,
        2,
        3,
    ):
        geometry = root.find(
            f".//svg:g[@id='geometry-{index}']",
            SVG,
        )

        assert geometry is not None

        classes = [
            element.attrib.get(
                "class"
            )
            for element in geometry
        ]

        candidate_index = classes.index(
            "candidate-wall"
        )

        source_index = classes.index(
            "source-wall"
        )

        assert (
            candidate_index
            < source_index
        )
