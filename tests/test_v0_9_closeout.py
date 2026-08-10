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

NODES = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_construction_extension_nodes.csv"
)

EDGES = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_construction_extension_dependencies.csv"
)

GRAMMAR = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_construction_extension_grammar.md"
)

CENTRAL_NODES = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

CENTRAL_EDGES = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

CENTRAL_GRAMMAR = (
    ROOT
    / "docs"
    / "specification"
    / "construction_grammar.md"
)

SYNTHESIS = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_exact_sevenfold_boundary_and_extension_synthesis.md"
)

CHECKPOINT = (
    ROOT
    / "docs"
    / "checkpoints"
    / "v0.9.0.md"
)

README = (
    ROOT
    / "README.md"
)


FROZEN = {
    ROOT
    / "docs"
    / "specification"
    / "v0.9_exact_sevenfold_constructibility_protocol.md": (
        "ac50f47c4a57000a831958b4e4738153"
        "3768ed8cebe1d40d309e5c66e3aa2d22"
    ),
    ROOT
    / "docs"
    / "specification"
    / "v0.9_native_incidence_registry.md": (
        "e26b1725d44ce2454324b97d4b63d11e"
        "e8e371cfabef64c1f2da3bb7835cfc35"
    ),
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_sevenfold_boundary.json": (
        "cc150e2c92efdebe130f86f2c03998336"
        "883abb985513e8e634977682c84442f"
    ),
    ROOT
    / "docs"
    / "specification"
    / "v0.9_one_trisection_heptagon_protocol.md": (
        "d125a37b1764c6dee558b36279dc45cf"
        "a10b2df6627d76ebecfba6b727fe629c"
    ),
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "one_trisection_heptagon.json": (
        "f82d8fc9307ac12cb9541f24c090500d"
        "6ac7784bb11eb673eb89c9f2cb433dad"
    ),
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_heptagon_synthesis.json": (
        "2d1b686f3fa9fdce3b5f218688bc15e7"
        "f538251a57865b5ff759f6f7dffdcfec"
    ),
    ROOT
    / "figures"
    / "generated"
    / "v0.9_exact_heptagon_synthesis.svg": (
        "4123b737b33d277531bf4b4a89ece680"
        "cbd0d0ab70393c0beb3abbc2f9df3eb9"
    ),
}


FROZEN_V08_GRAMMAR = {
    CENTRAL_NODES: (
        "5c13a735882ebb27c4e1b942bea605cf"
        "76d76f996c486ca049325d7246735bc7"
    ),
    CENTRAL_EDGES: (
        "cdb8f7fc881851e2c52ba84fec5f2f80"
        "c51e45193c47eef4f11f6e42512657a5"
    ),
    CENTRAL_GRAMMAR: (
        "3f2d7a4cb879565509be05dbc71f6cc8"
        "b5d8d57c54a7f7324393c9f71fe25110"
    ),
}


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


def test_v090_package_version() -> None:
    assert (
        njg.__version__
        == "0.9.0"
    )


def test_frozen_v09_artifacts_are_byte_identical() -> None:
    for path, digest in FROZEN.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_frozen_v08_central_grammar_is_byte_identical() -> None:
    for path, digest in FROZEN_V08_GRAMMAR.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_v09_additive_registry_contains_project_extension_nodes() -> None:
    nodes = {
        row[
            "node_id"
        ]: row
        for row
        in _csv_rows(
            NODES
        )
    }

    assert set(
        nodes
    ) == {
        "EXACT_SEVENFOLD_BOUNDARY",
        "TRISECT_ANGLE_EXTENSION",
        "EXACT_HEPTAGON_7",
    }

    assert (
        nodes[
            "EXACT_SEVENFOLD_BOUNDARY"
        ][
            "node_type"
        ]
        == "validation_result"
    )

    assert (
        nodes[
            "TRISECT_ANGLE_EXTENSION"
        ][
            "node_type"
        ]
        == "construction"
    )

    assert (
        nodes[
            "EXACT_HEPTAGON_7"
        ][
            "node_type"
        ]
        == "derived_geometry"
    )

    assert all(
        row[
            "claim_ids"
        ]
        == ""
        for row
        in nodes.values()
    )


def test_v09_additive_registry_contains_boundary_extension_edges() -> None:
    edges = {
        row[
            "edge_id"
        ]: row
        for row
        in _csv_rows(
            EDGES
        )
    }

    expected = {
        "V09-DEP-001": (
            "CONSTRUCTION_CIRCLE",
            "EXACT_SEVENFOLD_BOUNDARY",
            "validated_by",
        ),
        "V09-DEP-002": (
            "CORE_DIMENSIONS",
            "TRISECT_ANGLE_EXTENSION",
            "parameterizes",
        ),
        "V09-DEP-003": (
            "EXACT_SEVENFOLD_BOUNDARY",
            "TRISECT_ANGLE_EXTENSION",
            "extends",
        ),
        "V09-DEP-004": (
            "TRISECT_ANGLE_EXTENSION",
            "EXACT_HEPTAGON_7",
            "constructs_from",
        ),
        "V09-DEP-005": (
            "CONSTRUCTION_CIRCLE",
            "EXACT_HEPTAGON_7",
            "locates_on",
        ),
    }

    assert set(
        edges
    ) == set(
        expected
    )

    for identifier, (
        parent,
        child,
        relation,
    ) in expected.items():
        row = edges[
            identifier
        ]

        assert (
            row[
                "parent_node"
            ]
            == parent
        )

        assert (
            row[
                "child_node"
            ]
            == child
        )

        assert (
            row[
                "relation_type"
            ]
            == relation
        )


def test_v09_additive_grammar_marks_extension_as_project_only() -> None:
    text = GRAMMAR.read_text(
        encoding="utf-8"
    )

    required = (
        "# v0.9 exact-sevenfold project-extension grammar",
        "does **not** modify the frozen central construction grammar",
        "EXACT_SEVENFOLD_BOUNDARY",
        "TRISECT_ANGLE_EXTENSION",
        "EXACT_HEPTAGON_7",
        "explicitly a PROJECT construction extension",
        "zero cubic-capable operations",
        "one cubic-capable operation",
        "No node or dependency",
    )

    for phrase in required:
        assert phrase in text


def test_v09_synthesis_records_core_result() -> None:
    text = SYNTHESIS.read_text(
        encoding="utf-8"
    )

    required = (
        "# v0.9 Exact Sevenfold Boundary and Minimal Cubic Extension",
        "y^3 + y^2 - 2*y - 1",
        "EUCLIDEAN_EXACT_SEVENFOLD_EXCLUDED",
        "NO_NATIVE_EXACT_SEVENFOLD",
        "TRISECT_ANGLE",
        "ONE_TRISECTION_EXACT_HEPTAGON_CONFIRMED",
        "MINIMUM_ONE_CUBIC_CAPABLE_OPERATION_WITHIN_FROZEN_MODEL",
        "Method 2 < exact < Method 1",
        "not statistically independent validation",
        "Post-result renderer-only corrections",
        "central construction grammar remains frozen",
        "v0.9_construction_extension_nodes.csv",
    )

    for phrase in required:
        assert phrase in text


def test_v09_checkpoint_records_release_boundary() -> None:
    text = CHECKPOINT.read_text(
        encoding="utf-8"
    )

    required = (
        "# v0.9.0 Exact Sevenfold Boundary and Minimal Cubic Extension",
        "d986a18",
        "76397ad",
        "83dba52",
        "fb11105",
        "c684f28",
        "EUCLIDEAN_EXACT_SEVENFOLD_EXCLUDED",
        "ONE_TRISECTION_EXACT_HEPTAGON_CONFIRMED",
        "MINIMUM_ONE_CUBIC_CAPABLE_OPERATION_WITHIN_FROZEN_MODEL",
        "4123b737b33d277531bf4b4a89ece680",
        "v0.9_construction_extension_nodes.csv",
    )

    for phrase in required:
        assert phrase in text


def test_readme_exposes_v09_without_historical_overclaim() -> None:
    text = README.read_text(
        encoding="utf-8"
    )

    required = (
        "Version `v0.9.0`",
        "Exact Sevenfold Boundary and Minimal Cubic Extension",
        "EUCLIDEAN_EXACT_SEVENFOLD_EXCLUDED",
        "ONE_TRISECTION_EXACT_HEPTAGON_CONFIRMED",
        "MINIMUM_ONE_CUBIC_CAPABLE_OPERATION_WITHIN_FROZEN_MODEL",
        "not attributed",
        "source-consistency synthesis",
        "Version `v0.8.0` remains the historical Figure 194",
    )

    for phrase in required:
        assert phrase in text


def test_closeout_does_not_make_positive_historical_exact_claims() -> None:
    combined = (
        SYNTHESIS.read_text(
            encoding="utf-8"
        )
        + "\n"
        + CHECKPOINT.read_text(
            encoding="utf-8"
        )
        + "\n"
        + README.read_text(
            encoding="utf-8"
        )
    ).lower()

    forbidden = (
        "michell's exact heptagon construction",
        "sommerville's exact heptagon construction",
        "michell encoded the exact heptagon",
        "sommerville encoded the exact heptagon",
        "ancient exact-heptagon construction established",
        "proves angle trisection is uniquely simplest",
        "angle trisection is the uniquely simplest",
    )

    for phrase in forbidden:
        assert phrase not in combined



def test_v09_release_hook_is_narrow_and_version_scoped() -> None:
    conftest = (
        ROOT
        / "tests"
        / "conftest.py"
    )

    source = conftest.read_text(
        encoding="utf-8"
    )

    expected_fragments = (
        "test_v0_9_exact_heptagon_synthesis.py::",
        "test_v0_9_one_trisection_heptagon.py::",
        "test_v0_9_one_trisection_heptagon_protocol.py::",
        "test_v0_9_exact_sevenfold_boundary.py::",
        "test_v0_9_exact_sevenfold_constructibility_protocol.py::",
        "test_v0_8_closeout.py::",
    )

    for fragment in expected_fragments:
        assert fragment in source

    assert (
        source.count(
            "tests/test_"
        )
        == 15
    )

    assert (
        "njg.__version__"
        in source
    )

    assert (
        '"0.9.0"'
        in source
    )

    assert (
        "pytest.mark.skip"
        in source
    )
