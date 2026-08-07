from __future__ import annotations

import ast
import inspect
from math import degrees
from pathlib import Path

import pytest

from new_jerusalem_geometry import (
    GEOMETRY_SCHEMA_NAME,
    GEOMETRY_SCHEMA_VERSION,
    build_michell_composite,
    build_michell_composite_geometry_export,
    build_michell_composite_provenance,
    michell_composite_geometry_to_json,
    write_michell_composite_geometry_json,
)


ROOT = Path(__file__).resolve().parents[1]

SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_geometry_export.py"
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
    composite = (
        build_michell_composite()
    )

    export = (
        build_michell_composite_geometry_export(
            composite
        )
    )

    return (
        composite,
        export,
    )


def _objects_by_id():
    _, export = _build()

    return {
        record.object_id: record
        for record
        in export.objects
    }


def test_geometry_export_requires_supplied_composite() -> None:
    signature = inspect.signature(
        build_michell_composite_geometry_export
    )

    assert (
        tuple(
            signature.parameters
        )
        == ("composite",)
    )

    assert (
        signature.parameters[
            "composite"
        ].default
        is inspect.Parameter.empty
    )


def test_geometry_export_imports_no_builders_calibration_or_provenance() -> None:
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
        "provenance",
        "_svg",
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


def test_geometry_export_schema_and_object_inventory() -> None:
    _, export = _build()

    assert (
        export.schema_name
        == GEOMETRY_SCHEMA_NAME
        == "njg_michell_geometry"
    )

    assert (
        export.schema_version
        == GEOMETRY_SCHEMA_VERSION
        == "1.0"
    )

    assert (
        export.model_name
        == "NJG_MICHELL"
    )

    assert export.unit == 1.0

    identifiers = [
        record.object_id
        for record
        in export.objects
    ]

    assert len(identifiers) == 132
    assert len(
        set(identifiers)
    ) == 132

    assert export.object_count == 132


def test_geometry_and_provenance_object_ids_and_types_match_exactly() -> None:
    composite, export = _build()

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

    geometry_identity = tuple(
        (
            record.object_id,
            record.geometry_type,
        )
        for record
        in export.objects
    )

    provenance_identity = tuple(
        (
            record.object_id,
            record.geometry_type,
        )
        for record
        in provenance.objects
    )

    assert (
        geometry_identity
        == provenance_identity
    )


def test_core_geometry_is_exported_without_reconstruction() -> None:
    composite, _ = _build()

    objects = _objects_by_id()

    earth = dict(
        objects[
            "earth-circle"
        ].geometry
    )

    assert earth["centre"] == {
        "x": (
            composite
            .core
            .earth_circle
            .centre.x
        ),
        "y": (
            composite
            .core
            .earth_circle
            .centre.y
        ),
    }

    assert (
        earth["radius"]
        == composite
        .core
        .earth_circle
        .radius
    )

    square = dict(
        objects[
            "earth-square"
        ].geometry
    )

    assert (
        square["side"]
        == composite
        .core
        .earth_square
        .side
    )

    assert (
        square["perimeter"]
        == composite
        .core
        .earth_square
        .perimeter
    )


def test_all_twelve_moons_reuse_composite_circle_geometry() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    assert len(
        composite
        .wall_reconstruction
        .moons
    ) == 12

    for moon_name, moon in (
        composite
        .wall_reconstruction
        .moons
    ):
        record = objects[
            moon_name
        ]

        geometry = dict(
            record.geometry
        )

        assert geometry[
            "centre"
        ] == {
            "x": moon.centre.x,
            "y": moon.centre.y,
        }

        assert (
            geometry["radius"]
            == moon.radius
        )


def test_wall_export_reuses_lines_vertices_and_metrics() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    wall = (
        composite
        .wall_reconstruction
    )

    polygon = dict(
        objects[
            "polar-pivot-wall"
        ].geometry
    )

    assert (
        tuple(
            polygon[
                "side_lengths"
            ]
        )
        == wall.side_lengths
    )

    assert (
        polygon["perimeter"]
        == wall.perimeter
    )

    assert (
        polygon[
            "mean_side_length"
        ]
        == wall.mean_side_length
    )

    assert (
        polygon["area"]
        == wall.area
    )

    for index, line in enumerate(
        wall.lines
    ):
        record = objects[
            line.name
        ]

        geometry = dict(
            record.geometry
        )

        start, end = (
            wall.side_endpoints(
                index
            )
        )

        assert geometry["normal"] == {
            "x": line.normal.x,
            "y": line.normal.y,
        }

        assert (
            geometry["offset"]
            == line.offset
        )

        assert (
            geometry[
                "tangency_point"
            ]
            == {
                "x": (
                    line
                    .tangency_point.x
                ),
                "y": (
                    line
                    .tangency_point.y
                ),
            }
        )

        assert geometry[
            "side_start"
        ] == {
            "x": start.x,
            "y": start.y,
        }

        assert geometry[
            "side_end"
        ] == {
            "x": end.x,
            "y": end.y,
        }

        assert (
            geometry[
                "side_length"
            ]
            == wall
            .side_lengths[index]
        )


def test_sevenfold_export_matches_composite_points_and_angles() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    sevenfold = (
        composite.sevenfold
    )

    for index in range(7):
        geometry = dict(
            objects[
                f"sevenfold-point-"
                f"{index:02d}"
            ].geometry
        )

        point = (
            sevenfold.points[
                index
            ]
        )

        assert (
            geometry["x"]
            == point.x
        )

        assert (
            geometry["y"]
            == point.y
        )

        assert (
            geometry[
                "angle_radians"
            ]
            == sevenfold
            .angles_radians[
                index
            ]
        )

        assert (
            geometry[
                "angle_degrees"
            ]
            == sevenfold
            .angles_degrees[
                index
            ]
        )


def test_fourteenfold_export_matches_points_angles_and_gaps() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    fourteenfold = (
        composite.fourteenfold
    )

    for index in range(14):
        geometry = dict(
            objects[
                f"fourteenfold-point-"
                f"{index:02d}"
            ].geometry
        )

        point = (
            fourteenfold
            .points[index]
        )

        assert (
            geometry["x"]
            == point.x
        )

        assert (
            geometry["y"]
            == point.y
        )

        assert (
            geometry[
                "angle_radians"
            ]
            == fourteenfold
            .angles_radians[
                index
            ]
        )

        assert (
            geometry[
                "angle_degrees"
            ]
            == fourteenfold
            .angles_degrees[
                index
            ]
        )

        assert (
            geometry[
                "angular_gap_to_next_radians"
            ]
            == fourteenfold
            .angular_gaps_radians[
                index
            ]
        )

        assert (
            geometry[
                "angular_gap_to_next_degrees"
            ]
            == fourteenfold
            .angular_gaps_degrees[
                index
            ]
        )


def test_four_triangle_marks_remain_angular_only() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    for index, angle in enumerate(
        composite
        .four_triangle_angles_radians
    ):
        record = objects[
            f"four-triangle-mark-"
            f"{index:02d}"
        ]

        assert (
            record.geometry_type
            == "angular_mark"
        )

        geometry = dict(
            record.geometry
        )

        assert set(
            geometry
        ) == {
            "angle_radians",
            "angle_degrees",
        }

        assert (
            geometry[
                "angle_radians"
            ]
            == angle
        )

        assert (
            geometry[
                "angle_degrees"
            ]
            == pytest.approx(
                degrees(angle),
                abs=1.0e-15,
            )
        )


def test_scaffold_export_preserves_complete_septenary_point_state() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    assert len(
        composite
        .scaffold
        .points
    ) == 28

    for point in (
        composite
        .scaffold
        .points
    ):
        record = objects[
            f"scaffold-point-"
            f"{point.index:02d}"
        ]

        geometry = dict(
            record.geometry
        )

        attributes = dict(
            record.attributes
        )

        assert (
            geometry["x"]
            == point.point.x
        )

        assert (
            geometry["y"]
            == point.point.y
        )

        assert (
            geometry[
                "angle_radians"
            ]
            == point.angle_radians
        )

        assert (
            geometry[
                "angle_degrees"
            ]
            == pytest.approx(
                degrees(
                    point.angle_radians
                ),
                abs=1.0e-15,
            )
        )

        assert attributes == {
            "scaffold_index": (
                point.index
            ),
            "quadrant": (
                point.quadrant
            ),
            "local_index": (
                point.local_index
            ),
            "role": (
                point.role.value
            ),
        }


def test_heptagram_vertices_keep_exact_scaffold_mapping() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

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

        geometry = dict(
            record.geometry
        )

        vertex = (
            composite
            .scaffold_heptagram_candidate
            .vertices[
                vertex_index
            ]
        )

        assert geometry == {
            "x": vertex.x,
            "y": vertex.y,
        }

        assert (
            dict(
                record.attributes
            )[
                "source_scaffold_object_id"
            ]
            == (
                f"scaffold-point-"
                f"{scaffold_index:02d}"
            )
        )


def test_heptagram_edges_reuse_candidate_topology_and_lengths() -> None:
    composite, export = _build()

    objects = {
        record.object_id: record
        for record
        in export.objects
    }

    star = (
        composite
        .scaffold_heptagram_candidate
    )

    pairs = (
        star.edge_index_pairs()
    )

    lengths = (
        star.edge_lengths()
    )

    for edge_index, (
        pair,
        length,
    ) in enumerate(
        zip(
            pairs,
            lengths,
            strict=True,
        )
    ):
        start_index, end_index = pair

        record = objects[
            f"heptagram-edge-"
            f"{edge_index:02d}"
        ]

        geometry = dict(
            record.geometry
        )

        attributes = dict(
            record.attributes
        )

        assert (
            geometry["length"]
            == length
        )

        assert (
            geometry["start"]
            == {
                "x": (
                    star
                    .vertices[
                        start_index
                    ].x
                ),
                "y": (
                    star
                    .vertices[
                        start_index
                    ].y
                ),
            }
        )

        assert (
            geometry["end"]
            == {
                "x": (
                    star
                    .vertices[
                        end_index
                    ].x
                ),
                "y": (
                    star
                    .vertices[
                        end_index
                    ].y
                ),
            }
        )

        assert (
            attributes[
                "start_vertex_index"
            ]
            == start_index
        )

        assert (
            attributes[
                "end_vertex_index"
            ]
            == end_index
        )


def test_geometry_sections_have_expected_layer_counts() -> None:
    _, export = _build()

    sections = dict(
        export.sections
    )

    assert len(
        sections["core"][
            "object_ids"
        ]
    ) == 3

    assert len(
        sections[
            "moon_system"
        ]["object_ids"]
    ) == 12

    assert len(
        sections["wall"][
            "line_object_ids"
        ]
    ) == 12

    assert len(
        sections["wall"][
            "vertex_object_ids"
        ]
    ) == 12

    assert len(
        sections["sevenfold"][
            "object_ids"
        ]
    ) == 7

    assert len(
        sections[
            "fourteenfold"
        ]["object_ids"]
    ) == 14

    assert len(
        sections[
            "four_triangle_28"
        ]["object_ids"]
    ) == 28

    assert len(
        sections[
            "scaffold_28"
        ]["object_ids"]
    ) == 28

    assert len(
        sections[
            "heptagram"
        ]["vertex_object_ids"]
    ) == 7

    assert len(
        sections[
            "heptagram"
        ]["edge_object_ids"]
    ) == 7


def test_geometry_json_contains_no_evidence_vocabulary() -> None:
    _, export = _build()

    text = (
        michell_composite_geometry_to_json(
            export
        )
    )

    forbidden = (
        '"evidence_status"',
        '"source_status"',
        '"relation_type"',
        '"node_type"',
        '"claim"',
        '"claim_ids"',
    )

    for token in forbidden:
        assert token not in text


def test_geometry_json_is_deterministic_and_writer_preserves_bytes(
    tmp_path: Path,
) -> None:
    _, export = _build()

    first = (
        michell_composite_geometry_to_json(
            export
        )
    )

    second = (
        michell_composite_geometry_to_json(
            export
        )
    )

    assert first == second

    path = (
        write_michell_composite_geometry_json(
            export,
            tmp_path
            / "geometry.json",
        )
    )

    assert path.read_text(
        encoding="utf-8"
    ) == first


def test_geometry_export_is_public_package_api() -> None:
    import new_jerusalem_geometry as njg

    assert (
        njg.GEOMETRY_SCHEMA_NAME
        == "njg_michell_geometry"
    )

    assert (
        njg.GEOMETRY_SCHEMA_VERSION
        == "1.0"
    )

    assert (
        njg.GeometryObject
        is not None
    )

    assert (
        njg.MichellCompositeGeometryExport
        is not None
    )

    assert (
        njg.build_michell_composite_geometry_export
        is not None
    )

    assert (
        njg.michell_composite_geometry_to_json
        is not None
    )

    assert (
        njg.write_michell_composite_geometry_json
        is not None
    )
