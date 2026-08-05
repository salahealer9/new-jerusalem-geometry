from __future__ import annotations

import ast
import inspect
from math import pi
from pathlib import Path

import pytest

from new_jerusalem_geometry.heptagram_geometry import (
    HeptagramFamily,
)
from new_jerusalem_geometry.michell_composite import (
    COMPOSITE_MODEL_NAME,
    build_michell_composite,
)
from new_jerusalem_geometry.model_variants import (
    ObliqueModel,
)
from new_jerusalem_geometry.septenary_geometry import (
    MichellTriangleBase,
)


ROOT = Path(__file__).resolve().parents[1]

COMPOSITE_SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_composite.py"
)


def test_composite_has_only_unit_as_external_input() -> None:
    signature = inspect.signature(
        build_michell_composite
    )

    assert tuple(
        signature.parameters
    ) == ("unit",)

    assert (
        signature.parameters["unit"].default
        == 1.0
    )


def test_composite_core_and_moon_partition() -> None:
    composite = build_michell_composite()

    assert (
        composite.model_name
        == COMPOSITE_MODEL_NAME
        == "NJG_MICHELL"
    )

    assert composite.unit == pytest.approx(
        1.0
    )

    assert len(composite.moon_groups) == 4
    assert composite.moon_count == 12

    names = [
        name
        for group in composite.moon_groups
        for name, _ in group.members
    ]

    assert len(names) == 12
    assert len(set(names)) == 12


def test_composite_wall_uses_incidence_moons() -> None:
    composite = build_michell_composite()

    wall = composite.wall_reconstruction

    assert (
        wall.model
        is ObliqueModel.INCIDENCE
    )

    assert len(wall.moons) == 12
    assert len(wall.lines) == 12
    assert len(wall.vertices) == 12

    grouped_names = {
        name
        for group in composite.moon_groups
        for name, _ in group.members
    }

    wall_names = {
        name
        for name, _ in wall.moons
    }

    assert grouped_names == wall_names


def test_composite_seven_to_fourteen_chain() -> None:
    composite = build_michell_composite()

    assert len(
        composite.sevenfold.points
    ) == 7

    assert (
        composite.sevenfold.base_side
        is MichellTriangleBase.SOUTH
    )

    assert len(
        composite.fourteenfold.points
    ) == 14

    assert (
        composite.fourteenfold.primary.base_side
        is MichellTriangleBase.SOUTH
    )

    assert (
        composite.fourteenfold.reciprocal.base_side
        is MichellTriangleBase.NORTH
    )


def test_composite_four_triangle_closure_to_scaffold() -> None:
    composite = build_michell_composite()

    assert len(
        composite.four_triangle_angles_radians
    ) == 28

    assert len(
        composite.scaffold.points
    ) == 28

    assert (
        composite
        .four_triangle_scaffold_max_mismatch_radians
        <= 1.0e-12
    )

    assert (
        composite
        .four_triangle_scaffold_max_mismatch_radians
        == pytest.approx(
            2.220446049250313e-16,
            abs=1.0e-15,
        )
    )


def test_composite_star_is_scaffold_candidate() -> None:
    composite = build_michell_composite()

    candidate = (
        composite.scaffold_heptagram_candidate
    )

    assert len(candidate.vertices) == 7

    assert (
        candidate.family
        is HeptagramFamily.STEP_2
    )

    assert candidate.traversal_indices() == (
        0,
        2,
        4,
        6,
        1,
        3,
        5,
    )

    scaffold_points = [
        point.point
        for point in composite.scaffold.points
    ]

    assert all(
        vertex in scaffold_points
        for vertex in candidate.vertices
    )


def test_composite_is_scale_invariant() -> None:
    base = build_michell_composite(
        unit=1.0
    )

    scale = 2.5

    scaled = build_michell_composite(
        unit=scale
    )

    assert (
        scaled.core.dimensions.earth_radius
        == pytest.approx(
            scale
            * base.core.dimensions.earth_radius
        )
    )

    assert (
        scaled.wall_reconstruction.perimeter
        == pytest.approx(
            scale
            * base.wall_reconstruction.perimeter,
            abs=1.0e-12,
        )
    )

    assert (
        scaled.wall_reconstruction.area
        == pytest.approx(
            scale
            * scale
            * base.wall_reconstruction.area,
            abs=1.0e-10,
        )
    )

    assert (
        scaled.sevenfold.step_radians
        == pytest.approx(
            base.sevenfold.step_radians,
            abs=1.0e-15,
        )
    )

    assert (
        scaled.fourteenfold.angular_gaps_radians
        == pytest.approx(
            base.fourteenfold.angular_gaps_radians,
            abs=1.0e-15,
        )
    )

    base_edges = (
        base.scaffold_heptagram_candidate
        .edge_lengths()
    )

    scaled_edges = (
        scaled.scaffold_heptagram_candidate
        .edge_lengths()
    )

    assert scaled_edges == pytest.approx(
        tuple(
            scale * length
            for length in base_edges
        ),
        abs=1.0e-12,
    )


def test_composite_imports_no_plate_calibration_modules() -> None:
    tree = ast.parse(
        COMPOSITE_SOURCE.read_text(
            encoding="utf-8"
        )
    )

    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            ast.ImportFrom,
        ):
            modules.append(
                node.module or ""
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
        "registered_landmarks",
        "source_geometry",
        "figure12_",
        "figure14_",
    )

    violations = [
        module
        for module in modules
        if any(
            fragment in module
            for fragment in forbidden_fragments
        )
    ]

    assert violations == []


def test_composite_does_not_import_aligned_plate_anchor_builders() -> None:
    tree = ast.parse(
        COMPOSITE_SOURCE.read_text(
            encoding="utf-8"
        )
    )

    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(
            node,
            ast.ImportFrom,
        )
        for alias in node.names
    }

    forbidden = {
        "build_figure14_anchor_set",
        "build_figure14_aligned_heptagram",
        "verify_figure14_heptagrams",
        "compare_heptagram_to_anchors",
    }

    assert (
        imported_names
        & forbidden
    ) == set()


def test_composite_is_public_package_api() -> None:
    import new_jerusalem_geometry as njg

    assert (
        njg.COMPOSITE_MODEL_NAME
        == "NJG_MICHELL"
    )

    assert (
        njg.MichellComposite
        is not None
    )

    composite = (
        njg.build_michell_composite()
    )

    assert (
        composite.model_name
        == "NJG_MICHELL"
    )


def test_composite_is_recorded_in_construction_grammar() -> None:
    import csv

    nodes_path = (
        ROOT
        / "docs"
        / "specification"
        / "construction_nodes.csv"
    )

    dependencies_path = (
        ROOT
        / "docs"
        / "specification"
        / "construction_dependencies.csv"
    )

    with nodes_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        nodes = list(
            csv.DictReader(handle)
        )

    matches = [
        row
        for row in nodes
        if (
            row["node_id"]
            == "NJG_MICHELL_COMPOSITE"
        )
    ]

    assert len(matches) == 1

    node = matches[0]

    assert (
        node["node_type"]
        == "composite_geometry"
    )

    assert (
        node["implementation_reference"]
        == "michell_composite"
    )

    assert node["claim_ids"] == ""

    with dependencies_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        dependencies = list(
            csv.DictReader(handle)
        )

    incoming = [
        row
        for row in dependencies
        if (
            row["child_node"]
            == "NJG_MICHELL_COMPOSITE"
        )
    ]

    assert {
        row["parent_node"]
        for row in incoming
    } == {
        "CORE_DIMENSIONS",
        "MOON_GROUPS_4X3",
        "POLAR_PIVOT_WALL",
        "SCAFFOLD_28",
    }

    assert all(
        row["evidence_status"]
        == "implementation_only"
        for row in incoming
    )
