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
]

__version__ = "0.1.0"
