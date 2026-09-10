#!/usr/bin/env python3
"""Generate the Phase 10G Plato–Michell visual capstone."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from new_jerusalem_geometry.plato_michell_whorl_svg import (
    plato_michell_whorl_capstone_to_svg,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_whorl_reconstruction.json"
)
OUTPUT = (
    ROOT
    / "figures"
    / "generated"
    / "v1.0_plato_michell_whorl_capstone.svg"
)


def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))
    svg = plato_michell_whorl_capstone_to_svg(data) + "\n"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")

    digest = hashlib.sha256(svg.encode("utf-8")).hexdigest()
    print(f"input:  {INPUT.relative_to(ROOT)}")
    print(f"output: {OUTPUT.relative_to(ROOT)}")
    print(f"bytes:  {len(svg.encode('utf-8'))}")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    main()
