"""Named geometric variants of the New Jerusalem construction."""

from __future__ import annotations

from enum import Enum


class ObliqueModel(str, Enum):
    """Alternative placements of the eight non-cardinal Moon circles."""

    INCIDENCE = "NJG_INC"
    DIVISION_28 = "NJG_28"
    WIKIMEDIA_SVG = "NJG_SVG"

    def __str__(self) -> str:
        return self.value
