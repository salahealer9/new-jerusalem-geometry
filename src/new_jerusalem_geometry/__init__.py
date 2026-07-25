"""New Jerusalem Geometry."""

from .core_geometry import (
    CoreDiagram,
    CoreDimensions,
    build_core_geometry,
)
from .primitives import AxisAlignedSquare, Circle, Point2D
from .verification import (
    Check,
    VerificationReport,
    verify_core_geometry,
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
    "verify_core_geometry",
]

__version__ = "0.1.0"
