#!/usr/bin/env python3
"""Generate the frozen Phase 9D one-trisection exact-heptagon result."""

from __future__ import annotations

import hashlib
from pathlib import Path

from new_jerusalem_geometry.one_trisection_heptagon import (
    PHASE9C_PROTOCOL_SHA256,
    PHASE9C_PROTOCOL_TEST_SHA256,
    build_one_trisection_audit,
    one_trisection_audit_to_json,
    one_trisection_audit_to_markdown,
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
    / "v0.9_one_trisection_heptagon_protocol.md"
)

PROTOCOL_TEST = (
    ROOT
    / "tests"
    / "test_v0_9_one_trisection_heptagon_protocol.py"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "one_trisection_heptagon.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_one_trisection_heptagon_result.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main() -> int:
    assert (
        _sha256(
            PROTOCOL
        )
        == PHASE9C_PROTOCOL_SHA256
    )

    assert (
        _sha256(
            PROTOCOL_TEST
        )
        == PHASE9C_PROTOCOL_TEST_SHA256
    )

    audit = (
        build_one_trisection_audit()
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
        one_trisection_audit_to_json(
            audit
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        one_trisection_audit_to_markdown(
            audit
        ),
        encoding="utf-8",
    )

    construction = (
        audit.construction
    )

    print(
        "v0.9 one-trisection exact-heptagon audit"
    )
    print(
        "Stopping status:",
        audit.stopping_status,
    )
    print(
        "TRISECT_ANGLE calls:",
        construction.cubic.trisection_call_count,
    )
    print(
        "Theta degrees:",
        construction.anchor.theta_degrees,
    )
    print(
        "Phi degrees:",
        construction.cubic.phi_degrees,
    )
    print(
        "Constructed y:",
        construction.cubic.y,
    )
    print(
        "Constructed c=y/2:",
        construction.cubic.c,
    )
    print(
        "Exact target identification:",
        audit.exact_target_identification,
    )
    print(
        "Numeric y-target residual:",
        audit.target_numeric_residual,
    )
    print(
        "Numeric angle residual radians:",
        audit.target_angle_residual_radians,
    )
    print(
        "Max radius residual:",
        audit.max_radius_residual,
    )
    print(
        "Side-length range:",
        audit.side_length_range,
    )
    print(
        "Seven-step closure residual:",
        audit.seven_step_closure_residual,
    )
    print(
        "Criteria passed:",
        sum(
            criterion.passed
            for criterion in audit.criteria
        ),
        "/",
        len(
            audit.criteria
        ),
    )
    print(
        "Minimality:",
        audit.minimality_status,
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
        _sha256(
            JSON_OUT
        ),
    )
    print(
        "Markdown SHA256:",
        _sha256(
            MARKDOWN_OUT
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
