"""Generate the canonical NJG_MICHELL composite SVG."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
    write_michell_composite_svg,
)


DEFAULT_OUTPUT = Path(
    "figures/generated/njg_michell_composite.svg"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the complete unit-only "
            "NJG_MICHELL reconstruction."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    parser.add_argument(
        "--canvas-size",
        type=int,
        default=1200,
    )

    parser.add_argument(
        "--unit",
        type=float,
        default=1.0,
    )

    args = parser.parse_args()

    composite = build_michell_composite(
        unit=args.unit
    )

    path = write_michell_composite_svg(
        composite,
        args.output,
        canvas_size=args.canvas_size,
    )

    print(
        path
    )


if __name__ == "__main__":
    main()
