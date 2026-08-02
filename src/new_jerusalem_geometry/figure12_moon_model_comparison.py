"""Compare Figure 12 source-derived Moon centres with fixed candidates.

The candidates are evaluated without fitting translation, scale, rotation,
radius, or phase:

- NJG_MICHELL_28
- NJG_28
- NJG_SVG
- NJG_INC

The selected affine registration is already fixed upstream.

The comparison reports:

- all-twelve-centre RMS;
- oblique-eight RMS;
- cardinal-four RMS;
- maximum centre residual;
- oblique angular RMS;
- independent-pass residuals;
- the source-derived effective oblique beta.

No outer-wall geometry is used.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from math import atan2, cos, degrees, hypot, pi, sin, sqrt
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np

from .core_geometry import build_core_geometry
from .figure12_digitisation import (
    MOON_OBJECT_IDS,
)
from .figure12_source_geometry import (
    Figure12SourceGeometryReport,
    derive_figure12_source_geometry,
)
from .model_variants import ObliqueModel
from .oblique_geometry import (
    model_beta_radians,
)
from .septenary_geometry import (
    build_michell_28_point_scaffold,
)


CARDINAL_IDS = (
    "moon_north",
    "moon_east",
    "moon_south",
    "moon_west",
)

OBLIQUE_IDS = tuple(
    moon_id
    for moon_id in MOON_OBJECT_IDS
    if moon_id not in CARDINAL_IDS
)

CANDIDATE_ORDER = (
    "NJG_MICHELL_28",
    "NJG_28",
    "NJG_SVG",
    "NJG_INC",
)


@dataclass(frozen=True, slots=True)
class CandidateCentre:
    moon_id: str
    x_u: float
    y_u: float
    angle_degrees: float


@dataclass(frozen=True, slots=True)
class MoonCandidateFit:
    candidate: str
    beta_degrees: float
    all_rms_u: float
    all_maximum_u: float
    cardinal_rms_u: float
    oblique_rms_u: float
    oblique_maximum_u: float
    oblique_angular_rms_degrees: float


@dataclass(frozen=True, slots=True)
class MoonCandidatePassFit:
    pass_id: str
    candidate: str
    all_rms_u: float
    oblique_rms_u: float
    oblique_maximum_u: float


@dataclass(frozen=True, slots=True)
class MoonResidual:
    candidate: str
    moon_id: str
    observed_x_u: float
    observed_y_u: float
    candidate_x_u: float
    candidate_y_u: float
    distance_u: float


@dataclass(frozen=True, slots=True)
class Figure12MoonModelComparison:
    source_geometry: Figure12SourceGeometryReport
    candidate_fits: tuple[MoonCandidateFit, ...]
    pass_fits: tuple[MoonCandidatePassFit, ...]
    residuals: tuple[MoonResidual, ...]
    observed_beta_mean_degrees: float
    observed_beta_spatial_std_degrees: float
    pass_beta_means_degrees: tuple[
        tuple[str, float],
        ...,
    ]
    pass_beta_mean_std_degrees: float


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


def _candidate_beta_radians(
    candidate: str,
) -> float:
    diagram = build_core_geometry()

    if candidate == "NJG_MICHELL_28":
        return (
            build_michell_28_point_scaffold(
                diagram
            ).beta_radians
        )

    if candidate == "NJG_28":
        return model_beta_radians(
            diagram,
            ObliqueModel.DIVISION_28,
        )

    if candidate == "NJG_SVG":
        return model_beta_radians(
            diagram,
            ObliqueModel.WIKIMEDIA_SVG,
        )

    if candidate == "NJG_INC":
        return model_beta_radians(
            diagram,
            ObliqueModel.INCIDENCE,
        )

    raise ValueError(
        f"Unknown Moon candidate: {candidate}"
    )


def _angle_map(
    beta: float,
) -> dict[str, float]:
    return {
        "moon_east": 0.0,
        "moon_east_north": beta,
        "moon_north_east": (
            pi / 2.0 - beta
        ),
        "moon_north": pi / 2.0,
        "moon_north_west": (
            pi / 2.0 + beta
        ),
        "moon_west_north": (
            pi - beta
        ),
        "moon_west": pi,
        "moon_west_south": (
            pi + beta
        ),
        "moon_south_west": (
            3.0 * pi / 2.0 - beta
        ),
        "moon_south": (
            3.0 * pi / 2.0
        ),
        "moon_south_east": (
            3.0 * pi / 2.0 + beta
        ),
        "moon_east_south": (
            2.0 * pi - beta
        ),
    }


def build_candidate_centres(
    candidate: str,
) -> tuple[CandidateCentre, ...]:
    diagram = build_core_geometry()

    radius = (
        diagram.construction_circle.radius
    )

    beta = (
        _candidate_beta_radians(
            candidate
        )
    )

    angles = _angle_map(
        beta
    )

    missing = (
        set(MOON_OBJECT_IDS)
        - set(angles)
    )

    if missing:
        raise AssertionError(
            "Candidate angle map is incomplete: "
            f"{sorted(missing)}"
        )

    return tuple(
        CandidateCentre(
            moon_id=moon_id,
            x_u=(
                radius
                * cos(
                    angles[moon_id]
                )
            ),
            y_u=(
                radius
                * sin(
                    angles[moon_id]
                )
            ),
            angle_degrees=(
                degrees(
                    angles[moon_id]
                )
                % 360.0
            ),
        )
        for moon_id
        in MOON_OBJECT_IDS
    )


def _angular_difference_degrees(
    first: float,
    second: float,
) -> float:
    return (
        (
            first
            - second
            + 180.0
        )
        % 360.0
        - 180.0
    )


def _point_angle_degrees(
    x: float,
    y: float,
) -> float:
    return (
        degrees(
            atan2(
                y,
                x,
            )
        )
        % 360.0
    )


def _observed_beta_degrees(
    centres: Mapping[
        str,
        tuple[float, float],
    ],
) -> tuple[float, ...]:
    angles = {
        moon_id: (
            _point_angle_degrees(
                *centres[moon_id]
            )
        )
        for moon_id
        in OBLIQUE_IDS
    }

    beta_values = (
        angles["moon_north_west"] - 90.0,
        90.0 - angles["moon_north_east"],
        angles["moon_east_north"],
        360.0 - angles["moon_east_south"],
        angles["moon_south_east"] - 270.0,
        270.0 - angles["moon_south_west"],
        angles["moon_west_south"] - 180.0,
        180.0 - angles["moon_west_north"],
    )

    return tuple(
        float(value)
        for value in beta_values
    )


def _compare_centres(
    centres: Mapping[
        str,
        tuple[float, float],
    ],
    candidate: str,
) -> tuple[
    MoonCandidateFit,
    tuple[MoonResidual, ...],
]:
    candidate_centres = {
        item.moon_id: item
        for item
        in build_candidate_centres(
            candidate
        )
    }

    residuals: list[
        MoonResidual
    ] = []

    all_distances: list[
        float
    ] = []

    cardinal_distances: list[
        float
    ] = []

    oblique_distances: list[
        float
    ] = []

    angular_residuals: list[
        float
    ] = []

    for moon_id in MOON_OBJECT_IDS:
        observed_x, observed_y = (
            centres[
                moon_id
            ]
        )

        expected = (
            candidate_centres[
                moon_id
            ]
        )

        distance = hypot(
            observed_x
            - expected.x_u,
            observed_y
            - expected.y_u,
        )

        residuals.append(
            MoonResidual(
                candidate=candidate,
                moon_id=moon_id,
                observed_x_u=(
                    observed_x
                ),
                observed_y_u=(
                    observed_y
                ),
                candidate_x_u=(
                    expected.x_u
                ),
                candidate_y_u=(
                    expected.y_u
                ),
                distance_u=distance,
            )
        )

        all_distances.append(
            distance
        )

        if moon_id in CARDINAL_IDS:
            cardinal_distances.append(
                distance
            )
        else:
            oblique_distances.append(
                distance
            )

            observed_angle = (
                _point_angle_degrees(
                    observed_x,
                    observed_y,
                )
            )

            angular_residuals.append(
                _angular_difference_degrees(
                    observed_angle,
                    expected.angle_degrees,
                )
            )

    fit = MoonCandidateFit(
        candidate=candidate,
        beta_degrees=degrees(
            _candidate_beta_radians(
                candidate
            )
        ),
        all_rms_u=_rms(
            all_distances
        ),
        all_maximum_u=max(
            all_distances
        ),
        cardinal_rms_u=_rms(
            cardinal_distances
        ),
        oblique_rms_u=_rms(
            oblique_distances
        ),
        oblique_maximum_u=max(
            oblique_distances
        ),
        oblique_angular_rms_degrees=(
            _rms(
                angular_residuals
            )
        ),
    )

    return (
        fit,
        tuple(
            residuals
        ),
    )


def analyze_figure12_moon_models(
    pass_paths: Sequence[
        str | Path
    ],
) -> Figure12MoonModelComparison:
    source = (
        derive_figure12_source_geometry(
            pass_paths
        )
    )

    primary_centres = {
        moon.moon_id: (
            moon.centre_x_u,
            moon.centre_y_u,
        )
        for moon in source.moons
    }

    candidate_fits: list[
        MoonCandidateFit
    ] = []

    residuals: list[
        MoonResidual
    ] = []

    for candidate in CANDIDATE_ORDER:
        fit, rows = (
            _compare_centres(
                primary_centres,
                candidate,
            )
        )

        candidate_fits.append(
            fit
        )

        residuals.extend(
            rows
        )

    pass_fits: list[
        MoonCandidatePassFit
    ] = []

    pass_beta_means: list[
        tuple[str, float]
    ] = []

    pass_ids = sorted(
        {
            row.pass_id
            for row
            in source.moon_pass_fits
        }
    )

    for pass_id in pass_ids:
        centres = {
            row.moon_id: (
                row.centre_x_u,
                row.centre_y_u,
            )
            for row
            in source.moon_pass_fits
            if row.pass_id == pass_id
        }

        if (
            set(centres)
            != set(MOON_OBJECT_IDS)
        ):
            raise AssertionError(
                f"{pass_id} lacks the twelve Moon centres."
            )

        beta_values = (
            _observed_beta_degrees(
                centres
            )
        )

        pass_beta_means.append(
            (
                pass_id,
                float(
                    np.mean(
                        beta_values
                    )
                ),
            )
        )

        for candidate in CANDIDATE_ORDER:
            fit, _ = (
                _compare_centres(
                    centres,
                    candidate,
                )
            )

            pass_fits.append(
                MoonCandidatePassFit(
                    pass_id=pass_id,
                    candidate=candidate,
                    all_rms_u=(
                        fit.all_rms_u
                    ),
                    oblique_rms_u=(
                        fit.oblique_rms_u
                    ),
                    oblique_maximum_u=(
                        fit.oblique_maximum_u
                    ),
                )
            )

    primary_beta_values = (
        _observed_beta_degrees(
            primary_centres
        )
    )

    pass_beta_array = np.asarray(
        [
            beta
            for _, beta
            in pass_beta_means
        ],
        dtype=float,
    )

    return Figure12MoonModelComparison(
        source_geometry=source,
        candidate_fits=tuple(
            candidate_fits
        ),
        pass_fits=tuple(
            pass_fits
        ),
        residuals=tuple(
            residuals
        ),
        observed_beta_mean_degrees=float(
            np.mean(
                primary_beta_values
            )
        ),
        observed_beta_spatial_std_degrees=float(
            np.std(
                primary_beta_values
            )
        ),
        pass_beta_means_degrees=tuple(
            pass_beta_means
        ),
        pass_beta_mean_std_degrees=float(
            np.std(
                pass_beta_array
            )
        ),
    )


def _format_float(
    value: float,
) -> str:
    return format(
        value,
        ".12f",
    )


def write_figure12_moon_model_comparison(
    report: Figure12MoonModelComparison,
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
        root
        / "figure12_moon_candidate_summary.csv"
    )

    with summary_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        fieldnames = tuple(
            asdict(
                report.candidate_fits[0]
            )
        )

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in report.candidate_fits:
            writer.writerow(
                {
                    key: (
                        _format_float(value)
                        if isinstance(
                            value,
                            float,
                        )
                        else value
                    )
                    for key, value
                    in asdict(row).items()
                }
            )

    pass_path = (
        root
        / "figure12_moon_candidate_pass_fits.csv"
    )

    with pass_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        fieldnames = tuple(
            asdict(
                report.pass_fits[0]
            )
        )

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in report.pass_fits:
            writer.writerow(
                {
                    key: (
                        _format_float(value)
                        if isinstance(
                            value,
                            float,
                        )
                        else value
                    )
                    for key, value
                    in asdict(row).items()
                }
            )

    residual_path = (
        root
        / "figure12_moon_candidate_residuals.csv"
    )

    with residual_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        fieldnames = tuple(
            asdict(
                report.residuals[0]
            )
        )

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in report.residuals:
            writer.writerow(
                {
                    key: (
                        _format_float(value)
                        if isinstance(
                            value,
                            float,
                        )
                        else value
                    )
                    for key, value
                    in asdict(row).items()
                }
            )

    ranked = sorted(
        report.candidate_fits,
        key=lambda row: (
            row.oblique_rms_u
        ),
    )

    pass_rankings = {}

    for pass_id, _ in (
        report.pass_beta_means_degrees
    ):
        rows = sorted(
            (
                row
                for row
                in report.pass_fits
                if row.pass_id
                == pass_id
            ),
            key=lambda row: (
                row.oblique_rms_u
            ),
        )

        pass_rankings[
            pass_id
        ] = [
            row.candidate
            for row in rows
        ]

    json_path = (
        root
        / "figure12_moon_model_comparison.json"
    )

    payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure12-fixed-moon-model-comparison-v1"
        ),
        "candidate_parameters_fitted": False,
        "primary_ranking_metric": (
            "oblique_eight_centre_rms_u"
        ),
        "observed_beta": {
            "mean_degrees": (
                report.observed_beta_mean_degrees
            ),
            "spatial_std_degrees": (
                report.observed_beta_spatial_std_degrees
            ),
            "pass_means_degrees": dict(
                report.pass_beta_means_degrees
            ),
            "pass_mean_std_degrees": (
                report.pass_beta_mean_std_degrees
            ),
        },
        "primary_ranking": [
            row.candidate
            for row in ranked
        ],
        "pass_rankings": (
            pass_rankings
        ),
        "interpretation_boundary": (
            "Candidate ranking is descriptive source-plate "
            "agreement. Closely separated candidates must not "
            "be declared distinguishable unless their margins "
            "are large relative to independent-pass variation."
        ),
    }

    json_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    markdown_path = (
        root
        / "figure12_moon_model_comparison.md"
    )

    lines = [
        "# Figure 12 Moon-placement model comparison",
        "",
        "## Evidence boundary",
        "",
        (
            "The four candidate centre systems are evaluated "
            "without fitting translation, rotation, scale, radius, "
            "or phase."
        ),
        "",
        (
            "Only the source-derived Moon centres are used. "
            "Outer-wall geometry does not enter this comparison."
        ),
        "",
        "## Source-derived effective beta",
        "",
        (
            f"- Mean oblique beta: "
            f"{report.observed_beta_mean_degrees:.9f} degrees"
        ),
        (
            f"- Spatial standard deviation across eight oblique "
            f"Moons: "
            f"{report.observed_beta_spatial_std_degrees:.9f} degrees"
        ),
        (
            f"- Standard deviation of the three independent-pass "
            f"mean betas: "
            f"{report.pass_beta_mean_std_degrees:.9f} degrees"
        ),
        "",
        "## Fixed candidate comparison",
        "",
        (
            "| Rank | Candidate | beta (deg) | "
            "All-12 RMS (u) | Oblique-8 RMS (u) | "
            "Oblique max (u) | Angular RMS (deg) |"
        ),
        (
            "|---:|---|---:|---:|---:|---:|---:|"
        ),
    ]

    for rank, row in enumerate(
        ranked,
        start=1,
    ):
        lines.append(
            f"| {rank} | `{row.candidate}` | "
            f"{row.beta_degrees:.9f} | "
            f"{row.all_rms_u:.9f} | "
            f"{row.oblique_rms_u:.9f} | "
            f"{row.oblique_maximum_u:.9f} | "
            f"{row.oblique_angular_rms_degrees:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Independent-pass rankings",
            "",
        ]
    )

    for pass_id in sorted(
        pass_rankings
    ):
        lines.append(
            f"- `{pass_id}`: "
            + " < ".join(
                pass_rankings[
                    pass_id
                ]
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            (
                "The lowest residual is not automatically a unique "
                "model identification. The ranking margin must be "
                "compared with independent-pass measurement "
                "variation and with the physical separation of the "
                "candidate centre systems."
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
