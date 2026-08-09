#!/usr/bin/env python3
"""Generate the preregistered v0.8 Method 2 7 -> 21 -> 42 propagation."""

from __future__ import annotations

import hashlib
from math import pi
from pathlib import Path

from new_jerusalem_geometry.method2_propagation import (
    METHOD2_SOURCE_SHA256,
    PHASE8C_LOCAL_COMPARISON_SHA256,
    PROTOCOL_SHA256,
    build_method2_propagation,
    method2_propagation_to_json,
    method2_propagation_to_markdown,
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
    / "v0.8_method2_propagation_protocol.md"
)

METHOD2_SOURCE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "sevenfold_dual_method.py"
)

PHASE8C_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_method2_propagation_result.md"
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

    method2_sha = sha256(
        METHOD2_SOURCE
    )

    phase8c_json_sha = sha256(
        PHASE8C_JSON
    )

    if (
        protocol_sha
        != PROTOCOL_SHA256
    ):
        raise AssertionError(
            (
                "Phase 8D protocol hash changed",
                protocol_sha,
                PROTOCOL_SHA256,
            )
        )

    if (
        method2_sha
        != METHOD2_SOURCE_SHA256
    ):
        raise AssertionError(
            (
                "Frozen Phase 8C Method 2 source hash changed",
                method2_sha,
                METHOD2_SOURCE_SHA256,
            )
        )

    if (
        phase8c_json_sha
        != PHASE8C_LOCAL_COMPARISON_SHA256
    ):
        raise AssertionError(
            (
                "Frozen Phase 8C comparison JSON hash changed",
                phase8c_json_sha,
                PHASE8C_LOCAL_COMPARISON_SHA256,
            )
        )

    result = (
        build_method2_propagation()
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
        method2_propagation_to_json(
            result
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        method2_propagation_to_markdown(
            result
        ),
        encoding="utf-8",
    )

    deg = (
        180.0
        / pi
    )

    print(
        "v0.8 preregistered Method 2 propagation"
    )
    print(
        "Stopping status:",
        result.stopping_status,
    )
    print(
        "alpha_2:",
        result.alpha_2_radians
        * deg,
        "deg",
    )
    print(
        "local seven marks:",
        result.local_seven.semantic_count,
    )
    print(
        "21 semantic/distinct:",
        result.twenty_one.semantic_count,
        result.twenty_one.numerical_distinct_count,
    )
    print(
        "S2 rotation 2pi/3:",
        result.twenty_one_structural_checks
        .rotational_identity_2pi_over_3,
    )
    print(
        "S3 reciprocal rotation pi/3:",
        result.reciprocal_twenty_one
        .rotated_original_identity_pi_over_3,
    )
    print(
        "42 semantic/distinct:",
        result.forty_two.semantic_count,
        result.forty_two.numerical_distinct_count,
    )
    print(
        "S4 union:",
        result.forty_two_structural_checks
        .union_identity,
    )
    print(
        "S5 rotation pi/3:",
        result.forty_two_structural_checks
        .rotational_identity_pi_over_3,
    )
    print(
        "21 gap min/max:",
        result.twenty_one.minimum_gap_radians
        * deg,
        result.twenty_one.maximum_gap_radians
        * deg,
        "deg",
    )
    print(
        "21 RMS/max abs residual:",
        result.twenty_one.rms_gap_residual_radians
        * deg,
        result.twenty_one.maximum_absolute_gap_residual_radians
        * deg,
        "deg",
    )
    print(
        "21 normalized RMS:",
        result.twenty_one.normalized_rms_gap_residual,
    )
    print(
        "42 gap min/max:",
        result.forty_two.minimum_gap_radians
        * deg,
        result.forty_two.maximum_gap_radians
        * deg,
        "deg",
    )
    print(
        "42 RMS/max abs residual:",
        result.forty_two.rms_gap_residual_radians
        * deg,
        result.forty_two.maximum_absolute_gap_residual_radians
        * deg,
        "deg",
    )
    print(
        "42 normalized RMS:",
        result.forty_two.normalized_rms_gap_residual,
    )
    print(
        "RMS ratio 42/21:",
        result.comparison.rms_ratio_42_over_21,
    )
    print(
        "Max-abs ratio 42/21:",
        result.comparison.max_abs_ratio_42_over_21,
    )
    print(
        "RMS order:",
        result.comparison.rms_order,
    )
    print(
        "Max-abs order:",
        result.comparison.maximum_absolute_residual_order,
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
