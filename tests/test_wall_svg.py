from pathlib import Path
from xml.etree import ElementTree

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
    michell_outer_wall_to_svg,
    write_michell_outer_wall_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def _root() -> ElementTree.Element:
    diagram = build_core_geometry()

    return ElementTree.fromstring(
        michell_outer_wall_to_svg(diagram)
    )


def test_wall_svg_is_deterministic() -> None:
    diagram = build_core_geometry()

    first = michell_outer_wall_to_svg(diagram)
    second = michell_outer_wall_to_svg(diagram)

    assert first == second


def test_wall_svg_is_valid_xml() -> None:
    root = _root()

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "1200"
    assert root.attrib["height"] == "900"
    assert root.attrib["viewBox"] == "0 0 1200 900"


def test_wall_svg_contains_wall_polygon() -> None:
    root = _root()

    wall = root.find(
        ".//svg:polygon[@class='geometry wall-outline']",
        SVG,
    )

    assert wall is not None
    assert len(wall.attrib["points"].split()) == 12


def test_wall_svg_contains_twelve_moon_circles() -> None:
    root = _root()

    geometry = root.find(
        ".//svg:g[@id='wall-geometry']",
        SVG,
    )

    assert geometry is not None

    moons = [
        element
        for element in geometry.findall("svg:circle", SVG)
        if "moon-circle" in element.attrib.get("class", "")
    ]

    assert len(moons) == 12


def test_wall_svg_contains_tangencies_and_guides() -> None:
    root = _root()

    geometry = root.find(
        ".//svg:g[@id='wall-geometry']",
        SVG,
    )

    assert geometry is not None

    tangencies = [
        element
        for element in geometry.findall("svg:circle", SVG)
        if element.attrib.get("class") == "tangency-point"
    ]

    guides = [
        element
        for element in geometry.findall("svg:line", SVG)
        if "support-guide" in element.attrib.get("class", "")
    ]

    assert len(tangencies) == 12
    assert len(guides) == 12


def test_wall_svg_contains_eight_incidence_points() -> None:
    root = _root()

    geometry = root.find(
        ".//svg:g[@id='wall-geometry']",
        SVG,
    )

    assert geometry is not None

    incidence_points = [
        element
        for element in geometry.findall("svg:circle", SVG)
        if element.attrib.get("class") == "incidence-point"
    ]

    assert len(incidence_points) == 8


def test_wall_svg_contains_four_short_and_eight_long_labels() -> None:
    root = _root()

    labels = root.findall(
        ".//svg:g[@id='side-class-labels']/svg:text",
        SVG,
    )

    short_labels = [
        label
        for label in labels
        if label.attrib.get("data-side-class") == "short"
    ]

    long_labels = [
        label
        for label in labels
        if label.attrib.get("data-side-class") == "long"
    ]

    assert len(labels) == 12
    assert len(short_labels) == 4
    assert len(long_labels) == 8
    assert {label.text for label in short_labels} == {"S"}
    assert {label.text for label in long_labels} == {"L"}


def test_wall_svg_validation_and_file_output(
    tmp_path: Path,
) -> None:
    diagram = build_core_geometry()

    with pytest.raises(ValueError):
        michell_outer_wall_to_svg(
            diagram,
            canvas_width=900,
        )

    with pytest.raises(ValueError):
        michell_outer_wall_to_svg(
            diagram,
            canvas_height=600,
        )

    output = tmp_path / "nested" / "wall.svg"

    returned = write_michell_outer_wall_svg(
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
