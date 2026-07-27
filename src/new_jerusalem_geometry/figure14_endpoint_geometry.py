"""Source-derived geometry of the seven Figure 14 star endpoints.

This module analyses the correspondence-resolved star endpoints without
assuming a heptagram edge topology.

Three regular seven-vertex models are compared:

1. free similarity fit:
   centre, radius, and angular phase are fitted;

2. construction-circle fit:
   centre is fixed at the diagram origin, radius is fixed at 7u,
   and angular phase is fitted;

3. canonical construction-circle fit:
   centre is fixed at the origin, radius is fixed at 7u, and the
   first spatial endpoint is fixed at 90 degrees.

A regular {7/2} and a regular {7/3} use the same vertex set. Endpoint
coordinates alone therefore cannot distinguish their edge topology.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from math import degrees, pi, sqrt, tau
from pathlib import Path
from statistics import fmean
from typing import Sequence

import numpy as np

from .figure14_registered_landmarks import (
    AffineCalibrationReport,
)
from .figure14_semantic_correspondence import (
    STAR_IDS,
)


ENDPOINT_GEOMETRY_FIELDS = (
    "sequence_index",
    "landmark_id",
    "observed_x",
    "observed_y",
    "observed_radius_from_origin",
    "observed_angle_degrees",
    "click_rms_normalized",
    "pass_registered_rms_normalized",
    "free_fit_x",
    "free_fit_y",
    "free_fit_residual",
    "free_fit_radial_residual",
    "free_fit_angular_residual_degrees",
    "fixed_radius7_x",
    "fixed_radius7_y",
    "fixed_radius7_residual",
    "canonical_x",
    "canonical_y",
    "canonical_residual",
)


TOPOLOGY_IDENTIFIABILITY_STATEMENT = (
    "The seven endpoint coordinates determine a vertex set but do not "
    "distinguish a regular {7/2} from a regular {7/3}, because both "
    "topologies use the same seven vertices. Edge adjacency must be "
    "established from the printed line connections or an independent "
    "line-tracing audit."
)


@dataclass(frozen=True, slots=True)
class RegularSevenVertexFit:
    """One fitted or fixed regular seven-vertex model."""

    fit_id: str
    centre_x: float
    centre_y: float
    radius: float
    phase_degrees: float
    predicted_points: tuple[
        tuple[float, float],
        ...,
    ]
    residuals: tuple[float, ...]
    radial_residuals: tuple[float, ...]
    angular_residuals_degrees: tuple[float, ...]
    rms_residual: float
    maximum_residual: float
    radial_rms: float
    angular_rms_degrees: float
    angular_maximum_degrees: float


@dataclass(frozen=True, slots=True)
class StarEndpointGeometryReport:
    """Complete source-derived endpoint-geometry report."""

    endpoint_ids: tuple[str, ...]
    observed_points: tuple[
        tuple[float, float],
        ...,
    ]
    click_rms_normalized: tuple[float, ...]
    pass_registered_rms_normalized: tuple[float, ...]
    free_fit: RegularSevenVertexFit
    fixed_radius7_fit: RegularSevenVertexFit
    canonical_fit: RegularSevenVertexFit
    observed_side_lengths: tuple[float, ...]
    observed_step2_lengths: tuple[float, ...]
    observed_step3_lengths: tuple[float, ...]
    mean_side_length: float
    side_length_standard_deviation: float
    mean_step2_length: float
    step2_length_standard_deviation: float
    mean_step3_length: float
    step3_length_standard_deviation: float
    exact_radius7_side_length: float
    exact_radius7_step2_length: float
    exact_radius7_step3_length: float
    mean_pixels_per_unit: float
    registration_loo_rms_pixels: float
    registration_loo_equivalent_normalized: float
    free_fit_rms_fraction_of_registration_loo: float
    fixed_radius7_rms_fraction_of_registration_loo: float
    canonical_rms_fraction_of_registration_loo: float
    topology_identifiability_statement: str


def _root_mean_square(
    values: Sequence[float],
) -> float:
    if not values:
        return 0.0

    return sqrt(
        fmean(
            value * value
            for value in values
        )
    )


def _standard_deviation(
    values: Sequence[float],
) -> float:
    if not values:
        return 0.0

    centre = fmean(values)

    return sqrt(
        fmean(
            (value - centre) ** 2
            for value in values
        )
    )


def _wrapped_angles(
    values: np.ndarray,
) -> np.ndarray:
    return (
        values + pi
    ) % tau - pi


def _as_complex_points(
    points: Sequence[Sequence[float]],
) -> np.ndarray:
    array = np.asarray(
        points,
        dtype=float,
    )

    if array.shape != (7, 2):
        raise ValueError(
            "Figure 14 endpoint geometry requires exactly "
            "seven two-dimensional points."
        )

    if not np.all(np.isfinite(array)):
        raise ValueError(
            "Endpoint coordinates must be finite."
        )

    return (
        array[:, 0]
        + 1j * array[:, 1]
    )


def _build_fit_result(
    *,
    fit_id: str,
    observed: np.ndarray,
    centre: complex,
    radius: float,
    phase: float,
) -> RegularSevenVertexFit:
    if radius <= 0.0:
        raise ValueError(
            "Regular-fit radius must be positive."
        )

    indices = np.arange(
        len(observed),
        dtype=float,
    )

    spatial_step = (
        tau / len(observed)
    )

    predicted_angles = (
        phase
        + indices * spatial_step
    )

    predicted = (
        centre
        + radius
        * np.exp(
            1j * predicted_angles
        )
    )

    residuals_array = np.abs(
        observed - predicted
    )

    observed_from_centre = (
        observed - centre
    )

    observed_radii = np.abs(
        observed_from_centre
    )

    radial_residuals_array = (
        observed_radii - radius
    )

    observed_angles = np.angle(
        observed_from_centre
    )

    angular_residuals_radians = (
        _wrapped_angles(
            observed_angles
            - predicted_angles
        )
    )

    angular_residuals_degrees = np.degrees(
        angular_residuals_radians
    )

    residuals = tuple(
        float(value)
        for value in residuals_array
    )

    radial_residuals = tuple(
        float(value)
        for value in radial_residuals_array
    )

    angular_residuals = tuple(
        float(value)
        for value in angular_residuals_degrees
    )

    return RegularSevenVertexFit(
        fit_id=fit_id,
        centre_x=float(
            centre.real
        ),
        centre_y=float(
            centre.imag
        ),
        radius=float(radius),
        phase_degrees=float(
            degrees(
                phase % tau
            )
        ),
        predicted_points=tuple(
            (
                float(value.real),
                float(value.imag),
            )
            for value in predicted
        ),
        residuals=residuals,
        radial_residuals=(
            radial_residuals
        ),
        angular_residuals_degrees=(
            angular_residuals
        ),
        rms_residual=(
            _root_mean_square(
                residuals
            )
        ),
        maximum_residual=max(
            residuals
        ),
        radial_rms=(
            _root_mean_square(
                radial_residuals
            )
        ),
        angular_rms_degrees=(
            _root_mean_square(
                angular_residuals
            )
        ),
        angular_maximum_degrees=max(
            abs(value)
            for value in angular_residuals
        ),
    )


def fit_free_regular_seven_vertices(
    points: Sequence[Sequence[float]],
) -> RegularSevenVertexFit:
    """Fit centre, radius, and phase to seven spatially ordered points."""

    observed = _as_complex_points(
        points
    )

    indices = np.arange(
        len(observed),
        dtype=float,
    )

    template = np.exp(
        1j
        * indices
        * tau
        / len(observed)
    )

    centre = complex(
        np.mean(observed)
    )

    centred = (
        observed - centre
    )

    coefficient = np.sum(
        centred
        * np.conjugate(template)
    ) / np.sum(
        np.abs(template) ** 2
    )

    radius = float(
        abs(coefficient)
    )

    phase = float(
        np.angle(coefficient)
    )

    return _build_fit_result(
        fit_id="free_regular_seven_vertices",
        observed=observed,
        centre=centre,
        radius=radius,
        phase=phase,
    )


def fit_origin_radius7_with_free_phase(
    points: Sequence[Sequence[float]],
) -> RegularSevenVertexFit:
    """Fit phase with centre fixed at the origin and radius fixed at 7u."""

    observed = _as_complex_points(
        points
    )

    indices = np.arange(
        len(observed),
        dtype=float,
    )

    template = np.exp(
        1j
        * indices
        * tau
        / len(observed)
    )

    correlation = np.sum(
        observed
        * np.conjugate(template)
    )

    phase = float(
        np.angle(correlation)
    )

    return _build_fit_result(
        fit_id="origin_radius7_free_phase",
        observed=observed,
        centre=0.0 + 0.0j,
        radius=7.0,
        phase=phase,
    )


def fit_canonical_origin_radius7(
    points: Sequence[Sequence[float]],
) -> RegularSevenVertexFit:
    """Evaluate the canonical radius-7 fit with the first vertex at the top."""

    observed = _as_complex_points(
        points
    )

    return _build_fit_result(
        fit_id="canonical_origin_radius7_top",
        observed=observed,
        centre=0.0 + 0.0j,
        radius=7.0,
        phase=pi / 2.0,
    )


def analyze_star_endpoint_points(
    *,
    points: Sequence[Sequence[float]],
    endpoint_ids: Sequence[str] = STAR_IDS,
    click_rms_normalized: Sequence[float] | None = None,
    pass_registered_rms_normalized: Sequence[float] | None = None,
    mean_pixels_per_unit: float,
    registration_loo_rms_pixels: float,
) -> StarEndpointGeometryReport:
    """Analyse seven correspondence-resolved endpoint coordinates."""

    observed_complex = _as_complex_points(
        points
    )

    identifiers = tuple(
        endpoint_ids
    )

    if len(identifiers) != 7:
        raise ValueError(
            "Exactly seven endpoint identifiers are required."
        )

    if len(set(identifiers)) != 7:
        raise ValueError(
            "Endpoint identifiers must be unique."
        )

    if mean_pixels_per_unit <= 0.0:
        raise ValueError(
            "Mean pixel scale must be positive."
        )

    if registration_loo_rms_pixels < 0.0:
        raise ValueError(
            "Registration LOO RMS must not be negative."
        )

    if click_rms_normalized is None:
        click_values = (0.0,) * 7
    else:
        click_values = tuple(
            float(value)
            for value in click_rms_normalized
        )

    if pass_registered_rms_normalized is None:
        pass_values = (0.0,) * 7
    else:
        pass_values = tuple(
            float(value)
            for value in pass_registered_rms_normalized
        )

    if len(click_values) != 7:
        raise ValueError(
            "Click-uncertainty count must equal seven."
        )

    if len(pass_values) != 7:
        raise ValueError(
            "Pass-registration uncertainty count must equal seven."
        )

    free_fit = (
        fit_free_regular_seven_vertices(
            points
        )
    )

    fixed_radius7_fit = (
        fit_origin_radius7_with_free_phase(
            points
        )
    )

    canonical_fit = (
        fit_canonical_origin_radius7(
            points
        )
    )

    side_lengths = np.abs(
        np.roll(
            observed_complex,
            -1,
        )
        - observed_complex
    )

    step2_lengths = np.abs(
        np.roll(
            observed_complex,
            -2,
        )
        - observed_complex
    )

    step3_lengths = np.abs(
        np.roll(
            observed_complex,
            -3,
        )
        - observed_complex
    )

    side_values = tuple(
        float(value)
        for value in side_lengths
    )

    step2_values = tuple(
        float(value)
        for value in step2_lengths
    )

    step3_values = tuple(
        float(value)
        for value in step3_lengths
    )

    registration_loo_normalized = (
        registration_loo_rms_pixels
        / mean_pixels_per_unit
    )

    if registration_loo_normalized > 0.0:
        free_fraction = (
            free_fit.rms_residual
            / registration_loo_normalized
        )

        fixed_fraction = (
            fixed_radius7_fit.rms_residual
            / registration_loo_normalized
        )

        canonical_fraction = (
            canonical_fit.rms_residual
            / registration_loo_normalized
        )
    else:
        free_fraction = 0.0
        fixed_fraction = 0.0
        canonical_fraction = 0.0

    return StarEndpointGeometryReport(
        endpoint_ids=identifiers,
        observed_points=tuple(
            (
                float(value.real),
                float(value.imag),
            )
            for value in observed_complex
        ),
        click_rms_normalized=click_values,
        pass_registered_rms_normalized=(
            pass_values
        ),
        free_fit=free_fit,
        fixed_radius7_fit=(
            fixed_radius7_fit
        ),
        canonical_fit=canonical_fit,
        observed_side_lengths=(
            side_values
        ),
        observed_step2_lengths=(
            step2_values
        ),
        observed_step3_lengths=(
            step3_values
        ),
        mean_side_length=fmean(
            side_values
        ),
        side_length_standard_deviation=(
            _standard_deviation(
                side_values
            )
        ),
        mean_step2_length=fmean(
            step2_values
        ),
        step2_length_standard_deviation=(
            _standard_deviation(
                step2_values
            )
        ),
        mean_step3_length=fmean(
            step3_values
        ),
        step3_length_standard_deviation=(
            _standard_deviation(
                step3_values
            )
        ),
        exact_radius7_side_length=(
            14.0
            * np.sin(
                pi / 7.0
            )
        ),
        exact_radius7_step2_length=(
            14.0
            * np.sin(
                2.0 * pi / 7.0
            )
        ),
        exact_radius7_step3_length=(
            14.0
            * np.sin(
                3.0 * pi / 7.0
            )
        ),
        mean_pixels_per_unit=(
            mean_pixels_per_unit
        ),
        registration_loo_rms_pixels=(
            registration_loo_rms_pixels
        ),
        registration_loo_equivalent_normalized=(
            registration_loo_normalized
        ),
        free_fit_rms_fraction_of_registration_loo=(
            free_fraction
        ),
        fixed_radius7_rms_fraction_of_registration_loo=(
            fixed_fraction
        ),
        canonical_rms_fraction_of_registration_loo=(
            canonical_fraction
        ),
        topology_identifiability_statement=(
            TOPOLOGY_IDENTIFIABILITY_STATEMENT
        ),
    )


def derive_figure14_star_endpoint_geometry(
    calibration: AffineCalibrationReport,
) -> StarEndpointGeometryReport:
    """Analyse the resolved endpoints from an affine calibration report."""

    by_identifier = {
        item.landmark_id: item
        for item in calibration.landmarks
    }

    missing = set(STAR_IDS).difference(
        by_identifier
    )

    if missing:
        raise ValueError(
            "Affine calibration is missing star endpoints: "
            + ", ".join(
                sorted(missing)
            )
        )

    stars = tuple(
        by_identifier[
            landmark_id
        ]
        for landmark_id in STAR_IDS
    )

    if any(
        item.category != "star_endpoint"
        for item in stars
    ):
        raise ValueError(
            "Resolved star identifiers do not all have "
            "category star_endpoint."
        )

    return analyze_star_endpoint_points(
        points=tuple(
            (
                item.normalized_x,
                item.normalized_y,
            )
            for item in stars
        ),
        endpoint_ids=STAR_IDS,
        click_rms_normalized=tuple(
            item.click_rms_normalized
            for item in stars
        ),
        pass_registered_rms_normalized=tuple(
            item.pass_registered_rms_normalized
            for item in stars
        ),
        mean_pixels_per_unit=(
            calibration.mean_pixels_per_unit
        ),
        registration_loo_rms_pixels=(
            calibration.selected_fit.loo_rms_pixels
        ),
    )


def _format_float(
    value: float,
) -> str:
    return format(value, ".12f")


def write_endpoint_geometry_csv(
    path: str | Path,
    report: StarEndpointGeometryReport,
) -> Path:
    """Write one diagnostic row per resolved endpoint."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=ENDPOINT_GEOMETRY_FIELDS,
        )

        writer.writeheader()

        for index, landmark_id in enumerate(
            report.endpoint_ids
        ):
            observed_x, observed_y = (
                report.observed_points[index]
            )

            free_x, free_y = (
                report.free_fit.predicted_points[
                    index
                ]
            )

            fixed_x, fixed_y = (
                report.fixed_radius7_fit.predicted_points[
                    index
                ]
            )

            canonical_x, canonical_y = (
                report.canonical_fit.predicted_points[
                    index
                ]
            )

            observed_radius = sqrt(
                observed_x * observed_x
                + observed_y * observed_y
            )

            observed_angle = degrees(
                np.arctan2(
                    observed_y,
                    observed_x,
                )
            )

            writer.writerow(
                {
                    "sequence_index": index,
                    "landmark_id": landmark_id,
                    "observed_x": _format_float(
                        observed_x
                    ),
                    "observed_y": _format_float(
                        observed_y
                    ),
                    "observed_radius_from_origin": (
                        _format_float(
                            observed_radius
                        )
                    ),
                    "observed_angle_degrees": (
                        _format_float(
                            observed_angle
                        )
                    ),
                    "click_rms_normalized": (
                        _format_float(
                            report.click_rms_normalized[
                                index
                            ]
                        )
                    ),
                    "pass_registered_rms_normalized": (
                        _format_float(
                            report.pass_registered_rms_normalized[
                                index
                            ]
                        )
                    ),
                    "free_fit_x": _format_float(
                        free_x
                    ),
                    "free_fit_y": _format_float(
                        free_y
                    ),
                    "free_fit_residual": (
                        _format_float(
                            report.free_fit.residuals[
                                index
                            ]
                        )
                    ),
                    "free_fit_radial_residual": (
                        _format_float(
                            report.free_fit.radial_residuals[
                                index
                            ]
                        )
                    ),
                    "free_fit_angular_residual_degrees": (
                        _format_float(
                            report.free_fit.angular_residuals_degrees[
                                index
                            ]
                        )
                    ),
                    "fixed_radius7_x": (
                        _format_float(
                            fixed_x
                        )
                    ),
                    "fixed_radius7_y": (
                        _format_float(
                            fixed_y
                        )
                    ),
                    "fixed_radius7_residual": (
                        _format_float(
                            report.fixed_radius7_fit.residuals[
                                index
                            ]
                        )
                    ),
                    "canonical_x": _format_float(
                        canonical_x
                    ),
                    "canonical_y": _format_float(
                        canonical_y
                    ),
                    "canonical_residual": (
                        _format_float(
                            report.canonical_fit.residuals[
                                index
                            ]
                        )
                    ),
                }
            )

    return output_path


def write_endpoint_geometry_json(
    path: str | Path,
    report: StarEndpointGeometryReport,
) -> Path:
    """Write deterministic endpoint-geometry summary metadata."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    def fit_payload(
        fit: RegularSevenVertexFit,
    ) -> dict[str, object]:
        return {
            "fit_id": fit.fit_id,
            "centre_x": fit.centre_x,
            "centre_y": fit.centre_y,
            "radius": fit.radius,
            "phase_degrees": fit.phase_degrees,
            "rms_residual": fit.rms_residual,
            "maximum_residual": (
                fit.maximum_residual
            ),
            "radial_rms": fit.radial_rms,
            "angular_rms_degrees": (
                fit.angular_rms_degrees
            ),
            "angular_maximum_degrees": (
                fit.angular_maximum_degrees
            ),
        }

    payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure14-source-derived-star-endpoint-geometry"
        ),
        "endpoint_count": 7,
        "endpoint_order": list(
            report.endpoint_ids
        ),
        "free_regular_fit": fit_payload(
            report.free_fit
        ),
        "origin_radius7_free_phase_fit": (
            fit_payload(
                report.fixed_radius7_fit
            )
        ),
        "canonical_origin_radius7_fit": (
            fit_payload(
                report.canonical_fit
            )
        ),
        "chord_statistics": {
            "spatial_side": {
                "mean": report.mean_side_length,
                "standard_deviation": (
                    report.side_length_standard_deviation
                ),
                "exact_radius7": (
                    report.exact_radius7_side_length
                ),
            },
            "step_2": {
                "mean": report.mean_step2_length,
                "standard_deviation": (
                    report.step2_length_standard_deviation
                ),
                "exact_radius7": (
                    report.exact_radius7_step2_length
                ),
            },
            "step_3": {
                "mean": report.mean_step3_length,
                "standard_deviation": (
                    report.step3_length_standard_deviation
                ),
                "exact_radius7": (
                    report.exact_radius7_step3_length
                ),
            },
        },
        "registration_scale": {
            "mean_pixels_per_unit": (
                report.mean_pixels_per_unit
            ),
            "loo_rms_pixels": (
                report.registration_loo_rms_pixels
            ),
            "loo_rms_equivalent_normalized": (
                report.registration_loo_equivalent_normalized
            ),
        },
        "fit_residual_fraction_of_registration_loo": {
            "free_regular": (
                report.free_fit_rms_fraction_of_registration_loo
            ),
            "origin_radius7_free_phase": (
                report.fixed_radius7_rms_fraction_of_registration_loo
            ),
            "canonical_origin_radius7": (
                report.canonical_rms_fraction_of_registration_loo
            ),
        },
        "topology_identifiability": {
            "vertex_set_distinguishes_7_2_from_7_3": False,
            "statement": (
                report.topology_identifiability_statement
            ),
        },
    }

    output_path.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return output_path


def write_endpoint_geometry_markdown(
    path: str | Path,
    report: StarEndpointGeometryReport,
) -> Path:
    """Write a human-readable endpoint-geometry audit."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    lines = [
        "# Figure 14 source-derived star endpoint geometry",
        "",
        "## Evidence boundary",
        "",
        "This analysis uses the seven correspondence-resolved endpoint",
        "centroids obtained from the selected affine plate registration.",
        "No heptagram edge topology is assumed.",
        "",
        "## Regular seven-vertex fits",
        "",
        "| Model | Free parameters | Centre (u) | Radius (u) | Phase | RMS residual (u) | Maximum residual (u) | Angular RMS |",
        "|---|---|---|---:|---:|---:|---:|---:|",
        (
            "| Free regular fit | centre, radius, phase | "
            f"({report.free_fit.centre_x:+.9f}, "
            f"{report.free_fit.centre_y:+.9f}) | "
            f"{report.free_fit.radius:.9f} | "
            f"{report.free_fit.phase_degrees:.9f}° | "
            f"{report.free_fit.rms_residual:.9f} | "
            f"{report.free_fit.maximum_residual:.9f} | "
            f"{report.free_fit.angular_rms_degrees:.9f}° |"
        ),
        (
            "| Origin, radius 7 | phase only | "
            "(0, 0) | "
            "7.000000000 | "
            f"{report.fixed_radius7_fit.phase_degrees:.9f}° | "
            f"{report.fixed_radius7_fit.rms_residual:.9f} | "
            f"{report.fixed_radius7_fit.maximum_residual:.9f} | "
            f"{report.fixed_radius7_fit.angular_rms_degrees:.9f}° |"
        ),
        (
            "| Canonical origin, radius 7 | none | "
            "(0, 0) | "
            "7.000000000 | "
            "90.000000000° | "
            f"{report.canonical_fit.rms_residual:.9f} | "
            f"{report.canonical_fit.maximum_residual:.9f} | "
            f"{report.canonical_fit.angular_rms_degrees:.9f}° |"
        ),
        "",
        "## Registration scale",
        "",
        (
            f"- Mean affine scale: "
            f"{report.mean_pixels_per_unit:.6f} px/u"
        ),
        (
            f"- Registration leave-one-out RMS: "
            f"{report.registration_loo_rms_pixels:.6f} px"
        ),
        (
            f"- Registration leave-one-out equivalent: "
            f"{report.registration_loo_equivalent_normalized:.9f} u"
        ),
        (
            f"- Free-fit RMS / registration LOO scale: "
            f"{report.free_fit_rms_fraction_of_registration_loo:.6f}"
        ),
        (
            f"- Radius-7 fit RMS / registration LOO scale: "
            f"{report.fixed_radius7_rms_fraction_of_registration_loo:.6f}"
        ),
        (
            f"- Canonical fit RMS / registration LOO scale: "
            f"{report.canonical_rms_fraction_of_registration_loo:.6f}"
        ),
        "",
        "These ratios are scale comparisons, not statistical z-scores.",
        "",
        "## Chord statistics",
        "",
        "| Connection step | Geometric role | Observed mean (u) | Observed SD (u) | Exact radius-7 value (u) |",
        "|---:|---|---:|---:|---:|",
        (
            "| 1 | Seven-vertex perimeter | "
            f"{report.mean_side_length:.9f} | "
            f"{report.side_length_standard_deviation:.9f} | "
            f"{report.exact_radius7_side_length:.9f} |"
        ),
        (
            "| 2 | Possible `{7/2}` edge | "
            f"{report.mean_step2_length:.9f} | "
            f"{report.step2_length_standard_deviation:.9f} | "
            f"{report.exact_radius7_step2_length:.9f} |"
        ),
        (
            "| 3 | Possible `{7/3}` edge | "
            f"{report.mean_step3_length:.9f} | "
            f"{report.step3_length_standard_deviation:.9f} | "
            f"{report.exact_radius7_step3_length:.9f} |"
        ),
        "",
        "## Topology boundary",
        "",
        report.topology_identifiability_statement,
        "",
        "The endpoint geometry may establish regularity, centre, radius,",
        "and angular phase. It cannot by itself establish whether the",
        "printed edges connect every second or every third vertex.",
        "",
    ]

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
