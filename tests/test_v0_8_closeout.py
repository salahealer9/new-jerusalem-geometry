from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import new_jerusalem_geometry as njg


ROOT = Path(
    __file__
).resolve().parents[
    1
]

CLAIMS = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)

SOURCE_AUDIT = (
    ROOT
    / "docs"
    / "sources"
    / "v0.8_sevenfold_dual_method_source_audit.md"
)

NODES = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

EDGES = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

GRAMMAR = (
    ROOT
    / "docs"
    / "specification"
    / "construction_grammar.md"
)

SYNTHESIS = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_figure194_dual_method_synthesis.md"
)

CHECKPOINT = (
    ROOT
    / "docs"
    / "checkpoints"
    / "v0.8.0.md"
)

README = (
    ROOT
    / "README.md"
)

COMPOSITE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "michell_composite.py"
)

DUAL_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
)

PROPAGATION_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

SYMBOLIC_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_symbolic_gap_audit.json"
)

SVG = (
    ROOT
    / "figures"
    / "generated"
    / "v0.8_method2_7_21_42.svg"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _csv_rows(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(
                handle
            )
        )


def test_v080_package_version() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )


def test_frozen_source_claim_matrix_is_byte_identical() -> None:
    assert (
        _sha256(
            CLAIMS
        )
        == "c3ac054a93c73e42ebf915fe8d43768e90008495c8dc3f369894c5969ef8ed10"
    )


def test_frozen_phase8a_source_audit_is_byte_identical() -> None:
    assert (
        _sha256(
            SOURCE_AUDIT
        )
        == "48a7892bb7be5ebd1b0cfdc2e66f0de7a4f380b6926d7a1799c6693e7dd441b4"
    )


def test_frozen_v08_analysis_artifacts_are_byte_identical() -> None:
    expected = {
        DUAL_JSON: (
            "e5de2cf65eaeac7884d11a3617479a52"
            "a3aeefa28e45bd89cd3fe4e6172e396f"
        ),
        PROPAGATION_JSON: (
            "5af0b893ef9f18f5bb6c04e013f12298"
            "d816f426a2a248eccbd9230ab5ad4a43"
        ),
        SYMBOLIC_JSON: (
            "db314c890636a2a435d4065a42c49c08"
            "bba8df00c7e29a2cca156b00eef47078"
        ),
        SVG: (
            "11477e6db0ac662dd82d5cb23c73147c"
            "039683148720cecb56f39fc8cd8ee9a1"
        ),
    }

    for path, digest in expected.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_grammar_contains_distinct_method2_branch() -> None:
    nodes = {
        row[
            "node_id"
        ]: row
        for row
        in _csv_rows(
            NODES
        )
    }

    assert (
        nodes[
            "SEPTENARY_METHOD_2"
        ][
            "implementation_reference"
        ]
        == "sevenfold_dual_method"
    )

    assert (
        nodes[
            "METHOD2_21"
        ][
            "implementation_reference"
        ]
        == "method2_propagation"
    )

    assert (
        nodes[
            "METHOD2_42"
        ][
            "implementation_reference"
        ]
        == "method2_propagation"
    )


def test_grammar_has_source_described_7_21_42_edges() -> None:
    edges = {
        row[
            "edge_id"
        ]: row
        for row
        in _csv_rows(
            EDGES
        )
    }

    assert (
        edges[
            "DEP-032"
        ][
            "parent_node"
        ]
        == "CONSTRUCTION_CIRCLE"
    )

    assert (
        edges[
            "DEP-032"
        ][
            "child_node"
        ]
        == "SEPTENARY_METHOD_2"
    )

    assert (
        edges[
            "DEP-033"
        ][
            "parent_node"
        ]
        == "SEPTENARY_METHOD_2"
    )

    assert (
        edges[
            "DEP-033"
        ][
            "child_node"
        ]
        == "METHOD2_21"
    )

    assert (
        edges[
            "DEP-034"
        ][
            "parent_node"
        ]
        == "METHOD2_21"
    )

    assert (
        edges[
            "DEP-034"
        ][
            "child_node"
        ]
        == "METHOD2_42"
    )

    assert all(
        edges[
            identifier
        ][
            "evidence_status"
        ]
        == "stated_approximate"
        for identifier in (
            "DEP-032",
            "DEP-033",
            "DEP-034",
        )
    )


def test_method2_is_not_silently_inserted_into_njg_michell() -> None:
    source = COMPOSITE.read_text(
        encoding="utf-8"
    ).lower()

    forbidden = (
        "method2_propagation",
        "method2_symbolic_gap",
        "sevenfold_dual_method",
        "method2_21",
        "method2_42",
    )

    for token in forbidden:
        assert token not in source


def test_grammar_markdown_preserves_dual_branch_boundary() -> None:
    text = GRAMMAR.read_text(
        encoding="utf-8"
    )

    required = (
        "## v0.8 Figure 194 dual-method branch",
        "SEPTENARY_METHOD_2",
        "METHOD2_21",
        "METHOD2_42",
        "continues to use Method 1",
        "No grammar edge combines, averages, ranks, or optimizes",
    )

    for phrase in required:
        assert phrase in text


def test_synthesis_records_core_v08_findings() -> None:
    text = SYNTHESIS.read_text(
        encoding="utf-8"
    )

    required = (
        "Method 1",
        "Method 2",
        "alpha_2 = acos(5/8)",
        "alpha_2 < alpha_exact < alpha_1",
        "RMS_21   = sqrt(10)*delta",
        "RMS_42   = sqrt(6)*delta",
        "RMS_42 / RMS_21",
        "sqrt(3/5)",
        "post-result explanatory",
        "28-point versus Method 2 42-point ranking remains deferred",
    )

    for phrase in required:
        assert phrase in text


def test_checkpoint_records_release_boundary() -> None:
    text = CHECKPOINT.read_text(
        encoding="utf-8"
    )

    required = (
        "# v0.8.0 Figure 194 dual-method construction checkpoint",
        "d30a384",
        "a36daab",
        "05e8a89",
        "11b023e",
        "058a934",
        "767c61f",
        "da3fb63",
        "post-result explanatory derivation",
        "figures/generated/v0.8_method2_7_21_42.svg",
    )

    for phrase in required:
        assert phrase in text


def test_readme_exposes_v08_without_overclaiming() -> None:
    text = README.read_text(
        encoding="utf-8"
    )

    required = (
        "Version `v0.8.0`",
        "Method 1: 7 -> 14 -> 28",
        "Method 2: 7 -> 21 -> 42",
        "alpha_2 = acos(5/8)",
        "post-result explanatory",
        "visualization-only",
    )

    for phrase in required:
        assert phrase in text


def test_no_combined_method_claim_in_closeout_docs() -> None:
    combined = (
        SYNTHESIS.read_text(
            encoding="utf-8"
        )
        + "\n"
        + CHECKPOINT.read_text(
            encoding="utf-8"
        )
    ).lower()

    forbidden = (
        "michell's averaged method",
        "michell averaged the methods",
        "intentional compensation mechanism",
        "method 2 replaces method 1",
    )

    for phrase in forbidden:
        assert phrase not in combined
