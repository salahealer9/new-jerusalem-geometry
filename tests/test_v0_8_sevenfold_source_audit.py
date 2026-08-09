from __future__ import annotations

import csv
from pathlib import Path

import new_jerusalem_geometry as njg


ROOT = Path(
    __file__
).resolve().parents[
    1
]

CLAIMS = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)

AUDIT = (
    ROOT
    / "docs"
    / "sources"
    / "v0.8_sevenfold_dual_method_source_audit.md"
)


NEW_IDS = (
    "SEVEN-010",
    "SEVEN-011",
    "SEVEN-012",
    "SEVEN-013",
    "SEVEN-014",
)


def _rows() -> dict[
    str,
    dict[
        str,
        str,
    ],
]:
    with CLAIMS.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        return {
            row[
                "claim_id"
            ]: row
            for row in reader
        }


def test_phase8a_source_rows_exist_exactly_once() -> None:
    with CLAIMS.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(
                handle
            )
        )

    ids = [
        row[
            "claim_id"
        ]
        for row in rows
    ]

    for claim_id in NEW_IDS:
        assert (
            ids.count(
                claim_id
            )
            == 1
        )


def test_method2_source_rows_bind_to_figure194() -> None:
    rows = _rows()

    for claim_id in (
        "SEVEN-010",
        "SEVEN-011",
        "SEVEN-012",
        "SEVEN-013",
    ):
        row = rows[
            claim_id
        ]

        assert (
            row[
                "book"
            ]
            == "How the World Is Made"
        )

        assert (
            row[
                "printed_page"
            ]
            == "221"
        )

        assert (
            row[
                "pdf_page"
            ]
            == "239"
        )

        assert (
            row[
                "figure"
            ]
            == "194"
        )

        assert (
            row[
                "source_status"
            ]
            == "stated_approximate"
        )


def test_method2_chain_is_registered_as_7_21_42() -> None:
    rows = _rows()

    assert (
        "second approximate sevenfold method"
        in rows[
            "SEVEN-011"
        ][
            "mathematical_implication"
        ]
    )

    assert (
        "twenty-one-part division"
        in rows[
            "SEVEN-012"
        ][
            "mathematical_implication"
        ]
    )

    assert (
        "forty-two-point division"
        in rows[
            "SEVEN-013"
        ][
            "mathematical_implication"
        ]
    )


def test_method2_accuracy_is_not_inherited_from_method1() -> None:
    rows = _rows()

    method2_text = " ".join(
        rows[
            claim_id
        ][
            "claim"
        ]
        + " "
        + rows[
            claim_id
        ][
            "notes"
        ]
        for claim_id in (
            "SEVEN-011",
            "SEVEN-012",
            "SEVEN-013",
        )
    )

    assert (
        "1 in 1000"
        not in method2_text
    )

    assert (
        "one part in one thousand"
        not in method2_text
    )


def test_project_derivation_is_separate_from_source_claims() -> None:
    row = _rows()[
        "SEVEN-014"
    ]

    assert (
        row[
            "book"
        ]
        == "Present project"
    )

    assert (
        row[
            "source_status"
        ]
        == "project_derivation"
    )

    assert (
        "cos(alpha_2)=5/8"
        in row[
            "claim"
        ]
    )

    assert (
        "alpha_2=arccos(5/8)"
        in row[
            "claim"
        ]
    )


def test_phase8a_rows_are_not_implemented_yet() -> None:
    rows = _rows()

    assert all(
        rows[
            claim_id
        ][
            "implemented_model"
        ]
        == "not_yet_implemented"
        for claim_id in NEW_IDS
    )


def test_phase8a_audit_defers_numerical_comparison() -> None:
    text = AUDIT.read_text(
        encoding="utf-8"
    )

    required = (
        "does **not** calculate or register",
        "decimal value of `alpha_2`",
        "residual from exact `360/7`",
        "ranking against Method 1",
        "compensation",
        "Figure 14 residual",
        "pass/fail tolerance",
    )

    for phrase in required:
        assert phrase in text


def test_phase8a_audit_records_no_grammar_change() -> None:
    text = AUDIT.read_text(
        encoding="utf-8"
    )

    assert (
        "construction grammar is intentionally unchanged"
        in text
    )


def test_phase8a_package_version_remains_0_7_0() -> None:
    assert (
        njg.__version__
        == "0.7.0"
    )
