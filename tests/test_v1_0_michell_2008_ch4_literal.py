from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "extract_v1_0_michell_2008_ch4_literal.py"
)

JSON_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "michell_2008_ch4_literal.json"
)

MARKDOWN_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_michell_2008_ch4_literal_extraction.md"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _payload() -> dict:
    return json.loads(
        JSON_PATH.read_text(
            encoding="utf-8"
        )
    )


def _load_script_module():
    spec = importlib.util.spec_from_file_location(
        "michell_literal_phase10d",
        SCRIPT,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def test_phase10d_status_and_provenance() -> None:
    payload = _payload()

    assert (
        payload[
            "status"
        ]
        == (
            "MICHELL_2008_CH4_LITERAL_"
            "NUMERICAL_EXTRACTION_COMPLETE"
        )
    )

    assert (
        payload[
            "provenance_class"
        ]
        == "MICHELL_EXPLICIT"
    )


def test_phase10d_source_bundle_boundary() -> None:
    method = _payload()[
        "extraction_method"
    ]

    assert (
        method[
            "source_bundle_sha256"
        ]
        == (
            "f662aa6221a4ceb232025569fc501ca66"
            "13ebbdc6b44394d6631eec7e5a7137d"
        )
    )

    assert (
        method[
            "chapter_archive_sha256"
        ]
        == (
            "d0f722a81df4f91165ed529460c4e5f7"
            "c00682e75feb16f20cb85915c2d6bb92"
        )
    )

    assert (
        method[
            "manual_visual_extraction"
        ]
        is True
    )

    assert (
        method[
            "ocr_used"
        ]
        is False
    )

    assert (
        method[
            "source_bytes_committed_to_git"
        ]
        is False
    )


def test_phase10d_source_capture_hashes() -> None:
    captures = {
        item[
            "observation_id"
        ]: item
        for item in _payload()[
            "extraction_method"
        ][
            "source_captures"
        ]
    }

    expected = {
        "M08-P164-WHORL-TABLE": (
            164,
            (
                "857036985aefd737dd9a034a61b4d6a5"
                "27cf20126010fdc1d0a8d41099a2bf6c"
            ),
        ),
        "M08-P165-MUSICAL-SEQUENCE": (
            165,
            (
                "92905f19098445d37bfa721174938ffd"
                "75ae0791ee5fbc63ae17d6769699752a"
            ),
        ),
        "M08-P167-CONSTRUCTION-A": (
            167,
            (
                "573922b187d816a96a1fa95c00e65c0a"
                "f104d21997fcf21cca955de12d70cd7c"
            ),
        ),
        "M08-P167-CONSTRUCTION-B": (
            167,
            (
                "745bc278e09a39ef08633da271297882"
                "46c9e555bac036f3ba1785fbd05942a5"
            ),
        ),
    }

    assert set(captures) == set(expected)

    for key, (
        page,
        digest,
    ) in expected.items():
        assert (
            captures[
                key
            ][
                "ebook_page"
            ]
            == page
        )

        assert (
            captures[
                key
            ][
                "sha256"
            ]
            == digest
        )


def test_phase10d_michell_width_order_table() -> None:
    table = _payload()[
        "michell_explicit"
    ][
        "plato_whorl_table"
    ]

    assert (
        table[
            "width_rank_by_whorl"
        ]
        == {
            "1": 1,
            "2": 8,
            "3": 7,
            "4": 3,
            "5": 6,
            "6": 2,
            "7": 5,
            "8": 4,
        }
    )

    assert (
        table[
            "broadest_to_narrowest_whorl_order"
        ]
        == [
            1,
            6,
            4,
            8,
            7,
            5,
            3,
            2,
        ]
    )


def test_phase10d_musical_sequence_is_michell_explicit() -> None:
    musical = _payload()[
        "michell_explicit"
    ][
        "musical_argument"
    ]

    assert (
        musical[
            "canonical_voice_range_used"
        ]
        == "two octaves and a fifth"
    )

    assert (
        musical[
            "greek_musical_proportion_invoked"
        ]
        == [
            6,
            8,
            9,
            12,
        ]
    )

    assert (
        musical[
            "base_sequence"
        ]
        == [
            6,
            8,
            9,
            12,
            18,
            24,
            27,
            36,
        ]
    )

    assert (
        musical[
            "successive_interval_ratios"
        ]
        == [
            "4/3",
            "9/8",
            "4/3",
            "3/2",
            "4/3",
            "9/8",
            "4/3",
        ]
    )

    assert (
        musical[
            "octave_only_interpretation_described_as_not_stated_or_implied_by_plato"
        ]
        is True
    )


def test_phase10d_unscaled_construction() -> None:
    construction = _payload()[
        "michell_explicit"
    ][
        "unscaled_construction"
    ]

    assert (
        construction[
            "shaft_first_sequence_number"
        ]
        == 6
    )

    assert (
        construction[
            "shaft_musical_factor"
        ]
        == "2/3"
    )

    assert (
        construction[
            "shaft_radius"
        ]
        == 4
    )

    assert (
        construction[
            "full_radius"
        ]
        == 144
    )

    assert (
        construction[
            "center_out_whorl_numbers"
        ]
        == [
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
        ]
    )

    assert (
        construction[
            "center_out_ring_widths"
        ]
        == [
            18,
            12,
            27,
            9,
            24,
            8,
            6,
            36,
        ]
    )

    assert (
        construction[
            "michell_states_arranged_in_platos_order"
        ]
        is True
    )


def test_phase10d_scaled_construction() -> None:
    scaled = _payload()[
        "michell_explicit"
    ][
        "scaled_construction"
    ]

    assert (
        scaled[
            "scale_factor"
        ]
        == 180
    )

    assert (
        scaled[
            "shaft_radius"
        ]
        == 720
    )

    assert (
        scaled[
            "center_out_ring_widths"
        ]
        == [
            3240,
            2160,
            4860,
            1620,
            4320,
            1440,
            1080,
            6480,
        ]
    )

    assert (
        scaled[
            "total_eight_whorl_width"
        ]
        == 25200
    )

    assert (
        scaled[
            "outer_radius_including_shaft"
        ]
        == 25920
    )


def test_phase10d_printed_correspondence_values() -> None:
    items = _payload()[
        "michell_explicit"
    ][
        "printed_dimensional_correspondences"
    ]

    values = {
        item[
            "label"
        ]: item[
            "value"
        ]
        for item in items
    }

    assert values == {
        "central spindle radius": 720,
        "first cumulative radius": 3960,
        "second cumulative radius": 6120,
        "second ring width": 2160,
    }


def test_phase10d_source_relationship_is_not_back_projection() -> None:
    relation = _payload()[
        "source_relationship"
    ]

    assert (
        relation[
            "michell_applies_musical_numbers_to_plato_ordinal_order"
        ]
        is True
    )

    assert (
        relation[
            "base_sequence_presented_after_musical_theory_argument"
        ]
        is True
    )

    assert (
        relation[
            "numeric_width_sequence_presented_as_direct_quote_from_plato"
        ]
        is False
    )

    assert (
        relation[
            "project_reconstruction_used"
        ]
        is False
    )


def test_phase10d_historical_boundary() -> None:
    boundary = _payload()[
        "historical_boundary"
    ]

    assert (
        boundary[
            "plato_intention_established"
        ]
        is False
    )

    assert (
        boundary[
            "ancient_transmission_established"
        ]
        is False
    )

    assert (
        boundary[
            "michell_claims_endorsed_as_historical_fact"
        ]
        is False
    )

    assert (
        boundary[
            "new_jerusalem_correspondence_treated_as_michell_claim"
        ]
        is True
    )


def test_phase10d_regeneration_is_deterministic() -> None:
    module = _load_script_module()

    before_json = JSON_PATH.read_bytes()
    before_markdown = MARKDOWN_PATH.read_bytes()

    module.write_outputs()

    assert (
        JSON_PATH.read_bytes()
        == before_json
    )

    assert (
        MARKDOWN_PATH.read_bytes()
        == before_markdown
    )


def test_phase10d_frozen_result_hashes() -> None:
    assert (
        _sha256(
            JSON_PATH
        )
        == (
            "ef6e17b7d9de47157025a2bf3aa9812d"
            "79859a5cc3b7bbe44185a67bacc99807"
        )
    )

    assert (
        _sha256(
            MARKDOWN_PATH
        )
        == (
            "115fb957278642874a9d032224a19b69"
            "11df8bbdbc9d4594774daf865146a571"
        )
    )


def test_phase10d_markdown_contains_core_boundary() -> None:
    text = MARKDOWN_PATH.read_text(
        encoding="utf-8"
    )

    required = (
        "6, 8, 9, 12, 18, 24, 27, 36",
        "whorls: 8,  7,  6, 5,  4, 3, 2,  1",
        "widths: 18, 12, 27, 9, 24, 8, 6, 36",
        "Michell multiplies the construction by `180`",
        "does not back-project those numbers into Plato",
        "does not establish that Plato intended these exact numerical widths",
    )

    for phrase in required:
        assert phrase in text

