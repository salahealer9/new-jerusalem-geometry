from __future__ import annotations

from pathlib import Path
from fractions import Fraction
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]

PLATO_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_myth_of_er_literal.json"
)

MICHELL_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "michell_2008_ch4_literal.json"
)

JSON_OUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_whorl_reconstruction.json"
)

MARKDOWN_OUT = (
    ROOT
    / "docs"
    / "geometry"
    / "v1.0_plato_michell_whorl_reconstruction.md"
)

PLATO_SHA256 = (
    "42edbe735c6d91bc180198702f411889e"
    "05ea503989c24b0d44a134362a63f3c"
)

MICHELL_SHA256 = (
    "ef6e17b7d9de47157025a2bf3aa9812d"
    "79859a5cc3b7bbe44185a67bacc99807"
)


def sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def parse_fraction(
    value: str,
) -> Fraction:
    numerator, denominator = value.split(
        "/",
        1,
    )

    return Fraction(
        int(
            numerator
        ),
        int(
            denominator
        ),
    )


def reconstruct() -> dict:
    assert (
        sha256(
            PLATO_PATH
        )
        == PLATO_SHA256
    )

    assert (
        sha256(
            MICHELL_PATH
        )
        == MICHELL_SHA256
    )

    plato = json.loads(
        PLATO_PATH.read_text(
            encoding="utf-8"
        )
    )

    michell = json.loads(
        MICHELL_PATH.read_text(
            encoding="utf-8"
        )
    )

    plato_order = (
        plato[
            "literal_findings"
        ][
            "rim_widths"
        ][
            "order_broadest_to_narrowest_by_whorl_number"
        ]
    )

    explicit = michell[
        "michell_explicit"
    ]

    michell_order = (
        explicit[
            "plato_whorl_table"
        ][
            "broadest_to_narrowest_whorl_order"
        ]
    )

    assert (
        plato_order
        == michell_order
    )

    base_sequence = (
        explicit[
            "musical_argument"
        ][
            "base_sequence"
        ]
    )

    assert (
        len(
            base_sequence
        )
        == 8
    )

    assert (
        len(
            set(
                base_sequence
            )
        )
        == 8
    )

    sorted_for_width_rank = sorted(
        base_sequence,
        reverse=True,
    )

    width_by_whorl = {
        whorl: width
        for whorl, width in zip(
            plato_order,
            sorted_for_width_rank,
            strict=True,
        )
    }

    center_out_whorls = (
        explicit[
            "unscaled_construction"
        ][
            "center_out_whorl_numbers"
        ]
    )

    center_out_widths = [
        width_by_whorl[
            whorl
        ]
        for whorl in center_out_whorls
    ]

    first_sequence_number = (
        explicit[
            "unscaled_construction"
        ][
            "shaft_first_sequence_number"
        ]
    )

    shaft_factor = parse_fraction(
        explicit[
            "unscaled_construction"
        ][
            "shaft_musical_factor"
        ]
    )

    shaft_radius_fraction = (
        Fraction(
            first_sequence_number,
            1,
        )
        * shaft_factor
    )

    assert (
        shaft_radius_fraction.denominator
        == 1
    )

    shaft_radius = int(
        shaft_radius_fraction
    )

    cumulative_radii = [
        shaft_radius
    ]

    current = shaft_radius

    for width in center_out_widths:
        current += width

        cumulative_radii.append(
            current
        )

    scale_factor = (
        explicit[
            "scaled_construction"
        ][
            "scale_factor"
        ]
    )

    scaled_shaft_radius = (
        shaft_radius
        * scale_factor
    )

    scaled_ring_widths = [
        width
        * scale_factor
        for width in center_out_widths
    ]

    scaled_cumulative_radii = [
        radius
        * scale_factor
        for radius in cumulative_radii
    ]

    printed_ratios = [
        parse_fraction(
            value
        )
        for value in (
            explicit[
                "musical_argument"
            ][
                "successive_interval_ratios"
            ]
        )
    ]

    reconstructed_ratios = [
        Fraction(
            right,
            left,
        )
        for left, right in zip(
            base_sequence[
                :-1
            ],
            base_sequence[
                1:
            ],
            strict=True,
        )
    ]

    assert (
        reconstructed_ratios
        == printed_ratios
    )

    printed_unscaled = (
        explicit[
            "unscaled_construction"
        ]
    )

    printed_scaled = (
        explicit[
            "scaled_construction"
        ]
    )

    validation = {
        "plato_order_equals_michell_table": (
            plato_order
            == michell_order
        ),
        "musical_interval_ratios_reproduced": (
            reconstructed_ratios
            == printed_ratios
        ),
        "shaft_radius_reproduced": (
            shaft_radius
            == printed_unscaled[
                "shaft_radius"
            ]
        ),
        "center_out_ring_widths_reproduced": (
            center_out_widths
            == printed_unscaled[
                "center_out_ring_widths"
            ]
        ),
        "full_radius_reproduced": (
            cumulative_radii[
                -1
            ]
            == printed_unscaled[
                "full_radius"
            ]
        ),
        "scaled_shaft_radius_reproduced": (
            scaled_shaft_radius
            == printed_scaled[
                "shaft_radius"
            ]
        ),
        "scaled_ring_widths_reproduced": (
            scaled_ring_widths
            == printed_scaled[
                "center_out_ring_widths"
            ]
        ),
        "scaled_total_whorl_width_reproduced": (
            sum(
                scaled_ring_widths
            )
            == printed_scaled[
                "total_eight_whorl_width"
            ]
        ),
        "scaled_outer_radius_reproduced": (
            scaled_cumulative_radii[
                -1
            ]
            == printed_scaled[
                "outer_radius_including_shaft"
            ]
        ),
    }

    assert all(
        validation.values()
    )

    printed_correspondences = (
        explicit[
            "printed_dimensional_correspondences"
        ]
    )

    correspondence_values = {
        item[
            "label"
        ]: item[
            "value"
        ]
        for item in printed_correspondences
    }

    correspondence_checks = {
        "central_spindle_radius_720": (
            scaled_cumulative_radii[
                0
            ]
            == correspondence_values[
                "central spindle radius"
            ]
        ),
        "first_cumulative_radius_3960": (
            scaled_cumulative_radii[
                1
            ]
            == correspondence_values[
                "first cumulative radius"
            ]
        ),
        "second_cumulative_radius_6120": (
            scaled_cumulative_radii[
                2
            ]
            == correspondence_values[
                "second cumulative radius"
            ]
        ),
        "second_ring_width_2160": (
            scaled_ring_widths[
                1
            ]
            == correspondence_values[
                "second ring width"
            ]
        ),
    }

    assert all(
        correspondence_checks.values()
    )

    return {
        "audit_phase": "10E",
        "status": (
            "MICHELL_PLATO_NUMERICAL_"
            "RECONSTRUCTION_COMPLETE"
        ),
        "provenance_class": (
            "PROJECT_RECONSTRUCTION"
        ),
        "frozen_inputs": {
            "plato_literal_sha256": (
                PLATO_SHA256
            ),
            "michell_literal_sha256": (
                MICHELL_SHA256
            ),
        },
        "source_inputs": {
            "plato_width_order_broadest_to_narrowest": (
                plato_order
            ),
            "michell_width_order_broadest_to_narrowest": (
                michell_order
            ),
            "michell_base_sequence": (
                base_sequence
            ),
            "michell_shaft_first_sequence_number": (
                first_sequence_number
            ),
            "michell_shaft_factor": str(
                shaft_factor
            ),
            "michell_center_out_whorls": (
                center_out_whorls
            ),
            "michell_scale_factor": (
                scale_factor
            ),
        },
        "deterministic_algorithm": {
            "step_1": (
                "Verify Plato's ordinal rim-width order equals "
                "Michell's printed whorl table."
            ),
            "step_2": (
                "Sort Michell's eight distinct musical numbers "
                "from largest to smallest and assign them in the "
                "broadest-to-narrowest whorl order."
            ),
            "step_3": (
                "Read the resulting whorl widths in Michell's "
                "printed center-out whorl order 8,7,6,5,4,3,2,1."
            ),
            "step_4": (
                "Compute the shaft radius exactly as "
                "6 multiplied by 2/3."
            ),
            "step_5": (
                "Form cumulative radii by exact integer addition "
                "from the shaft outward."
            ),
            "step_6": (
                "Multiply the shaft radius, ring widths, and "
                "cumulative radii by Michell's printed scale "
                "factor 180."
            ),
            "free_parameters": 0,
            "permutation_searches": 0,
            "scale_fits": 0,
            "optimizations": 0,
            "nearest_match_choices": 0,
        },
        "reconstructed": {
            "descending_numbers_assigned_by_width_rank": (
                sorted_for_width_rank
            ),
            "width_by_whorl": {
                str(
                    key
                ): value
                for key, value in sorted(
                    width_by_whorl.items()
                )
            },
            "center_out_whorls": (
                center_out_whorls
            ),
            "center_out_ring_widths": (
                center_out_widths
            ),
            "shaft_radius": (
                shaft_radius
            ),
            "cumulative_radii_including_shaft": (
                cumulative_radii
            ),
            "full_radius": (
                cumulative_radii[
                    -1
                ]
            ),
            "scale_factor": (
                scale_factor
            ),
            "scaled_shaft_radius": (
                scaled_shaft_radius
            ),
            "scaled_ring_widths": (
                scaled_ring_widths
            ),
            "scaled_cumulative_radii_including_shaft": (
                scaled_cumulative_radii
            ),
            "scaled_total_whorl_width": sum(
                scaled_ring_widths
            ),
            "scaled_outer_radius": (
                scaled_cumulative_radii[
                    -1
                ]
            ),
            "successive_interval_ratios": [
                str(
                    ratio
                )
                for ratio in reconstructed_ratios
            ],
        },
        "exact_validation_against_michell_printed_values": (
            validation
        ),
        "printed_correspondence_value_checks": (
            correspondence_checks
        ),
        "historical_boundary": {
            "plato_supplies_numeric_widths": False,
            "michell_supplies_numeric_interpretation": True,
            "project_arithmetic_reproduces_michell": True,
            "historical_transmission_established": False,
            "plato_intention_established": False,
            "note": (
                "Exact arithmetic reproduction validates the "
                "internal numerical chain of Michell's printed "
                "construction. It does not establish that Plato "
                "intended Michell's numerical assignment."
            ),
        },
    }


def render_markdown(
    payload: dict,
) -> str:
    reconstructed = payload[
        "reconstructed"
    ]

    validation = payload[
        "exact_validation_against_michell_printed_values"
    ]

    lines = [
        "# v1.0 Plato / Michell whorl numerical reconstruction",
        "",
        "## Status",
        "",
        "`MICHELL_PLATO_NUMERICAL_RECONSTRUCTION_COMPLETE`",
        "",
        "Provenance class: `PROJECT_RECONSTRUCTION`.",
        "",
        "This phase performs exact deterministic arithmetic from the "
        "already-frozen Plato and Michell source extractions. It introduces "
        "no fit parameter, permutation search, scale optimization, or "
        "nearest-match choice.",
        "",
        "## Source relation",
        "",
        "The frozen Plato extraction gives the ordinal rim-width order:",
        "",
        "```text",
        "1 > 6 > 4 > 8 > 7 > 5 > 3 > 2",
        "```",
        "",
        "Michell's printed table gives the same ordinal order, while his "
        "musical argument supplies the eight numerical values:",
        "",
        "```text",
        "6, 8, 9, 12, 18, 24, 27, 36",
        "```",
        "",
        "Assigning the largest number to the broadest whorl, the next "
        "largest to the next-broadest, and so on gives:",
        "",
        "```text",
        "whorl 1 = 36",
        "whorl 6 = 27",
        "whorl 4 = 24",
        "whorl 8 = 18",
        "whorl 7 = 12",
        "whorl 5 = 9",
        "whorl 3 = 8",
        "whorl 2 = 6",
        "```",
        "",
        "Reading those widths from the center outward in Michell's printed "
        "whorl order `8, 7, 6, 5, 4, 3, 2, 1` produces:",
        "",
        "```text",
        "18, 12, 27, 9, 24, 8, 6, 36",
        "```",
        "",
        "## Shaft and cumulative radii",
        "",
        "Michell's shaft rule is reproduced exactly:",
        "",
        "```text",
        "6 × 2/3 = 4",
        "```",
        "",
        "Adding the ring widths successively from that shaft gives:",
        "",
        "```text",
        "4, 22, 34, 61, 70, 94, 102, 108, 144",
        "```",
        "",
        "Thus the eight whorls total `140`, and the complete unscaled "
        "radius is `144`.",
        "",
        "## Scale by 180",
        "",
        "Applying Michell's printed scale factor `180` gives:",
        "",
        "```text",
        "shaft radius: 720",
        "ring widths: 3240, 2160, 4860, 1620, 4320, 1440, 1080, 6480",
        "cumulative radii: 720, 3960, 6120, 10980, 12600, 16920, 18360, 19440, 25920",
        "total whorl width: 25200",
        "outer radius: 25920",
        "```",
        "",
        "The first two cumulative radii and the second ring width therefore "
        "reproduce Michell's printed values `3960`, `6120`, and `2160` "
        "without fitting.",
        "",
        "## Exact validation",
        "",
    ]

    for key, passed in validation.items():
        lines.append(
            f"- `{key}`: `{str(passed).lower()}`"
        )

    lines.extend(
        [
            "",
            "## Degrees of freedom",
            "",
            "```text",
            "free parameters: 0",
            "permutation searches: 0",
            "scale fits: 0",
            "optimizations: 0",
            "nearest-match choices: 0",
            "```",
            "",
            "## Historical boundary",
            "",
            "This exact arithmetic reproduction shows that Michell's printed "
            "numerical construction is internally reproducible from the "
            "frozen source inputs. It does **not** show that Plato supplied "
            "the numerical widths, intended Michell's assignment, or that "
            "the numerical scheme was historically transmitted from "
            "antiquity.",
            "",
        ]
    )

    return "\n".join(
        lines
    )


def write_outputs() -> None:
    payload = reconstruct()

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

    reconstructed = payload[
        "reconstructed"
    ]

    print(
        payload[
            "status"
        ]
    )

    print(
        "center_out_widths",
        reconstructed[
            "center_out_ring_widths"
        ],
    )

    print(
        "cumulative_radii",
        reconstructed[
            "cumulative_radii_including_shaft"
        ],
    )

    print(
        "scaled_cumulative_radii",
        reconstructed[
            "scaled_cumulative_radii_including_shaft"
        ],
    )

    print(
        "all_exact_checks",
        all(
            payload[
                "exact_validation_against_michell_printed_values"
            ].values()
        ),
    )


if __name__ == "__main__":
    main()

