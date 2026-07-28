from pathlib import Path
from xml.etree import ElementTree

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
    michell_figure14_heptagram_to_svg,
    write_michell_figure14_heptagram_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def _root() -> ElementTree.Element:
    diagram = build_core_geometry()

    return ElementTree.fromstring(
        michell_figure14_heptagram_to_svg(
            diagram
        )
    )


def test_figure14_svg_is_deterministic() -> None:
    diagram = build_core_geometry()

    first = michell_figure14_heptagram_to_svg(
        diagram
    )

    second = michell_figure14_heptagram_to_svg(
        diagram
    )

    assert first == second


def test_figure14_svg_is_valid_xml() -> None:
    root = _root()

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "1600"
    assert root.attrib["height"] == "920"
    assert root.attrib["viewBox"] == "0 0 1600 920"


def test_figure14_svg_contains_three_panels() -> None:
    root = _root()

    panels = [
        root.find(f".//svg:g[@id='panel-{index}']", SVG)
        for index in range(3)
    ]

    assert all(panel is not None for panel in panels)


def test_figure14_svg_contains_twenty_one_star_edges() -> None:
    root = _root()

    edges = root.findall(
        ".//svg:line[@class='geometry star-edge']",
        SVG,
    )

    assert len(edges) == 21


def test_figure14_svg_contains_twenty_one_candidate_vertices() -> None:
    root = _root()

    vertices = [
        element
        for element in root.findall(
            ".//svg:circle[@class='candidate-vertex']",
            SVG,
        )
        if "data-panel" in element.attrib
    ]

    assert len(vertices) == 21


def test_figure14_svg_contains_candidate_legend_symbol() -> None:
    root = _root()

    vertices = root.findall(
        ".//svg:circle[@class='candidate-vertex']",
        SVG,
    )

    legend_vertices = [
        element
        for element in vertices
        if "data-panel" not in element.attrib
    ]

    assert len(legend_vertices) == 1


def test_figure14_svg_repeats_anchor_evidence() -> None:
    root = _root()

    stated = root.findall(
        ".//svg:circle[@class='anchor-marker stated-anchor']",
        SVG,
    )

    inferred = root.findall(
        ".//svg:polygon[@class='anchor-marker inferred-anchor']",
        SVG,
    )

    assert len(stated) == 15
    assert len(inferred) == 6


def test_figure14_svg_contains_twenty_one_residuals() -> None:
    root = _root()

    residuals = root.findall(
        ".//svg:line[@class='geometry residual-vector']",
        SVG,
    )

    assert len(residuals) == 21


def test_figure14_svg_contains_thirty_six_moon_circles() -> None:
    root = _root()

    moons = root.findall(
        ".//svg:circle[@class='geometry incidence-moon']",
        SVG,
    )

    assert len(moons) == 36


def test_figure14_svg_validation_and_file_output(
    tmp_path: Path,
) -> None:
    diagram = build_core_geometry()

    with pytest.raises(ValueError):
        michell_figure14_heptagram_to_svg(
            diagram,
            canvas_width=1400,
        )

    with pytest.raises(ValueError):
        michell_figure14_heptagram_to_svg(
            diagram,
            canvas_height=800,
        )

    output = tmp_path / "nested" / "figure14.svg"

    returned = write_michell_figure14_heptagram_svg(
        diagram,
        output,
    )

    assert returned == output
    assert output.exists()
    assert output.read_text(
        encoding="utf-8"
    ).startswith(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )


def test_figure14_svg_uses_source_supported_step2_labels() -> None:
    diagram = build_core_geometry()

    svg = michell_figure14_heptagram_to_svg(
        diagram
    )

    assert "Heptagram family: {7/2}" in svg
    assert "Exact regular {7/2}" in svg
    assert "Michell 28-point {7/2}" in svg
    assert "Figure-14-aligned {7/2}" in svg
    assert "candidate {7/2}" in svg


def test_figure14_svg_does_not_present_step3_as_canonical() -> None:
    diagram = build_core_geometry()

    svg = michell_figure14_heptagram_to_svg(
        diagram
    )

    assert "Heptagram family: {7/3}" not in svg
    assert "Exact regular {7/3}" not in svg
    assert "Figure-14-aligned {7/3}" not in svg
