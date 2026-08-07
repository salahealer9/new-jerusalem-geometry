from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

from new_jerusalem_geometry import (
    PROVENANCE_SCHEMA_NAME,
    PROVENANCE_SCHEMA_VERSION,
    build_michell_composite,
    build_michell_composite_provenance,
    michell_composite_provenance_to_json,
    write_michell_composite_provenance_json,
)


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_provenance.py"
)

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
    return build_michell_composite_provenance(
        build_michell_composite(),
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


def _objects_by_id():
    provenance = _build()

    return {
        record.object_id: record
        for record
        in provenance.objects
    }


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_provenance_requires_supplied_composite() -> None:
    signature = inspect.signature(
        build_michell_composite_provenance
    )

    assert (
        tuple(
            signature.parameters
        )
        == (
            "composite",
            "construction_nodes_path",
            "construction_dependencies_path",
            "claim_matrix_path",
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


def test_provenance_imports_no_geometry_builders_or_calibration_modules() -> None:
    tree = ast.parse(
        SOURCE.read_text(
            encoding="utf-8"
        )
    )

    modules: list[str] = []
    names: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            modules.append(
                node.module or ""
            )

            names.update(
                alias.name
                for alias in node.names
            )

        elif isinstance(
            node,
            ast.Import,
        ):
            modules.extend(
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
        for module in modules
        if any(
            fragment in module
            for fragment
            in forbidden_fragments
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
        names
        & forbidden_builders
    ) == set()


def test_provenance_has_canonical_schema_and_unique_objects() -> None:
    provenance = _build()

    assert (
        provenance.schema_name
        == PROVENANCE_SCHEMA_NAME
        == "njg_michell_provenance"
    )

    assert (
        provenance.schema_version
        == PROVENANCE_SCHEMA_VERSION
        == "1.0"
    )

    assert (
        provenance.model_name
        == "NJG_MICHELL"
    )

    assert provenance.unit == 1.0

    identifiers = [
        record.object_id
        for record
        in provenance.objects
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )

    assert provenance.object_count == 132


def test_moon_objects_preserve_distinct_grammar_membership() -> None:
    objects = _objects_by_id()

    cardinal = objects[
        "moon-east"
    ]

    assert cardinal.grammar_nodes == (
        "CARDINAL_MOONS",
        "NJG_INC_MOONS",
        "MOON_GROUPS_4X3",
    )

    assert (
        cardinal.role
        == "cardinal_moon"
    )

    oblique = objects[
        "moon-q1-a"
    ]

    assert oblique.grammar_nodes == (
        "NJG_INC_MOONS",
        "MOON_GROUPS_4X3",
    )

    assert (
        oblique.role
        == "oblique_moon"
    )

    assert dict(
        oblique.attributes
    ) == {
        "moon_name": "moon-q1-a",
        "moon_group": "east",
        "moon_group_role": (
            "counterclockwise_outer"
        ),
    }


def test_wall_provenance_preserves_reconstruction_boundary() -> None:
    objects = _objects_by_id()

    wall = objects[
        "polar-pivot-wall"
    ]

    assert wall.grammar_nodes == (
        "POLAR_PIVOT_WALL",
    )

    assert len(
        wall.source_object_ids
    ) == 12

    line = objects[
        "wall_east"
    ]

    assert line.grammar_nodes == (
        "POLAR_PIVOT_WALL",
    )

    assert (
        line.source_object_ids
        == ("moon-east",)
    )

    assert (
        dict(
            line.attributes
        )["wall_moon_name"]
        == "moon-east"
    )


def test_scaffold_inventory_is_complete_and_role_labelled() -> None:
    provenance = _build()

    scaffold = [
        record
        for record
        in provenance.objects
        if record.object_id.startswith(
            "scaffold-point-"
        )
    ]

    assert len(scaffold) == 28

    assert {
        record.role
        for record in scaffold
    } == {
        "moon_centre",
        "inter_moon_gap",
        "intersection_positioner",
    }

    assert {
        dict(
            record.attributes
        )["scaffold_index"]
        for record in scaffold
    } == set(
        range(28)
    )


def test_heptagram_vertices_preserve_scaffold_source_indices() -> None:
    objects = _objects_by_id()

    expected = (
        7,
        11,
        15,
        19,
        23,
        27,
        3,
    )

    observed = tuple(
        dict(
            objects[
                f"heptagram-vertex-"
                f"{index:02d}"
            ].attributes
        )["scaffold_index"]
        for index in range(7)
    )

    assert observed == expected

    for vertex_index, scaffold_index in (
        enumerate(expected)
    ):
        record = objects[
            f"heptagram-vertex-"
            f"{vertex_index:02d}"
        ]

        assert record.grammar_nodes == (
            "FIG14_SCAFFOLD_VERTICES",
        )

        assert (
            record.source_object_ids
            == (
                (
                    f"scaffold-point-"
                    f"{scaffold_index:02d}"
                ),
            )
        )


def test_heptagram_edges_preserve_topology_separately() -> None:
    objects = _objects_by_id()

    edge = objects[
        "heptagram-edge-00"
    ]

    assert edge.grammar_nodes == (
        "FIG14_HEPTAGRAM_7_2",
    )

    assert (
        edge.source_object_ids
        == (
            "heptagram-vertex-00",
            "heptagram-vertex-02",
        )
    )

    attributes = dict(
        edge.attributes
    )

    assert (
        attributes[
            "start_vertex_index"
        ]
        == 0
    )

    assert (
        attributes[
            "end_vertex_index"
        ]
        == 2
    )


def test_grammar_snapshot_preserves_critical_evidence_boundaries() -> None:
    provenance = _build()

    edges = {
        row["edge_id"]: row
        for row
        in provenance
        .grammar_snapshot
        .dependencies
    }

    assert (
        edges[
            "DEP-011"
        ]["evidence_status"]
        == "project_inference"
    )

    assert (
        edges[
            "DEP-022"
        ]["evidence_status"]
        == "implementation_only"
    )

    assert (
        edges[
            "DEP-024"
        ]["evidence_status"]
        == "hypothesis_to_test"
    )

    assert (
        edges[
            "DEP-026"
        ]["evidence_status"]
        == "stated_exact"
    )


def test_provenance_hashes_authoritative_source_files() -> None:
    provenance = _build()

    hashes = dict(
        provenance.source_hashes
    )

    assert hashes == {
        (
            "docs/specification/"
            "construction_nodes.csv"
        ): _sha256(
            NODES_PATH
        ),
        (
            "docs/specification/"
            "construction_dependencies.csv"
        ): _sha256(
            DEPENDENCIES_PATH
        ),
        (
            "docs/sources/"
            "geometric_claim_matrix.csv"
        ): _sha256(
            CLAIMS_PATH
        ),
    }


def test_provenance_json_is_deterministic_and_writer_preserves_bytes(
    tmp_path: Path,
) -> None:
    provenance = _build()

    first = (
        michell_composite_provenance_to_json(
            provenance
        )
    )

    second = (
        michell_composite_provenance_to_json(
            provenance
        )
    )

    assert first == second

    path = (
        write_michell_composite_provenance_json(
            provenance,
            tmp_path
            / "provenance.json",
        )
    )

    assert path.read_text(
        encoding="utf-8"
    ) == first


def test_provenance_is_public_package_api() -> None:
    import new_jerusalem_geometry as njg

    assert (
        njg.PROVENANCE_SCHEMA_NAME
        == "njg_michell_provenance"
    )

    assert (
        njg.PROVENANCE_SCHEMA_VERSION
        == "1.0"
    )

    assert (
        njg.ProvenanceObject
        is not None
    )

    assert (
        njg.GrammarSnapshot
        is not None
    )

    assert (
        njg.MichellCompositeProvenance
        is not None
    )

    assert (
        njg.build_michell_composite_provenance
        is not None
    )
