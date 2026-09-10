from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import io
import json
import zipfile


ROOT = Path(__file__).resolve().parents[1]

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "michell_2008_ch4_literal.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_michell_2008_ch4_literal_extraction.md"
)


BUNDLE_SHA256 = (
    "f662aa6221a4ceb232025569fc501ca66"
    "13ebbdc6b44394d6631eec7e5a7137d"
)

CHAPTER_ARCHIVE_SHA256 = (
    "d0f722a81df4f91165ed529460c4e5f7"
    "c00682e75feb16f20cb85915c2d6bb92"
)

CHAPTER_MEMBER = (
    "chapter4/"
    "the_dimensions_of_paradise_v2008_"
    "chapter_4_plato.zip"
)

SOURCE_CAPTURES = (
    {
        "observation_id": "M08-P164-WHORL-TABLE",
        "ebook_page": 164,
        "filename": "Screenshot 2026-08-12 12.00.38.png",
        "sha256": (
            "857036985aefd737dd9a034a61b4d6a5"
            "27cf20126010fdc1d0a8d41099a2bf6c"
        ),
        "role": "whorl_order_table",
    },
    {
        "observation_id": "M08-P165-MUSICAL-SEQUENCE",
        "ebook_page": 165,
        "filename": "Screenshot 2026-08-12 12.00.42.png",
        "sha256": (
            "92905f19098445d37bfa721174938ffd"
            "75ae0791ee5fbc63ae17d6769699752a"
        ),
        "role": "musical_argument_and_base_sequence",
    },
    {
        "observation_id": "M08-P167-CONSTRUCTION-A",
        "ebook_page": 167,
        "filename": "Screenshot 2026-08-12 12.00.49.png",
        "sha256": (
            "573922b187d816a96a1fa95c00e65c0a"
            "f104d21997fcf21cca955de12d70cd7c"
        ),
        "role": "shaft_and_unscaled_whorl_construction",
    },
    {
        "observation_id": "M08-P167-CONSTRUCTION-B",
        "ebook_page": 167,
        "filename": "Screenshot 2026-08-12 12.00.54.png",
        "sha256": (
            "745bc278e09a39ef08633da271297882"
            "46c9e555bac036f3ba1785fbd05942a5"
        ),
        "role": "scale_and_dimensional_correspondences",
    },
)


def sha256_bytes(
    data: bytes,
) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def verify_local_source(
    source: Path,
) -> None:
    bundle_bytes = source.read_bytes()

    assert (
        sha256_bytes(
            bundle_bytes
        )
        == BUNDLE_SHA256
    )

    with zipfile.ZipFile(
        io.BytesIO(
            bundle_bytes
        )
    ) as outer:
        chapter_bytes = outer.read(
            CHAPTER_MEMBER
        )

    assert (
        sha256_bytes(
            chapter_bytes
        )
        == CHAPTER_ARCHIVE_SHA256
    )

    with zipfile.ZipFile(
        io.BytesIO(
            chapter_bytes
        )
    ) as chapter:
        by_basename = {
            Path(
                info.filename
            ).name: info.filename
            for info in chapter.infolist()
            if (
                not info.is_dir()
                and info.filename.endswith(
                    ".png"
                )
            )
        }

        for capture in SOURCE_CAPTURES:
            filename = capture[
                "filename"
            ]

            assert (
                filename
                in by_basename
            )

            observed = sha256_bytes(
                chapter.read(
                    by_basename[
                        filename
                    ]
                )
            )

            assert (
                observed
                == capture[
                    "sha256"
                ]
            )


def build_payload() -> dict:
    width_rank_by_whorl = {
        "1": 1,
        "2": 8,
        "3": 7,
        "4": 3,
        "5": 6,
        "6": 2,
        "7": 5,
        "8": 4,
    }

    return {
        "audit_phase": "10D",
        "status": (
            "MICHELL_2008_CH4_LITERAL_"
            "NUMERICAL_EXTRACTION_COMPLETE"
        ),
        "provenance_class": (
            "MICHELL_EXPLICIT"
        ),
        "extraction_method": {
            "source_form": (
                "user-purchased ebook screenshots"
            ),
            "manual_visual_extraction": True,
            "ocr_used": False,
            "source_bytes_committed_to_git": False,
            "source_bundle_sha256": (
                BUNDLE_SHA256
            ),
            "chapter_archive_sha256": (
                CHAPTER_ARCHIVE_SHA256
            ),
            "source_captures": list(
                SOURCE_CAPTURES
            ),
        },
        "michell_explicit": {
            "plato_whorl_table": {
                "width_rank_by_whorl": (
                    width_rank_by_whorl
                ),
                "broadest_to_narrowest_whorl_order": [
                    1,
                    6,
                    4,
                    8,
                    7,
                    5,
                    3,
                    2,
                ],
                "source_page": 164,
            },
            "musical_argument": {
                "octave_only_interpretation_described_as_not_stated_or_implied_by_plato": True,
                "canonical_voice_range_used": (
                    "two octaves and a fifth"
                ),
                "greek_musical_proportion_invoked": [
                    6,
                    8,
                    9,
                    12,
                ],
                "base_sequence": [
                    6,
                    8,
                    9,
                    12,
                    18,
                    24,
                    27,
                    36,
                ],
                "successive_interval_ratios": [
                    "4/3",
                    "9/8",
                    "4/3",
                    "3/2",
                    "4/3",
                    "9/8",
                    "4/3",
                ],
                "source_pages": [
                    165,
                    167,
                ],
            },
            "unscaled_construction": {
                "shaft_first_sequence_number": 6,
                "shaft_musical_factor": "2/3",
                "shaft_radius": 4,
                "full_radius": 144,
                "center_out_whorl_numbers": [
                    8,
                    7,
                    6,
                    5,
                    4,
                    3,
                    2,
                    1,
                ],
                "center_out_ring_widths": [
                    18,
                    12,
                    27,
                    9,
                    24,
                    8,
                    6,
                    36,
                ],
                "michell_states_arranged_in_platos_order": True,
                "source_page": 167,
            },
            "scaled_construction": {
                "scale_factor": 180,
                "shaft_radius": 720,
                "center_out_ring_widths": [
                    3240,
                    2160,
                    4860,
                    1620,
                    4320,
                    1440,
                    1080,
                    6480,
                ],
                "total_eight_whorl_width": 25200,
                "outer_radius_including_shaft": 25920,
                "source_page": 167,
            },
            "printed_dimensional_correspondences": [
                {
                    "label": "central spindle radius",
                    "value": 720,
                    "unit_as_printed": "feet",
                    "source_page": 167,
                },
                {
                    "label": "first cumulative radius",
                    "calculation_as_printed": (
                        "720 + 3240 = 3960"
                    ),
                    "value": 3960,
                    "interpretations_as_printed": [
                        "earth radius 3960 miles",
                        (
                            "cultivated land radius "
                            "3960 feet in Magnesia"
                        ),
                    ],
                    "source_page": 167,
                },
                {
                    "label": "second cumulative radius",
                    "calculation_as_printed": (
                        "3960 + 2160 = 6120"
                    ),
                    "value": 6120,
                    "interpretation_as_printed": (
                        "same numerical radius as the "
                        "outer circle in the New Jerusalem"
                    ),
                    "source_page": 167,
                },
                {
                    "label": "second ring width",
                    "value": 2160,
                    "interpretation_as_printed": (
                        "contains the circle of the moon, "
                        "diameter 2160 miles"
                    ),
                    "source_page": 167,
                },
            ],
        },
        "source_relationship": {
            "michell_applies_musical_numbers_to_plato_ordinal_order": True,
            "base_sequence_presented_after_musical_theory_argument": True,
            "numeric_width_sequence_presented_as_direct_quote_from_plato": False,
            "project_reconstruction_used": False,
            "note": (
                "Phase 10D records Michell's printed numerical "
                "construction and dimensional correspondences. "
                "It does not yet test or rederive the arithmetic."
            ),
        },
        "historical_boundary": {
            "plato_intention_established": False,
            "ancient_transmission_established": False,
            "michell_claims_endorsed_as_historical_fact": False,
            "new_jerusalem_correspondence_treated_as_michell_claim": True,
        },
    }


def render_markdown(
    payload: dict,
) -> str:
    explicit = payload[
        "michell_explicit"
    ]

    musical = explicit[
        "musical_argument"
    ]

    unscaled = explicit[
        "unscaled_construction"
    ]

    scaled = explicit[
        "scaled_construction"
    ]

    lines = [
        "# v1.0 Michell 2008 Chapter 4 literal numerical extraction",
        "",
        "## Status",
        "",
        "`MICHELL_2008_CH4_LITERAL_NUMERICAL_EXTRACTION_COMPLETE`",
        "",
        "Provenance class: `MICHELL_EXPLICIT`.",
        "",
        "This is a structured extraction from the frozen purchased 2008 "
        "ebook witness. The screenshot bytes remain outside Git; each "
        "observation is anchored by filename and SHA256.",
        "",
        "## Source pages",
        "",
        "- ebook page 164: Michell's whorl-order table;",
        "- ebook page 165: musical-theory argument and eight-number sequence;",
        "- ebook page 167: shaft construction, whorl widths, scale, and "
        "dimensional correspondences.",
        "",
        "## Michell's whorl ordering",
        "",
        "Michell's page-164 table gives the width rank of whorls 1 through 8. "
        "Read from broadest to narrowest, that order is:",
        "",
        "```text",
        "1, 6, 4, 8, 7, 5, 3, 2",
        "```",
        "",
        "## Musical-number construction",
        "",
        "Michell rejects an octave-only interpretation as something not "
        "stated or implied in Plato's text, then develops a musical range "
        "of two octaves and a fifth. The numerical sequence he presents is:",
        "",
        "```text",
        "6, 8, 9, 12, 18, 24, 27, 36",
        "```",
        "",
        "The successive interval ratios printed with the construction are:",
        "",
        "```text",
        "4/3, 9/8, 4/3, 3/2, 4/3, 9/8, 4/3",
        "```",
        "",
        "## Unscaled whorl construction",
        "",
        "Michell gives the central shaft radius as `6 × 2/3 = 4` and the "
        "full radius as `144`. From the center outward, the whorl numbers "
        "and widths are:",
        "",
        "```text",
        "whorls: 8,  7,  6, 5,  4, 3, 2,  1",
        "widths: 18, 12, 27, 9, 24, 8, 6, 36",
        "```",
        "",
        "He explicitly describes the rings as arranged in Plato's order and "
        "proportioned by the musical numbers.",
        "",
        "## Scaling printed by Michell",
        "",
        "Michell multiplies the construction by `180`, giving:",
        "",
        "```text",
        f"shaft radius: {scaled['shaft_radius']}",
        "ring widths: 3240, 2160, 4860, 1620, 4320, 1440, 1080, 6480",
        f"total whorl width: {scaled['total_eight_whorl_width']}",
        f"outer radius including shaft: {scaled['outer_radius_including_shaft']}",
        "```",
        "",
        "On the same page he identifies the numerical radius `3960` with "
        "the earth radius and with Magnesia's cultivated-land radius, "
        "identifies `6120` with the New Jerusalem outer-circle radius, "
        "and identifies the second ring width `2160` with the moon's "
        "diameter.",
        "",
        "## Source relationship",
        "",
        "This phase records Michell's numerical interpretation as Michell's "
        "own printed construction. It does not back-project those numbers "
        "into Plato, and it does not yet rederive or test the arithmetic.",
        "",
        "## Historical boundary",
        "",
        "The extraction does not establish that Plato intended these exact "
        "numerical widths, that the construction was transmitted from "
        "antiquity, or that Michell's historical interpretation is true. "
        "Those are separate evidential questions.",
        "",
        "## Source-image hashes",
        "",
    ]

    for capture in payload[
        "extraction_method"
    ][
        "source_captures"
    ]:
        lines.extend(
            [
                (
                    f"- page {capture['ebook_page']}, "
                    f"`{capture['filename']}`"
                ),
                (
                    f"  - SHA256: `{capture['sha256']}`"
                ),
            ]
        )

    lines.append(
        ""
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
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help=(
            "Local Michell 2008 source bundle "
            "created in Phase 10B2."
        ),
    )

    args = parser.parse_args()

    verify_local_source(
        args.source
    )

    write_outputs()

    payload = build_payload()

    print(
        payload[
            "status"
        ]
    )

    print(
        "base_sequence",
        payload[
            "michell_explicit"
        ][
            "musical_argument"
        ][
            "base_sequence"
        ],
    )

    print(
        "center_out_widths",
        payload[
            "michell_explicit"
        ][
            "unscaled_construction"
        ][
            "center_out_ring_widths"
        ],
    )

    print(
        "scale_factor",
        payload[
            "michell_explicit"
        ][
            "scaled_construction"
        ][
            "scale_factor"
        ],
    )


if __name__ == "__main__":
    main()

