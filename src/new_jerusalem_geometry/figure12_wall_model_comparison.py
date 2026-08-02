"""Compare Figure 12 wall-construction hypotheses with the source plate.

Two fixed wall rules are evaluated against the source-derived normalized
geometry:

REGULAR_DIRECTION_TANGENT
    The twelve outward wall normals retain the directions of a regular
    dodecagon. Each wall line is translated radially until tangent to its
    associated source-derived Moon circle.

RADIAL_SUPPORT
    Each wall normal points directly through its associated Moon centre.
    The wall line is the outward radial support tangent to that Moon.

The Moon centres and radii used here are source-derived measurements.
Therefore this comparison isolates the wall-construction rule from the
separate Moon-placement-model comparison.

No free wall parameters are fitted.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from math import atan2, cos, degrees, hypot, pi, radians, sin, sqrt
from pathlib import Path
from typing import Sequence

import numpy as np

from .figure12_source_geometry import (
    Figure12SourceGeometryReport,
    derive_figure12_source_geometry,
)


REGULAR_DIRECTION_TANGENT = (
    "REGULAR_DIRECTION_TANGENT"
)

RADIAL_SUPPORT = (
    "RADIAL_SUPPORT"
)

HYPOTHESES = (
    REGULAR_DIRECTION_TANGENT,
    RADIAL_SUPPORT,
)


WALL_MOON_PAIRS = (
    (
        "wall_north_west",
        "moon_north_west",
        120.0,
    ),
    (
        "wall_north",
        "moon_north",
        90.0,
    ),
    (
        "wall_north_east",
        "moon_north_east",
        60.0,
    ),
    (
        "wall_east_north",
        "moon_east_north",
        30.0,
    ),
    (
        "wall_east",
        "moon_east",
        0.0,
    ),
    (
        "wall_east_south",
        "moon_east_south",
        330.0,
    ),
    (
        "wall_south_east",
        "moon_south_east",
        300.0,
    ),
    (
        "wall_south",
        "moon_south",
        270.0,
    ),
    (
        "wall_south_west",
        "moon_south_west",
        240.0,
    ),
    (
        "wall_west_south",
        "moon_west_south",
        210.0,
    ),
    (
        "wall_west",
        "moon_west",
        180.0,
    ),
    (
        "wall_west_north",
        "moon_west_north",
        150.0,
    ),
)


@dataclass(frozen=True, slots=True)
class WallPrediction:
    hypothesis: str
    wall_id: str
    moon_id: str
    predicted_angle_degrees: float
    predicted_normal_x: float
    predicted_normal_y: float
    predicted_support_h_u: float


@dataclass(frozen=True, slots=True)
class WallResidual:
    hypothesis: str
    wall_id: str
    moon_id: str
    observed_angle_degrees: float
    predicted_angle_degrees: float
    angle_residual_degrees: float
    observed_support_h_u: float
    predicted_support_h_u: float
    support_residual_u: float


@dataclass(frozen=True, slots=True)
class WallHypothesisFit:
    dataset_id: str
    hypothesis: str
    angle_rms_degrees: float
    angle_maximum_degrees: float
    support_rms_u: float
    support_maximum_u: float


@dataclass(frozen=True, slots=True)
class Figure12WallModelComparison:
    source_geometry: Figure12SourceGeometryReport
    primary_fits: tuple[
        WallHypothesisFit,
        ...,
    ]
    pass_fits: tuple[
        WallHypothesisFit,
        ...,
    ]
    residuals: tuple[
        WallResidual,
        ...,
    ]


def _rms(
    values: Sequence[float],
) -> float:
    array = np.asarray(
        values,
        dtype=float,
    )

    return sqrt(
        float(
            np.mean(
                array * array
            )
        )
    )


def _angular_delta(
    observed: float,
    predicted: float,
) -> float:
    return (
        (
            observed
            - predicted
            + 180.0
        )
        % 360.0
        - 180.0
    )


def predict_wall(
    *,
    hypothesis: str,
    wall_id: str,
    moon_id: str,
    regular_angle_degrees: float,
    moon_x_u: float,
    moon_y_u: float,
    moon_radius_u: float,
) -> WallPrediction:
    """Predict one support line from one fixed wall hypothesis."""

    if hypothesis == REGULAR_DIRECTION_TANGENT:
        angle = (
            regular_angle_degrees
            % 360.0
        )

        angle_radians = radians(
            angle
        )

        normal_x = cos(
            angle_radians
        )

        normal_y = sin(
            angle_radians
        )

        support = (
            normal_x
            * moon_x_u
            + normal_y
            * moon_y_u
            + moon_radius_u
        )

    elif hypothesis == RADIAL_SUPPORT:
        centre_radius = hypot(
            moon_x_u,
            moon_y_u,
        )

        if centre_radius <= 0.0:
            raise ValueError(
                f"{moon_id} lies at the origin."
            )

        normal_x = (
            moon_x_u
            / centre_radius
        )

        normal_y = (
            moon_y_u
            / centre_radius
        )

        angle = (
            degrees(
                atan2(
                    normal_y,
                    normal_x,
                )
            )
            % 360.0
        )

        support = (
            centre_radius
            + moon_radius_u
        )

    else:
        raise ValueError(
            f"Unsupported wall hypothesis: {hypothesis}"
        )

    return WallPrediction(
        hypothesis=hypothesis,
        wall_id=wall_id,
        moon_id=moon_id,
        predicted_angle_degrees=angle,
        predicted_normal_x=normal_x,
        predicted_normal_y=normal_y,
        predicted_support_h_u=support,
    )


def _compare_dataset(
    *,
    dataset_id: str,
    moon_rows,
    wall_rows,
) -> tuple[
    tuple[WallHypothesisFit, ...],
    tuple[WallResidual, ...],
]:
    moons = {
        row.moon_id: row
        for row in moon_rows
    }

    walls = {
        row.wall_id: row
        for row in wall_rows
    }

    fits: list[
        WallHypothesisFit
    ] = []

    residual_rows: list[
        WallResidual
    ] = []

    for hypothesis in HYPOTHESES:
        angle_residuals = []
        support_residuals = []

        for (
            wall_id,
            moon_id,
            regular_angle,
        ) in WALL_MOON_PAIRS:
            moon = moons[
                moon_id
            ]

            wall = walls[
                wall_id
            ]

            prediction = predict_wall(
                hypothesis=hypothesis,
                wall_id=wall_id,
                moon_id=moon_id,
                regular_angle_degrees=(
                    regular_angle
                ),
                moon_x_u=(
                    moon.centre_x_u
                ),
                moon_y_u=(
                    moon.centre_y_u
                ),
                moon_radius_u=(
                    moon.radius_u
                ),
            )

            angle_residual = (
                _angular_delta(
                    wall.normal_angle_degrees,
                    prediction.predicted_angle_degrees,
                )
            )

            support_residual = (
                wall.support_h_u
                - prediction.predicted_support_h_u
            )

            angle_residuals.append(
                angle_residual
            )

            support_residuals.append(
                support_residual
            )

            residual_rows.append(
                WallResidual(
                    hypothesis=hypothesis,
                    wall_id=wall_id,
                    moon_id=moon_id,
                    observed_angle_degrees=(
                        wall.normal_angle_degrees
                    ),
                    predicted_angle_degrees=(
                        prediction.predicted_angle_degrees
                    ),
                    angle_residual_degrees=(
                        angle_residual
                    ),
                    observed_support_h_u=(
                        wall.support_h_u
                    ),
                    predicted_support_h_u=(
                        prediction.predicted_support_h_u
                    ),
                    support_residual_u=(
                        support_residual
                    ),
                )
            )

        fits.append(
            WallHypothesisFit(
                dataset_id=dataset_id,
                hypothesis=hypothesis,
                angle_rms_degrees=_rms(
                    angle_residuals
                ),
                angle_maximum_degrees=max(
                    abs(value)
                    for value
                    in angle_residuals
                ),
                support_rms_u=_rms(
                    support_residuals
                ),
                support_maximum_u=max(
                    abs(value)
                    for value
                    in support_residuals
                ),
            )
        )

    return (
        tuple(fits),
        tuple(residual_rows),
    )


def analyze_figure12_wall_models(
    pass_paths: Sequence[
        str | Path
    ],
) -> Figure12WallModelComparison:
    """Compare both fixed wall hypotheses."""

    source = (
        derive_figure12_source_geometry(
            pass_paths
        )
    )

    primary_fits, residuals = (
        _compare_dataset(
            dataset_id="primary",
            moon_rows=source.moons,
            wall_rows=source.walls,
        )
    )

    pass_fits: list[
        WallHypothesisFit
    ] = []

    pass_ids = sorted(
        {
            row.pass_id
            for row
            in source.moon_pass_fits
        }
    )

    for pass_id in pass_ids:
        moon_rows = tuple(
            row
            for row
            in source.moon_pass_fits
            if row.pass_id
            == pass_id
        )

        wall_rows = tuple(
            row
            for row
            in source.wall_pass_fits
            if row.pass_id
            == pass_id
        )

        fits, _ = (
            _compare_dataset(
                dataset_id=pass_id,
                moon_rows=moon_rows,
                wall_rows=wall_rows,
            )
        )

        pass_fits.extend(
            fits
        )

    return Figure12WallModelComparison(
        source_geometry=source,
        primary_fits=primary_fits,
        pass_fits=tuple(
            pass_fits
        ),
        residuals=residuals,
    )


def _format_float(
    value: float,
) -> str:
    return format(
        value,
        ".12f",
    )


def _write_dataclass_csv(
    path: Path,
    rows,
) -> Path:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = tuple(
        asdict(
            rows[0]
        )
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(
                {
                    key: (
                        _format_float(
                            value
                        )
                        if isinstance(
                            value,
                            float,
                        )
                        else value
                    )
                    for key, value
                    in asdict(
                        row
                    ).items()
                }
            )

    return path


def write_figure12_wall_model_comparison(
    report: Figure12WallModelComparison,
    output_directory: str | Path,
) -> tuple[Path, ...]:
    root = Path(
        output_directory
    )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        _write_dataclass_csv(
            root
            / "figure12_wall_hypothesis_summary.csv",
            report.primary_fits,
        )
    )

    pass_path = (
        _write_dataclass_csv(
            root
            / "figure12_wall_hypothesis_pass_fits.csv",
            report.pass_fits,
        )
    )

    residual_path = (
        _write_dataclass_csv(
            root
            / "figure12_wall_hypothesis_residuals.csv",
            report.residuals,
        )
    )

    angle_rank = sorted(
        report.primary_fits,
        key=lambda row: (
            row.angle_rms_degrees
        ),
    )

    support_rank = sorted(
        report.primary_fits,
        key=lambda row: (
            row.support_rms_u
        ),
    )

    pass_rankings = {}

    for pass_id in sorted(
        {
            row.dataset_id
            for row
            in report.pass_fits
        }
    ):
        rows = tuple(
            row
            for row
            in report.pass_fits
            if row.dataset_id
            == pass_id
        )

        pass_rankings[
            pass_id
        ] = {
            "angle": [
                row.hypothesis
                for row in sorted(
                    rows,
                    key=lambda item: (
                        item.angle_rms_degrees
                    ),
                )
            ],
            "support": [
                row.hypothesis
                for row in sorted(
                    rows,
                    key=lambda item: (
                        item.support_rms_u
                    ),
                )
            ],
        }

    json_path = (
        root
        / "figure12_wall_model_comparison.json"
    )

    json_payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure12-fixed-wall-model-comparison-v1"
        ),
        "candidate_parameters_fitted": False,
        "moon_geometry_input": (
            "source_plate_measurement"
        ),
        "angle_ranking": [
            row.hypothesis
            for row in angle_rank
        ],
        "support_ranking": [
            row.hypothesis
            for row in support_rank
        ],
        "pass_rankings": (
            pass_rankings
        ),
        "interpretation_boundary": (
            "This comparison tests two project-level wall "
            "construction rules against the source-derived plate. "
            "It does not establish that Michell explicitly stated "
            "the regular-direction tangent construction."
        ),
    }

    json_path.write_text(
        json.dumps(
            json_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path = (
        root
        / "figure12_wall_model_comparison.md"
    )

    regular = next(
        row
        for row
        in report.primary_fits
        if row.hypothesis
        == REGULAR_DIRECTION_TANGENT
    )

    radial = next(
        row
        for row
        in report.primary_fits
        if row.hypothesis
        == RADIAL_SUPPORT
    )

    lines = [
        "# Figure 12 wall-model comparison",
        "",
        "## Evidence boundary",
        "",
        (
            "The wall rules are evaluated against the "
            "source-derived normalized Figure 12 geometry."
        ),
        "",
        (
            "The source-derived Moon centres and radii are used "
            "for both candidates so that this stage isolates the "
            "wall-construction rule."
        ),
        "",
        "## Primary comparison",
        "",
        "| Hypothesis | Angle RMS (deg) | Angle max (deg) | Support RMS (u) | Support max (u) |",
        "|---|---:|---:|---:|---:|",
    ]

    for row in sorted(
        report.primary_fits,
        key=lambda item: (
            item.angle_rms_degrees
        ),
    ):
        lines.append(
            f"| `{row.hypothesis}` | "
            f"{row.angle_rms_degrees:.9f} | "
            f"{row.angle_maximum_degrees:.9f} | "
            f"{row.support_rms_u:.9f} | "
            f"{row.support_maximum_u:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Relative performance",
            "",
            (
                "- Radial/regular angle-RMS ratio: "
                f"{radial.angle_rms_degrees / regular.angle_rms_degrees:.9f}"
            ),
            (
                "- Radial/regular support-RMS ratio: "
                f"{radial.support_rms_u / regular.support_rms_u:.9f}"
            ),
            "",
            "## Independent-pass comparison",
            "",
        ]
    )

    for pass_id in sorted(
        pass_rankings
    ):
        ranking = (
            pass_rankings[
                pass_id
            ]
        )

        lines.append(
            f"- `{pass_id}` angle: "
            + " < ".join(
                ranking["angle"]
            )
        )

        lines.append(
            f"- `{pass_id}` support: "
            + " < ".join(
                ranking["support"]
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            (
                "A preferred plate fit does not by itself turn "
                "the corresponding construction into an explicit "
                "historical statement. The regular-direction "
                "tangent rule remains a project reconstruction "
                "unless primary-source construction instructions "
                "establish it uniquely."
            ),
            "",
        ]
    )

    markdown_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return (
        summary_path,
        pass_path,
        residual_path,
        json_path,
        markdown_path,
    )
