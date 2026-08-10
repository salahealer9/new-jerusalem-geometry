#!/usr/bin/env python3
"""Generate the v0.9 exact-sevenfold Euclidean/native-incidence audit."""

from __future__ import annotations

import hashlib
from pathlib import Path

from new_jerusalem_geometry.exact_sevenfold_boundary import (
    PROTOCOL_SHA256,
    REGISTRY_SPEC_SHA256,
    build_exact_sevenfold_boundary_audit,
    exact_sevenfold_boundary_to_json,
    exact_sevenfold_boundary_to_markdown,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

PROTOCOL = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_exact_sevenfold_constructibility_protocol.md"
)

REGISTRY_SPEC = (
    ROOT
    / "docs"
    / "specification"
    / "v0.9_native_incidence_registry.md"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_sevenfold_boundary.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_exact_sevenfold_boundary_result.md"
)


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main() -> int:
    if (
        sha256(
            PROTOCOL
        )
        != PROTOCOL_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 9A protocol hash changed."
        )

    if (
        sha256(
            REGISTRY_SPEC
        )
        != REGISTRY_SPEC_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 9B registry specification hash changed."
        )

    audit = (
        build_exact_sevenfold_boundary_audit()
    )

    JSON_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MARKDOWN_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUT.write_text(
        exact_sevenfold_boundary_to_json(
            audit
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        exact_sevenfold_boundary_to_markdown(
            audit
        ),
        encoding="utf-8",
    )

    p = audit.polynomial_audit
    c = audit.census

    print(
        "v0.9 exact-sevenfold boundary audit"
    )
    print(
        "Stopping status:",
        audit.stopping_status,
    )
    print(
        "Target polynomial:",
        p.polynomial_text,
    )
    print(
        "Target algebraic degree:",
        p.algebraic_degree,
    )
    print(
        "Irreducible over Q:",
        p.irreducible_over_q,
    )
    print(
        "Euclidean closure:",
        audit.euclidean_closure_status,
    )
    print(
        "N0 lineage checks:",
        len(
            audit.n0_seed_lineage_checks
        ),
    )
    print(
        "N1 lineage checks:",
        len(
            audit.n1_seed_lineage_checks
        ),
        "(finite census disabled)",
    )
    print(
        "Radial directions:",
        c.radial_direction_count,
    )
    print(
        "Pairwise radial separations:",
        c.pairwise_separation_count,
    )
    print(
        "Native line directions:",
        c.native_line_count,
    )
    print(
        "Semantic candidates:",
        c.candidate_count_semantic,
    )
    print(
        "Target-injected reference classes excluded:",
        c.target_injected_candidate_count_excluded,
    )
    print(
        "Exact native candidates:",
        c.exact_candidate_count,
    )
    print(
        "Native-incidence status:",
        c.native_incidence_status,
    )
    print(
        "Closest descriptive candidate:",
        c.closest_descriptive_candidate_id,
    )
    print(
        "Closest descriptive angle degrees:",
        c.closest_descriptive_angle_degrees,
    )
    print(
        "Closest descriptive residual degrees:",
        c.closest_descriptive_residual_degrees,
    )
    print(
        "Question C:",
        audit.question_c_status,
    )
    print(
        "JSON:",
        JSON_OUT.relative_to(
            ROOT
        ),
    )
    print(
        "Markdown:",
        MARKDOWN_OUT.relative_to(
            ROOT
        ),
    )
    print(
        "JSON SHA256:",
        sha256(
            JSON_OUT
        ),
    )
    print(
        "Markdown SHA256:",
        sha256(
            MARKDOWN_OUT
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
