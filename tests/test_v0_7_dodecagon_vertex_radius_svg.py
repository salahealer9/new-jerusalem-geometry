from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.dodecagon_vertex_radius_audit import (
    build_vertex_radius_audit,
)
from new_jerusalem_geometry.dodecagon_vertex_radius_svg import (
    regular_baseline_svg,
    source_constraints_svg,
)


ROOT = Path(
    __file__
).resolve().parents[
    1
]

SOURCE_SVG = (
    ROOT
    / "figures"
    / "generated"
    / "sommerville_dodecagon_source_constraints.svg"
)

BASELINE_SVG = (
    ROOT
    / "figures"
    / "generated"
    / "sommerville_dodecagon_regular_baseline.svg"
)


def test_source_constraints_svg_is_deterministic() -> None:
    audit = (
        build_vertex_radius_audit()
    )

    assert (
        SOURCE_SVG.read_text(
            encoding="utf-8"
        )
        == source_constraints_svg(
            audit
        )
    )


def test_regular_baseline_svg_is_deterministic() -> None:
    audit = (
        build_vertex_radius_audit()
    )

    assert (
        BASELINE_SVG.read_text(
            encoding="utf-8"
        )
        == regular_baseline_svg(
            audit
        )
    )


def test_svgs_have_no_opaque_background_rectangle() -> None:
    for path in (
        SOURCE_SVG,
        BASELINE_SVG,
    ):
        text = path.read_text(
            encoding="utf-8"
        )

        assert (
            "<rect"
            not in text
        )


def test_source_svg_has_semantic_vertex_ids() -> None:
    text = SOURCE_SVG.read_text(
        encoding="utf-8"
    )

    for index in range(
        12
    ):
        assert (
            f'id="wall_vertex_{index:02d}"'
            in text
        )


def test_baseline_svg_has_vertex_correspondence_lines() -> None:
    text = BASELINE_SVG.read_text(
        encoding="utf-8"
    )

    for index in range(
        12
    ):
        assert (
            f'id="baseline-displacement-wall_vertex_{index:02d}"'
            in text
        )


def test_geometry_only_svgs_do_not_contain_exposed_dimensional_targets() -> None:
    text = (
        SOURCE_SVG.read_text(
            encoding="utf-8"
        )
        + "\n"
        + BASELINE_SVG.read_text(
            encoding="utf-8"
        )
    )

    banned = (
        "63" + "36",
        "63" + "00",
        "17" + "6:17" + "5",
        "316" + "80",
    )

    assert not any(
        token in text
        for token in banned
    )
