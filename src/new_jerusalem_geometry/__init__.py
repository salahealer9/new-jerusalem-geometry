"""New Jerusalem Geometry."""

from .core_geometry import (
    CoreDiagram,
    CoreDimensions,
    build_core_geometry,
)
from .export_svg import (
    core_diagram_to_svg,
    write_core_svg,
)
from .primitives import AxisAlignedSquare, Circle, Point2D
from .verification import (
    Check,
    VerificationReport,
    verify_core_geometry,
)

from .model_variants import ObliqueModel
from .oblique_geometry import (
    ConstructionIntersection,
    ObliqueMoon,
    ObliquePlacement,
    build_oblique_placement,
    build_square_construction_intersections,
    model_beta_radians,
    square_intersection_angle,
)
from .oblique_verification import (
    ObliqueVerificationReport,
    verify_oblique_placement,
)

from .comparison_svg import (
    oblique_models_comparison_to_svg,
    write_oblique_models_comparison_svg,
)

from .wall_geometry import (
    OuterWall,
    WallLine,
    build_ordered_moon_circles,
    build_radial_support_wall,
)

from .polar_pivot_wall import (
    POLAR_INDICES,
    POLAR_PIVOT_WALL_IDS,
    build_polar_pivot_tangent_wall,
    wall_normal_angle_degrees,
)

from .wall_verification import (
    WallVerificationReport,
    verify_outer_wall,
)

from .wall_svg import (
    michell_outer_wall_to_svg,
    write_michell_outer_wall_svg,
)

from .septenary_geometry import (
    MichellGapArithmetic,
    MichellSeptenaryScaffold,
    ScaffoldRole,
    SeptenaryPoint,
    build_michell_28_point_scaffold,
    build_michell_gap_arithmetic,
    michell_heptagon_step_angle,
    michell_scaffold_local_offsets,
)

from .septenary_verification import (
    SeptenaryVerificationReport,
    verify_michell_28_point_scaffold,
)

from .septenary_svg import (
    michell_28_point_scaffold_to_svg,
    write_michell_28_point_scaffold_svg,
)

from .heptagram_geometry import (
    AnchorEvidence,
    Figure14Anchor,
    Figure14AnchorRole,
    HeptagramFamily,
    HeptagramGeometry,
    build_figure14_aligned_heptagram,
    build_figure14_anchor_set,
    build_regular_heptagram,
    build_scaffold_heptagram,
)

from .heptagram_verification import (
    Figure14VerificationReport,
    HeptagramFit,
    compare_heptagram_to_anchors,
    verify_figure14_heptagrams,
)

from .heptagram_svg import (
    michell_figure14_heptagram_to_svg,
    write_michell_figure14_heptagram_svg,
)

__all__ = [
    "AxisAlignedSquare",
    "Check",
    "Circle",
    "CoreDiagram",
    "CoreDimensions",
    "Point2D",
    "VerificationReport",
    "build_core_geometry",
    "core_diagram_to_svg",
    "verify_core_geometry",
    "write_core_svg",
    "ConstructionIntersection",
    "ObliqueModel",
    "ObliqueMoon",
    "ObliquePlacement",
    "ObliqueVerificationReport",
    "build_oblique_placement",
    "build_square_construction_intersections",
    "model_beta_radians",
    "square_intersection_angle",
    "verify_oblique_placement",
    "oblique_models_comparison_to_svg",
    "write_oblique_models_comparison_svg",
    "OuterWall",
    "WallLine",
    "WallVerificationReport",
    "build_ordered_moon_circles",
    "build_radial_support_wall",
    "POLAR_INDICES",
    "POLAR_PIVOT_WALL_IDS",
    "build_polar_pivot_tangent_wall",
    "wall_normal_angle_degrees",
    "verify_outer_wall",
    "michell_outer_wall_to_svg",
    "write_michell_outer_wall_svg",
    "MichellGapArithmetic",
    "MichellSeptenaryScaffold",
    "ScaffoldRole",
    "SeptenaryPoint",
    "SeptenaryVerificationReport",
    "build_michell_28_point_scaffold",
    "build_michell_gap_arithmetic",
    "michell_heptagon_step_angle",
    "michell_scaffold_local_offsets",
    "verify_michell_28_point_scaffold",
    "michell_28_point_scaffold_to_svg",
    "write_michell_28_point_scaffold_svg",
    "AnchorEvidence",
    "Figure14Anchor",
    "Figure14AnchorRole",
    "Figure14VerificationReport",
    "HeptagramFamily",
    "HeptagramFit",
    "HeptagramGeometry",
    "build_figure14_aligned_heptagram",
    "build_figure14_anchor_set",
    "build_regular_heptagram",
    "build_scaffold_heptagram",
    "compare_heptagram_to_anchors",
    "verify_figure14_heptagrams",
    "michell_figure14_heptagram_to_svg",
    "write_michell_figure14_heptagram_svg",
]

__version__ = "0.2.0"
