"""Forward source-traceable composite reconstruction of Michell's geometry.

NJG_MICHELL joins the already audited geometric layers into one deterministic
construction.

The only external geometric input is the scale unit.

No Figure 12 or Figure 14 plate calibration, digitisation, registration, or
source-measurement result is used to generate the composite. Those datasets
remain held-out validation targets.

Evidence boundaries remain explicit:

- the exact-incidence Moon placement is source-supported;
- the four-by-three Moon grouping is source-stated;
- the polar-pivot wall is the project's preferred source-supported
  reconstruction, not a uniquely stated Michell algorithm;
- the 7 -> 14 -> 28 septenary chain follows Michell's approximate Method 1;
- the heptagram selected from the 28-point scaffold remains a project
  candidate for Figure 14 rather than an established historical dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import tau

from .core_geometry import (
    CoreDiagram,
    build_core_geometry,
)
from .heptagram_geometry import (
    HeptagramFamily,
    HeptagramGeometry,
    build_scaffold_heptagram,
)
from .model_variants import ObliqueModel
from .moon_geometry import (
    MichellMoonGroup,
    build_michell_moon_groups,
)
from .polar_pivot_wall import (
    build_polar_pivot_tangent_wall,
)
from .septenary_geometry import (
    MichellFourteenfoldDivision,
    MichellSeptenaryScaffold,
    MichellSevenfoldDivision,
    MichellTriangleBase,
    build_michell_28_point_scaffold,
    build_michell_fourteenfold_division,
    build_michell_sevenfold_division,
    michell_four_triangle_division_angles,
)
from .wall_geometry import OuterWall


COMPOSITE_MODEL_NAME = "NJG_MICHELL"


@dataclass(frozen=True, slots=True)
class MichellComposite:
    """One complete forward NJG_MICHELL construction."""

    core: CoreDiagram
    moon_groups: tuple[MichellMoonGroup, ...]
    wall_reconstruction: OuterWall
    sevenfold: MichellSevenfoldDivision
    fourteenfold: MichellFourteenfoldDivision
    four_triangle_angles_radians: tuple[float, ...]
    scaffold: MichellSeptenaryScaffold
    scaffold_heptagram_candidate: HeptagramGeometry
    four_triangle_scaffold_max_mismatch_radians: float

    @property
    def model_name(self) -> str:
        return COMPOSITE_MODEL_NAME

    @property
    def unit(self) -> float:
        return self.core.dimensions.unit

    @property
    def moon_count(self) -> int:
        return sum(
            len(group.members)
            for group in self.moon_groups
        )


def _normalised_sorted_scaffold_angles(
    scaffold: MichellSeptenaryScaffold,
) -> tuple[float, ...]:
    """Return the scaffold's 28 angles in cyclic numeric order."""

    return tuple(
        sorted(
            point.angle_radians % tau
            for point in scaffold.points
        )
    )


def build_michell_composite(
    unit: float = 1.0,
) -> MichellComposite:
    """Build the complete forward NJG_MICHELL composite.

    The construction is intentionally parameter-minimal. ``unit`` is the
    only caller-supplied geometric quantity.

    The source-faithful Moon branch is fixed to NJG_INC. No source-plate
    calibration quantity is accepted as an argument.
    """

    core = build_core_geometry(
        unit=unit
    )

    moon_groups = build_michell_moon_groups(
        core,
        ObliqueModel.INCIDENCE,
    )

    wall = build_polar_pivot_tangent_wall(
        core,
        ObliqueModel.INCIDENCE,
    )

    sevenfold = build_michell_sevenfold_division(
        core,
        MichellTriangleBase.SOUTH,
    )

    fourteenfold = build_michell_fourteenfold_division(
        core,
        MichellTriangleBase.SOUTH,
    )

    four_triangle_angles = (
        michell_four_triangle_division_angles(
            core
        )
    )

    scaffold = build_michell_28_point_scaffold(
        core
    )

    scaffold_angles = (
        _normalised_sorted_scaffold_angles(
            scaffold
        )
    )

    if (
        len(four_triangle_angles) != 28
        or len(scaffold_angles) != 28
    ):
        raise AssertionError(
            "The four-triangle and scaffold "
            "representations must each contain 28 marks."
        )

    maximum_mismatch = max(
        abs(
            triangle_angle
            - scaffold_angle
        )
        for triangle_angle, scaffold_angle
        in zip(
            four_triangle_angles,
            scaffold_angles,
            strict=True,
        )
    )

    if maximum_mismatch > 1.0e-12:
        raise AssertionError(
            "Four-triangle construction does not close "
            "onto the role-labelled 28-point scaffold: "
            f"{maximum_mismatch:.16e} rad."
        )

    scaffold_heptagram_candidate = (
        build_scaffold_heptagram(
            core,
            scaffold=scaffold,
            family=HeptagramFamily.STEP_2,
        )
    )

    return MichellComposite(
        core=core,
        moon_groups=moon_groups,
        wall_reconstruction=wall,
        sevenfold=sevenfold,
        fourteenfold=fourteenfold,
        four_triangle_angles_radians=(
            four_triangle_angles
        ),
        scaffold=scaffold,
        scaffold_heptagram_candidate=(
            scaffold_heptagram_candidate
        ),
        four_triangle_scaffold_max_mismatch_radians=(
            maximum_mismatch
        ),
    )
