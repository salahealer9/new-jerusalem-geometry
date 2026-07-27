import hashlib
import struct
import zlib
from pathlib import Path

import pytest

from new_jerusalem_geometry.source_preparation import (
    read_png_dimensions,
    sha256_file,
)


def _write_minimal_png(
    path: Path,
    *,
    width: int,
    height: int,
) -> None:
    signature = b"\x89PNG\r\n\x1a\n"

    ihdr_data = struct.pack(
        ">IIBBBBB",
        width,
        height,
        8,
        2,
        0,
        0,
        0,
    )

    chunk_type = b"IHDR"

    ihdr = (
        struct.pack(">I", len(ihdr_data))
        + chunk_type
        + ihdr_data
        + struct.pack(
            ">I",
            zlib.crc32(
                chunk_type + ihdr_data
            )
            & 0xFFFFFFFF,
        )
    )

    path.write_bytes(signature + ihdr)


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "source.bin"
    content = b"New Jerusalem Geometry\n"

    path.write_bytes(content)

    assert sha256_file(path) == hashlib.sha256(
        content
    ).hexdigest()


def test_read_png_dimensions(
    tmp_path: Path,
) -> None:
    path = tmp_path / "image.png"

    _write_minimal_png(
        path,
        width=2480,
        height=3508,
    )

    assert read_png_dimensions(path) == (
        2480,
        3508,
    )


def test_read_png_dimensions_rejects_non_png(
    tmp_path: Path,
) -> None:
    path = tmp_path / "not-an-image.bin"
    path.write_bytes(b"not a png")

    with pytest.raises(
        ValueError,
        match="Not a valid PNG",
    ):
        read_png_dimensions(path)
