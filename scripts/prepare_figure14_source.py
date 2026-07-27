#!/usr/bin/env python3
"""Render Michell's Figure 14 source page and record provenance.

The source PDF and generated PNG remain local and must not be committed.
The JSON manifest contains no source content and may later be committed
after review.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

from new_jerusalem_geometry.source_preparation import (
    build_manifest,
)


DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure14"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Render the PDF page containing Michell's "
            "Figure 14 and record its provenance."
        )
    )

    parser.add_argument(
        "--pdf",
        type=Path,
        required=True,
        help="Path to the local City of Revelation PDF.",
    )

    parser.add_argument(
        "--page",
        type=int,
        default=69,
        help=(
            "One-based PDF page number containing Figure 14. "
            "Default: 69."
        ),
    )

    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Rendering resolution. Default: 300 DPI.",
    )

    parser.add_argument(
        "--output-directory",
        type=Path,
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=(
            "Local untracked output directory. "
            f"Default: {DEFAULT_OUTPUT_DIRECTORY}"
        ),
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.pdf.is_file():
        print(f"ERROR: PDF not found: {args.pdf}")
        return 1

    if args.page < 1:
        print("ERROR: --page must be at least 1.")
        return 1

    if args.dpi < 72:
        print("ERROR: --dpi must be at least 72.")
        return 1

    renderer = shutil.which("pdftoppm")

    if renderer is None:
        print(
            "ERROR: pdftoppm was not found. "
            "Install the poppler-utils package."
        )
        return 1

    args.output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_stem = (
        args.output_directory
        / f"city_of_revelation_page_{args.page:03d}"
    )

    output_path = output_stem.with_suffix(".png")
    manifest_path = (
        args.output_directory
        / "figure14_source_manifest.json"
    )

    command = [
        renderer,
        "-f",
        str(args.page),
        "-l",
        str(args.page),
        "-r",
        str(args.dpi),
        "-png",
        "-singlefile",
        str(args.pdf),
        str(output_stem),
    ]

    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        print("ERROR: PDF page rendering failed.")

        if completed.stderr:
            print(completed.stderr.strip())

        return completed.returncode

    if not output_path.is_file():
        print(
            "ERROR: renderer completed but the PNG "
            f"was not created: {output_path}"
        )
        return 1

    manifest = build_manifest(
        pdf_path=args.pdf,
        output_path=output_path,
        page=args.page,
        dpi=args.dpi,
        renderer=renderer,
    )

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    width = manifest["extraction"][
        "png_width_pixels"
    ]

    height = manifest["extraction"][
        "png_height_pixels"
    ]

    print("Figure 14 source preparation")
    print("=" * 28)
    print(f"Source PDF:       {args.pdf}")
    print(
        f"SHA-256:          "
        f"{manifest['source']['sha256']}"
    )
    print(f"PDF page:         {args.page}")
    print(f"Resolution:       {args.dpi} DPI")
    print(f"Rendered PNG:     {output_path}")
    print(f"Pixel dimensions: {width} × {height}")
    print(f"Manifest:         {manifest_path}")
    print()
    print(
        "The PDF and PNG are local working files "
        "and must remain untracked."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
