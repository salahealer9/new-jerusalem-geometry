from collections import Counter
from pathlib import Path
import csv


CLAIM_MATRIX = Path(
    "docs/sources/geometric_claim_matrix.csv"
)


EXPECTED_FIELDS = (
    "claim_id",
    "claim",
    "book",
    "printed_page",
    "pdf_page",
    "figure",
    "source_status",
    "mathematical_implication",
    "implemented_model",
    "notes",
)


def _rows():
    with CLAIM_MATRIX.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle
        )

        assert (
            tuple(reader.fieldnames or ())
            == EXPECTED_FIELDS
        )

        return list(
            reader
        )


def test_claim_matrix_has_unique_ids() -> None:
    rows = _rows()

    counts = Counter(
        row["claim_id"]
        for row in rows
    )

    duplicates = {
        claim_id: count
        for claim_id, count
        in counts.items()
        if count != 1
    }

    assert duplicates == {}


def test_claim_matrix_has_no_blank_claim_ids() -> None:
    rows = _rows()

    assert all(
        row["claim_id"].strip()
        for row in rows
    )


def test_claim_matrix_rows_match_header() -> None:
    rows = _rows()

    assert rows

    for row in rows:
        assert set(row) == set(
            EXPECTED_FIELDS
        )


def test_seven_002_is_verified_by_scaffold_model() -> None:
    rows = {
        row["claim_id"]: row
        for row in _rows()
    }

    claim = rows["SEVEN-002"]

    assert (
        claim["source_status"]
        == "stated_approximate"
    )

    assert (
        claim["implemented_model"]
        == "michell_28_point_scaffold"
    )

    assert (
        "0.0008191945196658335"
        in claim["notes"]
    )

    assert (
        "below 0.001"
        in claim["notes"]
    )
