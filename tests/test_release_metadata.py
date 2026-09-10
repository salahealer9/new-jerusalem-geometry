from __future__ import annotations

from pathlib import Path
import re
import tomllib

import new_jerusalem_geometry as njg


ROOT = Path(__file__).resolve().parents[1]


def test_v100_version_metadata_is_consistent() -> None:
    expected = "1.0.0"

    assert njg.__version__ == expected

    with (
        ROOT
        / "pyproject.toml"
    ).open(
        "rb"
    ) as handle:
        pyproject = tomllib.load(
            handle
        )

    assert (
        pyproject["project"]["version"]
        == expected
    )

    citation = (
        ROOT
        / "CITATION.cff"
    ).read_text(
        encoding="utf-8"
    )

    match = re.search(
        r'^version:\s*"([^"]+)"$',
        citation,
        flags=re.MULTILINE,
    )

    assert match is not None
    assert match.group(1) == expected

    # The v0.9 release date must not survive the v1.0 metadata bump.
    # The actual v1.0 date is inserted only in the final signed release
    # commit on main, immediately before the signed v1.0.0 tag.
    assert 'date-released: "2026-08-10"' not in citation


def test_v040_checkpoint_records_frozen_validation_boundary() -> None:
    checkpoint = (
        ROOT
        / "docs"
        / "checkpoints"
        / "v0.4.0.md"
    ).read_text(
        encoding="utf-8"
    )

    assert (
        "43096326d5c1862fc7e33f9d90eb1df861c3b642"
        in checkpoint
    )

    assert (
        "frozen forward validation with no refitting"
        in checkpoint
    )

    assert (
        "217 passed"
        in checkpoint
    )

    assert (
        "0.031023606 u"
        in checkpoint
    )

    assert (
        "-0.379134 percent"
        in checkpoint
    )
