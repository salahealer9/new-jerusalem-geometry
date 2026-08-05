"""Source-described grouping of Michell's twelve Moon circles.

Michell's Figure 12 arranges the twelve Moon circles in four groups
of three, one group at each cardinal side.

This module represents that grouping independently of any outer-wall
construction.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, pi
from typing import TypeAlias

from .core_geometry import CoreDiagram
from .model_variants import ObliqueModel
from .oblique_geometry import build_oblique_placement
from .primitives import Circle


NamedCircle: TypeAlias = tuple[str, Circle]

CARDINAL_DIRECTIONS = (
    "east",
    "north",
    "west",
    "south",
)


@dataclass(frozen=True, slots=True)
class MichellMoonGroup:
    """One source-described cardinal group of three Moon circles.

    Members are stored in cyclic order around the construction circle:

    clockwise outer Moon,
    cardinal Moon,
    counter-clockwise outer Moon.
    """

    direction: str
    clockwise_outer: NamedCircle
    cardinal: NamedCircle
    counterclockwise_outer: NamedCircle

    @property
    def members(self) -> tuple[NamedCircle, ...]:
        return (
            self.clockwise_outer,
            self.cardinal,
            self.counterclockwise_outer,
        )

    @property
    def member_names(self) -> tuple[str, ...]:
        return tuple(
            name
            for name, _ in self.members
        )


def _positive_angle(circle: Circle) -> float:
    """Return the centre angle in the half-open interval [0, 2*pi)."""

    angle = atan2(
        circle.centre.y,
        circle.centre.x,
    )

    return (
        angle
        if angle >= 0.0
        else angle + 2.0 * pi
    )


def build_michell_moon_groups(
    diagram: CoreDiagram,
    model: ObliqueModel = ObliqueModel.INCIDENCE,
) -> tuple[MichellMoonGroup, ...]:
    """Return Michell's four cardinal groups of three Moon circles.

    The grouping is determined from the cyclic order of the complete
    twelve-Moon system. Each cardinal Moon is grouped with its immediate
    clockwise and counter-clockwise oblique neighbours.

    This represents Michell's source-stated four-by-three organization.
    It does not depend on an outer-wall construction.
    """

    if not isinstance(model, ObliqueModel):
        model = ObliqueModel(model)

    placement = build_oblique_placement(
        diagram,
        model,
    )

    moons: list[NamedCircle] = [
        (
            f"moon-{direction}",
            circle,
        )
        for direction, circle
        in diagram.cardinal_moons
    ]

    moons.extend(
        (
            moon.name,
            moon.circle,
        )
        for moon in placement.moons
    )

    moons.sort(
        key=lambda item: _positive_angle(
            item[1]
        )
    )

    if len(moons) != 12:
        raise ValueError(
            "Michell Moon grouping requires "
            f"twelve circles; received {len(moons)}."
        )

    cardinal_names = {
        f"moon-{direction}"
        for direction in CARDINAL_DIRECTIONS
    }

    groups: list[MichellMoonGroup] = []

    for direction in CARDINAL_DIRECTIONS:
        cardinal_name = (
            f"moon-{direction}"
        )

        cardinal_index = next(
            (
                index
                for index, (name, _)
                in enumerate(moons)
                if name == cardinal_name
            ),
            None,
        )

        if cardinal_index is None:
            raise ValueError(
                f"Missing cardinal Moon {cardinal_name!r}."
            )

        clockwise_outer = moons[
            (cardinal_index - 1) % len(moons)
        ]

        cardinal = moons[
            cardinal_index
        ]

        counterclockwise_outer = moons[
            (cardinal_index + 1) % len(moons)
        ]

        if (
            clockwise_outer[0]
            in cardinal_names
            or counterclockwise_outer[0]
            in cardinal_names
        ):
            raise ValueError(
                "Each Michell Moon group must contain "
                "one cardinal Moon and two oblique Moons."
            )

        groups.append(
            MichellMoonGroup(
                direction=direction,
                clockwise_outer=clockwise_outer,
                cardinal=cardinal,
                counterclockwise_outer=(
                    counterclockwise_outer
                ),
            )
        )

    grouped_names = [
        name
        for group in groups
        for name, _ in group.members
    ]

    if (
        len(grouped_names) != 12
        or len(set(grouped_names)) != 12
    ):
        raise ValueError(
            "The four Moon groups must partition "
            "the twelve circles exactly once."
        )

    all_names = {
        name
        for name, _ in moons
    }

    if set(grouped_names) != all_names:
        raise ValueError(
            "Moon groups do not cover the complete "
            "twelve-Moon system."
        )

    return tuple(groups)
