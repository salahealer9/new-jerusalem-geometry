from __future__ import annotations

from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]

FREEZE = (
    ROOT
    / "data"
    / "provenance"
    / "njg_michell_v1_0"
    / "michell_dimensions_paradise_2008_source_freeze.json"
)

PHASE10A_PROTOCOL = (
    ROOT
    / "docs"
    / "specification"
    / "v1.0_plato_historical_source_protocol.md"
)

PHASE10A_MANIFEST = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_source_manifest.csv"
)

PHASE10A_TEST = (
    ROOT
    / "tests"
    / "test_v1_0_plato_historical_source_protocol.py"
)


def _record() -> dict:
    return json.loads(
        FREEZE.read_text(
            encoding="utf-8"
        )
    )


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_michell_2008_source_freeze_exists() -> None:
    assert FREEZE.is_file()


def test_michell_2008_source_status_and_class() -> None:
    record = _record()

    assert (
        record[
            "status"
        ]
        == (
            "MICHELL_2008_CHAPTER4_"
            "SOURCE_WITNESS_FROZEN"
        )
    )

    assert (
        record[
            "provenance_class"
        ]
        == "MICHELL_EXPLICIT"
    )


def test_michell_2008_bibliographic_identity() -> None:
    identity = _record()[
        "bibliographic_identity"
    ]

    assert (
        identity[
            "author"
        ]
        == "John Michell"
    )

    assert (
        identity[
            "title"
        ]
        == "The Dimensions of Paradise"
    )

    assert (
        identity[
            "edition"
        ]
        == "Second U.S. edition"
    )

    assert (
        identity[
            "publisher"
        ]
        == "Inner Traditions"
    )

    assert (
        identity[
            "publication_year"
        ]
        == 2008
    )

    assert (
        identity[
            "isbn_13"
        ]
        == "978-1-59477-773-8"
    )


def test_michell_2008_chapter_scope() -> None:
    scope = _record()[
        "chapter_scope"
    ]

    assert (
        scope[
            "chapter_number"
        ]
        == 4
    )

    assert (
        scope[
            "chapter_title"
        ]
        == "The Cities of Plato"
    )

    assert (
        scope[
            "ebook_page_range"
        ]
        == "121-193 of 248"
    )

    assert (
        scope[
            "chapter_screenshot_count"
        ]
        == 79
    )

    assert (
        scope[
            "frontmatter_screenshot_count"
        ]
        == 9
    )

    assert (
        scope[
            "total_screenshot_count"
        ]
        == 88
    )


def test_michell_2008_source_hash_boundary() -> None:
    record = _record()

    assert (
        record[
            "source_storage"
        ][
            "bundle_sha256"
        ]
        == (
            "f662aa6221a4ceb232025569fc501ca66"
            "13ebbdc6b44394d6631eec7e5a7137d"
        )
    )

    assert (
        record[
            "source_storage"
        ][
            "bundle_manifest_sha256"
        ]
        == (
            "ed60002c9afd98db27e615198c1429de"
            "a6f70d6b2cc7d02377d032f779d9746c"
        )
    )

    assert (
        record[
            "chapter_archive"
        ][
            "sha256"
        ]
        == (
            "d0f722a81df4f91165ed529460c4e5f7"
            "c00682e75feb16f20cb85915c2d6bb92"
        )
    )


def test_michell_2008_source_bytes_are_not_committed() -> None:
    record = _record()

    assert (
        record[
            "source_storage"
        ][
            "repository_contains_source_bytes"
        ]
        is False
    )

    assert (
        record[
            "source_storage"
        ][
            "local_reference"
        ].startswith(
            ".local_sources/"
        )
    )


def test_michell_2008_freeze_defers_extraction() -> None:
    boundary = _record()[
        "claim_boundary"
    ]

    assert (
        boundary[
            "allowed"
        ]
        == [
            "SOURCE_IDENTITY",
            "SOURCE_PROVENANCE",
            "SOURCE_SCOPE",
        ]
    )

    assert (
        "MICHELL_LITERAL_EXTRACTION"
        in boundary[
            "deferred"
        ]
    )

    assert (
        "PROJECT_RECONSTRUCTION"
        in boundary[
            "deferred"
        ]
    )


def test_phase10a_surfaces_remain_frozen() -> None:
    assert (
        _sha256(
            PHASE10A_PROTOCOL
        )
        == (
            "5890ff8aca969eff96a227be1a2be9ad2"
            "ac420c64b6b9739404f34750127bed5"
        )
    )

    assert (
        _sha256(
            PHASE10A_MANIFEST
        )
        == (
            "a1a2e4f62126d11853372ae26949393d"
            "55f7bec75e37a0f640179dfdf7553d79"
        )
    )

    assert (
        _sha256(
            PHASE10A_TEST
        )
        == (
            "2fa6c834d329de4c493a7566e620eabc"
            "3eaef338c2d18c6a1c14af8171535050"
        )
    )


def test_frontmatter_hash_inventory_has_nine_unique_entries() -> None:
    items = _record()[
        "frontmatter"
    ]

    assert (
        len(
            items
        )
        == 9
    )

    hashes = {
        item[
            "sha256"
        ]
        for item in items
    }

    assert (
        len(
            hashes
        )
        == 9
    )


def test_copyright_page_is_in_frontmatter_inventory() -> None:
    items = _record()[
        "frontmatter"
    ]

    matches = [
        item
        for item in items
        if (
            item[
                "role"
            ]
            == "copyright_and_cip"
        )
    ]

    assert (
        len(
            matches
        )
        == 1
    )

    assert (
        matches[
            0
        ][
            "sha256"
        ]
        == (
            "669623adfc95e1dccb7319186e8b3108"
            "1729e3c6d732ad4283951c7d3342f6a8"
        )
    )
