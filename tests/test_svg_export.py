from pathlib import Path
from xml.etree import ElementTree
import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
    core_diagram_to_svg,
    write_core_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def test_svg_output_is_deterministic() -> None:
    diagram = build_core_geometry()

    first = core_diagram_to_svg(diagram)
    second = core_diagram_to_svg(diagram)

    assert first == second


def test_svg_is_valid_xml() -> None:
    diagram = build_core_geometry()
    svg_text = core_diagram_to_svg(diagram)

    root = ElementTree.fromstring(svg_text)

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["viewBox"] == "-9 -9 18 18"
    assert root.attrib["width"] == "900"
    assert root.attrib["height"] == "900"
    assert root.attrib["preserveAspectRatio"] == "xMidYMid meet"


def test_svg_contains_expected_objects() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(core_diagram_to_svg(diagram))

    circles = root.findall(".//svg:circle", SVG)
    rectangles = root.findall(".//svg:rect", SVG)

    assert len(circles) == 6
    assert len(rectangles) == 1

    ids = {
        element.attrib["id"]
        for element in circles + rectangles
    }

    assert ids == {
        "construction-circle",
        "earth-square",
        "earth-circle",
        "moon-east",
        "moon-north",
        "moon-west",
        "moon-south",
    }


def test_svg_coordinates_match_core_model() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(core_diagram_to_svg(diagram))

    elements = {
        element.attrib["id"]: element
        for element in root.findall(".//*[@id]")
    }

    earth = elements["earth-circle"]
    construction = elements["construction-circle"]
    square = elements["earth-square"]

    assert float(earth.attrib["cx"]) == 0.0
    assert float(earth.attrib["cy"]) == 0.0
    assert float(earth.attrib["r"]) == 5.5

    assert float(construction.attrib["r"]) == 7.0

    assert float(square.attrib["x"]) == -5.5
    assert float(square.attrib["y"]) == -5.5
    assert float(square.attrib["width"]) == 11.0
    assert float(square.attrib["height"]) == 11.0

    east = elements["moon-east"]
    north = elements["moon-north"]
    west = elements["moon-west"]
    south = elements["moon-south"]

    assert (
        float(east.attrib["cx"]),
        float(east.attrib["cy"]),
        float(east.attrib["r"]),
    ) == (7.0, 0.0, 1.5)

    assert (
        float(north.attrib["cx"]),
        float(north.attrib["cy"]),
        float(north.attrib["r"]),
    ) == (0.0, 7.0, 1.5)

    assert (
        float(west.attrib["cx"]),
        float(west.attrib["cy"]),
        float(west.attrib["r"]),
    ) == (-7.0, 0.0, 1.5)

    assert (
        float(south.attrib["cx"]),
        float(south.attrib["cy"]),
        float(south.attrib["r"]),
    ) == (0.0, -7.0, 1.5)


def test_write_core_svg_creates_parent_directories(
    tmp_path: Path,
) -> None:
    diagram = build_core_geometry()
    output = tmp_path / "nested" / "core.svg"

    returned_path = write_core_svg(diagram, output)

    assert returned_path == output
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )

def test_svg_accepts_custom_canvas_size() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        core_diagram_to_svg(
            diagram,
            canvas_size=1200,
        )
    )

    assert root.attrib["width"] == "1200"
    assert root.attrib["height"] == "1200"


def test_svg_rejects_invalid_canvas_size() -> None:
    diagram = build_core_geometry()

    import pytest

    with pytest.raises(ValueError):
        core_diagram_to_svg(
            diagram,
            canvas_size=0,
        )