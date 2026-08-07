from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

from new_jerusalem_geometry import (
    build_michell_composite,
    build_michell_composite_provenance,
    michell_composite_to_svg,
)


ROOT = Path(__file__).resolve().parents[1]

NODES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

DEPENDENCIES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

CLAIMS_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)


def _build():
    composite = build_michell_composite()

    provenance = (
        build_michell_composite_provenance(
            composite,
            construction_nodes_path=(
                NODES_PATH
            ),
            construction_dependencies_path=(
                DEPENDENCIES_PATH
            ),
            claim_matrix_path=(
                CLAIMS_PATH
            ),
        )
    )

    root = ET.fromstring(
        michell_composite_to_svg(
            composite
        )
    )

    return (
        composite,
        provenance,
        root,
    )


def _elements_by_id(
    root: ET.Element,
) -> dict[str, ET.Element]:
    result: dict[
        str,
        ET.Element,
    ] = {}

    for element in root.iter():
        identifier = element.get(
            "id"
        )

        if identifier is None:
            continue

        assert (
            identifier
            not in result
        )

        result[identifier] = (
            element
        )

    return result


def test_every_manifest_rendered_svg_id_resolves_exactly_once() -> None:
    _, provenance, root = _build()

    elements = _elements_by_id(
        root
    )

    rendered = [
        record
        for record
        in provenance.objects
        if (
            record.rendered_svg_id
            is not None
        )
    ]

    assert len(rendered) == 59

    for record in rendered:
        svg_id = (
            record.rendered_svg_id
        )

        assert svg_id is not None
        assert svg_id in elements

        element = elements[
            svg_id
        ]

        assert (
            element.get(
                "data-provenance-id"
            )
            == record.object_id
        )


def test_every_svg_provenance_id_resolves_to_manifest_object() -> None:
    _, provenance, root = _build()

    objects = {
        record.object_id: record
        for record
        in provenance.objects
    }

    linked_elements = [
        element
        for element in root.iter()
        if (
            element.get(
                "data-provenance-id"
            )
            is not None
        )
    ]

    assert len(
        linked_elements
    ) == 59

    for element in linked_elements:
        provenance_id = (
            element.get(
                "data-provenance-id"
            )
        )

        assert provenance_id is not None
        assert provenance_id in objects

        record = objects[
            provenance_id
        ]

        assert (
            record.rendered_svg_id
            == element.get("id")
        )

        assert (
            record.object_id
            == provenance_id
        )


def test_scaffold_svg_provenance_ids_are_complete() -> None:
    _, provenance, root = _build()

    elements = _elements_by_id(
        root
    )

    objects = {
        record.object_id: record
        for record
        in provenance.objects
    }

    for index in range(28):
        identifier = (
            f"scaffold-point-"
            f"{index:02d}"
        )

        assert identifier in elements
        assert identifier in objects

        element = elements[
            identifier
        ]

        record = objects[
            identifier
        ]

        assert (
            element.get(
                "data-provenance-id"
            )
            == identifier
        )

        assert (
            int(
                element.get(
                    "data-scaffold-index",
                    "-1",
                )
            )
            == index
        )

        assert (
            record.rendered_svg_id
            == identifier
        )

        assert (
            dict(
                record.attributes
            )["scaffold_index"]
            == index
        )


def test_heptagram_svg_keeps_vertex_and_topology_provenance_separate() -> None:
    _, provenance, root = _build()

    elements = _elements_by_id(
        root
    )

    objects = {
        record.object_id: record
        for record
        in provenance.objects
    }

    for index in range(7):
        vertex_id = (
            f"heptagram-vertex-"
            f"{index:02d}"
        )

        vertex = objects[
            vertex_id
        ]

        assert vertex.grammar_nodes == (
            "FIG14_SCAFFOLD_VERTICES",
        )

        assert (
            elements[
                vertex_id
            ].get(
                "data-provenance-id"
            )
            == vertex_id
        )

        edge_id = (
            f"heptagram-edge-"
            f"{index:02d}"
        )

        edge = objects[
            edge_id
        ]

        assert edge.grammar_nodes == (
            "FIG14_HEPTAGRAM_7_2",
        )

        assert (
            elements[
                edge_id
            ].get(
                "data-provenance-id"
            )
            == edge_id
        )
