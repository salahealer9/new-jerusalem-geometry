#!/usr/bin/env python3
"""Generate the frozen v0.8 Method 2 7 -> 21 -> 42 SVG."""

from __future__ import annotations

import hashlib
from pathlib import Path

from new_jerusalem_geometry.method2_propagation_svg import (
    PROPAGATION_SHA256,
    SYMBOLIC_AUDIT_SHA256,
    write_method2_propagation_svg,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

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

OUTPUT = (
    ROOT
    / "figures"
    / "generated"
    / "v0.8_method2_7_21_42.svg"
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
            PROPAGATION_JSON
        )
        != PROPAGATION_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 8E propagation JSON hash changed."
        )

    if (
        sha256(
            SYMBOLIC_JSON
        )
        != SYMBOLIC_AUDIT_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 8F symbolic-audit JSON hash changed."
        )

    write_method2_propagation_svg(
        PROPAGATION_JSON,
        SYMBOLIC_JSON,
        OUTPUT,
    )

    print(
        "Wrote:",
        OUTPUT.relative_to(
            ROOT
        ),
    )

    print(
        "SVG SHA256:",
        sha256(
            OUTPUT
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
