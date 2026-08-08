from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.dodecagon_vertex_radius_svg import (
    write_phase7b_svgs,
)


paths = write_phase7b_svgs(
    Path(
        "figures/generated"
    )
)

for path in paths:
    print(
        path
    )

    print(
        "bytes:",
        path.stat().st_size,
    )
