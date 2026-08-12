from __future__ import annotations

from pathlib import Path
import csv
import hashlib
import io
import json


ROOT = Path(__file__).resolve().parents[1]

PLATO = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_myth_of_er_literal.json"
)

MICHELL = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "michell_2008_ch4_literal.json"
)

RECONSTRUCTION = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_whorl_reconstruction.json"
)

PROTOCOL = (
    ROOT
    / "docs"
    / "specification"
    / "v1.0_plato_historical_source_protocol.md"
)

MANIFEST = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_source_manifest.csv"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_historical_synthesis.json"
)

CSV_OUT = (
    ROOT
    / "docs"
    / "sources"
    / "v1.0_plato_michell_claim_matrix.csv"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v1.0_plato_michell_historical_synthesis.md"
)


FROZEN_HASHES = {
    "plato_literal": (
        "42edbe735c6d91bc180198702f411889e"
        "05ea503989c24b0d44a134362a63f3c"
    ),
    "michell_literal": (
        "ef6e17b7d9de47157025a2bf3aa9812d"
        "79859a5cc3b7bbe44185a67bacc99807"
    ),
    "reconstruction": (
        "9a17ad61347c6f1892adeed5b510c3994"
        "9d7412b61100095ab07f25036f20217"
    ),
    "protocol": (
        "5890ff8aca969eff96a227be1a2be9ad2"
        "ac420c64b6b9739404f34750127bed5"
    ),
    "manifest": (
        "a1a2e4f62126d11853372ae26949393d"
        "55f7bec75e37a0f640179dfdf7553d79"
    ),
}


ALLOWED_CLASSES = {
    "DIRECT_PLATO_TEXT",
    "MICHELL_EXPLICIT",
    "PROJECT_RECONSTRUCTION",
    "SUPPORTING_HISTORICAL_CONTEXT",
    "ARCHIVAL_PENDING",
    "INTERPRETIVE_EXCLUDED",
}


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def verify_frozen_inputs() -> None:
    observed = {
        "plato_literal": sha256(
            PLATO
        ),
        "michell_literal": sha256(
            MICHELL
        ),
        "reconstruction": sha256(
            RECONSTRUCTION
        ),
        "protocol": sha256(
            PROTOCOL
        ),
        "manifest": sha256(
            MANIFEST
        ),
    }

    assert (
        observed
        == FROZEN_HASHES
    )


def read_manifest() -> dict[str, dict[str, str]]:
    with MANIFEST.open(
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    return {
        row[
            "source_id"
        ]: row
        for row in rows
    }


def build_claim_rows(
    plato: dict,
    michell: dict,
    reconstruction: dict,
    manifest: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    width_order = (
        "1 > 6 > 4 > 8 > 7 > 5 > 3 > 2"
    )

    rows = [
        {
            "claim_id": "V10-PLATO-001",
            "claim": (
                "Republic 10 describes eight nested whorls."
            ),
            "provenance_class": "DIRECT_PLATO_TEXT",
            "evidence_phase": "10C",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "plato_myth_of_er_literal.json"
            ),
            "status": "verified",
            "notes": (
                "Literal extraction from frozen English and Greek "
                "Republic witnesses."
            ),
        },
        {
            "claim_id": "V10-PLATO-002",
            "claim": (
                "Plato's rim-width order from broadest to narrowest is "
                + width_order
                + "."
            ),
            "provenance_class": "DIRECT_PLATO_TEXT",
            "evidence_phase": "10C",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "plato_myth_of_er_literal.json"
            ),
            "status": "verified",
            "notes": (
                "Ordinal ranking only."
            ),
        },
        {
            "claim_id": "V10-PLATO-003",
            "claim": (
                "The audited Plato passage supplies no numerical "
                "magnitudes or ratios for the rim widths."
            ),
            "provenance_class": "DIRECT_PLATO_TEXT",
            "evidence_phase": "10C",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "plato_myth_of_er_literal.json"
            ),
            "status": "verified_negative",
            "notes": (
                "Later numerical assignments must not be "
                "back-projected into Plato."
            ),
        },
        {
            "claim_id": "V10-MICHELL-001",
            "claim": (
                "Michell's 2008 whorl table uses the same ordinal "
                "width order as the Plato extraction."
            ),
            "provenance_class": "MICHELL_EXPLICIT",
            "evidence_phase": "10D",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "michell_2008_ch4_literal.json"
            ),
            "status": "verified",
            "notes": (
                "The source table is recorded independently from "
                "the project reconstruction."
            ),
        },
        {
            "claim_id": "V10-MICHELL-002",
            "claim": (
                "Michell supplies the musical-number sequence "
                "6, 8, 9, 12, 18, 24, 27, 36."
            ),
            "provenance_class": "MICHELL_EXPLICIT",
            "evidence_phase": "10D",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "michell_2008_ch4_literal.json"
            ),
            "status": "verified",
            "notes": (
                "This numerical sequence is Michell's interpretive "
                "input, not a numerical sequence stated by Plato."
            ),
        },
        {
            "claim_id": "V10-MICHELL-003",
            "claim": (
                "Michell prints shaft radius 4, scale factor 180, "
                "and center-out widths 18, 12, 27, 9, 24, 8, 6, 36."
            ),
            "provenance_class": "MICHELL_EXPLICIT",
            "evidence_phase": "10D",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "michell_2008_ch4_literal.json"
            ),
            "status": "verified",
            "notes": (
                "Literal numerical extraction from the frozen "
                "2008 purchased witness."
            ),
        },
        {
            "claim_id": "V10-MICHELL-004",
            "claim": (
                "Michell prints the numerical correspondences "
                "3960, 6120, and 2160 for Earth/Magnesia, "
                "New Jerusalem, and Moon dimensions respectively."
            ),
            "provenance_class": "MICHELL_EXPLICIT",
            "evidence_phase": "10D",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "michell_2008_ch4_literal.json"
            ),
            "status": "verified_as_michell_claim",
            "notes": (
                "Recording Michell's printed correspondences does "
                "not endorse their historical interpretation."
            ),
        },
        {
            "claim_id": "V10-RECON-001",
            "claim": (
                "Assigning Michell's eight distinct musical numbers "
                "by Plato's ordinal width rank deterministically "
                "reproduces Michell's center-out whorl widths."
            ),
            "provenance_class": "PROJECT_RECONSTRUCTION",
            "evidence_phase": "10E",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "plato_michell_whorl_reconstruction.json"
            ),
            "status": "verified",
            "notes": (
                "Zero permutation searches and zero fitted parameters."
            ),
        },
        {
            "claim_id": "V10-RECON-002",
            "claim": (
                "The exact cumulative radii are "
                "4, 22, 34, 61, 70, 94, 102, 108, 144; "
                "after scaling by 180 they are "
                "720, 3960, 6120, 10980, 12600, 16920, "
                "18360, 19440, 25920."
            ),
            "provenance_class": "PROJECT_RECONSTRUCTION",
            "evidence_phase": "10E",
            "evidence_artifact": (
                "data/analysis/njg_michell_v1_0/"
                "plato_michell_whorl_reconstruction.json"
            ),
            "status": "verified",
            "notes": (
                "Exact integer arithmetic from frozen inputs."
            ),
        },
        {
            "claim_id": "V10-HIST-001",
            "claim": (
                "The audited evidence does not establish that Plato "
                "supplied or intended Michell's numerical whorl widths."
            ),
            "provenance_class": "PROJECT_RECONSTRUCTION",
            "evidence_phase": "10F",
            "evidence_artifact": (
                "docs/geometry/"
                "v1.0_plato_michell_historical_synthesis.md"
            ),
            "status": "boundary_conclusion",
            "notes": (
                "Plato contributes ordinal information; Michell adds "
                "the numerical interpretation."
            ),
        },
        {
            "claim_id": "V10-HIST-002",
            "claim": (
                "The audited evidence does not establish ancient "
                "historical transmission of Michell's numerical scheme."
            ),
            "provenance_class": "PROJECT_RECONSTRUCTION",
            "evidence_phase": "10F",
            "evidence_artifact": (
                "docs/geometry/"
                "v1.0_plato_michell_historical_synthesis.md"
            ),
            "status": "boundary_conclusion",
            "notes": (
                "Numerical reproducibility is not evidence of "
                "historical transmission."
            ),
        },
        {
            "claim_id": "V10-ARCHIVE-001",
            "claim": (
                "The Sommerville 1974 note remains an archival lead "
                "and is non-gating for this Plato/Michell audit."
            ),
            "provenance_class": "ARCHIVAL_PENDING",
            "evidence_phase": "10A",
            "evidence_artifact": (
                "docs/sources/v1.0_plato_source_manifest.csv"
            ),
            "status": "pending",
            "notes": (
                manifest[
                    "SOMMERVILLE_1974_NOTE"
                ][
                    "notes"
                ]
            ),
        },
        {
            "claim_id": "V10-INTERP-001",
            "claim": (
                "The later interpretive framework is excluded from "
                "the v1.0 historical evidential layer."
            ),
            "provenance_class": "INTERPRETIVE_EXCLUDED",
            "evidence_phase": "10A",
            "evidence_artifact": (
                "docs/sources/v1.0_plato_source_manifest.csv"
            ),
            "status": "excluded",
            "notes": (
                manifest[
                    "USER_INTERPRETIVE_FRAMEWORK"
                ][
                    "notes"
                ]
            ),
        },
    ]

    assert (
        len(
            {
                row[
                    "claim_id"
                ]
                for row in rows
            }
        )
        == len(
            rows
        )
    )

    for row in rows:
        assert (
            row[
                "provenance_class"
            ]
            in ALLOWED_CLASSES
        )

    return rows


def build_synthesis() -> tuple[dict, list[dict[str, str]]]:
    verify_frozen_inputs()

    plato = json.loads(
        PLATO.read_text(
            encoding="utf-8"
        )
    )

    michell = json.loads(
        MICHELL.read_text(
            encoding="utf-8"
        )
    )

    reconstruction = json.loads(
        RECONSTRUCTION.read_text(
            encoding="utf-8"
        )
    )

    manifest = read_manifest()

    claims = build_claim_rows(
        plato,
        michell,
        reconstruction,
        manifest,
    )

    plato_width_order = (
        plato[
            "literal_findings"
        ][
            "rim_widths"
        ][
            "order_broadest_to_narrowest_by_whorl_number"
        ]
    )

    michell_width_order = (
        michell[
            "michell_explicit"
        ][
            "plato_whorl_table"
        ][
            "broadest_to_narrowest_whorl_order"
        ]
    )

    assert (
        plato_width_order
        == michell_width_order
    )

    exact_checks = (
        reconstruction[
            "exact_validation_against_michell_printed_values"
        ]
    )

    assert exact_checks
    assert all(
        exact_checks.values()
    )

    dof = (
        reconstruction[
            "deterministic_algorithm"
        ]
    )

    assert (
        dof[
            "free_parameters"
        ]
        == 0
    )

    assert (
        dof[
            "permutation_searches"
        ]
        == 0
    )

    payload = {
        "audit_phase": "10F",
        "status": (
            "PLATO_MICHELL_HISTORICAL_SYNTHESIS_COMPLETE"
        ),
        "frozen_inputs": dict(
            FROZEN_HASHES
        ),
        "provenance_layers": {
            "plato": "DIRECT_PLATO_TEXT",
            "michell": "MICHELL_EXPLICIT",
            "reconstruction": "PROJECT_RECONSTRUCTION",
            "sommerville": "ARCHIVAL_PENDING",
            "later_interpretation": "INTERPRETIVE_EXCLUDED",
        },
        "established": {
            "plato": {
                "total_whorls": (
                    plato[
                        "literal_findings"
                    ][
                        "whorl_structure"
                    ][
                        "total_whorls"
                    ]
                ),
                "width_order_broadest_to_narrowest": (
                    plato_width_order
                ),
                "numeric_width_values_stated": False,
            },
            "michell": {
                "same_ordinal_width_order": True,
                "musical_number_sequence": (
                    michell[
                        "michell_explicit"
                    ][
                        "musical_argument"
                    ][
                        "base_sequence"
                    ]
                ),
                "shaft_radius": (
                    michell[
                        "michell_explicit"
                    ][
                        "unscaled_construction"
                    ][
                        "shaft_radius"
                    ]
                ),
                "scale_factor": (
                    michell[
                        "michell_explicit"
                    ][
                        "scaled_construction"
                    ][
                        "scale_factor"
                    ]
                ),
                "center_out_widths": (
                    michell[
                        "michell_explicit"
                    ][
                        "unscaled_construction"
                    ][
                        "center_out_ring_widths"
                    ]
                ),
            },
            "project_reconstruction": {
                "all_printed_values_reproduced_exactly": True,
                "free_parameters": (
                    dof[
                        "free_parameters"
                    ]
                ),
                "permutation_searches": (
                    dof[
                        "permutation_searches"
                    ]
                ),
                "scaled_cumulative_radii": (
                    reconstruction[
                        "reconstructed"
                    ][
                        "scaled_cumulative_radii_including_shaft"
                    ]
                ),
            },
        },
        "comparative_findings": {
            "ordinal_continuity_plato_to_michell": True,
            "numerical_magnitudes_added_in_michell_layer": True,
            "michell_numeric_sequence_is_direct_plato_text": False,
            "project_arithmetic_requires_fit": False,
            "numerical_reproducibility_implies_historical_transmission": False,
        },
        "historical_boundary": {
            "plato_numeric_intention_established": False,
            "ancient_transmission_established": False,
            "michell_numerical_interpretation_documented": True,
            "michell_internal_arithmetic_reproduced": True,
            "sommerville_archival_status": (
                manifest[
                    "SOMMERVILLE_1974_NOTE"
                ][
                    "current_status"
                ]
            ),
            "interpretive_framework_status": (
                manifest[
                    "USER_INTERPRETIVE_FRAMEWORK"
                ][
                    "current_status"
                ]
            ),
        },
        "claim_count": len(
            claims
        ),
    }

    return (
        payload,
        claims,
    )


def render_claim_csv(
    claims: list[dict[str, str]],
) -> str:
    fieldnames = [
        "claim_id",
        "claim",
        "provenance_class",
        "evidence_phase",
        "evidence_artifact",
        "status",
        "notes",
    ]

    buffer = io.StringIO()

    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        lineterminator="\n",
    )

    writer.writeheader()
    writer.writerows(
        claims
    )

    return buffer.getvalue()


def render_markdown(
    payload: dict,
) -> str:
    established = payload[
        "established"
    ]

    lines = [
        "# v1.0 Plato / Michell historical synthesis",
        "",
        "## Status",
        "",
        "`PLATO_MICHELL_HISTORICAL_SYNTHESIS_COMPLETE`",
        "",
        "This synthesis preserves the v1.0 evidential separation between "
        "Plato's text, Michell's interpretation, and project reconstruction.",
        "",
        "## What Plato supplies",
        "",
        "The frozen Republic extraction establishes eight nested whorls and "
        "the ordinal rim-width order:",
        "",
        "```text",
        "1 > 6 > 4 > 8 > 7 > 5 > 3 > 2",
        "```",
        "",
        "The audited passage does not supply numerical magnitudes or ratios "
        "for those rim widths.",
        "",
        "## What Michell adds",
        "",
        "Michell's 2008 table preserves the same ordinal order, but his "
        "musical argument supplies the numerical sequence:",
        "",
        "```text",
        "6, 8, 9, 12, 18, 24, 27, 36",
        "```",
        "",
        "His printed construction then gives:",
        "",
        "```text",
        "shaft radius: 4",
        "center-out widths: 18, 12, 27, 9, 24, 8, 6, 36",
        "scale factor: 180",
        "```",
        "",
        "These values belong to the `MICHELL_EXPLICIT` layer, not the "
        "`DIRECT_PLATO_TEXT` layer.",
        "",
        "## What the project reproduces",
        "",
        "Using the frozen ordinal order and Michell's frozen numerical inputs, "
        "the project reproduces the construction exactly with no fitted "
        "parameter and no permutation search.",
        "",
        "The scaled cumulative radii are:",
        "",
        "```text",
        "720, 3960, 6120, 10980, 12600, 16920, 18360, 19440, 25920",
        "```",
        "",
        "This reproduces Michell's printed `3960`, `6120`, and `2160` "
        "correspondence values without fitting.",
        "",
        "## Historical conclusion",
        "",
        "The source chain supports a precise but limited conclusion: Plato "
        "provides an ordinal eight-whorl structure; Michell documents a "
        "later numerical interpretation of that structure; and the project "
        "can reproduce Michell's arithmetic exactly.",
        "",
        "The audited evidence does **not** establish that Plato supplied or "
        "intended Michell's numerical magnitudes, and numerical agreement "
        "does **not** establish historical transmission from antiquity.",
        "",
        "## Parallel boundaries",
        "",
        "The Sommerville 1974 note remains `ARCHIVAL_PENDING` and is "
        "non-gating for this Plato/Michell audit. The later interpretive "
        "framework remains `INTERPRETIVE_EXCLUDED` from the v1.0 historical "
        "evidential layer.",
        "",
        "## Claim matrix",
        "",
        "The canonical claim-by-claim provenance table is:",
        "",
        "`docs/sources/v1.0_plato_michell_claim_matrix.csv`",
        "",
        f"Total claims: `{payload['claim_count']}`.",
        "",
    ]

    return "\n".join(
        lines
    )


def write_outputs() -> None:
    payload, claims = build_synthesis()

    JSON_OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    CSV_OUT.parent.mkdir(
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

    CSV_OUT.write_text(
        render_claim_csv(
            claims
        ),
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
        "claim_count",
        payload[
            "claim_count"
        ],
    )

    print(
        "plato_numeric_intention_established",
        payload[
            "historical_boundary"
        ][
            "plato_numeric_intention_established"
        ],
    )

    print(
        "ancient_transmission_established",
        payload[
            "historical_boundary"
        ][
            "ancient_transmission_established"
        ],
    )


if __name__ == "__main__":
    main()

