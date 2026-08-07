"""Deterministic provenance manifest for the NJG_MICHELL composite.

The provenance layer describes an already constructed ``MichellComposite``.

It does not construct geometry and does not assign independent evidence
statuses to geometric objects. Evidential interpretation remains in the
existing construction grammar and geometric claim matrix.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .michell_composite import MichellComposite


PROVENANCE_SCHEMA_NAME = "njg_michell_provenance"
PROVENANCE_SCHEMA_VERSION = "1.0"

NODES_SOURCE_ID = (
    "docs/specification/construction_nodes.csv"
)
DEPENDENCIES_SOURCE_ID = (
    "docs/specification/construction_dependencies.csv"
)
CLAIMS_SOURCE_ID = (
    "docs/sources/geometric_claim_matrix.csv"
)


AttributeValue = str | int | float | bool


@dataclass(frozen=True, slots=True)
class ProvenanceObject:
    """Provenance record for one computational geometric object."""

    object_id: str
    geometry_type: str
    grammar_nodes: tuple[str, ...]
    role: str | None = None
    source_object_ids: tuple[str, ...] = ()
    rendered_svg_id: str | None = None
    attributes: tuple[
        tuple[str, AttributeValue],
        ...,
    ] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible representation."""

        return {
            "object_id": self.object_id,
            "geometry_type": self.geometry_type,
            "grammar_nodes": list(
                self.grammar_nodes
            ),
            "role": self.role,
            "source_object_ids": list(
                self.source_object_ids
            ),
            "rendered_svg_id": (
                self.rendered_svg_id
            ),
            "attributes": dict(
                self.attributes
            ),
        }


@dataclass(frozen=True, slots=True)
class GrammarSnapshot:
    """Relevant construction grammar and claim records."""

    nodes: tuple[dict[str, str], ...]
    dependencies: tuple[
        dict[str, str],
        ...,
    ]
    claims: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a deterministic JSON-compatible representation."""

        return {
            "nodes": [
                dict(row)
                for row in self.nodes
            ],
            "dependencies": [
                dict(row)
                for row in self.dependencies
            ],
            "claims": [
                dict(row)
                for row in self.claims
            ],
        }


@dataclass(frozen=True, slots=True)
class MichellCompositeProvenance:
    """Complete provenance manifest for one NJG_MICHELL composite."""

    schema_name: str
    schema_version: str
    model_name: str
    unit: float
    source_hashes: tuple[
        tuple[str, str],
        ...,
    ]
    objects: tuple[
        ProvenanceObject,
        ...,
    ]
    grammar_snapshot: GrammarSnapshot

    @property
    def object_count(self) -> int:
        return len(
            self.objects
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the canonical JSON-compatible manifest."""

        return {
            "schema_name": self.schema_name,
            "schema_version": (
                self.schema_version
            ),
            "model_name": self.model_name,
            "unit": self.unit,
            "source_hashes": dict(
                self.source_hashes
            ),
            "object_count": (
                self.object_count
            ),
            "objects": [
                record.to_dict()
                for record in self.objects
            ],
            "grammar_snapshot": (
                self.grammar_snapshot.to_dict()
            ),
        }


def _read_csv(
    path: str | Path,
) -> list[dict[str, str]]:
    with Path(path).open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def _sha256(
    path: str | Path,
) -> str:
    digest = hashlib.sha256()

    with Path(path).open(
        "rb"
    ) as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(
                block
            )

    return digest.hexdigest()


def _claim_ids(
    value: str,
) -> set[str]:
    return {
        item.strip()
        for item in value.split(";")
        if item.strip()
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


def _moon_group_context(
    composite: MichellComposite,
) -> dict[str, tuple[str, str]]:
    """Map each Moon name to cardinal group and role."""

    context: dict[
        str,
        tuple[str, str],
    ] = {}

    for group in composite.moon_groups:
        members = (
            (
                "clockwise_outer",
                group.clockwise_outer,
            ),
            (
                "cardinal",
                group.cardinal,
            ),
            (
                "counterclockwise_outer",
                group.counterclockwise_outer,
            ),
        )

        for role, member in members:
            name, _ = member

            if name in context:
                raise ValueError(
                    "Moon appears in more than one "
                    f"group: {name}"
                )

            context[name] = (
                group.direction,
                role,
            )

    if len(context) != 12:
        raise ValueError(
            "Expected twelve uniquely grouped "
            "Moon circles."
        )

    return context


def _star_scaffold_indices(
    composite: MichellComposite,
) -> tuple[int, ...]:
    """Resolve each star vertex to its unique scaffold point."""

    scaffold_points = (
        composite.scaffold.points
    )

    result: list[int] = []

    for vertex in (
        composite
        .scaffold_heptagram_candidate
        .vertices
    ):
        matches = [
            index
            for index, point
            in enumerate(
                scaffold_points
            )
            if point.point == vertex
        ]

        if len(matches) != 1:
            raise ValueError(
                "Each scaffold-derived heptagram "
                "vertex must match exactly one "
                "scaffold point."
            )

        result.append(
            matches[0]
        )

    return tuple(
        result
    )


def _build_object_records(
    composite: MichellComposite,
) -> tuple[ProvenanceObject, ...]:
    """Build the deterministic object-level provenance inventory."""

    records: list[
        ProvenanceObject
    ] = []

    records.append(
        ProvenanceObject(
            object_id=(
                "njg-michell-composite"
            ),
            geometry_type="composite",
            grammar_nodes=(
                "NJG_MICHELL_COMPOSITE",
            ),
            role="composite_root",
            rendered_svg_id=(
                "njg-michell-composite"
            ),
        )
    )

    records.extend(
        (
            ProvenanceObject(
                object_id="earth-circle",
                geometry_type="circle",
                grammar_nodes=(
                    "EARTH_CIRCLE",
                ),
                role="earth_circle",
                rendered_svg_id=(
                    "earth-circle"
                ),
            ),
            ProvenanceObject(
                object_id="earth-square",
                geometry_type="square",
                grammar_nodes=(
                    "EARTH_SQUARE",
                ),
                role="earth_square",
                rendered_svg_id=(
                    "earth-square"
                ),
            ),
            ProvenanceObject(
                object_id=(
                    "construction-circle"
                ),
                geometry_type="circle",
                grammar_nodes=(
                    "CONSTRUCTION_CIRCLE",
                ),
                role=(
                    "construction_circle"
                ),
                rendered_svg_id=(
                    "construction-circle"
                ),
            ),
        )
    )

    moon_context = (
        _moon_group_context(
            composite
        )
    )

    for moon_name, _moon in (
        composite
        .wall_reconstruction
        .moons
    ):
        group_direction, group_role = (
            moon_context[
                moon_name
            ]
        )

        if group_role == "cardinal":
            grammar_nodes = (
                "CARDINAL_MOONS",
                "NJG_INC_MOONS",
                "MOON_GROUPS_4X3",
            )
            role = "cardinal_moon"
        else:
            grammar_nodes = (
                "NJG_INC_MOONS",
                "MOON_GROUPS_4X3",
            )
            role = "oblique_moon"

        records.append(
            ProvenanceObject(
                object_id=moon_name,
                geometry_type="circle",
                grammar_nodes=(
                    grammar_nodes
                ),
                role=role,
                rendered_svg_id=(
                    moon_name
                ),
                attributes=(
                    (
                        "moon_name",
                        moon_name,
                    ),
                    (
                        "moon_group",
                        group_direction,
                    ),
                    (
                        "moon_group_role",
                        group_role,
                    ),
                ),
            )
        )

    wall_vertex_ids = tuple(
        f"wall-vertex-{index:02d}"
        for index in range(
            len(
                composite
                .wall_reconstruction
                .vertices
            )
        )
    )

    records.append(
        ProvenanceObject(
            object_id=(
                "polar-pivot-wall"
            ),
            geometry_type="polygon",
            grammar_nodes=(
                "POLAR_PIVOT_WALL",
            ),
            role="outer_wall",
            source_object_ids=(
                wall_vertex_ids
            ),
            rendered_svg_id=(
                "polar-pivot-wall"
            ),
        )
    )

    for index, line in enumerate(
        composite
        .wall_reconstruction
        .lines
    ):
        records.append(
            ProvenanceObject(
                object_id=line.name,
                geometry_type="line",
                grammar_nodes=(
                    "POLAR_PIVOT_WALL",
                ),
                role="wall_line",
                source_object_ids=(
                    line.moon_name,
                ),
                attributes=(
                    (
                        "wall_index",
                        index,
                    ),
                    (
                        "wall_moon_name",
                        line.moon_name,
                    ),
                ),
            )
        )

    for index, _vertex in enumerate(
        composite
        .wall_reconstruction
        .vertices
    ):
        records.append(
            ProvenanceObject(
                object_id=(
                    f"wall-vertex-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                grammar_nodes=(
                    "POLAR_PIVOT_WALL",
                ),
                role="wall_vertex",
                attributes=(
                    (
                        "wall_vertex_index",
                        index,
                    ),
                ),
            )
        )

    for index, _point in enumerate(
        composite.sevenfold.points
    ):
        records.append(
            ProvenanceObject(
                object_id=(
                    f"sevenfold-point-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                grammar_nodes=(
                    "SEPTENARY_METHOD_1",
                ),
                role="sevenfold_point",
                attributes=(
                    (
                        "sevenfold_index",
                        index,
                    ),
                    (
                        "triangle_base",
                        _enum_value(
                            composite
                            .sevenfold
                            .base_side
                        ),
                    ),
                ),
            )
        )

    for index, _point in enumerate(
        composite.fourteenfold.points
    ):
        records.append(
            ProvenanceObject(
                object_id=(
                    f"fourteenfold-point-"
                    f"{index:02d}"
                ),
                geometry_type="point",
                grammar_nodes=(
                    "RECIPROCAL_TRIANGLE_14",
                ),
                role=(
                    "fourteenfold_point"
                ),
                attributes=(
                    (
                        "fourteenfold_index",
                        index,
                    ),
                ),
            )
        )

    for index, _angle in enumerate(
        composite
        .four_triangle_angles_radians
    ):
        records.append(
            ProvenanceObject(
                object_id=(
                    f"four-triangle-mark-"
                    f"{index:02d}"
                ),
                geometry_type=(
                    "angular_mark"
                ),
                grammar_nodes=(
                    "SCAFFOLD_28",
                ),
                role=(
                    "four_triangle_angular_mark"
                ),
                attributes=(
                    (
                        "angular_mark_index",
                        index,
                    ),
                ),
            )
        )

    for index, point in enumerate(
        composite.scaffold.points
    ):
        object_id = (
            f"scaffold-point-"
            f"{index:02d}"
        )

        records.append(
            ProvenanceObject(
                object_id=object_id,
                geometry_type="point",
                grammar_nodes=(
                    "SCAFFOLD_28",
                ),
                role=point.role.value,
                rendered_svg_id=(
                    object_id
                ),
                attributes=(
                    (
                        "scaffold_index",
                        index,
                    ),
                    (
                        "scaffold_role",
                        point.role.value,
                    ),
                ),
            )
        )

    scaffold_indices = (
        _star_scaffold_indices(
            composite
        )
    )

    for vertex_index, scaffold_index in (
        enumerate(
            scaffold_indices
        )
    ):
        object_id = (
            f"heptagram-vertex-"
            f"{vertex_index:02d}"
        )

        records.append(
            ProvenanceObject(
                object_id=object_id,
                geometry_type="point",
                grammar_nodes=(
                    "FIG14_SCAFFOLD_VERTICES",
                ),
                role="heptagram_vertex",
                source_object_ids=(
                    (
                        f"scaffold-point-"
                        f"{scaffold_index:02d}"
                    ),
                ),
                rendered_svg_id=(
                    object_id
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
                ),
            )
        )

    edge_pairs = (
        composite
        .scaffold_heptagram_candidate
        .edge_index_pairs()
    )

    for edge_index, (
        start_index,
        end_index,
    ) in enumerate(
        edge_pairs
    ):
        object_id = (
            f"heptagram-edge-"
            f"{edge_index:02d}"
        )

        records.append(
            ProvenanceObject(
                object_id=object_id,
                geometry_type="line",
                grammar_nodes=(
                    "FIG14_HEPTAGRAM_7_2",
                ),
                role="heptagram_edge",
                source_object_ids=(
                    (
                        f"heptagram-vertex-"
                        f"{start_index:02d}"
                    ),
                    (
                        f"heptagram-vertex-"
                        f"{end_index:02d}"
                    ),
                ),
                rendered_svg_id=(
                    object_id
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
                ),
            )
        )

    identifiers = [
        record.object_id
        for record in records
    ]

    if len(identifiers) != len(
        set(identifiers)
    ):
        raise ValueError(
            "Provenance object identifiers "
            "must be unique."
        )

    known_objects = set(
        identifiers
    )

    unknown_sources = {
        source_id
        for record in records
        for source_id
        in record.source_object_ids
        if source_id not in known_objects
    }

    if unknown_sources:
        raise ValueError(
            "Unknown provenance source "
            f"objects: {sorted(unknown_sources)}"
        )

    return tuple(
        records
    )


def _build_grammar_snapshot(
    objects: tuple[
        ProvenanceObject,
        ...,
    ],
    *,
    node_rows: list[
        dict[str, str]
    ],
    dependency_rows: list[
        dict[str, str]
    ],
    claim_rows: list[
        dict[str, str]
    ],
) -> GrammarSnapshot:
    """Build the ancestor-closed grammar snapshot."""

    nodes_by_id = {
        row["node_id"]: row
        for row in node_rows
    }

    referenced_nodes = {
        node_id
        for record in objects
        for node_id
        in record.grammar_nodes
    }

    unknown_nodes = (
        referenced_nodes
        - nodes_by_id.keys()
    )

    if unknown_nodes:
        raise ValueError(
            "Unknown construction-grammar "
            f"nodes: {sorted(unknown_nodes)}"
        )

    included_nodes = set(
        referenced_nodes
    )

    changed = True

    while changed:
        changed = False

        for edge in dependency_rows:
            child = edge[
                "child_node"
            ]
            parent = edge[
                "parent_node"
            ]

            if (
                child in included_nodes
                and parent
                not in included_nodes
            ):
                included_nodes.add(
                    parent
                )
                changed = True

    selected_nodes = tuple(
        dict(row)
        for row in node_rows
        if row["node_id"]
        in included_nodes
    )

    selected_dependencies = tuple(
        dict(row)
        for row in dependency_rows
        if (
            row["parent_node"]
            in included_nodes
            and row["child_node"]
            in included_nodes
        )
    )

    wanted_claims: set[str] = set()

    for row in selected_nodes:
        wanted_claims.update(
            _claim_ids(
                row["claim_ids"]
            )
        )

    for row in selected_dependencies:
        wanted_claims.update(
            _claim_ids(
                row["claim_ids"]
            )
        )

    claims_by_id = {
        row["claim_id"]: row
        for row in claim_rows
    }

    unknown_claims = (
        wanted_claims
        - claims_by_id.keys()
    )

    if unknown_claims:
        raise ValueError(
            "Unknown geometric claim "
            f"identifiers: {sorted(unknown_claims)}"
        )

    selected_claims = tuple(
        dict(row)
        for row in claim_rows
        if row["claim_id"]
        in wanted_claims
    )

    return GrammarSnapshot(
        nodes=selected_nodes,
        dependencies=(
            selected_dependencies
        ),
        claims=selected_claims,
    )


def build_michell_composite_provenance(
    composite: MichellComposite,
    *,
    construction_nodes_path: str | Path,
    construction_dependencies_path: str | Path,
    claim_matrix_path: str | Path,
) -> MichellCompositeProvenance:
    """Build provenance for one supplied NJG_MICHELL composite."""

    objects = _build_object_records(
        composite
    )

    node_rows = _read_csv(
        construction_nodes_path
    )

    dependency_rows = _read_csv(
        construction_dependencies_path
    )

    claim_rows = _read_csv(
        claim_matrix_path
    )

    snapshot = _build_grammar_snapshot(
        objects,
        node_rows=node_rows,
        dependency_rows=(
            dependency_rows
        ),
        claim_rows=claim_rows,
    )

    source_hashes = (
        (
            NODES_SOURCE_ID,
            _sha256(
                construction_nodes_path
            ),
        ),
        (
            DEPENDENCIES_SOURCE_ID,
            _sha256(
                construction_dependencies_path
            ),
        ),
        (
            CLAIMS_SOURCE_ID,
            _sha256(
                claim_matrix_path
            ),
        ),
    )

    return MichellCompositeProvenance(
        schema_name=(
            PROVENANCE_SCHEMA_NAME
        ),
        schema_version=(
            PROVENANCE_SCHEMA_VERSION
        ),
        model_name=(
            composite.model_name
        ),
        unit=composite.unit,
        source_hashes=source_hashes,
        objects=objects,
        grammar_snapshot=snapshot,
    )


def michell_composite_provenance_to_json(
    provenance: MichellCompositeProvenance,
) -> str:
    """Serialize provenance deterministically."""

    return (
        json.dumps(
            provenance.to_dict(),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n"
    )


def write_michell_composite_provenance_json(
    provenance: MichellCompositeProvenance,
    output_path: str | Path,
) -> Path:
    """Write deterministic NJG_MICHELL provenance JSON."""

    path = Path(
        output_path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        michell_composite_provenance_to_json(
            provenance
        ),
        encoding="utf-8",
    )

    return path
