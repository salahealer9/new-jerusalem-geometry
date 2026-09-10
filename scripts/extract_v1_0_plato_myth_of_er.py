from __future__ import annotations

from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET


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

ENGLISH = (
    SOURCE_DIR
    / "tlg0059.tlg030.perseus-eng2.xml"
)

GREEK = (
    SOURCE_DIR
    / "tlg0059.tlg030.perseus-grc2.xml"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_myth_of_er_literal.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_myth_of_er_literal_extraction.md"
)

TEI = "{http://www.tei-c.org/ns/1.0}"

SECTIONS = (
    "616d",
    "616e",
    "617a",
    "617b",
)


def sha256_bytes(
    data: bytes,
) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def sha256_text(
    text: str,
) -> str:
    return sha256_bytes(
        text.encode(
            "utf-8"
        )
    )


def normalize_text(
    text: str,
) -> str:
    return " ".join(
        text.split()
    )


def verify_source_hashes() -> dict:
    record = json.loads(
        FREEZE.read_text(
            encoding="utf-8"
        )
    )

    by_role = {
        witness[
            "role"
        ]: witness
        for witness in record[
            "witnesses"
        ]
    }

    observed = {
        "english_translation": sha256_bytes(
            ENGLISH.read_bytes()
        ),
        "greek_edition": sha256_bytes(
            GREEK.read_bytes()
        ),
    }

    for role, digest in observed.items():
        assert (
            digest
            == by_role[
                role
            ][
                "sha256"
            ]
        )

    return record


def extract_stephanus_sections(
    path: Path,
) -> dict[str, str]:
    root = ET.parse(
        path
    ).getroot()

    book = None

    for element in root.iter(
        TEI + "div"
    ):
        if (
            element.get(
                "type"
            )
            == "textpart"
            and element.get(
                "subtype"
            )
            == "book"
            and element.get(
                "n"
            )
            == "10"
        ):
            book = element
            break

    assert (
        book
        is not None
    )

    collected: dict[
        str,
        list[str],
    ] = {}

    current: str | None = None

    def walk(
        element: ET.Element,
    ) -> None:
        nonlocal current

        local = element.tag.rsplit(
            "}",
            1,
        )[
            -1
        ]

        if (
            local
            == "note"
        ):
            return

        if (
            local
            == "milestone"
            and element.get(
                "unit"
            )
            == "section"
            and element.get(
                "resp"
            )
            == "Stephanus"
        ):
            current = element.get(
                "n"
            )

            if current is not None:
                collected.setdefault(
                    current,
                    [],
                )

            return

        if (
            current is not None
            and element.text
        ):
            collected[
                current
            ].append(
                element.text
            )

        for child in element:
            walk(
                child
            )

            if (
                current is not None
                and child.tail
            ):
                collected[
                    current
                ].append(
                    child.tail
                )

    walk(
        book
    )

    return {
        section: normalize_text(
            "".join(
                pieces
            )
        )
        for section, pieces in collected.items()
    }


def validate_literal_anchors(
    english: dict[str, str],
    greek: dict[str, str],
) -> None:
    english_required = {
        "616d": (
            "eight of the whorls in all",
            "lying within one another",
        ),
        "616e": (
            "first and outmost whorl had the broadest circular rim",
            "that of the sixth was second",
            "eighth that of the second",
        ),
        "617a": (
            "seven inner circles revolved gently in the opposite direction",
            "the eighth moved most swiftly",
        ),
        "617b": (
            "seventh, sixth and fifth",
            "from all the eight there was the concord of a single harmony",
        ),
    }

    greek_required = {
        "616d": (
            "ὀκτὼ γὰρ εἶναι τοὺς σύμπαντας σφονδύλους",
            "ἐν ἀλλήλοις ἐγκειμένους",
        ),
        "616e": (
            "πρῶτόν τε καὶ ἐξωτάτω",
            "τὸν δὲ τοῦ ἕκτου δεύτερον",
            "ὄγδοον δὲ τὸν τοῦ δευτέρου",
        ),
        "617a": (
            "τοὺς μὲν ἐντὸς ἑπτὰ κύκλους",
            "τὴν ἐναντίαν τῷ ὅλῳ",
            "τάχιστα μὲν ἰέναι τὸν ὄγδοον",
        ),
        "617b": (
            "ἕβδομον καὶ ἕκτον καὶ πέμπτον",
            "ἐκ πασῶν δὲ ὀκτὼ οὐσῶν μίαν ἁρμονίαν συμφωνεῖν",
        ),
    }

    for section, anchors in english_required.items():
        for anchor in anchors:
            assert (
                anchor
                in english[
                    section
                ]
            )

    for section, anchors in greek_required.items():
        for anchor in anchors:
            assert (
                anchor
                in greek[
                    section
                ]
            )


def build_payload() -> dict:
    freeze = verify_source_hashes()

    english = extract_stephanus_sections(
        ENGLISH
    )

    greek = extract_stephanus_sections(
        GREEK
    )

    for section in SECTIONS:
        assert section in english
        assert section in greek

    validate_literal_anchors(
        english,
        greek,
    )

    section_hashes = {
        section: {
            "english_normalized_sha256": sha256_text(
                english[
                    section
                ]
            ),
            "greek_normalized_sha256": sha256_text(
                greek[
                    section
                ]
            ),
        }
        for section in SECTIONS
    }

    return {
        "audit_phase": "10C",
        "status": (
            "PLATO_MYTH_OF_ER_"
            "LITERAL_EXTRACTION_COMPLETE"
        ),
        "provenance_class": (
            "DIRECT_PLATO_TEXT"
        ),
        "source_boundary": {
            "work_urn": freeze[
                "work_urn"
            ],
            "upstream_commit": freeze[
                "upstream_commit"
            ],
            "english_sha256": sha256_bytes(
                ENGLISH.read_bytes()
            ),
            "greek_sha256": sha256_bytes(
                GREEK.read_bytes()
            ),
            "stephanus_sections": list(
                SECTIONS
            ),
            "normalized_section_sha256": (
                section_hashes
            ),
            "notes_excluded_from_section_text": True,
        },
        "literal_findings": {
            "whorl_structure": {
                "total_whorls": 8,
                "nested_within_one_another": True,
                "first_whorl_explicitly_outermost": True,
                "shaft_passes_through_middle_of_eighth": True,
            },
            "rim_widths": {
                "order_broadest_to_narrowest_by_whorl_number": [
                    1,
                    6,
                    4,
                    8,
                    7,
                    5,
                    3,
                    2,
                ],
                "numerical_magnitudes_or_ratios_stated": False,
                "statement_type": (
                    "ordinal ranking only"
                ),
            },
            "appearance": {
                "whorl_1": "spangled",
                "whorl_7": "brightest",
                "whorl_8": (
                    "takes its color from whorl 7"
                ),
                "whorls_2_and_5": (
                    "similar to one another and more yellow "
                    "than the two previously described"
                ),
                "whorl_3": "whitest",
                "whorl_4": "slightly ruddy",
                "whorl_6": "second in whiteness",
            },
            "motion": {
                "whole_spindle": (
                    "turns as a whole with one movement"
                ),
                "inner_circle_count": 7,
                "inner_circles_relative_direction": (
                    "opposite to the whole"
                ),
                "speed_groups_fastest_to_slowest": [
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
                ],
                "speed_order_is_separate_from_width_order": True,
            },
            "acoustic_structure": {
                "siren_on_each_rim": True,
                "siren_count_implied_by_rims": 8,
                "one_tone_each": True,
                "combined_result": (
                    "single harmony"
                ),
            },
        },
        "negative_findings": {
            "explicit_numeric_rim_width_values": False,
            "explicit_numeric_rim_width_ratios": False,
            "michell_musical_width_sequence": False,
            "central_shaft_radius_value": False,
            "scale_factor_180": False,
            "new_jerusalem_dimensional_correspondence": False,
        },
        "interpretive_boundary": {
            "michell_material_used": False,
            "project_reconstruction_used": False,
            "historical_transmission_claim_made": False,
            "note": (
                "Phase 10C records only literal content of "
                "Republic 10, Stephanus 616d-617b from the "
                "frozen Plato witnesses."
            ),
        },
    }


def render_markdown(
    payload: dict,
) -> str:
    findings = payload[
        "literal_findings"
    ]

    source = payload[
        "source_boundary"
    ]

    lines = [
        "# v1.0 Plato Myth of Er literal extraction",
        "",
        "## Status",
        "",
        "`PLATO_MYTH_OF_ER_LITERAL_EXTRACTION_COMPLETE`",
        "",
        "Provenance class: `DIRECT_PLATO_TEXT`.",
        "",
        "This result is limited to the frozen Plato witnesses and "
        "contains no Michell-derived numerical reconstruction.",
        "",
        "## Frozen source boundary",
        "",
        f"- Perseus upstream commit: `{source['upstream_commit']}`",
        f"- Work URN: `{source['work_urn']}`",
        "- Stephanus sections: `616d`, `616e`, `617a`, `617b`",
        "- TEI editorial notes are excluded from the normalized passage text.",
        "",
        "## Literal findings",
        "",
        "Plato describes eight whorls nested within one another. "
        "The first is explicitly the outermost, and the spindle shaft "
        "passes through the middle of the eighth.",
        "",
        "The rim-width order, from broadest to narrowest, is:",
        "",
        "```text",
        "whorl 1 > whorl 6 > whorl 4 > whorl 8 > "
        "whorl 7 > whorl 5 > whorl 3 > whorl 2",
        "```",
        "",
        "This is an ordinal ranking. The passage gives no numerical "
        "magnitude or ratio for the rim widths.",
        "",
        "The whole spindle turns with one movement while the seven inner "
        "circles move gently in the opposite direction. Their speed groups, "
        "from fastest to slowest, are:",
        "",
        "```text",
        "8 > (7 = 6 = 5) > 4 > 3 > 2",
        "```",
        "",
        "The speed order is a separate textual attribute and is not used "
        "as a substitute for the rim-width order.",
        "",
        "The passage also distinguishes the whorls by appearance and "
        "places one Siren on each rim, each sounding one tone; the eight "
        "tones combine into a single harmony.",
        "",
        "## Negative findings",
        "",
        "Within this literal extraction Plato does **not** supply:",
        "",
        "- numerical magnitudes for the eight rim widths;",
        "- numerical ratios for those widths;",
        "- Michell's later musical-number width sequence;",
        "- a numerical central-shaft radius;",
        "- a scale factor of 180;",
        "- a New Jerusalem dimensional correspondence.",
        "",
        "These absences are part of the historical boundary: later Michell "
        "numbers may not be back-projected into Plato.",
        "",
        "## Source-section hashes",
        "",
    ]

    for section in SECTIONS:
        hashes = source[
            "normalized_section_sha256"
        ][
            section
        ]

        lines.extend(
            [
                f"### {section}",
                "",
                (
                    "- English normalized text SHA256: "
                    f"`{hashes['english_normalized_sha256']}`"
                ),
                (
                    "- Greek normalized text SHA256: "
                    f"`{hashes['greek_normalized_sha256']}`"
                ),
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "No Michell source, numerical fit, project reconstruction, or "
            "historical-transmission claim enters this Phase 10C result.",
            "",
        ]
    )

    return "\n".join(
        lines
    )


def write_outputs() -> None:
    payload = build_payload()

    JSON_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    MARKDOWN_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_OUT.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    MARKDOWN_OUT.write_text(
        render_markdown(
            payload
        ),
        encoding="utf-8",
    )


def main() -> None:
    write_outputs()

    payload = json.loads(
        JSON_OUT.read_text(
            encoding="utf-8"
        )
    )

    print(
        payload[
            "status"
        ]
    )

    print(
        "width_order",
        payload[
            "literal_findings"
        ][
            "rim_widths"
        ][
            "order_broadest_to_narrowest_by_whorl_number"
        ],
    )

    print(
        "numeric_width_values",
        payload[
            "negative_findings"
        ][
            "explicit_numeric_rim_width_values"
        ],
    )

    print(
        JSON_OUT
    )

    print(
        MARKDOWN_OUT
    )


if __name__ == "__main__":
    main()

