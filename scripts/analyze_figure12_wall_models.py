#!/usr/bin/env python3
"""Compare fixed Figure 12 wall-construction hypotheses."""

from pathlib import Path

from new_jerusalem_geometry.figure12_wall_model_comparison import (
    analyze_figure12_wall_models,
    write_figure12_wall_model_comparison,
)


INPUT = Path(
    "data/calibration/figure12/digitisation/raw"
)

OUTPUT = Path(
    "data/working/figure12/wall_models"
)


def main() -> int:
    pass_paths = tuple(
        INPUT
        / (
            "figure12_observations_"
            f"pass-{index:02d}.csv"
        )
        for index in (1, 2, 3)
    )

    report = (
        analyze_figure12_wall_models(
            pass_paths
        )
    )

    outputs = (
        write_figure12_wall_model_comparison(
            report,
            OUTPUT,
        )
    )

    print(
        "Figure 12 wall-model comparison"
    )
    print(
        "=" * 31
    )

    for row in sorted(
        report.primary_fits,
        key=lambda item: (
            item.angle_rms_degrees
        ),
    ):
        print(
            f"{row.hypothesis:28s} "
            f"angle_RMS={row.angle_rms_degrees:.9f}°  "
            f"support_RMS={row.support_rms_u:.9f} u"
        )

    print()
    print("Independent passes")
    print("------------------")

    for pass_id in (
        "pass-01",
        "pass-02",
        "pass-03",
    ):
        rows = tuple(
            row
            for row
            in report.pass_fits
            if row.dataset_id
            == pass_id
        )

        angle = sorted(
            rows,
            key=lambda item: (
                item.angle_rms_degrees
            ),
        )

        support = sorted(
            rows,
            key=lambda item: (
                item.support_rms_u
            ),
        )

        print(
            f"{pass_id}: "
            f"angle {angle[0].hypothesis} < {angle[1].hypothesis}; "
            f"support {support[0].hypothesis} < {support[1].hypothesis}"
        )

    print()
    print("Outputs:")

    for path in outputs:
        print(
            f"  {path}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
