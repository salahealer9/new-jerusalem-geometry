#!/usr/bin/env python3
"""Generate the preregistered v0.8 local dual-method comparison."""

from __future__ import annotations

import hashlib
from math import pi
from pathlib import Path

from new_jerusalem_geometry.sevenfold_dual_method import (
    PHASE8A_SOURCE_AUDIT_SHA256,
    PROTOCOL_SHA256,
    build_dual_method_comparison,
    dual_method_comparison_to_json,
    dual_method_comparison_to_markdown,
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
    / "v0.8_dual_method_numerical_comparison_protocol.md"
)

PHASE8A_SOURCE_AUDIT = (
    ROOT
    / "docs"
    / "sources"
    / "v0.8_sevenfold_dual_method_source_audit.md"
)

METHOD1_SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "septenary_geometry.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_dual_method_comparison_result.md"
)


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main() -> int:
    protocol_sha = sha256(
        PROTOCOL
    )

    source_audit_sha = sha256(
        PHASE8A_SOURCE_AUDIT
    )

    method1_sha = sha256(
        METHOD1_SOURCE
    )

    if (
        protocol_sha
        != PROTOCOL_SHA256
    ):
        raise AssertionError(
            (
                "Phase 8B protocol hash changed: ",
                protocol_sha,
                PROTOCOL_SHA256,
            )
        )

    if (
        source_audit_sha
        != PHASE8A_SOURCE_AUDIT_SHA256
    ):
        raise AssertionError(
            (
                "Phase 8A source-audit hash changed: ",
                source_audit_sha,
                PHASE8A_SOURCE_AUDIT_SHA256,
            )
        )

    protocol_text = PROTOCOL.read_text(
        encoding="utf-8"
    )

    if (
        method1_sha
        not in protocol_text
    ):
        raise AssertionError(
            "Current Method 1 source hash is not frozen "
            "inside the Phase 8B protocol."
        )

    result = (
        build_dual_method_comparison(
            method1_source_sha256=(
                method1_sha
            ),
        )
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
        dual_method_comparison_to_json(
            result
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        dual_method_comparison_to_markdown(
            result
        ),
        encoding="utf-8",
    )

    degrees = (
        180.0
        / pi
    )

    print(
        "v0.8 preregistered local dual-method comparison"
    )
    print(
        "Stopping status:",
        result.stopping_status,
    )
    print(
        "Exact step:",
        result.alpha_exact_radians
        * degrees,
        "deg",
    )
    print(
        "Method 1:",
        result.method_1.alpha_radians
        * degrees,
        "deg",
    )
    print(
        "Method 1 signed residual:",
        result.method_1.signed_residual_radians
        * degrees,
        "deg",
    )
    print(
        "Method 2:",
        result.method_2.alpha_radians
        * degrees,
        "deg",
    )
    print(
        "Method 2 signed residual:",
        result.method_2.signed_residual_radians
        * degrees,
        "deg",
    )
    print(
        "R1 bracketing:",
        result.relationships.bracketing,
    )
    print(
        "R2 opposite signed errors:",
        result.relationships.opposite_signed_errors,
    )
    print(
        "R3 absolute accuracy order:",
        result.relationships.absolute_accuracy_order,
    )
    print(
        "R4 |error2|/|error1|:",
        result.relationships.absolute_error_ratio,
    )
    print(
        "R5 midpoint signed residual:",
        result.exploratory.midpoint_signed_residual_radians
        * degrees,
        "deg",
    )
    print(
        "Method 2 identity error:",
        result.implementation_checks
        .method_2_identity_absolute_error_radians,
        "rad",
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
