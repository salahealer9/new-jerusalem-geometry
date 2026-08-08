from __future__ import annotations

from pathlib import Path

from new_jerusalem_geometry.dodecagon_vertex_radius_audit import (
    OBLIQUE_PAIR_VERTEX,
    POLAR_ADJACENT_VERTEX,
    write_vertex_radius_audit,
)


OUTPUT = Path(
    "data/analysis/njg_michell_v0_7/"
    "dodecagon_vertex_radius_audit.json"
)


path = write_vertex_radius_audit(
    OUTPUT
)

import json

document = json.loads(
    path.read_text(
        encoding="utf-8"
    )
)

comparison = document[
    "normalized_comparison"
]

classes = document[
    "class_summaries"
]

print(
    path
)

print()

print(
    "Stopping status:",
    document[
        "stopping_status"
    ],
)

print(
    "Historical targets loaded:",
    document[
        "determinacy"
    ][
        "historical_dimensional_targets_loaded"
    ],
)

print(
    "Historical comparison metrics calculated:",
    document[
        "determinacy"
    ][
        "historical_comparison_metrics_calculated"
    ],
)

print()

print(
    "Regular baseline radius:",
    f"{comparison['regular_baseline_radius']:.15g}",
    "u",
)

print(
    "Polar-adjacent class:",
    classes[
        POLAR_ADJACENT_VERTEX
    ][
        "vertex_count"
    ],
    "vertices; mean radius",
    (
        f"{comparison['polar_adjacent_mean_radius']:.15g}"
    ),
    "u",
)

print(
    "Oblique-pair class:",
    classes[
        OBLIQUE_PAIR_VERTEX
    ][
        "vertex_count"
    ],
    "vertices; mean radius",
    (
        f"{comparison['oblique_pair_mean_radius']:.15g}"
    ),
    "u",
)

print(
    "Polar minus regular:",
    (
        f"{comparison['polar_adjacent_minus_regular']:.15g}"
    ),
    "u",
)

print(
    "Oblique minus regular:",
    (
        f"{comparison['oblique_pair_minus_regular']:.15g}"
    ),
    "u",
)

print(
    "Raw normalized class ratio:",
    (
        f"{comparison['polar_adjacent_to_oblique_pair_ratio']:.15g}"
    ),
)

print(
    "Maximum absolute radial displacement:",
    (
        f"{comparison['maximum_absolute_radial_displacement_from_regular']:.15g}"
    ),
    "u",
)

print(
    "Polar-adjacent matches regular:",
    comparison[
        "polar_adjacent_matches_regular"
    ],
)

print(
    "Oblique-pair all inward:",
    comparison[
        "oblique_pair_vertices_all_inward"
    ],
)
