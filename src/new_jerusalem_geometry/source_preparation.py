"""Utilities for reproducible source-page preparation.

These functions contain no copyrighted source material. They calculate
checksums, inspect rendered PNG files, and build provenance metadata.
"""

from __future__ import annotations

import hashlib
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of a file."""

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def read_png_dimensions(path: Path) -> tuple[int, int]:
    """Read PNG width and height without an image dependency."""

    with path.open("rb") as handle:
        signature = handle.read(8)

        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError(
                f"Not a valid PNG file: {path}"
            )

        length_bytes = handle.read(4)
        chunk_type = handle.read(4)

        if len(length_bytes) != 4:
            raise ValueError(
                f"PNG lacks a valid IHDR chunk: {path}"
            )

        chunk_length = struct.unpack(
            ">I",
            length_bytes,
        )[0]

        if chunk_type != b"IHDR" or chunk_length < 8:
            raise ValueError(
                f"PNG lacks a valid IHDR chunk: {path}"
            )

        dimensions = handle.read(8)

        if len(dimensions) != 8:
            raise ValueError(
                f"PNG has an incomplete IHDR chunk: {path}"
            )

        width, height = struct.unpack(
            ">II",
            dimensions,
        )

    return width, height


def command_version(executable: str) -> str:
    """Return the first available executable-version line."""

    attempts = (
        [executable, "-v"],
        [executable, "--version"],
    )

    for command in attempts:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )

        combined = "\n".join(
            part
            for part in (
                completed.stdout,
                completed.stderr,
            )
            if part
        ).strip()

        if combined:
            return combined.splitlines()[0]

    return "version unavailable"


def build_manifest(
    *,
    pdf_path: Path,
    output_path: Path,
    page: int,
    dpi: int,
    renderer: str,
) -> dict[str, Any]:
    """Build the source-provenance manifest."""

    width, height = read_png_dimensions(
        output_path
    )

    return {
        "schema_version": 1,
        "source": {
            "bibliographic_work": (
                "John Michell, City of Revelation"
            ),
            "local_filename": pdf_path.name,
            "sha256": sha256_file(pdf_path),
            "file_size_bytes": pdf_path.stat().st_size,
        },
        "extraction": {
            "pdf_page_1_based": page,
            "dpi": dpi,
            "renderer": renderer,
            "renderer_version": command_version(
                renderer
            ),
            "png_filename": output_path.name,
            "png_width_pixels": width,
            "png_height_pixels": height,
            "rendered_at_utc": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "repository_policy": {
            "source_pdf_committed": False,
            "rendered_page_committed": False,
            "manifest_candidate_for_commit": True,
        },
    }
