#!/usr/bin/env python3
"""Generate the Figure 12 three-model wall evidence comparison."""

from pathlib import Path

from new_jerusalem_geometry.figure12_wall_evidence_svg import (
    analyze_figure12_wall_evidence,
    write_figure12_wall_evidence_json,
    write_figure12_wall_evidence_svg,
)


RAW = Path(
    "data/calibration/figure12/digitisation/raw"
)

DEFAULT_SVG = Path(
    "figures/generated/"
    "figure12_wall_evidence_comparison.svg"
)

DEFAULT_JSON = Path(
    "data/working/figure12/wall_evidence/"
    "figure12_complete_exact_wall_comparison.json"
)


def main() -> int:
    pass_paths = tuple(
        RAW
        / (
            "figure12_observations_"
            f"pass-{index:02d}.csv"
        )
        for index in (
            1,
            2,
            3,
        )
    )

    report = (
        analyze_figure12_wall_evidence(
            pass_paths
        )
    )

    svg_path = (
        write_figure12_wall_evidence_svg(
            report,
            DEFAULT_SVG,
        )
    )

    json_path = (
        write_figure12_wall_evidence_json(
            report,
            DEFAULT_JSON,
        )
    )

    print(
        "Figure 12 wall evidence comparison"
    )

    print(
        "=" * 34
    )

    print()

    for fit in report.fits:
        print(
            f"{fit.candidate:28s} "
            f"angle_RMS={fit.angle_rms_degrees:.9f}°  "
            f"support_RMS={fit.support_rms_u:.9f} u"
        )

    print()
    print(
        f"SVG:  {svg_path}"
    )

    print(
        f"JSON: {json_path}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
