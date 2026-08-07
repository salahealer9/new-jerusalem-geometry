"""Deterministic numerical geometry export for NJG_MICHELL.

The exporter is a pure downstream view of an already constructed
``MichellComposite``.

It does not reconstruct geometry, consume provenance, or use source-plate
calibration data.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from math import degrees
from pathlib import Path
from typing import Any

from .michell_composite import MichellComposite


GEOMETRY_SCHEMA_NAME = "njg_michell_geometry"
GEOMETRY_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class GeometryObject:
    """One machine-readable geometric object."""

    object_id: str
    geometry_type: str
    geometry: tuple[
        tuple[str, Any],
        ...,
    ] = ()
    attributes: tuple[
        tuple[str, Any],
        ...,
    ] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""

        return {
            "object_id": self.object_id,
            "geometry_type": self.geometry_type,
            "geometry": dict(
                self.geometry
            ),
            "attributes": dict(
                self.attributes
            ),
        }


@dataclass(frozen=True, slots=True)
class MichellCompositeGeometryExport:
    """Complete numerical export of one supplied composite."""

    schema_name: str
    schema_version: str
    model_name: str
    unit: float
    coordinate_system: tuple[
        tuple[str, Any],
        ...,
    ]
    sections: tuple[
        tuple[str, dict[str, Any]],
        ...,
    ]
    objects: tuple[
        GeometryObject,
        ...,
    ]

    @property
    def object_count(self) -> int:
        return len(
            self.objects
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON-compatible document."""

        return {
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "model_name": self.model_name,
            "unit": self.unit,
            "coordinate_system": dict(
                self.coordinate_system
            ),
            "object_count": self.object_count,
            "sections": {
                name: dict(data)
                for name, data
                in self.sections
            },
            "objects": [
                record.to_dict()
                for record in self.objects
            ],
        }


def _point(
    point: object,
) -> dict[str, float]:
    """Serialize one Point2D-like object."""

    return {
        "x": float(
            getattr(
                point,
                "x",
            )
        ),
        "y": float(
            getattr(
                point,
                "y",
            )
        ),
    }


def _circle(
    circle: object,
) -> dict[str, Any]:
    """Serialize one Circle-like object."""

    return {
        "centre": _point(
            getattr(
                circle,
                "centre",
            )
        ),
        "radius": float(
            getattr(
                circle,
                "radius",
            )
        ),
    }


def _enum_value(
    value: object,
) -> str:
    raw = getattr(
        value,
        "value",
        value,
    )

    return str(
        raw
    )


def _star_scaffold_indices(
    composite: MichellComposite,
) -> tuple[int, ...]:
    """Resolve each star vertex to exactly one scaffold point."""

    result: list[int] = []

    for vertex in (
        composite
        .scaffold_heptagram_candidate
        .vertices
    ):
        matches = [
            index
            for index, scaffold_point
            in enumerate(
                composite.scaffold.points
            )
            if (
                scaffold_point.point
                == vertex
            )
        ]

        if len(matches) != 1:
            raise ValueError(
                "Each heptagram vertex must "
                "match exactly one scaffold point."
            )

        result.append(
            matches[0]
        )

    return tuple(
        result
    )


def _build_objects(
    composite: MichellComposite,
) -> tuple[GeometryObject, ...]:
    """Build the canonical ordered 132-object inventory."""

    objects: list[
        GeometryObject
    ] = []

    core = composite.core
    wall = composite.wall_reconstruction
    sevenfold = composite.sevenfold
    fourteenfold = composite.fourteenfold
    scaffold = composite.scaffold
    star = (
        composite
        .scaffold_heptagram_candidate
    )

    # Composite root.
    objects.append(
        GeometryObject(
            object_id=(
                "njg-michell-composite"
            ),
            geometry_type="composite",
            geometry=(
                (
                    "unit",
                    composite.unit,
                ),
                (
                    "moon_count",
                    composite.moon_count,
                ),
                (
                    "wall_side_count",
                    len(
                        wall.lines
                    ),
                ),
                (
                    "scaffold_point_count",
                    len(
                        scaffold.points
                    ),
                ),
                (
                    "heptagram_vertex_count",
                    len(
                        star.vertices
                    ),
                ),
            ),
        )
    )

    # Core.
    objects.extend(
        (
            GeometryObject(
                object_id="earth-circle",
                geometry_type="circle",
                geometry=tuple(
                    _circle(
                        core.earth_circle
                    ).items()
                ),
            ),
            GeometryObject(
                object_id="earth-square",
                geometry_type="square",
                geometry=(
                    (
                        "centre",
                        _point(
                            core
                            .earth_square
                            .centre
                        ),
                    ),
                    (
                        "side",
                        core
                        .earth_square
                        .side,
                    ),
                    (
                        "half_side",
                        core
                        .earth_square
                        .half_side,
                    ),
                    (
                        "perimeter",
                        core
                        .earth_square
                        .perimeter,
                    ),
                ),
            ),
            GeometryObject(
                object_id=(
                    "construction-circle"
                ),
                geometry_type="circle",
                geometry=tuple(
                    _circle(
                        core
                        .construction_circle
                    ).items()
                ),
            ),
        )
    )

    # Twelve Moon circles.
    for moon_name, moon in wall.moons:
        objects.append(
            GeometryObject(
                object_id=moon_name,
                geometry_type="circle",
                geometry=tuple(
                    _circle(
                        moon
                    ).items()
                ),
                attributes=(
                    (
                        "moon_name",
                        moon_name,
                    ),
                ),
            )
        )

    wall_line_ids = tuple(
        line.name
        for line in wall.lines
    )

    wall_vertex_ids = tuple(
        f"wall-vertex-{index:02d}"
        for index in range(
            len(
                wall.vertices
            )
        )
    )

    # Wall polygon summary.
    objects.append(
        GeometryObject(
            object_id=(
                "polar-pivot-wall"
            ),
            geometry_type="polygon",
            geometry=(
                (
                    "vertex_ids",
                    list(
                        wall_vertex_ids
                    ),
                ),
                (
                    "side_ids",
                    list(
                        wall_line_ids
                    ),
                ),
                (
                    "side_lengths",
                    list(
                        wall.side_lengths
                    ),
                ),
                (
                    "perimeter",
                    wall.perimeter,
                ),
                (
                    "mean_side_length",
                    wall.mean_side_length,
                ),
                (
                    "area",
                    wall.area,
                ),
            ),
        )
    )

    # Wall support lines and finite polygon sides.
    for index, line in enumerate(
        wall.lines
    ):
        start, end = (
            wall.side_endpoints(
                index
            )
        )

        objects.append(
            GeometryObject(
                object_id=line.name,
                geometry_type="line",
                geometry=(
                    (
                        "normal",
                        _point(
                            line.normal
                        ),
                    ),
                    (
                        "offset",
                        line.offset,
                    ),
                    (
                        "tangency_point",
                        _point(
                            line
                            .tangency_point
                        ),
                    ),
                    (
                        "side_start",
                        _point(
                            start
                        ),
                    ),
                    (
                        "side_end",
                        _point(
                            end
                        ),
                    ),
                    (
                        "side_length",
                        wall
                        .side_lengths[
                            index
                        ],
                    ),
                ),
                attributes=(
                    (
                        "wall_index",
                        index,
                    ),
                    (
                        "moon_name",
                        line.moon_name,
                    ),
                ),
            )
        )

    # Wall vertices.
    for index, vertex in enumerate(
        wall.vertices
    ):
        objects.append(
            GeometryObject(
                object_id=(
                    f"wall-vertex-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                geometry=(
                    (
                        "x",
                        vertex.x,
                    ),
                    (
                        "y",
                        vertex.y,
                    ),
                ),
                attributes=(
                    (
                        "wall_vertex_index",
                        index,
                    ),
                ),
            )
        )

    # Sevenfold Method-1 points.
    for index, (
        point,
        angle_radians,
        angle_degrees,
    ) in enumerate(
        zip(
            sevenfold.points,
            sevenfold.angles_radians,
            sevenfold.angles_degrees,
            strict=True,
        )
    ):
        objects.append(
            GeometryObject(
                object_id=(
                    f"sevenfold-point-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                geometry=(
                    (
                        "x",
                        point.x,
                    ),
                    (
                        "y",
                        point.y,
                    ),
                    (
                        "angle_radians",
                        angle_radians,
                    ),
                    (
                        "angle_degrees",
                        angle_degrees,
                    ),
                ),
                attributes=(
                    (
                        "sevenfold_index",
                        index,
                    ),
                    (
                        "base_side",
                        _enum_value(
                            sevenfold
                            .base_side
                        ),
                    ),
                ),
            )
        )

    # Reciprocal fourteenfold points.
    for index, (
        point,
        angle_radians,
        angle_degrees,
        gap_radians,
        gap_degrees,
    ) in enumerate(
        zip(
            fourteenfold.points,
            fourteenfold
            .angles_radians,
            fourteenfold
            .angles_degrees,
            fourteenfold
            .angular_gaps_radians,
            fourteenfold
            .angular_gaps_degrees,
            strict=True,
        )
    ):
        objects.append(
            GeometryObject(
                object_id=(
                    f"fourteenfold-point-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                geometry=(
                    (
                        "x",
                        point.x,
                    ),
                    (
                        "y",
                        point.y,
                    ),
                    (
                        "angle_radians",
                        angle_radians,
                    ),
                    (
                        "angle_degrees",
                        angle_degrees,
                    ),
                    (
                        "angular_gap_to_next_radians",
                        gap_radians,
                    ),
                    (
                        "angular_gap_to_next_degrees",
                        gap_degrees,
                    ),
                ),
                attributes=(
                    (
                        "fourteenfold_index",
                        index,
                    ),
                ),
            )
        )

    # Independent four-triangle 28 angular marks.
    for index, angle_radians in enumerate(
        composite
        .four_triangle_angles_radians
    ):
        objects.append(
            GeometryObject(
                object_id=(
                    f"four-triangle-mark-"
                    f"{index:02d}"
                ),
                geometry_type=(
                    "angular_mark"
                ),
                geometry=(
                    (
                        "angle_radians",
                        angle_radians,
                    ),
                    (
                        "angle_degrees",
                        degrees(
                            angle_radians
                        ),
                    ),
                ),
                attributes=(
                    (
                        "angular_mark_index",
                        index,
                    ),
                ),
            )
        )

    # Role-labelled scaffold.
    for scaffold_point in (
        scaffold.points
    ):
        index = (
            scaffold_point.index
        )

        objects.append(
            GeometryObject(
                object_id=(
                    f"scaffold-point-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                geometry=(
                    (
                        "x",
                        scaffold_point
                        .point.x,
                    ),
                    (
                        "y",
                        scaffold_point
                        .point.y,
                    ),
                    (
                        "angle_radians",
                        scaffold_point
                        .angle_radians,
                    ),
                    (
                        "angle_degrees",
                        degrees(
                            scaffold_point
                            .angle_radians
                        ),
                    ),
                ),
                attributes=(
                    (
                        "scaffold_index",
                        index,
                    ),
                    (
                        "quadrant",
                        scaffold_point
                        .quadrant,
                    ),
                    (
                        "local_index",
                        scaffold_point
                        .local_index,
                    ),
                    (
                        "role",
                        scaffold_point
                        .role.value,
                    ),
                ),
            )
        )

    scaffold_indices = (
        _star_scaffold_indices(
            composite
        )
    )

    # Scaffold-derived heptagram vertices.
    for vertex_index, (
        vertex,
        scaffold_index,
    ) in enumerate(
        zip(
            star.vertices,
            scaffold_indices,
            strict=True,
        )
    ):
        source_id = (
            f"scaffold-point-"
            f"{scaffold_index:02d}"
        )

        objects.append(
            GeometryObject(
                object_id=(
                    f"heptagram-vertex-"
                    f"{vertex_index:02d}"
                ),
                geometry_type="point",
                geometry=(
                    (
                        "x",
                        vertex.x,
                    ),
                    (
                        "y",
                        vertex.y,
                    ),
                ),
                attributes=(
                    (
                        "heptagram_vertex_index",
                        vertex_index,
                    ),
                    (
                        "scaffold_index",
                        scaffold_index,
                    ),
                    (
                        "source_scaffold_object_id",
                        source_id,
                    ),
                ),
            )
        )

    edge_pairs = (
        star.edge_index_pairs()
    )

    edge_lengths = (
        star.edge_lengths()
    )

    # Heptagram edges.
    for edge_index, (
        pair,
        edge_length,
    ) in enumerate(
        zip(
            edge_pairs,
            edge_lengths,
            strict=True,
        )
    ):
        start_index, end_index = pair

        start = star.vertices[
            start_index
        ]

        end = star.vertices[
            end_index
        ]

        start_id = (
            f"heptagram-vertex-"
            f"{start_index:02d}"
        )

        end_id = (
            f"heptagram-vertex-"
            f"{end_index:02d}"
        )

        objects.append(
            GeometryObject(
                object_id=(
                    f"heptagram-edge-"
                    f"{edge_index:02d}"
                ),
                geometry_type="line",
                geometry=(
                    (
                        "start",
                        _point(
                            start
                        ),
                    ),
                    (
                        "end",
                        _point(
                            end
                        ),
                    ),
                    (
                        "length",
                        edge_length,
                    ),
                ),
                attributes=(
                    (
                        "heptagram_edge_index",
                        edge_index,
                    ),
                    (
                        "start_vertex_index",
                        start_index,
                    ),
                    (
                        "end_vertex_index",
                        end_index,
                    ),
                    (
                        "start_vertex_object_id",
                        start_id,
                    ),
                    (
                        "end_vertex_object_id",
                        end_id,
                    ),
                ),
            )
        )

    identifiers = [
        record.object_id
        for record in objects
    ]

    if len(identifiers) != len(
        set(identifiers)
    ):
        raise ValueError(
            "Geometry object identifiers "
            "must be unique."
        )

    if len(objects) != 132:
        raise AssertionError(
            "The frozen v0.5 geometry schema "
            "requires exactly 132 objects; "
            f"got {len(objects)}."
        )

    return tuple(
        objects
    )


def _build_sections(
    composite: MichellComposite,
) -> tuple[
    tuple[str, dict[str, Any]],
    ...,
]:
    """Build deterministic construction-layer summaries."""

    dimensions = (
        composite.core.dimensions
    )

    wall = (
        composite.wall_reconstruction
    )

    sevenfold = composite.sevenfold
    fourteenfold = (
        composite.fourteenfold
    )

    scaffold = composite.scaffold

    star = (
        composite
        .scaffold_heptagram_candidate
    )

    moon_ids = [
        name
        for name, _
        in wall.moons
    ]

    wall_line_ids = [
        line.name
        for line in wall.lines
    ]

    wall_vertex_ids = [
        f"wall-vertex-{index:02d}"
        for index in range(
            len(
                wall.vertices
            )
        )
    ]

    sevenfold_ids = [
        f"sevenfold-point-{index:02d}"
        for index in range(7)
    ]

    fourteenfold_ids = [
        f"fourteenfold-point-{index:02d}"
        for index in range(14)
    ]

    four_triangle_ids = [
        f"four-triangle-mark-{index:02d}"
        for index in range(28)
    ]

    scaffold_ids = [
        f"scaffold-point-{index:02d}"
        for index in range(28)
    ]

    heptagram_vertex_ids = [
        f"heptagram-vertex-{index:02d}"
        for index in range(7)
    ]

    heptagram_edge_ids = [
        f"heptagram-edge-{index:02d}"
        for index in range(7)
    ]

    return (
        (
            "core",
            {
                "object_ids": [
                    "earth-circle",
                    "earth-square",
                    "construction-circle",
                ],
                "earth_diameter": (
                    dimensions
                    .earth_diameter
                ),
                "earth_radius": (
                    dimensions
                    .earth_radius
                ),
                "earth_square_side": (
                    dimensions
                    .earth_square_side
                ),
                "moon_diameter": (
                    dimensions
                    .moon_diameter
                ),
                "moon_radius": (
                    dimensions
                    .moon_radius
                ),
                "construction_radius": (
                    dimensions
                    .construction_radius
                ),
            },
        ),
        (
            "moon_system",
            {
                "object_ids": moon_ids,
                "moon_count": (
                    composite
                    .moon_count
                ),
                "model": (
                    wall.model.value
                ),
            },
        ),
        (
            "wall",
            {
                "polygon_object_id": (
                    "polar-pivot-wall"
                ),
                "line_object_ids": (
                    wall_line_ids
                ),
                "vertex_object_ids": (
                    wall_vertex_ids
                ),
                "side_lengths": list(
                    wall.side_lengths
                ),
                "perimeter": (
                    wall.perimeter
                ),
                "mean_side_length": (
                    wall
                    .mean_side_length
                ),
                "area": wall.area,
            },
        ),
        (
            "sevenfold",
            {
                "object_ids": (
                    sevenfold_ids
                ),
                "base_side": (
                    _enum_value(
                        sevenfold
                        .base_side
                    )
                ),
                "radius": (
                    sevenfold.radius
                ),
                "step_radians": (
                    sevenfold
                    .step_radians
                ),
                "step_degrees": (
                    degrees(
                        sevenfold
                        .step_radians
                    )
                ),
            },
        ),
        (
            "fourteenfold",
            {
                "object_ids": (
                    fourteenfold_ids
                ),
                "primary_base_side": (
                    _enum_value(
                        fourteenfold
                        .primary
                        .base_side
                    )
                ),
                "reciprocal_base_side": (
                    _enum_value(
                        fourteenfold
                        .reciprocal
                        .base_side
                    )
                ),
            },
        ),
        (
            "four_triangle_28",
            {
                "object_ids": (
                    four_triangle_ids
                ),
                (
                    "four_triangle_scaffold_"
                    "max_mismatch_radians"
                ): (
                    composite
                    .four_triangle_scaffold_max_mismatch_radians
                ),
            },
        ),
        (
            "scaffold_28",
            {
                "object_ids": (
                    scaffold_ids
                ),
                "radius": (
                    scaffold.radius
                ),
                "heptagon_step_radians": (
                    scaffold
                    .heptagon_step_radians
                ),
                "heptagon_step_degrees": (
                    scaffold
                    .heptagon_step_degrees
                ),
                "beta_radians": (
                    scaffold
                    .beta_radians
                ),
                "beta_degrees": (
                    scaffold
                    .beta_degrees
                ),
            },
        ),
        (
            "heptagram",
            {
                "vertex_object_ids": (
                    heptagram_vertex_ids
                ),
                "edge_object_ids": (
                    heptagram_edge_ids
                ),
                "family_step": (
                    star.family.value
                ),
                "traversal_indices": list(
                    star
                    .traversal_indices()
                ),
            },
        ),
    )


def build_michell_composite_geometry_export(
    composite: MichellComposite,
) -> MichellCompositeGeometryExport:
    """Build complete numerical geometry for one supplied composite."""

    coordinate_system = (
        (
            "dimension",
            2,
        ),
        (
            "geometry",
            "Euclidean",
        ),
        (
            "origin",
            {
                "x": (
                    composite
                    .core
                    .origin.x
                ),
                "y": (
                    composite
                    .core
                    .origin.y
                ),
            },
        ),
        (
            "positive_x",
            "right",
        ),
        (
            "positive_y",
            "up",
        ),
        (
            "angle_origin",
            "positive x-axis",
        ),
        (
            "angle_direction",
            "counter-clockwise",
        ),
        (
            "angle_units",
            [
                "radians",
                "degrees",
            ],
        ),
    )

    return (
        MichellCompositeGeometryExport(
            schema_name=(
                GEOMETRY_SCHEMA_NAME
            ),
            schema_version=(
                GEOMETRY_SCHEMA_VERSION
            ),
            model_name=(
                composite.model_name
            ),
            unit=composite.unit,
            coordinate_system=(
                coordinate_system
            ),
            sections=(
                _build_sections(
                    composite
                )
            ),
            objects=(
                _build_objects(
                    composite
                )
            ),
        )
    )


def michell_composite_geometry_to_json(
    geometry_export: MichellCompositeGeometryExport,
) -> str:
    """Serialize the complete geometry deterministically."""

    return (
        json.dumps(
            geometry_export.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


def write_michell_composite_geometry_json(
    geometry_export: MichellCompositeGeometryExport,
    output_path: str | Path,
) -> Path:
    """Write deterministic complete geometry JSON."""

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        michell_composite_geometry_to_json(
            geometry_export
        ),
        encoding="utf-8",
    )

    return path
