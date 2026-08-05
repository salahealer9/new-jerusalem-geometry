from __future__ import annotations

import pytest

from new_jerusalem_geometry.core_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.model_variants import (
    ObliqueModel,
)
from new_jerusalem_geometry.moon_geometry import (
    CARDINAL_DIRECTIONS,
    build_michell_moon_groups,
)
from new_jerusalem_geometry.wall_geometry import (
    build_ordered_moon_circles,
)


EXPECTED_GROUPS = {
    "east": (
        "moon-q4-b",
        "moon-east",
        "moon-q1-a",
    ),
    "north": (
        "moon-q1-b",
        "moon-north",
        "moon-q2-a",
    ),
    "west": (
        "moon-q2-b",
        "moon-west",
        "moon-q3-a",
    ),
    "south": (
        "moon-q3-b",
        "moon-south",
        "moon-q4-a",
    ),
}


def test_michell_has_four_groups_of_three() -> None:
    diagram = build_core_geometry()

    groups = build_michell_moon_groups(
        diagram
    )

    assert len(groups) == 4

    assert tuple(
        group.direction
        for group in groups
    ) == CARDINAL_DIRECTIONS

    assert all(
        len(group.members) == 3
        for group in groups
    )


def test_michell_group_members_match_cardinal_sides() -> None:
    diagram = build_core_geometry()

    groups = build_michell_moon_groups(
        diagram
    )

    actual = {
        group.direction: group.member_names
        for group in groups
    }

    assert actual == EXPECTED_GROUPS


def test_each_group_has_one_cardinal_and_two_oblique_moons() -> None:
    diagram = build_core_geometry()

    groups = build_michell_moon_groups(
        diagram
    )

    for group in groups:
        assert (
            group.cardinal[0]
            == f"moon-{group.direction}"
        )

        assert group.clockwise_outer[0].startswith(
            "moon-q"
        )

        assert (
            group.counterclockwise_outer[0]
            .startswith("moon-q")
        )


def test_groups_partition_existing_ordered_twelve_moons() -> None:
    diagram = build_core_geometry()

    groups = build_michell_moon_groups(
        diagram
    )

    grouped_names = {
        name
        for group in groups
        for name, _ in group.members
    }

    ordered_names = {
        name
        for name, _ in build_ordered_moon_circles(
            diagram
        )
    }

    assert len(grouped_names) == 12
    assert grouped_names == ordered_names


@pytest.mark.parametrize(
    "model",
    tuple(ObliqueModel),
)
def test_four_by_three_grouping_is_model_stable(
    model: ObliqueModel,
) -> None:
    diagram = build_core_geometry()

    groups = build_michell_moon_groups(
        diagram,
        model,
    )

    assert {
        group.direction: group.member_names
        for group in groups
    } == EXPECTED_GROUPS
