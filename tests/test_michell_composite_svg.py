from __future__ import annotations

import ast
import inspect
from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from new_jerusalem_geometry.michell_composite import (
    MichellComposite,
    build_michell_composite,
)
from new_jerusalem_geometry.michell_composite_svg import (
    michell_composite_to_svg,
    write_michell_composite_svg,
)


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_composite_svg.py"
)

SVG_NS = {
    "svg": "http://www.w3.org/2000/svg",
}


def _root(
    composite: MichellComposite,
) -> ET.Element:
    return ET.fromstring(
        michell_composite_to_svg(
            composite
        )
    )


def _element_by_id(
    root: ET.Element,
    identifier: str,
) -> ET.Element:
    matches = [
        element
        for element in root.iter()
        if element.get("id") == identifier
    ]

    assert len(matches) == 1

    return matches[0]


def test_renderer_requires_supplied_composite() -> None:
    signature = inspect.signature(
        michell_composite_to_svg
    )

    assert (
        tuple(signature.parameters)
        == (
            "composite",
            "canvas_size",
            "title",
            "description",
        )
    )

    assert (
        signature.parameters[
            "composite"
        ].default
        is inspect.Parameter.empty
    )

    assert "unit" not in (
        signature.parameters
    )


def test_renderer_has_no_geometry_builder_or_calibration_imports() -> None:
    tree = ast.parse(
        SOURCE.read_text(
            encoding="utf-8"
        )
    )

    imported_modules: list[str] = []
    imported_names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            imported_modules.append(
                node.module or ""
            )

            imported_names.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            imported_modules.extend(
                alias.name
                for alias in node.names
            )

    forbidden_fragments = (
        "calibration",
        "digitisation",
        "registration",
        "source_geometry",
        "registered_landmarks",
        "figure12_",
        "figure14_",
    )

    violations = [
        module
        for module in imported_modules
        if any(
            fragment in module
            for fragment in forbidden_fragments
        )
    ]

    assert violations == []

    forbidden_builders = {
        "build_michell_composite",
        "build_core_geometry",
        "build_oblique_placement",
        "build_ordered_moon_circles",
        "build_polar_pivot_tangent_wall",
        "build_michell_28_point_scaffold",
        "build_scaffold_heptagram",
        "build_figure14_anchor_set",
        "build_figure14_aligned_heptagram",
    }

    assert (
        imported_names
        & forbidden_builders
    ) == set()


def test_svg_contains_canonical_geometry_layers() -> None:
    composite = build_michell_composite()

    root = _root(
        composite
    )

    expected = {
        "njg-michell-composite",
        "wall",
        "polar-pivot-wall",
        "construction-circle-layer",
        "construction-circle",
        "earth-square-layer",
        "earth-square",
        "earth-circle-layer",
        "earth-circle",
        "moon-system",
        "scaffold",
        "heptagram",
    }

    identifiers = {
        element.get("id")
        for element in root.iter()
        if element.get("id")
    }

    assert expected <= identifiers


def test_svg_layer_grammar_annotations_are_fixed() -> None:
    root = _root(
        build_michell_composite()
    )

    expected = {
        "wall": "POLAR_PIVOT_WALL",
        "construction-circle-layer": (
            "CONSTRUCTION_CIRCLE"
        ),
        "earth-square-layer": "EARTH_SQUARE",
        "earth-circle-layer": "EARTH_CIRCLE",
        "moon-system": "MOON_GROUPS_4X3",
        "scaffold": "SCAFFOLD_28",
        "heptagram": "FIG14_HEPTAGRAM_7_2",
    }

    for identifier, grammar_node in (
        expected.items()
    ):
        element = _element_by_id(
            root,
            identifier,
        )

        assert (
            element.get(
                "data-grammar-node"
            )
            == grammar_node
        )

    heptagram = _element_by_id(
        root,
        "heptagram",
    )

    assert (
        heptagram.get(
            "data-vertex-source"
        )
        == "FIG14_SCAFFOLD_VERTICES"
    )


def test_svg_uses_all_twelve_composite_moons() -> None:
    composite = build_michell_composite()

    root = _root(
        composite
    )

    moon_group = _element_by_id(
        root,
        "moon-system",
    )

    rendered = [
        element
        for element in moon_group
        if element.tag.endswith(
            "circle"
        )
    ]

    assert len(rendered) == 12

    rendered_names = {
        element.get("data-moon")
        for element in rendered
    }

    expected_names = {
        name
        for name, _
        in composite.wall_reconstruction.moons
    }

    assert rendered_names == expected_names


def test_svg_contains_all_twenty_eight_scaffold_points() -> None:
    composite = build_michell_composite()

    root = _root(
        composite
    )

    scaffold_group = _element_by_id(
        root,
        "scaffold",
    )

    rendered = [
        element
        for element in scaffold_group
        if element.get(
            "data-scaffold-index"
        )
        is not None
    ]

    assert len(rendered) == 28

    indices = {
        int(
            element.get(
                "data-scaffold-index",
                "-1",
            )
        )
        for element in rendered
    }

    assert indices == set(
        range(28)
    )


def test_svg_star_uses_exact_composite_vertices_and_edges() -> None:
    composite = build_michell_composite()

    root = _root(
        composite
    )

    group = _element_by_id(
        root,
        "heptagram",
    )

    vertices = [
        element
        for element in group
        if (
            element.get(
                "data-vertex-index"
            )
            is not None
        )
    ]

    edges = [
        element
        for element in group
        if (
            element.get(
                "data-start-index"
            )
            is not None
        )
    ]

    assert len(vertices) == 7
    assert len(edges) == 7

    for element in vertices:
        index = int(
            element.get(
                "data-vertex-index",
                "-1",
            )
        )

        expected = (
            composite
            .scaffold_heptagram_candidate
            .vertices[index]
        )

        assert float(
            element.get(
                "cx",
                "nan",
            )
        ) == pytest.approx(
            expected.x,
            abs=1.0e-11,
        )

        assert float(
            element.get(
                "cy",
                "nan",
            )
        ) == pytest.approx(
            expected.y,
            abs=1.0e-11,
        )

    rendered_pairs = tuple(
        (
            int(
                element.get(
                    "data-start-index",
                    "-1",
                )
            ),
            int(
                element.get(
                    "data-end-index",
                    "-1",
                )
            ),
        )
        for element in edges
    )

    assert rendered_pairs == (
        composite
        .scaffold_heptagram_candidate
        .edge_index_pairs()
    )


def test_svg_is_deterministic_and_transparent() -> None:
    composite = build_michell_composite()

    first = michell_composite_to_svg(
        composite
    )

    second = michell_composite_to_svg(
        composite
    )

    assert first == second

    assert (
        "Rendering background: transparent"
        in first
    )

    root = ET.fromstring(
        first
    )

    style_text = "\n".join(
        element.text or ""
        for element in root.iter()
        if element.tag.endswith(
            "style"
        )
    )

    assert "background-color" not in style_text
    assert "background:" not in style_text


def test_writer_preserves_renderer_bytes(
    tmp_path: Path,
) -> None:
    composite = build_michell_composite()

    expected = michell_composite_to_svg(
        composite
    )

    path = write_michell_composite_svg(
        composite,
        tmp_path / "composite.svg",
    )

    assert path.read_text(
        encoding="utf-8"
    ) == expected


def test_composite_svg_renderer_is_public_package_api() -> None:
    import new_jerusalem_geometry as njg

    assert (
        njg.michell_composite_to_svg
        is not None
    )

    assert (
        njg.write_michell_composite_svg
        is not None
    )

    composite = (
        njg.build_michell_composite()
    )

    svg = (
        njg.michell_composite_to_svg(
            composite
        )
    )

    assert (
        'data-model="NJG_MICHELL"'
        in svg
    )
