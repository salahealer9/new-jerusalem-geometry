from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

NODE_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

EDGE_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)


ALLOWED_NODE_TYPES = {
    "source_geometry",
    "derived_geometry",
    "construction",
    "auxiliary_geometry",
    "project_reconstruction",
    "bookkeeping",
    "project_inference",
    "composite_geometry",
    "project_candidate",
    "source_calibrated_result",
}


ALLOWED_RELATION_TYPES = {
    "parameterizes",
    "intersects",
    "extends",
    "constrains",
    "constructs_from",
    "tangent_constraint",
    "construction_domain",
    "repeats_fourfold",
    "locates_on",
    "role_correspondence",
    "selects_moon_centres",
    "selects_junctions",
    "defines_gap_bisectors",
    "combines",
    "selects",
    "connects",
    "candidate_correspondence",
}


ALLOWED_EVIDENCE_STATUSES = {
    "stated_exact",
    "stated_approximate",
    "conventional_exact",
    "project_derivation",
    "project_inference",
    "project_result",
    "project_idealisation",
    "external_reconstruction",
    "implementation_only",
    "hypothesis_to_test",
}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def test_construction_node_identifiers_are_unique() -> None:
    rows = _read(NODE_PATH)

    identifiers = [
        row["node_id"]
        for row in rows
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_construction_edge_identifiers_are_unique() -> None:
    rows = _read(EDGE_PATH)

    identifiers = [
        row["edge_id"]
        for row in rows
    ]

    assert len(identifiers) == len(
        set(identifiers)
    )


def test_construction_edges_reference_known_nodes() -> None:
    nodes = {
        row["node_id"]
        for row in _read(NODE_PATH)
    }

    for edge in _read(EDGE_PATH):
        assert edge["parent_node"] in nodes
        assert edge["child_node"] in nodes


def test_construction_vocabularies_are_controlled() -> None:
    for node in _read(NODE_PATH):
        assert (
            node["node_type"]
            in ALLOWED_NODE_TYPES
        )

    for edge in _read(EDGE_PATH):
        assert (
            edge["relation_type"]
            in ALLOWED_RELATION_TYPES
        )

        assert (
            edge["evidence_status"]
            in ALLOWED_EVIDENCE_STATUSES
        )


def test_construction_dependency_graph_is_acyclic() -> None:
    nodes = {
        row["node_id"]
        for row in _read(NODE_PATH)
    }

    graph: dict[str, list[str]] = defaultdict(
        list
    )

    indegree = {
        node: 0
        for node in nodes
    }

    for edge in _read(EDGE_PATH):
        parent = edge["parent_node"]
        child = edge["child_node"]

        graph[parent].append(
            child
        )

        indegree[child] += 1

    frontier = [
        node
        for node, degree
        in indegree.items()
        if degree == 0
    ]

    visited = 0

    while frontier:
        node = frontier.pop()
        visited += 1

        for child in graph[node]:
            indegree[child] -= 1

            if indegree[child] == 0:
                frontier.append(
                    child
                )

    assert visited == len(nodes)


CLAIM_MATRIX_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)


def _claim_ids(
    value: str,
) -> set[str]:
    return {
        item.strip()
        for item in value.split(";")
        if item.strip()
    }


def test_construction_claim_references_exist() -> None:
    claim_rows = _read(
        CLAIM_MATRIX_PATH
    )

    known_claims = {
        row["claim_id"]
        for row in claim_rows
    }

    referenced_claims: set[str] = set()

    for node in _read(NODE_PATH):
        referenced_claims.update(
            _claim_ids(
                node["claim_ids"]
            )
        )

    for edge in _read(EDGE_PATH):
        referenced_claims.update(
            _claim_ids(
                edge["claim_ids"]
            )
        )

    unknown = (
        referenced_claims
        - known_claims
    )

    assert unknown == set()
