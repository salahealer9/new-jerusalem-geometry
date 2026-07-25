from pathlib import Path
from xml.etree import ElementTree

import pytest

from new_jerusalem_geometry import (
    ObliqueModel,
    build_core_geometry,
    oblique_models_comparison_to_svg,
    write_oblique_models_comparison_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def test_comparison_svg_is_deterministic() -> None:
    diagram = build_core_geometry()

    first = oblique_models_comparison_to_svg(diagram)
    second = oblique_models_comparison_to_svg(diagram)

    assert first == second


def test_comparison_svg_is_valid_xml() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        oblique_models_comparison_to_svg(diagram)
    )

    assert root.tag == "{http://www.w3.org/2000/svg}svg"
    assert root.attrib["width"] == "1800"
    assert root.attrib["height"] == "720"
    assert root.attrib["viewBox"] == "0 0 1800 720"


def test_comparison_contains_three_model_panels() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        oblique_models_comparison_to_svg(diagram)
    )

    for model in ObliqueModel:
        panel = root.find(
            f".//svg:g[@id='panel-{model.value}']",
            SVG,
        )
        geometry = root.find(
            f".//svg:g[@id='geometry-{model.value}']",
            SVG,
        )

        assert panel is not None
        assert geometry is not None


def test_each_panel_contains_eight_oblique_moons() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        oblique_models_comparison_to_svg(diagram)
    )

    for model in ObliqueModel:
        geometry = root.find(
            f".//svg:g[@id='geometry-{model.value}']",
            SVG,
        )

        assert geometry is not None

        oblique_moons = [
            element
            for element in geometry.findall("svg:circle", SVG)
            if "oblique-moon" in element.attrib.get("class", "")
        ]

        assert len(oblique_moons) == 8


def test_each_panel_contains_four_cardinal_moons() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        oblique_models_comparison_to_svg(diagram)
    )

    for model in ObliqueModel:
        geometry = root.find(
            f".//svg:g[@id='geometry-{model.value}']",
            SVG,
        )

        assert geometry is not None

        cardinal_moons = [
            element
            for element in geometry.findall("svg:circle", SVG)
            if "cardinal-moon" in element.attrib.get("class", "")
        ]

        assert len(cardinal_moons) == 4


def test_each_panel_contains_eight_targets_and_guides() -> None:
    diagram = build_core_geometry()
    root = ElementTree.fromstring(
        oblique_models_comparison_to_svg(diagram)
    )

    for model in ObliqueModel:
        geometry = root.find(
            f".//svg:g[@id='geometry-{model.value}']",
            SVG,
        )

        assert geometry is not None

        targets = [
            element
            for element in geometry.findall("svg:circle", SVG)
            if element.attrib.get("class") == "target-point"
        ]

        guides = [
            element
            for element in geometry.findall("svg:line", SVG)
            if "incidence-guide" in element.attrib.get("class", "")
        ]

        assert len(targets) == 8
        assert len(guides) == 8


def test_comparison_rejects_small_canvas() -> None:
    diagram = build_core_geometry()

    with pytest.raises(ValueError):
        oblique_models_comparison_to_svg(
            diagram,
            canvas_width=1000,
        )

    with pytest.raises(ValueError):
        oblique_models_comparison_to_svg(
            diagram,
            canvas_height=500,
        )


def test_write_comparison_svg_creates_file(
    tmp_path: Path,
) -> None:
    diagram = build_core_geometry()
    output = tmp_path / "nested" / "comparison.svg"

    returned = write_oblique_models_comparison_svg(
        diagram,
        output,
    )

    assert returned == output
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith(
        '<?xml version="1.0" encoding="UTF-8"?>'
    )
