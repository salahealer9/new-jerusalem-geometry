#!/usr/bin/env python3
"""Create white-background paper derivatives of frozen canonical SVGs.

This is a publication-only transformation. It must not alter canonical SVGs.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "figures" / "generated"
OUT_DIR = ROOT / "paper" / "figures"

FIGURES = (
    ("figure01_njg_michell_composite.svg", "njg_michell_composite.svg",
     "complete unit-only generative reconstruction"),
    ("figure02_figure14_heptagram.svg", "michell_figure14_heptagram.svg",
     "source-calibrated Figure 14 {7/2} comparison"),
    ("figure03_method1_28_point_scaffold.svg", "michell_28_point_scaffold.svg",
     "Michell Method 1 approximate 7-14-28 scaffold"),
    ("figure04_method2_7_21_42.svg", "v0.8_method2_7_21_42.svg",
     "Michell Method 2 approximate 7-21-42 propagation"),
    ("figure05_exact_heptagon_synthesis.svg", "v0.9_exact_heptagon_synthesis.svg",
     "exact sevenfold boundary and one-trisection synthesis"),
    ("figure06_plato_michell_whorls.svg", "v1.0_plato_michell_whorl_capstone.svg",
     "Plato-Michell eight-whorl historical/numerical synthesis"),
)

SVG_OPEN_RE = re.compile(r"<svg\b([^>]*)>", re.IGNORECASE)
VIEWBOX_RE = re.compile(
    r'\bviewBox="([^"]+)"',
    re.IGNORECASE,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def white_background_svg(text: str) -> tuple[str, str]:
    """Return paper SVG and conversion mode."""
    m = SVG_OPEN_RE.search(text)
    if not m:
        raise ValueError("SVG root element not found")

    attrs = m.group(1)
    vm = VIEWBOX_RE.search(attrs)
    if not vm:
        raise ValueError("SVG viewBox is required for deterministic paper export")

    parts = vm.group(1).split()
    if len(parts) != 4:
        raise ValueError(f"Unexpected viewBox: {vm.group(1)!r}")

    min_x, min_y, vb_w, vb_h = parts

    # Phase 10G already contains a full-canvas background. Convert only that
    # paper derivative from the canonical near-white fill to pure white.
    if (
        'v1.0_plato_michell_whorl_capstone' in text
        or 'The Spindle of Necessity' in text
    ):
        old = '<rect x="0" y="0" width="1800" height="1080" fill="#fbfaf7" />'
        if old not in text:
            raise ValueError(
                "Expected Phase 10G full-canvas background was not found"
            )
        return (
            text.replace(
                old,
                '<rect x="0" y="0" width="1800" height="1080" fill="#ffffff" />',
                1,
            ),
            "near-white-to-white",
        )

    rect = (
        f'<rect id="paper-background" x="{min_x}" y="{min_y}" '
        f'width="{vb_w}" height="{vb_h}" fill="#ffffff" />'
    )

    # Insert immediately after the root opening tag. SVG title/desc/metadata
    # remain intact; the new rect is the first rendered object.
    end = m.end()
    return text[:end] + "\n" + rect + text[end:], "transparent-to-white"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []

    for paper_name, source_name, role in FIGURES:
        source_path = SRC_DIR / source_name
        out_path = OUT_DIR / paper_name

        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        source_bytes = source_path.read_bytes()
        source_text = source_bytes.decode("utf-8")

        paper_text, mode = white_background_svg(source_text)

        # Publication-only title normalization for Figure 5.
        # The canonical v0.9 artifact remains byte-identical; the paper
        # derivative omits the internal development-version prefix.
        if source_name == "v0.9_exact_heptagon_synthesis.svg":
            paper_text = paper_text.replace(
                "<title>v0.9 exact-heptagon synthesis</title>",
                "<title>Exact-heptagon synthesis</title>",
                1,
            )
            paper_text = paper_text.replace(
                "v0.9 exact-heptagon comparison and one-trisection synthesis",
                "Exact-heptagon comparison and one-trisection synthesis",
                1,
            )
            mode += "+paper-title-normalization"

        paper_bytes = paper_text.encode("utf-8")
        out_path.write_bytes(paper_bytes)

        rows.append(
            {
                "paper_figure": str(out_path.relative_to(ROOT)),
                "canonical_source": str(source_path.relative_to(ROOT)),
                "canonical_sha256": sha256_bytes(source_bytes),
                "paper_sha256": sha256_bytes(paper_bytes),
                "transformation": mode,
                "scientific_geometry_changed": "false",
                "role": role,
            }
        )

    manifest = OUT_DIR / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=(
                "paper_figure",
                "canonical_source",
                "canonical_sha256",
                "paper_sha256",
                "transformation",
                "scientific_geometry_changed",
                "role",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"wrote {len(rows)} paper SVGs")
    print(manifest.relative_to(ROOT))


if __name__ == "__main__":
    main()
