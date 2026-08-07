from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from math import isclose
from pathlib import Path
import xml.etree.ElementTree as ET

from new_jerusalem_geometry import (
    build_michell_composite,
    build_michell_composite_geometry_export,
    build_michell_composite_provenance,
    michell_composite_geometry_to_json,
    michell_composite_provenance_to_json,
    michell_composite_to_svg,
)


ROOT = Path(__file__).resolve().parents[1]

NODES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_nodes.csv"
)

DEPENDENCIES_PATH = (
    ROOT
    / "docs"
    / "specification"
    / "construction_dependencies.csv"
)

CLAIMS_PATH = (
    ROOT
    / "docs"
    / "sources"
    / "geometric_claim_matrix.csv"
)


REGISTERED_SCALES = (
    0.25,
    0.73,
    1.0,
    2.75,
    8.0,
)

RTOL = 1.0e-12
ATOL = 1.0e-12


def _assert_close(
    actual: float,
    expected: float,
) -> None:
    assert isclose(
        actual,
        expected,
        rel_tol=RTOL,
        abs_tol=ATOL,
    ), (
        f"{actual!r} != {expected!r}"
    )


def _assert_scaled_point(
    actual: object,
    reference: object,
    scale: float,
) -> None:
    _assert_close(
        actual.x,
        reference.x * scale,
    )

    _assert_close(
        actual.y,
        reference.y * scale,
    )


def _assert_scaled_xy_dict(
    actual: dict[str, float],
    reference: dict[str, float],
    scale: float,
) -> None:
    _assert_close(
        actual["x"],
        reference["x"] * scale,
    )

    _assert_close(
        actual["y"],
        reference["y"] * scale,
    )


@lru_cache(maxsize=None)
def _bundle(
    scale: float,
):
    composite = build_michell_composite(
        unit=scale
    )

    geometry = (
        build_michell_composite_geometry_export(
            composite
        )
    )

    provenance = (
        build_michell_composite_provenance(
            composite,
            construction_nodes_path=(
                NODES_PATH
            ),
            construction_dependencies_path=(
                DEPENDENCIES_PATH
            ),
            claim_matrix_path=(
                CLAIMS_PATH
            ),
        )
    )

    svg = michell_composite_to_svg(
        composite
    )

    return (
        composite,
        geometry,
        provenance,
        svg,
    )


def _geometry_objects(
    scale: float,
):
    return {
        record.object_id: record
        for record in _bundle(
            scale
        )[1].objects
    }


def _identity(
    records,
) -> tuple[
    tuple[str, str],
    ...,
]:
    return tuple(
        (
            record.object_id,
            record.geometry_type,
        )
        for record in records
    )


def _moon_group_signature(
    composite,
):
    return tuple(
        (
            group.direction,
            group.clockwise_outer[0],
            group.cardinal[0],
            group.counterclockwise_outer[0],
        )
        for group
        in composite.moon_groups
    )


def _svg_summary(
    svg: str,
) -> dict[str, object]:
    root = ET.fromstring(
        svg
    )

    elements = list(
        root.iter()
    )

    provenance_ids = tuple(
        sorted(
            element.get(
                "data-provenance-id"
            )
            for element in elements
            if element.get(
                "data-provenance-id"
            )
            is not None
        )
    )

    moon_count = sum(
        "moon-circle"
        in (
            element.get(
                "class",
                "",
            ).split()
        )
        for element in elements
    )

    scaffold_count = sum(
        element.get(
            "data-scaffold-index"
        )
        is not None
        for element in elements
    )

    vertex_count = sum(
        "heptagram-vertex"
        in (
            element.get(
                "class",
                "",
            ).split()
        )
        for element in elements
    )

    edge_count = sum(
        "heptagram-edge"
        in (
            element.get(
                "class",
                "",
            ).split()
        )
        for element in elements
    )

    return {
        "provenance_ids": (
            provenance_ids
        ),
        "provenance_link_count": (
            len(provenance_ids)
        ),
        "moon_count": moon_count,
        "scaffold_count": (
            scaffold_count
        ),
        "vertex_count": (
            vertex_count
        ),
        "edge_count": edge_count,
    }


def test_registered_scale_set_is_fixed_positive_and_spans_32x() -> None:
    assert REGISTERED_SCALES == (
        0.25,
        0.73,
        1.0,
        2.75,
        8.0,
    )

    assert all(
        scale > 0.0
        for scale in REGISTERED_SCALES
    )

    assert (
        max(REGISTERED_SCALES)
        / min(REGISTERED_SCALES)
        == 32.0
    )


def test_complete_downstream_path_succeeds_at_every_registered_scale() -> None:
    for scale in REGISTERED_SCALES:
        (
            composite,
            geometry,
            provenance,
            svg,
        ) = _bundle(scale)

        assert (
            composite.unit
            == scale
        )

        assert (
            geometry.unit
            == scale
        )

        assert (
            provenance.unit
            == scale
        )

        assert (
            geometry.object_count
            == 132
        )

        assert (
            provenance.object_count
            == 132
        )

        assert svg.startswith(
            "<svg"
        ) or "<svg" in svg[:500]


def test_core_quantities_obey_linear_scale_law() -> None:
    reference = _bundle(
        1.0
    )[0].core

    for scale in REGISTERED_SCALES:
        core = _bundle(
            scale
        )[0].core

        _assert_scaled_point(
            core.earth_circle.centre,
            reference.earth_circle.centre,
            scale,
        )

        _assert_close(
            core.earth_circle.radius,
            reference
            .earth_circle
            .radius
            * scale,
        )

        _assert_scaled_point(
            core.earth_square.centre,
            reference.earth_square.centre,
            scale,
        )

        _assert_close(
            core.earth_square.side,
            reference
            .earth_square
            .side
            * scale,
        )

        _assert_close(
            core.construction_circle.radius,
            reference
            .construction_circle
            .radius
            * scale,
        )


def test_moon_geometry_obeys_linear_scale_law() -> None:
    reference = dict(
        _bundle(
            1.0
        )[0]
        .wall_reconstruction
        .moons
    )

    for scale in REGISTERED_SCALES:
        moons = dict(
            _bundle(
                scale
            )[0]
            .wall_reconstruction
            .moons
        )

        assert (
            tuple(moons)
            == tuple(reference)
        )

        for name in reference:
            _assert_scaled_point(
                moons[name].centre,
                reference[name].centre,
                scale,
            )

            _assert_close(
                moons[name].radius,
                reference[name].radius
                * scale,
            )


def test_wall_support_geometry_obeys_scale_laws() -> None:
    reference = (
        _bundle(
            1.0
        )[0]
        .wall_reconstruction
    )

    for scale in REGISTERED_SCALES:
        wall = (
            _bundle(
                scale
            )[0]
            .wall_reconstruction
        )

        assert len(
            wall.lines
        ) == 12

        for actual, expected in zip(
            wall.lines,
            reference.lines,
            strict=True,
        ):
            assert (
                actual.name
                == expected.name
            )

            assert (
                actual.moon_name
                == expected.moon_name
            )

            _assert_close(
                actual.normal.x,
                expected.normal.x,
            )

            _assert_close(
                actual.normal.y,
                expected.normal.y,
            )

            _assert_close(
                actual.offset,
                expected.offset
                * scale,
            )

            _assert_scaled_point(
                actual.tangency_point,
                expected.tangency_point,
                scale,
            )

        for actual, expected in zip(
            wall.vertices,
            reference.vertices,
            strict=True,
        ):
            _assert_scaled_point(
                actual,
                expected,
                scale,
            )

        for actual, expected in zip(
            wall.side_lengths,
            reference.side_lengths,
            strict=True,
        ):
            _assert_close(
                actual,
                expected * scale,
            )

        _assert_close(
            wall.perimeter,
            reference.perimeter
            * scale,
        )

        _assert_close(
            wall.mean_side_length,
            reference.mean_side_length
            * scale,
        )


def test_wall_area_obeys_quadratic_scale_law() -> None:
    reference_area = (
        _bundle(
            1.0
        )[0]
        .wall_reconstruction
        .area
    )

    for scale in REGISTERED_SCALES:
        area = (
            _bundle(
                scale
            )[0]
            .wall_reconstruction
            .area
        )

        _assert_close(
            area,
            reference_area
            * scale
            * scale,
        )


def test_sevenfold_coordinates_scale_and_angles_are_invariant() -> None:
    reference = _bundle(
        1.0
    )[0].sevenfold

    for scale in REGISTERED_SCALES:
        sevenfold = _bundle(
            scale
        )[0].sevenfold

        assert (
            sevenfold.base_side
            == reference.base_side
        )

        _assert_close(
            sevenfold.radius,
            reference.radius
            * scale,
        )

        _assert_close(
            sevenfold.step_radians,
            reference.step_radians,
        )

        for actual, expected in zip(
            sevenfold.angles_radians,
            reference.angles_radians,
            strict=True,
        ):
            _assert_close(
                actual,
                expected,
            )

        for actual, expected in zip(
            sevenfold.points,
            reference.points,
            strict=True,
        ):
            _assert_scaled_point(
                actual,
                expected,
                scale,
            )


def test_fourteenfold_coordinates_scale_and_angles_are_invariant() -> None:
    reference = _bundle(
        1.0
    )[0].fourteenfold

    for scale in REGISTERED_SCALES:
        fourteenfold = _bundle(
            scale
        )[0].fourteenfold

        assert (
            fourteenfold
            .primary
            .base_side
            == reference
            .primary
            .base_side
        )

        assert (
            fourteenfold
            .reciprocal
            .base_side
            == reference
            .reciprocal
            .base_side
        )

        for actual, expected in zip(
            fourteenfold
            .angles_radians,
            reference
            .angles_radians,
            strict=True,
        ):
            _assert_close(
                actual,
                expected,
            )

        for actual, expected in zip(
            fourteenfold
            .angular_gaps_radians,
            reference
            .angular_gaps_radians,
            strict=True,
        ):
            _assert_close(
                actual,
                expected,
            )

        for actual, expected in zip(
            fourteenfold.points,
            reference.points,
            strict=True,
        ):
            _assert_scaled_point(
                actual,
                expected,
                scale,
            )


def test_four_triangle_angles_and_closure_mismatch_are_invariant() -> None:
    reference = _bundle(
        1.0
    )[0]

    for scale in REGISTERED_SCALES:
        composite = _bundle(
            scale
        )[0]

        assert len(
            composite
            .four_triangle_angles_radians
        ) == 28

        for actual, expected in zip(
            composite
            .four_triangle_angles_radians,
            reference
            .four_triangle_angles_radians,
            strict=True,
        ):
            _assert_close(
                actual,
                expected,
            )

        _assert_close(
            composite
            .four_triangle_scaffold_max_mismatch_radians,
            reference
            .four_triangle_scaffold_max_mismatch_radians,
        )


def test_scaffold_geometry_scales_and_semantics_are_invariant() -> None:
    reference = _bundle(
        1.0
    )[0].scaffold

    for scale in REGISTERED_SCALES:
        scaffold = _bundle(
            scale
        )[0].scaffold

        _assert_close(
            scaffold.radius,
            reference.radius
            * scale,
        )

        _assert_close(
            scaffold.beta_radians,
            reference.beta_radians,
        )

        _assert_close(
            scaffold.heptagon_step_radians,
            reference
            .heptagon_step_radians,
        )

        assert len(
            scaffold.points
        ) == 28

        for actual, expected in zip(
            scaffold.points,
            reference.points,
            strict=True,
        ):
            assert (
                actual.index
                == expected.index
            )

            assert (
                actual.quadrant
                == expected.quadrant
            )

            assert (
                actual.local_index
                == expected.local_index
            )

            assert (
                actual.role
                == expected.role
            )

            _assert_close(
                actual.angle_radians,
                expected.angle_radians,
            )

            _assert_scaled_point(
                actual.point,
                expected.point,
                scale,
            )


def test_moon_grouping_is_exactly_scale_invariant() -> None:
    reference = (
        _moon_group_signature(
            _bundle(
                1.0
            )[0]
        )
    )

    assert len(reference) == 4

    for scale in REGISTERED_SCALES:
        signature = (
            _moon_group_signature(
                _bundle(
                    scale
                )[0]
            )
        )

        assert (
            signature
            == reference
        )


def test_wall_semantic_correspondence_is_exactly_scale_invariant() -> None:
    reference = tuple(
        (
            line.name,
            line.moon_name,
        )
        for line in (
            _bundle(
                1.0
            )[0]
            .wall_reconstruction
            .lines
        )
    )

    for scale in REGISTERED_SCALES:
        observed = tuple(
            (
                line.name,
                line.moon_name,
            )
            for line in (
                _bundle(
                    scale
                )[0]
                .wall_reconstruction
                .lines
            )
        )

        assert (
            observed
            == reference
        )


def test_heptagram_phase_topology_and_metric_scaling() -> None:
    reference_composite = (
        _bundle(
            1.0
        )[0]
    )

    reference_star = (
        reference_composite
        .scaffold_heptagram_candidate
    )

    expected_scaffold_indices = (
        7,
        11,
        15,
        19,
        23,
        27,
        3,
    )

    expected_pairs = (
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 1),
        (1, 3),
        (3, 5),
        (5, 0),
    )

    reference_lengths = (
        reference_star.edge_lengths()
    )

    for scale in REGISTERED_SCALES:
        composite = _bundle(
            scale
        )[0]

        star = (
            composite
            .scaffold_heptagram_candidate
        )

        scaffold_indices = []

        for vertex in star.vertices:
            matches = [
                point.index
                for point
                in composite
                .scaffold
                .points
                if point.point == vertex
            ]

            assert len(matches) == 1

            scaffold_indices.append(
                matches[0]
            )

        assert tuple(
            scaffold_indices
        ) == expected_scaffold_indices

        assert (
            star.family
            == reference_star.family
        )

        assert (
            star.traversal_indices()
            == reference_star
            .traversal_indices()
        )

        assert (
            star.edge_index_pairs()
            == expected_pairs
        )

        for actual, expected in zip(
            star.vertices,
            reference_star.vertices,
            strict=True,
        ):
            _assert_scaled_point(
                actual,
                expected,
                scale,
            )

        for actual, expected in zip(
            star.edge_lengths(),
            reference_lengths,
            strict=True,
        ):
            _assert_close(
                actual,
                expected * scale,
            )


def test_geometry_and_provenance_object_identity_is_scale_invariant() -> None:
    (
        _,
        reference_geometry,
        reference_provenance,
        _,
    ) = _bundle(
        1.0
    )

    reference_identity = (
        _identity(
            reference_geometry.objects
        )
    )

    assert (
        reference_identity
        == _identity(
            reference_provenance.objects
        )
    )

    assert len(
        reference_identity
    ) == 132

    for scale in REGISTERED_SCALES:
        (
            _,
            geometry,
            provenance,
            _,
        ) = _bundle(scale)

        assert (
            _identity(
                geometry.objects
            )
            == reference_identity
        )

        assert (
            _identity(
                provenance.objects
            )
            == reference_identity
        )


def test_provenance_is_scale_invariant_except_for_explicit_unit() -> None:
    reference = deepcopy(
        _bundle(
            1.0
        )[2].to_dict()
    )

    assert (
        reference.pop("unit")
        == 1.0
    )

    for scale in REGISTERED_SCALES:
        candidate = deepcopy(
            _bundle(
                scale
            )[2].to_dict()
        )

        assert (
            candidate.pop("unit")
            == scale
        )

        assert (
            candidate
            == reference
        )


def test_svg_structure_and_provenance_ids_are_scale_invariant() -> None:
    reference = _svg_summary(
        _bundle(
            1.0
        )[3]
    )

    assert (
        reference[
            "moon_count"
        ]
        == 12
    )

    assert (
        reference[
            "scaffold_count"
        ]
        == 28
    )

    assert (
        reference[
            "vertex_count"
        ]
        == 7
    )

    assert (
        reference[
            "edge_count"
        ]
        == 7
    )

    assert (
        reference[
            "provenance_link_count"
        ]
        == 59
    )

    for scale in REGISTERED_SCALES:
        observed = _svg_summary(
            _bundle(
                scale
            )[3]
        )

        assert (
            observed
            == reference
        )


def test_three_way_geometry_provenance_svg_join_holds_at_every_scale() -> None:
    for scale in REGISTERED_SCALES:
        (
            _,
            geometry,
            provenance,
            svg,
        ) = _bundle(scale)

        geometry_ids = {
            record.object_id
            for record
            in geometry.objects
        }

        provenance_ids = {
            record.object_id
            for record
            in provenance.objects
        }

        assert (
            geometry_ids
            == provenance_ids
        )

        assert len(
            geometry_ids
        ) == 132

        svg_ids = set(
            _svg_summary(
                svg
            )[
                "provenance_ids"
            ]
        )

        assert len(
            svg_ids
        ) == 59

        assert (
            svg_ids
            <= geometry_ids
        )

        assert (
            svg_ids
            <= provenance_ids
        )

        rendered_manifest_ids = {
            record.object_id
            for record
            in provenance.objects
            if (
                record.rendered_svg_id
                is not None
            )
        }

        assert (
            svg_ids
            == rendered_manifest_ids
        )


def test_geometry_export_scale_laws_cover_all_numeric_families() -> None:
    reference = _geometry_objects(
        1.0
    )

    for scale in REGISTERED_SCALES:
        objects = _geometry_objects(
            scale
        )

        root = dict(
            objects[
                "njg-michell-composite"
            ].geometry
        )

        assert (
            root["unit"]
            == scale
        )

        for key in (
            "moon_count",
            "wall_side_count",
            "scaffold_point_count",
            "heptagram_vertex_count",
        ):
            assert (
                root[key]
                == dict(
                    reference[
                        "njg-michell-composite"
                    ].geometry
                )[key]
            )

        circle_ids = (
            "earth-circle",
            "construction-circle",
            "moon-east",
            "moon-q1-a",
            "moon-q1-b",
            "moon-north",
            "moon-q2-a",
            "moon-q2-b",
            "moon-west",
            "moon-q3-a",
            "moon-q3-b",
            "moon-south",
            "moon-q4-a",
            "moon-q4-b",
        )

        for object_id in circle_ids:
            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            _assert_scaled_xy_dict(
                actual["centre"],
                expected["centre"],
                scale,
            )

            _assert_close(
                actual["radius"],
                expected["radius"]
                * scale,
            )

        square = dict(
            objects[
                "earth-square"
            ].geometry
        )

        reference_square = dict(
            reference[
                "earth-square"
            ].geometry
        )

        _assert_scaled_xy_dict(
            square["centre"],
            reference_square[
                "centre"
            ],
            scale,
        )

        for key in (
            "side",
            "half_side",
            "perimeter",
        ):
            _assert_close(
                square[key],
                reference_square[key]
                * scale,
            )

        wall_polygon = dict(
            objects[
                "polar-pivot-wall"
            ].geometry
        )

        reference_wall = dict(
            reference[
                "polar-pivot-wall"
            ].geometry
        )

        for actual, expected in zip(
            wall_polygon[
                "side_lengths"
            ],
            reference_wall[
                "side_lengths"
            ],
            strict=True,
        ):
            _assert_close(
                actual,
                expected * scale,
            )

        for key in (
            "perimeter",
            "mean_side_length",
        ):
            _assert_close(
                wall_polygon[key],
                reference_wall[key]
                * scale,
            )

        _assert_close(
            wall_polygon["area"],
            reference_wall["area"]
            * scale
            * scale,
        )

        for index in range(12):
            line_id = (
                _bundle(
                    1.0
                )[0]
                .wall_reconstruction
                .lines[index]
                .name
            )

            actual = dict(
                objects[
                    line_id
                ].geometry
            )

            expected = dict(
                reference[
                    line_id
                ].geometry
            )

            _assert_close(
                actual["normal"]["x"],
                expected["normal"]["x"],
            )

            _assert_close(
                actual["normal"]["y"],
                expected["normal"]["y"],
            )

            _assert_close(
                actual["offset"],
                expected["offset"]
                * scale,
            )

            for key in (
                "tangency_point",
                "side_start",
                "side_end",
            ):
                _assert_scaled_xy_dict(
                    actual[key],
                    expected[key],
                    scale,
                )

            _assert_close(
                actual["side_length"],
                expected[
                    "side_length"
                ]
                * scale,
            )

        for index in range(12):
            object_id = (
                f"wall-vertex-"
                f"{index:02d}"
            )

            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            _assert_close(
                actual["x"],
                expected["x"]
                * scale,
            )

            _assert_close(
                actual["y"],
                expected["y"]
                * scale,
            )

        for prefix, count in (
            (
                "sevenfold-point",
                7,
            ),
            (
                "fourteenfold-point",
                14,
            ),
            (
                "scaffold-point",
                28,
            ),
        ):
            for index in range(count):
                object_id = (
                    f"{prefix}-"
                    f"{index:02d}"
                )

                actual = dict(
                    objects[
                        object_id
                    ].geometry
                )

                expected = dict(
                    reference[
                        object_id
                    ].geometry
                )

                _assert_close(
                    actual["x"],
                    expected["x"]
                    * scale,
                )

                _assert_close(
                    actual["y"],
                    expected["y"]
                    * scale,
                )

                _assert_close(
                    actual[
                        "angle_radians"
                    ],
                    expected[
                        "angle_radians"
                    ],
                )

                _assert_close(
                    actual[
                        "angle_degrees"
                    ],
                    expected[
                        "angle_degrees"
                    ],
                )

        for index in range(14):
            object_id = (
                f"fourteenfold-point-"
                f"{index:02d}"
            )

            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            _assert_close(
                actual[
                    "angular_gap_to_next_radians"
                ],
                expected[
                    "angular_gap_to_next_radians"
                ],
            )

            _assert_close(
                actual[
                    "angular_gap_to_next_degrees"
                ],
                expected[
                    "angular_gap_to_next_degrees"
                ],
            )

        for index in range(28):
            object_id = (
                f"four-triangle-mark-"
                f"{index:02d}"
            )

            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            assert set(actual) == {
                "angle_radians",
                "angle_degrees",
            }

            _assert_close(
                actual[
                    "angle_radians"
                ],
                expected[
                    "angle_radians"
                ],
            )

            _assert_close(
                actual[
                    "angle_degrees"
                ],
                expected[
                    "angle_degrees"
                ],
            )

        for index in range(7):
            object_id = (
                f"heptagram-vertex-"
                f"{index:02d}"
            )

            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            _assert_close(
                actual["x"],
                expected["x"]
                * scale,
            )

            _assert_close(
                actual["y"],
                expected["y"]
                * scale,
            )

        for index in range(7):
            object_id = (
                f"heptagram-edge-"
                f"{index:02d}"
            )

            actual = dict(
                objects[
                    object_id
                ].geometry
            )

            expected = dict(
                reference[
                    object_id
                ].geometry
            )

            _assert_scaled_xy_dict(
                actual["start"],
                expected["start"],
                scale,
            )

            _assert_scaled_xy_dict(
                actual["end"],
                expected["end"],
                scale,
            )

            _assert_close(
                actual["length"],
                expected["length"]
                * scale,
            )


def test_geometry_export_contains_no_evidence_vocabulary_at_any_scale() -> None:
    forbidden = (
        '"evidence_status"',
        '"source_status"',
        '"relation_type"',
        '"node_type"',
        '"claim_ids"',
    )

    for scale in REGISTERED_SCALES:
        text = (
            michell_composite_geometry_to_json(
                _bundle(
                    scale
                )[1]
            )
        )

        for token in forbidden:
            assert token not in text


def test_same_input_generation_is_byte_deterministic_at_every_scale() -> None:
    for scale in REGISTERED_SCALES:
        first_composite = (
            build_michell_composite(
                unit=scale
            )
        )

        second_composite = (
            build_michell_composite(
                unit=scale
            )
        )

        first_geometry = (
            build_michell_composite_geometry_export(
                first_composite
            )
        )

        second_geometry = (
            build_michell_composite_geometry_export(
                second_composite
            )
        )

        assert (
            michell_composite_geometry_to_json(
                first_geometry
            )
            == michell_composite_geometry_to_json(
                second_geometry
            )
        )

        first_provenance = (
            build_michell_composite_provenance(
                first_composite,
                construction_nodes_path=(
                    NODES_PATH
                ),
                construction_dependencies_path=(
                    DEPENDENCIES_PATH
                ),
                claim_matrix_path=(
                    CLAIMS_PATH
                ),
            )
        )

        second_provenance = (
            build_michell_composite_provenance(
                second_composite,
                construction_nodes_path=(
                    NODES_PATH
                ),
                construction_dependencies_path=(
                    DEPENDENCIES_PATH
                ),
                claim_matrix_path=(
                    CLAIMS_PATH
                ),
            )
        )

        assert (
            michell_composite_provenance_to_json(
                first_provenance
            )
            == michell_composite_provenance_to_json(
                second_provenance
            )
        )

        assert (
            michell_composite_to_svg(
                first_composite
            )
            == michell_composite_to_svg(
                second_composite
            )
        )
