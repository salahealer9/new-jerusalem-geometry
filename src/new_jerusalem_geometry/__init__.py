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

from .moon_geometry import (
    CARDINAL_DIRECTIONS,
    MichellMoonGroup,
    build_michell_moon_groups,
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
    MichellFourteenfoldDivision,
    MichellGapArithmetic,
    MichellSeptenaryScaffold,
    MichellSevenfoldDivision,
    MichellTriangleBase,
    ScaffoldRole,
    SeptenaryPoint,
    build_michell_28_point_scaffold,
    build_michell_fourteenfold_division,
    build_michell_gap_arithmetic,
    build_michell_sevenfold_division,
    michell_four_triangle_division_angles,
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

from .michell_composite import (
    COMPOSITE_MODEL_NAME,
    MichellComposite,
    build_michell_composite,
)

from .michell_composite_svg import (
    michell_composite_to_svg,
    write_michell_composite_svg,
)

from .michell_provenance import (
    GrammarSnapshot,
    MichellCompositeProvenance,
    PROVENANCE_SCHEMA_NAME,
    PROVENANCE_SCHEMA_VERSION,
    ProvenanceObject,
    build_michell_composite_provenance,
    michell_composite_provenance_to_json,
    write_michell_composite_provenance_json,
)

from .michell_geometry_export import (
    GEOMETRY_SCHEMA_NAME,
    GEOMETRY_SCHEMA_VERSION,
    GeometryObject,
    MichellCompositeGeometryExport,
    build_michell_composite_geometry_export,
    michell_composite_geometry_to_json,
    write_michell_composite_geometry_json,
)

__all__ = [
    "COMPOSITE_MODEL_NAME",
    "MichellComposite",
    "build_michell_composite",
    "michell_composite_to_svg",
    "write_michell_composite_svg",
    "GrammarSnapshot",
    "MichellCompositeProvenance",
    "PROVENANCE_SCHEMA_NAME",
    "PROVENANCE_SCHEMA_VERSION",
    "ProvenanceObject",
    "build_michell_composite_provenance",
    "michell_composite_provenance_to_json",
    "write_michell_composite_provenance_json",
    "GEOMETRY_SCHEMA_NAME",
    "GEOMETRY_SCHEMA_VERSION",
    "GeometryObject",
    "MichellCompositeGeometryExport",
    "build_michell_composite_geometry_export",
    "michell_composite_geometry_to_json",
    "write_michell_composite_geometry_json",
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
    "CARDINAL_DIRECTIONS",
    "MichellMoonGroup",
    "build_michell_moon_groups",
    "wall_normal_angle_degrees",
    "verify_outer_wall",
    "michell_outer_wall_to_svg",
    "write_michell_outer_wall_svg",
    "MichellFourteenfoldDivision",
    "MichellGapArithmetic",
    "MichellSeptenaryScaffold",
    "MichellSevenfoldDivision",
    "MichellTriangleBase",
    "ScaffoldRole",
    "SeptenaryPoint",
    "SeptenaryVerificationReport",
    "build_michell_28_point_scaffold",
    "build_michell_fourteenfold_division",
    "build_michell_gap_arithmetic",
    "build_michell_sevenfold_division",
    "michell_four_triangle_division_angles",
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

__version__ = "1.0.0"
