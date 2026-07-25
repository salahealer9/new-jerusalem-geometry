from pathlib import Path
from xml.etree import ElementTree

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
    michell_28_point_scaffold_to_svg,
    write_michell_28_point_scaffold_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def _root() -> ElementTree.Element:
    diagram = build_core_geometry()

    return ElementTree.fromstring(
        michell_28_point_scaffold_to_svg(diagram)
    )


def test_septenary_svg_is_deterministic() -> None:
    diagram = build_core_geometry()

    first = michell_28_point_scaffold_to_svg(
        diagram
    )

    second = michell_28_point_scaffold_to_svg(
        diagram
    )

    assert first == second


def test_septenary_svg_is_valid_xml() -> None:
    root = _root()

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "1400"
    assert root.attrib["height"] == "900"
    assert root.attrib["viewBox"] == "0 0 1400 900"


def test_svg_contains_twenty_eight_role_markers() -> None:
    root = _root()

    geometry = root.find(
        ".//svg:g[@id='scaffold-geometry']",
        SVG,
    )

    assert geometry is not None

    markers = [
        element
        for element in list(geometry)
        if "scaffold-marker"
        in element.attrib.get("class", "")
    ]

    assert len(markers) == 28

    roles = [
        marker.attrib["data-role"]
        for marker in markers
    ]

    assert roles.count("moon_centre") == 12
    assert roles.count("inter_moon_gap") == 8
    assert (
        roles.count("intersection_positioner")
        == 8
    )


def test_svg_contains_twelve_scaffold_moons() -> None:
    root = _root()

    moons = root.findall(
        ".//svg:circle[@class='geometry scaffold-moon']",
        SVG,
    )

    assert len(moons) == 12


def test_svg_contains_twelve_incidence_moons() -> None:
    root = _root()

    moons = root.findall(
        ".//svg:circle[@class='geometry incidence-moon']",
        SVG,
    )

    assert len(moons) == 12


def test_svg_contains_twelve_displacement_segments() -> None:
    root = _root()

    segments = root.findall(
        ".//svg:line[@class='geometry displacement']",
        SVG,
    )

    assert len(segments) == 12


def test_svg_contains_eight_square_circle_points() -> None:
    root = _root()

    points = root.findall(
        ".//svg:circle[@class='square-circle-point']",
        SVG,
    )

    assert len(points) == 8


def test_svg_contains_magnified_displacement_inset() -> None:
    root = _root()

    inset = root.find(
        ".//svg:g[@id='displacement-inset']",
        SVG,
    )

    assert inset is not None
    assert inset.attrib["data-magnification"] == "40"


def test_svg_validation_and_file_output(
    tmp_path: Path,
) -> None:
    diagram = build_core_geometry()

    with pytest.raises(ValueError):
        michell_28_point_scaffold_to_svg(
            diagram,
            canvas_width=1100,
        )

    with pytest.raises(ValueError):
        michell_28_point_scaffold_to_svg(
            diagram,
            canvas_height=700,
        )

    with pytest.raises(ValueError):
        michell_28_point_scaffold_to_svg(
            diagram,
            displacement_magnification=0.0,
        )

    output = tmp_path / "nested" / "scaffold.svg"

    returned = write_michell_28_point_scaffold_svg(
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
