#!/usr/bin/env python3
"""Export the bounded v1.0 Sommerville archival-search closeout.

This exporter records metadata only.  The research-use-only archival scans
are deliberately not read, copied, embedded, or redistributed by this script.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = ROOT / "data/reference/v1_0_sommerville_archival_closeout.json"
MD_OUT = ROOT / "docs/checkpoints/v1_0_sommerville_archival_closeout.md"

RECORD = {
    "status": "V1_0_SOMMERVILLE_ARCHIVAL_SEARCH_SUPPLIED_MATERIALS_REVIEWED",
    "scientific_content_reopened": False,
    "collection": {
        "repository": "Thompson Library Special Collections, The Ohio State University",
        "collection_name": "William S. Burroughs Papers",
        "collection_identifier": "SPEC.RARE.0087",
        "requested_location": "box 30, folders 253-254",
    },
    "research_target": (
        "Direct primary witness to the Ian Sommerville geometric work reported "
        "by John Michell and associated in the project with a 1974 source."
    ),
    "delivery": {
        "files_finalized_and_link_supplied_date": "2026-09-02",
        "quoted_scan_count": 58,
        "supplied_pdf_page_count": 50,
        "page_count_difference": 8,
        "completeness_clarification_requested_date": "2026-09-02",
        "completeness_confirmation_received": False,
        "interpretation": (
            "The difference is recorded as an unresolved scan-count versus "
            "PDF-page-count issue; it is not classified as eight missing pages."
        ),
    },
    "supplied_files": [
        {
            "filename": "SPEC-RARE-CMS-0087-b30-f253.pdf",
            "pdf_pages": 12,
            "sha256": "56450ebbae8706125898df2816f57969c4d31d8f4727449b834655946dacdf61",
            "redistribution": "NO",
            "access_boundary": "research-use-only archival reproduction",
        },
        {
            "filename": "SPEC-RARE-CMS-0087-b30-f254.pdf",
            "pdf_pages": 38,
            "sha256": "2df9a4d351ce3cc1c5ecce087b92e28f0da1f60cf00fd65c78f72164401497a0",
            "redistribution": "NO",
            "access_boundary": "research-use-only archival reproduction",
        },
    ],
    "review_outcome": {
        "direct_1974_geometric_witness_found": False,
        "dodecagon_derivation_found": False,
        "project_relevant_numeric_source_found": False,
        "classification": "BOUNDED_NEGATIVE_ARCHIVAL_EVIDENCE",
        "primary_source_status_after_review": "ARCHIVAL_PENDING",
    },
    "contextual_evidence": {
        "relevant": True,
        "summary": (
            "Posthumous 1978 correspondence from Edith Sommerville records "
            "that Ian Sommerville's papers/property had been tampered with and "
            "that material was missing; it also records that John Michell had "
            "been contacted about material belonging to Ian."
        ),
        "interpretive_limit": (
            "The supplied-folder negative result therefore cannot establish "
            "that the reported primary item never existed."
        ),
    },
    "release_interpretation": (
        "The targeted archival branch is complete for the materials supplied. "
        "No direct witness was recovered.  The scientific and mathematical "
        "results are unchanged, and ARCHIVAL_PENDING is retained."
    ),
}


def canonical_json_bytes(obj: object) -> bytes:
    return (
        json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)

    json_bytes = canonical_json_bytes(RECORD)
    JSON_OUT.write_bytes(json_bytes)
    json_sha = sha256_bytes(json_bytes)

    md = f"""# v1.0 Sommerville archival-search closeout

## Status

`{RECORD["status"]}`

Scientific content reopened: **NO**

Primary-source status after review: **ARCHIVAL_PENDING**

## Archival target

- Repository: Thompson Library Special Collections, The Ohio State University
- Collection: William S. Burroughs Papers
- Identifier: `SPEC.RARE.0087`
- Requested location: box 30, folders 253--254
- Research target: direct primary witness to the Ian Sommerville geometric work
  reported by John Michell and associated in the project with a 1974 source.

## Supplied research files

The watermarked PDFs are research-use-only archival reproductions and are
**not redistributed** by the project.

| File | PDF pages | SHA-256 |
| --- | ---: | --- |
| `SPEC-RARE-CMS-0087-b30-f253.pdf` | 12 | `56450ebbae8706125898df2816f57969c4d31d8f4727449b834655946dacdf61` |
| `SPEC-RARE-CMS-0087-b30-f254.pdf` | 38 | `2df9a4d351ce3cc1c5ecce087b92e28f0da1f60cf00fd65c78f72164401497a0` |

Total supplied PDF pages: **50**.

The archive's original quotation referred to **58 scans/pages**.  A
completeness clarification was requested on 2026-09-02.  No confirmation is
recorded at this checkpoint.  The eight-count difference is therefore logged
as an unresolved **scan-count versus PDF-page-count** issue, not as a finding
that eight pages are missing.

## Review result

No direct witness to the reported 1974 geometric work was identified in the
materials supplied.  In particular, the review recovered no project-relevant
dodecagon derivation or numerical source capable of independently validating
the Sommerville-attributed values.

Classification:

`BOUNDED_NEGATIVE_ARCHIVAL_EVIDENCE`

This does **not** change the unresolved primary-source classification:

`ARCHIVAL_PENDING`

## Contextual archival evidence

The supplied posthumous correspondence includes a 1978 letter from Edith
Sommerville stating that Ian Sommerville's papers/property had been tampered
with before recovery and that material was missing.  The same correspondence
records that John Michell had been contacted regarding material belonging to
Ian.

Accordingly, failure to locate the geometric primary item in the supplied
folders cannot establish that the item never existed.

## Release consequence

The targeted archival-search branch is closed for the materials supplied.

No geometry, theorem, numerical result, figure, construction grammar, or
source-calibrated result is changed.  The only manuscript consequence is a
bounded provenance statement documenting the negative archival search and its
limitation.

## Machine-readable record

`data/reference/v1_0_sommerville_archival_closeout.json`

SHA-256: `{json_sha}`
"""
    MD_OUT.write_text(md, encoding="utf-8")

    print("v1.0 Sommerville archival-search closeout exported")
    print()
    print(f"JSON: {JSON_OUT.relative_to(ROOT)}")
    print(f"JSON SHA256: {json_sha}")
    print()
    print(f"Markdown: {MD_OUT.relative_to(ROOT)}")
    print(f"Markdown SHA256: {sha256_bytes(md.encode('utf-8'))}")
    print()
    print("DIRECT 1974 GEOMETRIC WITNESS: NOT FOUND")
    print("PRIMARY SOURCE STATUS: ARCHIVAL_PENDING")
    print("EVIDENCE CLASS: BOUNDED_NEGATIVE_ARCHIVAL_EVIDENCE")
    print("SCIENTIFIC CONTENT REOPENED: NO")


if __name__ == "__main__":
    main()
