from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.dodecagon_geometry_freeze_svg import (
    load_frozen_phase7b_audit,
    write_phase7c_svgs,
)


audit = load_frozen_phase7b_audit()

paths = write_phase7c_svgs(
    Path(
        "figures/generated"
    )
)

print(
    "Phase 7C stopping status:",
    "EXISTING_FROZEN_WALL_IS_COMPLETE_DODECAGON_GEOMETRY",
)

print(
    "Historical targets loaded:",
    False,
)

print(
    "Historical comparison metrics calculated:",
    False,
)

print()

comparison = audit[
    "normalized_comparison"
]

print(
    "Polar-adjacent radius:",
    f"{comparison['polar_adjacent_mean_radius']:.15g}",
    "u",
)

print(
    "Oblique-pair radius:",
    f"{comparison['oblique_pair_mean_radius']:.15g}",
    "u",
)

print(
    "Oblique inward displacement:",
    f"{comparison['oblique_pair_minus_regular']:.15g}",
    "u",
)

print(
    "Raw normalized class ratio:",
    f"{comparison['polar_adjacent_to_oblique_pair_ratio']:.15g}",
)

print()

for path in paths:
    print(
        path
    )

    print(
        "bytes:",
        path.stat().st_size,
    )
