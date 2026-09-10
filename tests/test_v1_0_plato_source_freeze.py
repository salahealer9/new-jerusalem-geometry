from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIR = (
    ROOT
    / "data"
    / "sources"
    / "v1_0"
    / "plato"
)

FREEZE = (
    SOURCE_DIR
    / "source_freeze.json"
)

MANIFEST = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_source_manifest.csv"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _record() -> dict:
    return json.loads(
        FREEZE.read_text(
            encoding="utf-8"
        )
    )


def test_plato_source_freeze_exists() -> None:
    assert FREEZE.is_file()


def test_plato_source_freeze_status() -> None:
    record = _record()

    assert (
        record[
            "status"
        ]
        == "PLATO_PRIMARY_WITNESSES_FROZEN"
    )

    assert (
        record[
            "work_urn"
        ]
        == "urn:cts:greekLit:tlg0059.tlg030"
    )


def test_plato_source_freeze_is_pinned_to_git_commit() -> None:
    record = _record()

    commit = record[
        "upstream_commit"
    ]

    assert re.fullmatch(
        r"[0-9a-f]{40}",
        commit,
    )

    for witness in record[
        "witnesses"
    ]:
        assert (
            commit
            in witness[
                "upstream_url"
            ]
        )

        assert (
            "/master/"
            not in witness[
                "upstream_url"
            ]
        )


def test_plato_frozen_witness_hashes_match() -> None:
    record = _record()

    assert (
        len(
            record[
                "witnesses"
            ]
        )
        == 2
    )

    for witness in record[
        "witnesses"
    ]:
        path = (
            ROOT
            / witness[
                "local_path"
            ]
        )

        assert path.is_file()

        assert (
            _sha256(
                path
            )
            == witness[
                "sha256"
            ]
        )


def test_plato_freeze_has_expected_cts_witnesses() -> None:
    record = _record()

    urns = {
        witness[
            "cts_urn"
        ]
        for witness in record[
            "witnesses"
        ]
    }

    assert urns == {
        (
            "urn:cts:greekLit:"
            "tlg0059.tlg030.perseus-eng2"
        ),
        (
            "urn:cts:greekLit:"
            "tlg0059.tlg030.perseus-grc2"
        ),
    }


def test_plato_xml_witnesses_are_well_formed_tei() -> None:
    import xml.etree.ElementTree as ET

    record = _record()

    expected_names = {
        "tlg0059.tlg030.perseus-eng2.xml",
        "tlg0059.tlg030.perseus-grc2.xml",
    }

    observed_names = set()

    for witness in record[
        "witnesses"
    ]:
        path = (
            ROOT
            / witness[
                "local_path"
            ]
        )

        observed_names.add(
            path.name
        )

        tree = ET.parse(
            path
        )

        root = tree.getroot()

        assert (
            root.tag.endswith(
                "TEI"
            )
        )

        assert (
            path.stat().st_size
            > 1000
        )

    assert (
        observed_names
        == expected_names
    )


def test_plato_manifest_promotes_only_plato_source() -> None:
    with MANIFEST.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    by_id = {
        row[
            "source_id"
        ]: row
        for row in rows
    }

    assert (
        by_id[
            "PLATO_REPUBLIC_MYTH_OF_ER"
        ][
            "current_status"
        ]
        == "pending_freeze"
    )

    assert (
        by_id[
            "MICHELL_DIMENSIONS_OF_PARADISE"
        ][
            "current_status"
        ]
        == "pending_freeze"
    )


def test_plato_freeze_does_not_promote_michell_or_project_claims() -> None:
    record = _record()

    assert (
        record[
            "claim_boundary"
        ][
            "allowed"
        ]
        == [
            "DIRECT_PLATO_TEXT",
        ]
    )

    assert (
        "MICHELL_EXPLICIT"
        in record[
            "claim_boundary"
        ][
            "not_yet_allowed"
        ]
    )

    assert (
        "PROJECT_RECONSTRUCTION"
        in record[
            "claim_boundary"
        ][
            "not_yet_allowed"
        ]
    )
