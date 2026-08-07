"""Generate the canonical complete NJG_MICHELL geometry JSON."""

from __future__ import annotations

import argparse
from pathlib import Path

from new_jerusalem_geometry import (
    build_michell_composite,
    build_michell_composite_geometry_export,
    write_michell_composite_geometry_json,
)


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUTPUT = (
    ROOT
    / "data"
    / "geometry"
    / "njg_michell_v0_5"
    / "njg_michell_geometry.json"
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the complete numerical "
            "NJG_MICHELL geometry export."
        )
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
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

    geometry_export = (
        build_michell_composite_geometry_export(
            composite
        )
    )

    path = (
        write_michell_composite_geometry_json(
            geometry_export,
            args.output,
        )
    )

    print(path)
    print(
        "Objects:",
        geometry_export.object_count,
    )

    sections = dict(
        geometry_export.sections
    )

    print(
        "Core objects:",
        len(
            sections["core"][
                "object_ids"
            ]
        ),
    )

    print(
        "Moon circles:",
        len(
            sections["moon_system"][
                "object_ids"
            ]
        ),
    )

    print(
        "Wall lines:",
        len(
            sections["wall"][
                "line_object_ids"
            ]
        ),
    )

    print(
        "Wall vertices:",
        len(
            sections["wall"][
                "vertex_object_ids"
            ]
        ),
    )

    print(
        "Sevenfold points:",
        len(
            sections["sevenfold"][
                "object_ids"
            ]
        ),
    )

    print(
        "Fourteenfold points:",
        len(
            sections["fourteenfold"][
                "object_ids"
            ]
        ),
    )

    print(
        "Four-triangle marks:",
        len(
            sections["four_triangle_28"][
                "object_ids"
            ]
        ),
    )

    print(
        "Scaffold points:",
        len(
            sections["scaffold_28"][
                "object_ids"
            ]
        ),
    )

    print(
        "Heptagram vertices:",
        len(
            sections["heptagram"][
                "vertex_object_ids"
            ]
        ),
    )

    print(
        "Heptagram edges:",
        len(
            sections["heptagram"][
                "edge_object_ids"
            ]
        ),
    )


if __name__ == "__main__":
    main()
