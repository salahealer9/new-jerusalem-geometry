#!/usr/bin/env python3
"""Generate the frozen v0.9 exact-heptagon synthesis artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path

from new_jerusalem_geometry.exact_heptagon_synthesis import (
    PHASE9E_PROTOCOL_SHA256,
    build_exact_heptagon_synthesis,
    synthesis_to_json,
    synthesis_to_markdown,
    synthesis_to_svg,
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
    / "v0.9_exact_heptagon_synthesis_protocol.md"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_9"
    / "exact_heptagon_synthesis.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v0.9_exact_heptagon_synthesis.md"
)

SVG_OUT = (
    ROOT
    / "figures"
    / "generated"
    / "v0.9_exact_heptagon_synthesis.svg"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def main() -> int:
    if (
        _sha256(
            PROTOCOL
        )
        != PHASE9E_PROTOCOL_SHA256
    ):
        raise AssertionError(
            "Frozen Phase 9E synthesis protocol hash changed."
        )

    synthesis = (
        build_exact_heptagon_synthesis(
            root=ROOT
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

    SVG_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUT.write_text(
        synthesis_to_json(
            synthesis
        ),
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        synthesis_to_markdown(
            synthesis
        ),
        encoding="utf-8",
    )

    SVG_OUT.write_text(
        synthesis_to_svg(
            synthesis
        ),
        encoding="utf-8",
    )

    scaffold = (
        synthesis.scaffold_aggregate
    )

    plate = (
        synthesis.figure14_plate_aggregate
    )

    print(
        "v0.9 exact-heptagon comparison and visual synthesis"
    )
    print(
        "Stopping status:",
        synthesis.stopping_status,
    )
    print(
        "Fixed orientation degrees:",
        synthesis.fixed_orientation_degrees,
    )
    print(
        "Orientation fit applied:",
        synthesis.orientation_fit_applied,
    )
    print(
        "Exact vertex angles degrees:",
        ", ".join(
            f"{value:.9f}"
            for value in synthesis.exact_vertex_angles_degrees
        ),
    )
    print()
    print(
        "Step comparisons:"
    )

    for row in synthesis.step_comparisons:
        print(
            " ",
            row.method_id,
            f"step={row.step_degrees:.12f}",
            f"residual={row.signed_residual_degrees:+.12f}",
            f"closure={row.seven_step_closure_degrees:+.12f}",
        )

    print()
    print(
        "Scaffold angular RMS degrees:",
        scaffold.angular_rms_degrees,
    )
    print(
        "Scaffold angular maximum degrees:",
        scaffold.angular_maximum_degrees,
    )
    print(
        "Scaffold Euclidean RMS u:",
        scaffold.euclidean_rms_u,
    )
    print(
        "Scaffold Euclidean RMS model ft:",
        scaffold.euclidean_rms_model_feet,
    )
    print()
    print(
        "Figure 14 plate angular RMS degrees:",
        plate.angular_rms_degrees,
    )
    print(
        "Figure 14 plate angular maximum degrees:",
        plate.angular_maximum_degrees,
    )
    print(
        "Figure 14 plate radial RMS u:",
        plate.radial_rms_u,
    )
    print(
        "Figure 14 plate Euclidean RMS u:",
        plate.euclidean_rms_u,
    )
    print(
        "Figure 14 plate Euclidean RMS model ft:",
        plate.euclidean_rms_model_feet,
    )
    print()
    print(
        "Wall comparison performed:",
        synthesis.context.wall_comparison_performed,
    )
    print(
        "Interpretation:",
        synthesis.interpretation_status,
    )
    print()
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
        "SVG:",
        SVG_OUT.relative_to(
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
    print(
        "SVG SHA256:",
        _sha256(
            SVG_OUT
        ),
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
