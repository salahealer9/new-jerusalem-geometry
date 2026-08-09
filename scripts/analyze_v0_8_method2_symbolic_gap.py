#!/usr/bin/env python3
"""Generate the v0.8 post-result Method 2 symbolic gap audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from new_jerusalem_geometry.method2_symbolic_gap import (
    PHASE8C_LOCAL_COMPARISON_SHA256,
    PHASE8E_PROPAGATION_JSON_SHA256,
    SPECIFICATION_SHA256,
    build_method2_symbolic_gap_audit,
    method2_symbolic_gap_audit_to_json,
    method2_symbolic_gap_audit_to_markdown,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

SPECIFICATION = (
    ROOT
    / "docs"
    / "specification"
    / "v0.8_method2_symbolic_gap_audit.md"
)

PROPAGATION_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "method2_propagation.json"
)

LOCAL_COMPARISON_JSON = (
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
    / "method2_symbolic_gap_audit.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.8_method2_symbolic_gap_audit_result.md"
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
            SPECIFICATION
        )
        != SPECIFICATION_SHA256
    ):
        raise AssertionError(
            "Phase 8F explanatory specification hash changed."
        )

    if (
        sha256(
            PROPAGATION_JSON
        )
        != PHASE8E_PROPAGATION_JSON_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 8E propagation JSON hash changed."
        )

    if (
        sha256(
            LOCAL_COMPARISON_JSON
        )
        != PHASE8C_LOCAL_COMPARISON_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 8C local comparison JSON hash changed."
        )

    propagation_payload = json.loads(
        PROPAGATION_JSON.read_text(
            encoding="utf-8"
        )
    )

    local_payload = json.loads(
        LOCAL_COMPARISON_JSON.read_text(
            encoding="utf-8"
        )
    )

    audit = (
        build_method2_symbolic_gap_audit(
            propagation_payload,
            local_payload,
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
        method2_symbolic_gap_audit_to_json(
            audit
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        method2_symbolic_gap_audit_to_markdown(
            audit
        ),
        encoding="utf-8",
    )

    print(
        "v0.8 Method 2 symbolic gap-structure audit"
    )
    print(
        "Evidential status:",
        audit.evidential_status,
    )
    print(
        "Stopping status:",
        audit.stopping_status,
    )
    print(
        "delta degrees:",
        audit.delta_degrees,
    )
    print(
        "21 pattern:",
        audit.twenty_one.class_pattern_base,
        "x",
        audit.twenty_one.class_pattern_repetitions,
    )
    print(
        "21 classes:",
        [
            (
                row.class_label,
                row.a_pi_over_3,
                row.b_alpha,
                row.count,
                row.delta_residual_coefficient,
            )
            for row
            in audit.twenty_one.signature_classes
        ],
    )
    print(
        "42 pattern:",
        audit.forty_two.class_pattern_base,
        "x",
        audit.forty_two.class_pattern_repetitions,
    )
    print(
        "42 classes:",
        [
            (
                row.class_label,
                row.a_pi_over_3,
                row.b_alpha,
                row.count,
                row.delta_residual_coefficient,
            )
            for row
            in audit.forty_two.signature_classes
        ],
    )
    print(
        "RMS coefficients:",
        audit.twenty_one.rms_delta_coefficient_symbolic,
        audit.forty_two.rms_delta_coefficient_symbolic,
    )
    print(
        "raw RMS ratio:",
        audit.cross_relations.raw_rms_ratio_symbolic,
        audit.cross_relations.raw_rms_ratio_frozen,
    )
    print(
        "max ratio:",
        audit.cross_relations.max_abs_ratio_symbolic,
        audit.cross_relations.max_abs_ratio_frozen,
    )
    print(
        "normalized RMS ratio:",
        audit.cross_relations.normalized_rms_ratio_symbolic,
        audit.cross_relations.normalized_rms_ratio_frozen,
    )
    print(
        "21 range/closure error rad:",
        audit.cross_relations
        .twenty_one_range_vs_closure_absolute_error_radians,
    )
    print(
        "42 range/closure error rad:",
        audit.cross_relations
        .forty_two_range_vs_closure_absolute_error_radians,
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
