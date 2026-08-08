"""Geometry-only audit of frozen NJG_MICHELL dodecagon vertex radii.

Phase 7B does not load historical dimensional targets and does not calculate
historical residuals.  It audits the already-frozen POLAR_PIVOT_WALL and a
parameter-free regular-dodecagon baseline sharing the inherited apothem.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import cos, hypot, pi, sin
from pathlib import Path
from typing import Any, Iterable

from .michell_composite import build_michell_composite


SCHEMA_VERSION = "1.0"

PROTOCOL_PATH = (
    "docs/specification/"
    "v0.7_dodecagon_vertex_radius_audit_protocol.md"
)

PROTOCOL_SHA256 = (
    "ae064694591bc341f70ba334c173c6a8"
    "a52afcd0fc73a2b1b1a557636f772c23"
)

PHASE7A_CLARIFICATION_PATH = (
    "docs/sources/"
    "v0.7_sommerville_dodecagon_source_clarification.md"
)

PHASE7A_CLARIFICATION_SHA256 = (
    "da8f237ae413c85b755a6e148a62fd9d"
    "402c63ffd833d50e110d1c1c5520bae2"
)

FROZEN_GEOMETRY_PATH = (
    "data/geometry/njg_michell_v0_5/"
    "njg_michell_geometry.json"
)

FROZEN_GEOMETRY_SHA256 = (
    "19e22356378d581a2adb35c8f8b8ee023"
    "7f61ab365d8cbc05abc378568e3b6cb"
)

WALL_MODEL = "POLAR_PIVOT_WALL"

VERTEX_COUNT = 12

POLAR_SIDE_INDICES = frozenset(
    {
        0,
        3,
        6,
        9,
    }
)

POLAR_ADJACENT_VERTEX = (
    "POLAR_ADJACENT_VERTEX"
)

OBLIQUE_PAIR_VERTEX = (
    "OBLIQUE_PAIR_VERTEX"
)

EXPECTED_CLASS_COUNTS = {
    POLAR_ADJACENT_VERTEX: 8,
    OBLIQUE_PAIR_VERTEX: 4,
}

REGULAR_APOTHEM = 8.5

ABS_TOL = 1.0e-12
REL_TOL = 1.0e-12


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class AuditedVertex:
    index: int
    vertex_id: str
    point: Point
    incident_side_indices: tuple[int, int]
    incident_side_classes: tuple[str, str]
    vertex_class: str
    radius: float
    angle_radians: float
    regular_point: Point
    regular_radius: float
    radial_difference_from_regular: float


def _sha256(
    path: str | Path,
) -> str:
    return hashlib.sha256(
        Path(
            path
        ).read_bytes()
    ).hexdigest()


def verify_frozen_inputs() -> None:
    checks = (
        (
            PROTOCOL_PATH,
            PROTOCOL_SHA256,
        ),
        (
            PHASE7A_CLARIFICATION_PATH,
            PHASE7A_CLARIFICATION_SHA256,
        ),
        (
            FROZEN_GEOMETRY_PATH,
            FROZEN_GEOMETRY_SHA256,
        ),
    )

    for path, expected in checks:
        actual = _sha256(
            path
        )

        if actual != expected:
            raise ValueError(
                "Frozen input hash mismatch: "
                f"{path}: {actual} != {expected}"
            )


def _xy(
    point: Any,
) -> Point:
    """Normalize repository point representations to a tiny local type."""

    if hasattr(
        point,
        "x",
    ) and hasattr(
        point,
        "y",
    ):
        return Point(
            float(
                point.x
            ),
            float(
                point.y
            ),
        )

    if isinstance(
        point,
        dict,
    ):
        return Point(
            float(
                point[
                    "x"
                ]
            ),
            float(
                point[
                    "y"
                ]
            ),
        )

    if isinstance(
        point,
        (
            tuple,
            list,
        ),
    ) and len(
        point
    ) == 2:
        return Point(
            float(
                point[
                    0
                ]
            ),
            float(
                point[
                    1
                ]
            ),
        )

    raise TypeError(
        "Unsupported wall-vertex representation: "
        f"{type(point)!r}"
    )


def side_class(
    side_index: int,
) -> str:
    if side_index in POLAR_SIDE_INDICES:
        return "polar"

    return "oblique"


def incident_side_indices(
    vertex_index: int,
) -> tuple[int, int]:
    """Return the two sides incident on one frozen wall vertex.

    In the frozen OuterWall ordering, line/side i runs from vertex i-1 to
    vertex i.  Therefore vertex i is incident on sides i and i+1.
    """

    return (
        vertex_index,
        (
            vertex_index
            + 1
        )
        % VERTEX_COUNT,
    )


def classify_vertex(
    vertex_index: int,
) -> str:
    sides = incident_side_indices(
        vertex_index
    )

    if any(
        side_index
        in POLAR_SIDE_INDICES
        for side_index in sides
    ):
        return POLAR_ADJACENT_VERTEX

    return OBLIQUE_PAIR_VERTEX


def regular_circumradius() -> float:
    return (
        REGULAR_APOTHEM
        / cos(
            pi
            / 12.0
        )
    )


def regular_vertex(
    vertex_index: int,
) -> Point:
    """Regular baseline vertex matching the frozen wall cyclic ordering."""

    angle = (
        pi
        / 12.0
        + vertex_index
        * pi
        / 6.0
    )

    radius = regular_circumradius()

    return Point(
        radius
        * cos(
            angle
        ),
        radius
        * sin(
            angle
        ),
    )


def _angle(
    point: Point,
) -> float:
    # atan2 imported locally so the public import boundary remains obvious.
    from math import atan2

    value = atan2(
        point.y,
        point.x,
    )

    if value < 0.0:
        value += (
            2.0
            * pi
        )

    return value


def _class_summary(
    rows: Iterable[AuditedVertex],
) -> dict[str, Any]:
    rows = tuple(
        rows
    )

    radii = tuple(
        row.radius
        for row in rows
    )

    if not radii:
        raise ValueError(
            "Cannot summarize empty vertex class."
        )

    minimum = min(
        radii
    )

    maximum = max(
        radii
    )

    mean = sum(
        radii
    ) / len(
        radii
    )

    spread = (
        maximum
        - minimum
    )

    return {
        "vertex_count": len(
            rows
        ),
        "vertex_ids": [
            row.vertex_id
            for row in rows
        ],
        "radii_normalized": [
            row.radius
            for row in rows
        ],
        "minimum_radius_normalized": minimum,
        "maximum_radius_normalized": maximum,
        "mean_radius_normalized": mean,
        "within_class_spread_normalized": spread,
        "numerically_degenerate": (
            spread
            <= ABS_TOL
        ),
    }


def build_vertex_radius_audit(
    *,
    verify_hashes: bool = True,
) -> dict[str, Any]:
    if verify_hashes:
        verify_frozen_inputs()

    composite = build_michell_composite(
        unit=1.0
    )

    wall = (
        composite
        .wall_reconstruction
    )

    vertices = tuple(
        _xy(
            point
        )
        for point in wall.vertices
    )

    if len(
        vertices
    ) != VERTEX_COUNT:
        raise ValueError(
            "Frozen wall topology mismatch: "
            f"expected {VERTEX_COUNT} vertices, "
            f"found {len(vertices)}"
        )

    baseline_radius = (
        regular_circumradius()
    )

    audited: list[
        AuditedVertex
    ] = []

    for index, point in enumerate(
        vertices
    ):
        sides = (
            incident_side_indices(
                index
            )
        )

        classes = tuple(
            side_class(
                side
            )
            for side in sides
        )

        regular = regular_vertex(
            index
        )

        radius = hypot(
            point.x,
            point.y,
        )

        audited.append(
            AuditedVertex(
                index=index,
                vertex_id=(
                    f"wall_vertex_{index:02d}"
                ),
                point=point,
                incident_side_indices=sides,
                incident_side_classes=classes,
                vertex_class=(
                    classify_vertex(
                        index
                    )
                ),
                radius=radius,
                angle_radians=_angle(
                    point
                ),
                regular_point=regular,
                regular_radius=baseline_radius,
                radial_difference_from_regular=(
                    radius
                    - baseline_radius
                ),
            )
        )

    class_counts = {
        label: sum(
            row.vertex_class
            == label
            for row in audited
        )
        for label in EXPECTED_CLASS_COUNTS
    }

    if (
        class_counts
        != EXPECTED_CLASS_COUNTS
    ):
        raise ValueError(
            "Frozen wall semantic-class count mismatch: "
            f"{class_counts}"
        )

    class_summaries = {
        label: _class_summary(
            row
            for row in audited
            if row.vertex_class
            == label
        )
        for label in EXPECTED_CLASS_COUNTS
    }

    polar_mean = (
        class_summaries[
            POLAR_ADJACENT_VERTEX
        ][
            "mean_radius_normalized"
        ]
    )

    oblique_mean = (
        class_summaries[
            OBLIQUE_PAIR_VERTEX
        ][
            "mean_radius_normalized"
        ]
    )

    regular_differences = [
        row.radial_difference_from_regular
        for row in audited
    ]

    polar_matches_regular = all(
        abs(
            row.radial_difference_from_regular
        )
        <= ABS_TOL
        for row in audited
        if row.vertex_class
        == POLAR_ADJACENT_VERTEX
    )

    oblique_all_inward = all(
        row.radial_difference_from_regular
        < -ABS_TOL
        for row in audited
        if row.vertex_class
        == OBLIQUE_PAIR_VERTEX
    )

    if (
        class_summaries[
            POLAR_ADJACENT_VERTEX
        ][
            "numerically_degenerate"
        ]
        and class_summaries[
            OBLIQUE_PAIR_VERTEX
        ][
            "numerically_degenerate"
        ]
    ):
        stopping_status = (
            "TWO_SEMANTIC_RADIUS_CLASSES_CONFIRMED"
        )
    else:
        stopping_status = (
            "SEMANTIC_CLASSES_NOT_RADIUS_DEGENERATE"
        )

    document = {
        "schema_version": SCHEMA_VERSION,
        "phase": "7B",
        "audit_name": (
            "frozen_dodecagon_vertex_radius_audit"
        ),
        "protocol": {
            "path": PROTOCOL_PATH,
            "sha256": PROTOCOL_SHA256,
        },
        "phase7a_source_clarification": {
            "path": (
                PHASE7A_CLARIFICATION_PATH
            ),
            "sha256": (
                PHASE7A_CLARIFICATION_SHA256
            ),
        },
        "frozen_geometry_input": {
            "path": FROZEN_GEOMETRY_PATH,
            "sha256": (
                FROZEN_GEOMETRY_SHA256
            ),
            "wall_model": WALL_MODEL,
            "geometry_rebuilt_from_frozen_code": True,
            "geometry_modified": False,
        },
        "numerical_tolerance": {
            "absolute_normalized": ABS_TOL,
            "relative": REL_TOL,
            "purpose": (
                "floating-point geometric identity only"
            ),
        },
        "wall_topology": {
            "side_count": (
                len(
                    wall.side_lengths
                )
            ),
            "vertex_count": len(
                vertices
            ),
            "polar_side_indices": sorted(
                POLAR_SIDE_INDICES
            ),
            "oblique_side_indices": [
                index
                for index in range(
                    VERTEX_COUNT
                )
                if index
                not in POLAR_SIDE_INDICES
            ],
        },
        "semantic_vertex_classes": {
            "classification_rule": (
                "vertex i is incident on sides i and i+1; "
                "at least one polar side => "
                "POLAR_ADJACENT_VERTEX, otherwise "
                "OBLIQUE_PAIR_VERTEX"
            ),
            "expected_counts": (
                EXPECTED_CLASS_COUNTS
            ),
            "observed_counts": (
                class_counts
            ),
        },
        "regular_dodecagon_baseline": {
            "centre": [
                0.0,
                0.0,
            ],
            "side_count": (
                VERTEX_COUNT
            ),
            "apothem_normalized": (
                REGULAR_APOTHEM
            ),
            "side_normal_step_degrees": (
                30.0
            ),
            "first_vertex_angle_degrees": (
                15.0
            ),
            "circumradius_normalized": (
                baseline_radius
            ),
            "free_parameters": 0,
        },
        "vertices": [
            {
                "index": row.index,
                "vertex_id": (
                    row.vertex_id
                ),
                "x_normalized": (
                    row.point.x
                ),
                "y_normalized": (
                    row.point.y
                ),
                "incident_side_indices": list(
                    row.incident_side_indices
                ),
                "incident_side_classes": list(
                    row.incident_side_classes
                ),
                "vertex_class": (
                    row.vertex_class
                ),
                "radius_normalized": (
                    row.radius
                ),
                "angle_radians": (
                    row.angle_radians
                ),
                "regular_x_normalized": (
                    row.regular_point.x
                ),
                "regular_y_normalized": (
                    row.regular_point.y
                ),
                "regular_radius_normalized": (
                    row.regular_radius
                ),
                "radial_difference_from_regular_normalized": (
                    row.radial_difference_from_regular
                ),
            }
            for row in audited
        ],
        "class_summaries": (
            class_summaries
        ),
        "normalized_comparison": {
            "regular_baseline_radius": (
                baseline_radius
            ),
            "polar_adjacent_mean_radius": (
                polar_mean
            ),
            "oblique_pair_mean_radius": (
                oblique_mean
            ),
            "polar_adjacent_minus_regular": (
                polar_mean
                - baseline_radius
            ),
            "oblique_pair_minus_regular": (
                oblique_mean
                - baseline_radius
            ),
            "polar_adjacent_to_oblique_pair_ratio": (
                polar_mean
                / oblique_mean
            ),
            "maximum_absolute_radial_displacement_from_regular": max(
                abs(
                    value
                )
                for value in regular_differences
            ),
            "polar_adjacent_matches_regular": (
                polar_matches_regular
            ),
            "oblique_pair_vertices_all_inward": (
                oblique_all_inward
            ),
        },
        "determinacy": {
            "new_continuous_parameters_introduced": 0,
            "new_fitted_scale_parameters_introduced": 0,
            "new_discrete_candidate_choices_introduced": 0,
            "historical_dimensional_targets_loaded": False,
            "historical_comparison_metrics_calculated": False,
        },
        "interpretation": {
            "independent_forward_prediction": False,
            "historical_dimensional_comparison_phase": (
                "downstream"
            ),
            "source_term_correction": (
                "decagon -> dodecagon vertex radii"
            ),
        },
        "stopping_status": (
            stopping_status
        ),
    }

    return document


def canonical_json_bytes(
    document: dict[str, Any],
) -> bytes:
    return (
        json.dumps(
            document,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode(
        "utf-8"
    )


def write_vertex_radius_audit(
    path: str | Path,
) -> Path:
    path = Path(
        path
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    document = (
        build_vertex_radius_audit()
    )

    path.write_bytes(
        canonical_json_bytes(
            document
        )
    )

    return path
