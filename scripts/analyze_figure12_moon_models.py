#!/usr/bin/env python3
"""Compare fixed Moon-placement candidates with Figure 12 source data."""

from pathlib import Path

from new_jerusalem_geometry.figure12_moon_model_comparison import (
    analyze_figure12_moon_models,
    write_figure12_moon_model_comparison,
)


INPUT = Path(
    "data/calibration/figure12/digitisation/raw"
)

OUTPUT = Path(
    "data/working/figure12/moon_models"
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
        analyze_figure12_moon_models(
            pass_paths
        )
    )

    outputs = (
        write_figure12_moon_model_comparison(
            report,
            OUTPUT,
        )
    )

    print(
        "Figure 12 Moon-placement comparison"
    )
    print(
        "=" * 35
    )

    print(
        f"Observed beta mean:      "
        f"{report.observed_beta_mean_degrees:.9f}°"
    )

    print(
        f"Observed beta spatial σ: "
        f"{report.observed_beta_spatial_std_degrees:.9f}°"
    )

    print(
        f"Pass-mean beta σ:        "
        f"{report.pass_beta_mean_std_degrees:.9f}°"
    )

    print()
    print(
        "Fixed-candidate ranking"
    )
    print(
        "-----------------------"
    )

    ranked = sorted(
        report.candidate_fits,
        key=lambda row: (
            row.oblique_rms_u
        ),
    )

    for rank, row in enumerate(
        ranked,
        start=1,
    ):
        print(
            f"{rank}. {row.candidate:15s} "
            f"beta={row.beta_degrees:.9f}°  "
            f"oblique_RMS={row.oblique_rms_u:.9f} u  "
            f"max={row.oblique_maximum_u:.9f} u"
        )

    print()
    print(
        "Independent-pass rankings"
    )
    print(
        "-------------------------"
    )

    pass_ids = sorted(
        {
            row.pass_id
            for row in report.pass_fits
        }
    )

    for pass_id in pass_ids:
        rows = sorted(
            (
                row
                for row in report.pass_fits
                if row.pass_id
                == pass_id
            ),
            key=lambda row: (
                row.oblique_rms_u
            ),
        )

        print(
            f"{pass_id}: "
            + " < ".join(
                row.candidate
                for row in rows
            )
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
