from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "extract_v1_0_plato_myth_of_er.py"
)

JSON_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_myth_of_er_literal.json"
)

MARKDOWN_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_myth_of_er_literal_extraction.md"
)

ENGLISH = (
    ROOT
    / "data"
    / "sources"
    / "v1_0"
    / "plato"
    / "tlg0059.tlg030.perseus-eng2.xml"
)

GREEK = (
    ROOT
    / "data"
    / "sources"
    / "v1_0"
    / "plato"
    / "tlg0059.tlg030.perseus-grc2.xml"
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
        "plato_literal_phase10c",
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


def test_phase10c_frozen_source_hashes() -> None:
    assert (
        _sha256(
            ENGLISH
        )
        == (
            "36826064d30be3b40d20b820f4904ed1"
            "70d375e41dd3f450cbe4eb733054766d"
        )
    )

    assert (
        _sha256(
            GREEK
        )
        == (
            "da2bfcf943497bb147fc49ae4b47bf09"
            "19e1db790bcf7de830dc259e76379d4f"
        )
    )


def test_phase10c_status_and_provenance() -> None:
    payload = _payload()

    assert (
        payload[
            "status"
        ]
        == (
            "PLATO_MYTH_OF_ER_"
            "LITERAL_EXTRACTION_COMPLETE"
        )
    )

    assert (
        payload[
            "provenance_class"
        ]
        == "DIRECT_PLATO_TEXT"
    )


def test_phase10c_whorl_structure_is_literal() -> None:
    structure = _payload()[
        "literal_findings"
    ][
        "whorl_structure"
    ]

    assert (
        structure[
            "total_whorls"
        ]
        == 8
    )

    assert (
        structure[
            "nested_within_one_another"
        ]
        is True
    )

    assert (
        structure[
            "first_whorl_explicitly_outermost"
        ]
        is True
    )

    assert (
        structure[
            "shaft_passes_through_middle_of_eighth"
        ]
        is True
    )


def test_phase10c_width_order_is_exact_ordinal_order() -> None:
    widths = _payload()[
        "literal_findings"
    ][
        "rim_widths"
    ]

    assert (
        widths[
            "order_broadest_to_narrowest_by_whorl_number"
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

    assert (
        widths[
            "numerical_magnitudes_or_ratios_stated"
        ]
        is False
    )

    assert (
        widths[
            "statement_type"
        ]
        == "ordinal ranking only"
    )


def test_phase10c_motion_order_is_kept_separate() -> None:
    motion = _payload()[
        "literal_findings"
    ][
        "motion"
    ]

    assert (
        motion[
            "inner_circle_count"
        ]
        == 7
    )

    assert (
        motion[
            "inner_circles_relative_direction"
        ]
        == "opposite to the whole"
    )

    assert (
        motion[
            "speed_groups_fastest_to_slowest"
        ]
        == [
            [
                8
            ],
            [
                7,
                6,
                5,
            ],
            [
                4
            ],
            [
                3
            ],
            [
                2
            ],
        ]
    )

    assert (
        motion[
            "speed_order_is_separate_from_width_order"
        ]
        is True
    )


def test_phase10c_acoustic_structure() -> None:
    acoustic = _payload()[
        "literal_findings"
    ][
        "acoustic_structure"
    ]

    assert (
        acoustic[
            "siren_on_each_rim"
        ]
        is True
    )

    assert (
        acoustic[
            "siren_count_implied_by_rims"
        ]
        == 8
    )

    assert (
        acoustic[
            "one_tone_each"
        ]
        is True
    )

    assert (
        acoustic[
            "combined_result"
        ]
        == "single harmony"
    )


def test_phase10c_negative_findings_block_michell_back_projection() -> None:
    negative = _payload()[
        "negative_findings"
    ]

    assert (
        negative[
            "explicit_numeric_rim_width_values"
        ]
        is False
    )

    assert (
        negative[
            "explicit_numeric_rim_width_ratios"
        ]
        is False
    )

    assert (
        negative[
            "michell_musical_width_sequence"
        ]
        is False
    )

    assert (
        negative[
            "central_shaft_radius_value"
        ]
        is False
    )

    assert (
        negative[
            "scale_factor_180"
        ]
        is False
    )

    assert (
        negative[
            "new_jerusalem_dimensional_correspondence"
        ]
        is False
    )


def test_phase10c_normalized_section_hashes() -> None:
    observed = _payload()[
        "source_boundary"
    ][
        "normalized_section_sha256"
    ]

    expected = {
        "616d": {
            "english_normalized_sha256": (
                "7d28c794f7facf18448c33a5c9c61abf"
                "bfc606c5566dab82a2215ade7c31686b"
            ),
            "greek_normalized_sha256": (
                "cd2f08a891368c4734dd927df6eb703f8"
                "710b06db2e541c84f2ecbb7233643ef"
            ),
        },
        "616e": {
            "english_normalized_sha256": (
                "216c7110851c1bcdeda55538a82d0c901"
                "d7df80b0a7d79945e0e24468d1e8a3a"
            ),
            "greek_normalized_sha256": (
                "dd3ef29e55182e1798938c2ac37e12de8"
                "8e17044242e01651ea0b4d513e0e84a"
            ),
        },
        "617a": {
            "english_normalized_sha256": (
                "8468d82da5a81578ec03300fffeecfba4"
                "98a8943844e6ea0c4f5ff74bd8e24c3"
            ),
            "greek_normalized_sha256": (
                "118c5b05eab4d9a9e600b95df10c9f34"
                "7ba937fabe14a69f9e9302b8869f2759"
            ),
        },
        "617b": {
            "english_normalized_sha256": (
                "398a45f3b81422f7ef005042e54e3507b"
                "8059d0ae73ae206bbb4d4aacb4d11ec"
            ),
            "greek_normalized_sha256": (
                "c0c2a0af077f2b7a5b1f5f3a960ae302"
                "76059c3c1e7cfee3189a156a988934b1"
            ),
        },
    }

    assert observed == expected


def test_phase10c_regeneration_is_deterministic() -> None:
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


def test_phase10c_frozen_result_hashes() -> None:
    assert (
        _sha256(
            JSON_PATH
        )
        == (
            "42edbe735c6d91bc180198702f411889e"
            "05ea503989c24b0d44a134362a63f3c"
        )
    )

    assert (
        _sha256(
            MARKDOWN_PATH
        )
        == (
            "ab9c3362a446f639655b78502f684e9b"
            "1a768a354914a5bc57fad2ade790c238"
        )
    )


def test_phase10c_interpretive_boundary() -> None:
    boundary = _payload()[
        "interpretive_boundary"
    ]

    assert (
        boundary[
            "michell_material_used"
        ]
        is False
    )

    assert (
        boundary[
            "project_reconstruction_used"
        ]
        is False
    )

    assert (
        boundary[
            "historical_transmission_claim_made"
        ]
        is False
    )


def test_phase10c_markdown_states_the_boundary() -> None:
    text = MARKDOWN_PATH.read_text(
        encoding="utf-8"
    )

    required = (
        "eight whorls nested within one another",
        "whorl 1 > whorl 6 > whorl 4 > whorl 8",
        "ordinal ranking",
        "no numerical magnitude or ratio",
        "8 > (7 = 6 = 5) > 4 > 3 > 2",
        "No Michell source, numerical fit, project reconstruction",
    )

    for phrase in required:
        assert phrase in text

