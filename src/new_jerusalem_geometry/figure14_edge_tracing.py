"""Near-endpoint line-tracing audit for Michell's Figure 14.

The seven calibrated endpoint coordinates alone cannot distinguish a
regular {7/2} from a regular {7/3}, because both use the same vertex set.

This module examines the two printed strokes immediately inside every
endpoint. Working near the endpoints avoids ambiguity at the internal
line crossings.

For every endpoint and pass, the two observed ray directions are compared
against the unordered direction pair expected for:

- step 1: the seven-vertex perimeter;
- step 2: the {7/2} heptagram;
- step 3: the {7/3} heptagram.

The two ray clicks may be made in either order. The analysis chooses the
minimum-error assignment to the two expected directions.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from math import acos, degrees, sqrt
from pathlib import Path
from statistics import fmean
from typing import Sequence

import numpy as np

from .figure14_registration import (
    apply_registration_matrix,
    pixel_to_cartesian,
)
from .figure14_semantic_correspondence import (
    STAR_IDS,
)
from .source_preparation import sha256_file


EDGE_TRACE_FIELDS = (
    "schema_version",
    "pass_id",
    "source_image",
    "source_image_sha256",
    "image_width_pixels",
    "image_height_pixels",
    "reference_matrix_sha256",
    "reference_landmarks_sha256",
    "endpoint_index",
    "endpoint_id",
    "ray_index",
    "pixel_x",
    "pixel_y",
    "endpoint_pixel_x",
    "endpoint_pixel_y",
    "radial_distance_pixels",
)

EDGE_TOPOLOGY_DETAIL_FIELDS = (
    "pass_id",
    "endpoint_index",
    "endpoint_id",
    "candidate_step",
    "candidate_notation",
    "ray_0_target_id",
    "ray_1_target_id",
    "ray_0_angular_residual_degrees",
    "ray_1_angular_residual_degrees",
    "pair_rms_degrees",
    "pair_maximum_degrees",
    "endpoint_pass_winner",
)


STEP_NOTATION = {
    1: "perimeter",
    2: "{7/2}",
    3: "{7/3}",
}


@dataclass(frozen=True, slots=True)
class EdgeTraceReference:
    """Affine calibration and endpoint positions used by the trace audit."""

    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    inverse_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    endpoint_ids: tuple[str, ...]
    endpoint_pixels: tuple[
        tuple[float, float],
        ...,
    ]
    endpoint_normalized: tuple[
        tuple[float, float],
        ...,
    ]
    matrix_sha256: str
    landmarks_sha256: str


@dataclass(frozen=True, slots=True)
class EdgeRaySample:
    """One clicked sample on a printed stroke near an endpoint."""

    pass_id: str
    endpoint_index: int
    endpoint_id: str
    ray_index: int
    pixel_x: float
    pixel_y: float
    radial_distance_pixels: float


@dataclass(frozen=True, slots=True)
class EdgeTracePass:
    """One independent fourteen-click endpoint-ray pass."""

    path: Path
    pass_id: str
    source_image: str
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    reference_matrix_sha256: str
    reference_landmarks_sha256: str
    samples: tuple[EdgeRaySample, ...]


@dataclass(frozen=True, slots=True)
class EndpointCandidateFit:
    """One topology candidate at one endpoint in one pass."""

    step: int
    notation: str
    assigned_target_indices: tuple[int, int]
    assigned_target_ids: tuple[str, str]
    angular_residuals_degrees: tuple[float, float]
    rms_degrees: float
    maximum_degrees: float


@dataclass(frozen=True, slots=True)
class EndpointPassTopology:
    """Candidate comparison for one endpoint in one pass."""

    pass_id: str
    endpoint_index: int
    endpoint_id: str
    candidates: tuple[EndpointCandidateFit, ...]
    winning_step: int
    winning_notation: str


@dataclass(frozen=True, slots=True)
class TopologyCandidateSummary:
    """Aggregate evidence for one connection step."""

    step: int
    notation: str
    rms_degrees: float
    maximum_degrees: float
    endpoint_pass_wins: int
    endpoint_pass_count: int


@dataclass(frozen=True, slots=True)
class EdgeTopologyReport:
    """Complete near-endpoint line-topology audit."""

    passes: tuple[EdgeTracePass, ...]
    endpoint_results: tuple[EndpointPassTopology, ...]
    candidate_summaries: tuple[TopologyCandidateSummary, ...]
    selected_step: int
    selected_notation: str
    selected_rms_degrees: float
    selected_maximum_degrees: float
    second_best_rms_degrees: float
    rms_margin_degrees: float
    unanimous_endpoint_passes: bool


def _matrix_tuple(
    matrix: np.ndarray,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:
    return tuple(
        tuple(
            float(value)
            for value in row
        )
        for row in matrix
    )  # type: ignore[return-value]


def _rms(
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


def _angle_degrees(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    first_norm = float(
        np.linalg.norm(first)
    )

    second_norm = float(
        np.linalg.norm(second)
    )

    if first_norm <= 0.0 or second_norm <= 0.0:
        raise ValueError(
            "Ray and candidate vectors must be non-zero."
        )

    cosine = float(
        np.dot(first, second)
        / (first_norm * second_norm)
    )

    cosine = min(
        1.0,
        max(-1.0, cosine),
    )

    return degrees(
        acos(cosine)
    )


def load_edge_trace_reference(
    *,
    matrix_path: str | Path,
    landmarks_path: str | Path,
) -> EdgeTraceReference:
    """Load the selected affine calibration and resolved endpoints."""

    matrix_file = Path(matrix_path)
    landmarks_file = Path(
        landmarks_path
    )

    payload = json.loads(
        matrix_file.read_text(
            encoding="utf-8"
        )
    )

    if payload.get("selected_model") != "affine":
        raise ValueError(
            "Edge tracing requires the selected affine calibration."
        )

    source = payload[
        "source_image"
    ]

    inverse_matrix = np.asarray(
        payload[
            "inverse_cartesian_pixel_to_model"
        ],
        dtype=float,
    )

    if inverse_matrix.shape != (3, 3):
        raise ValueError(
            "Inverse affine matrix must have shape (3, 3)."
        )

    with landmarks_file.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    by_identifier = {
        row["landmark_id"]: row
        for row in rows
        if row["category"] == "star_endpoint"
    }

    missing = set(STAR_IDS).difference(
        by_identifier
    )

    if missing:
        raise ValueError(
            "Registered landmark file is missing star endpoints: "
            + ", ".join(
                sorted(missing)
            )
        )

    endpoint_pixels = tuple(
        (
            float(
                by_identifier[
                    landmark_id
                ]["pixel_centroid_x"]
            ),
            float(
                by_identifier[
                    landmark_id
                ]["pixel_centroid_y"]
            ),
        )
        for landmark_id in STAR_IDS
    )

    endpoint_normalized = tuple(
        (
            float(
                by_identifier[
                    landmark_id
                ]["normalized_x"]
            ),
            float(
                by_identifier[
                    landmark_id
                ]["normalized_y"]
            ),
        )
        for landmark_id in STAR_IDS
    )

    return EdgeTraceReference(
        source_image=str(
            source["filename"]
        ),
        source_image_sha256=str(
            source["sha256"]
        ),
        image_width_pixels=int(
            source["width_pixels"]
        ),
        image_height_pixels=int(
            source["height_pixels"]
        ),
        inverse_matrix=_matrix_tuple(
            inverse_matrix
        ),
        endpoint_ids=STAR_IDS,
        endpoint_pixels=endpoint_pixels,
        endpoint_normalized=(
            endpoint_normalized
        ),
        matrix_sha256=sha256_file(
            matrix_file
        ),
        landmarks_sha256=sha256_file(
            landmarks_file
        ),
    )


def write_edge_trace_csv(
    path: str | Path,
    *,
    reference: EdgeTraceReference,
    source_image_path: str | Path,
    pass_id: str,
    samples: Sequence[
        tuple[int, int, float, float]
    ],
) -> Path:
    """Write one complete fourteen-click edge-tracing pass."""

    if not pass_id.strip():
        raise ValueError(
            "pass_id must not be empty."
        )

    source_path = Path(
        source_image_path
    )

    if not source_path.is_file():
        raise FileNotFoundError(
            f"Source image not found: {source_path}"
        )

    source_digest = sha256_file(
        source_path
    )

    if (
        source_digest
        != reference.source_image_sha256
    ):
        raise ValueError(
            "Local source image does not match the affine "
            "calibration source hash."
        )

    expected_keys = {
        (endpoint_index, ray_index)
        for endpoint_index in range(7)
        for ray_index in range(2)
    }

    observed_keys = {
        (
            int(endpoint_index),
            int(ray_index),
        )
        for (
            endpoint_index,
            ray_index,
            _,
            _,
        ) in samples
    }

    if len(samples) != 14:
        raise ValueError(
            "A complete edge-tracing pass requires exactly "
            "fourteen samples."
        )

    if observed_keys != expected_keys:
        raise ValueError(
            "Each endpoint must contain ray indices 0 and 1."
        )

    ordered = sorted(
        samples,
        key=lambda item: (
            item[0],
            item[1],
        ),
    )

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
            fieldnames=EDGE_TRACE_FIELDS,
        )

        writer.writeheader()

        for (
            endpoint_index,
            ray_index,
            pixel_x,
            pixel_y,
        ) in ordered:
            endpoint_id = (
                reference.endpoint_ids[
                    endpoint_index
                ]
            )

            endpoint_x, endpoint_y = (
                reference.endpoint_pixels[
                    endpoint_index
                ]
            )

            distance = sqrt(
                (float(pixel_x) - endpoint_x) ** 2
                + (float(pixel_y) - endpoint_y) ** 2
            )

            writer.writerow(
                {
                    "schema_version": 1,
                    "pass_id": pass_id,
                    "source_image": (
                        reference.source_image
                    ),
                    "source_image_sha256": (
                        reference.source_image_sha256
                    ),
                    "image_width_pixels": (
                        reference.image_width_pixels
                    ),
                    "image_height_pixels": (
                        reference.image_height_pixels
                    ),
                    "reference_matrix_sha256": (
                        reference.matrix_sha256
                    ),
                    "reference_landmarks_sha256": (
                        reference.landmarks_sha256
                    ),
                    "endpoint_index": endpoint_index,
                    "endpoint_id": endpoint_id,
                    "ray_index": ray_index,
                    "pixel_x": format(
                        float(pixel_x),
                        ".6f",
                    ),
                    "pixel_y": format(
                        float(pixel_y),
                        ".6f",
                    ),
                    "endpoint_pixel_x": format(
                        endpoint_x,
                        ".6f",
                    ),
                    "endpoint_pixel_y": format(
                        endpoint_y,
                        ".6f",
                    ),
                    "radial_distance_pixels": format(
                        distance,
                        ".6f",
                    ),
                }
            )

    return output_path


def load_edge_trace_pass(
    path: str | Path,
) -> EdgeTracePass:
    """Load and validate one endpoint-ray tracing pass."""

    input_path = Path(path)

    with input_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(
            csv.DictReader(handle)
        )

    if len(rows) != 14:
        raise ValueError(
            f"Expected fourteen edge-ray samples in {input_path}; "
            f"found {len(rows)}."
        )

    singleton_fields = (
        "pass_id",
        "source_image",
        "source_image_sha256",
        "image_width_pixels",
        "image_height_pixels",
        "reference_matrix_sha256",
        "reference_landmarks_sha256",
    )

    singletons: dict[str, str] = {}

    for field in singleton_fields:
        values = {
            row[field]
            for row in rows
        }

        if len(values) != 1:
            raise ValueError(
                f"Inconsistent {field} in {input_path}."
            )

        singletons[field] = next(
            iter(values)
        )

    samples = tuple(
        EdgeRaySample(
            pass_id=row["pass_id"],
            endpoint_index=int(
                row["endpoint_index"]
            ),
            endpoint_id=row["endpoint_id"],
            ray_index=int(
                row["ray_index"]
            ),
            pixel_x=float(
                row["pixel_x"]
            ),
            pixel_y=float(
                row["pixel_y"]
            ),
            radial_distance_pixels=float(
                row["radial_distance_pixels"]
            ),
        )
        for row in rows
    )

    expected_identity = tuple(
        (
            endpoint_index,
            STAR_IDS[endpoint_index],
            ray_index,
        )
        for endpoint_index in range(7)
        for ray_index in range(2)
    )

    observed_identity = tuple(
        (
            sample.endpoint_index,
            sample.endpoint_id,
            sample.ray_index,
        )
        for sample in samples
    )

    if observed_identity != expected_identity:
        raise ValueError(
            "Edge-ray rows do not match the fixed endpoint order."
        )

    return EdgeTracePass(
        path=input_path,
        pass_id=singletons["pass_id"],
        source_image=singletons[
            "source_image"
        ],
        source_image_sha256=singletons[
            "source_image_sha256"
        ],
        image_width_pixels=int(
            singletons[
                "image_width_pixels"
            ]
        ),
        image_height_pixels=int(
            singletons[
                "image_height_pixels"
            ]
        ),
        reference_matrix_sha256=singletons[
            "reference_matrix_sha256"
        ],
        reference_landmarks_sha256=singletons[
            "reference_landmarks_sha256"
        ],
        samples=samples,
    )


def _fit_endpoint_candidate(
    *,
    endpoint_index: int,
    observed_vectors: np.ndarray,
    endpoint_points: np.ndarray,
    step: int,
) -> EndpointCandidateFit:
    target_indices = (
        (endpoint_index - step) % 7,
        (endpoint_index + step) % 7,
    )

    endpoint = endpoint_points[
        endpoint_index
    ]

    expected_vectors = np.asarray(
        [
            endpoint_points[target_index]
            - endpoint
            for target_index in target_indices
        ],
        dtype=float,
    )

    direct = (
        _angle_degrees(
            observed_vectors[0],
            expected_vectors[0],
        ),
        _angle_degrees(
            observed_vectors[1],
            expected_vectors[1],
        ),
    )

    swapped = (
        _angle_degrees(
            observed_vectors[0],
            expected_vectors[1],
        ),
        _angle_degrees(
            observed_vectors[1],
            expected_vectors[0],
        ),
    )

    if (
        direct[0] * direct[0]
        + direct[1] * direct[1]
        <= swapped[0] * swapped[0]
        + swapped[1] * swapped[1]
    ):
        residuals = direct
        assigned_indices = (
            target_indices[0],
            target_indices[1],
        )
    else:
        residuals = swapped
        assigned_indices = (
            target_indices[1],
            target_indices[0],
        )

    return EndpointCandidateFit(
        step=step,
        notation=STEP_NOTATION[step],
        assigned_target_indices=(
            assigned_indices
        ),
        assigned_target_ids=tuple(
            STAR_IDS[index]
            for index in assigned_indices
        ),
        angular_residuals_degrees=(
            residuals
        ),
        rms_degrees=_rms(
            residuals
        ),
        maximum_degrees=max(
            residuals
        ),
    )


def analyze_edge_trace_passes(
    *,
    reference: EdgeTraceReference,
    pass_paths: Sequence[str | Path],
) -> EdgeTopologyReport:
    """Compare perimeter, {7/2}, and {7/3} endpoint-ray topology."""

    if len(pass_paths) < 2:
        raise ValueError(
            "At least two independent edge-tracing passes "
            "are required."
        )

    passes = tuple(
        load_edge_trace_pass(path)
        for path in pass_paths
    )

    if len(
        {
            item.pass_id
            for item in passes
        }
    ) != len(passes):
        raise ValueError(
            "Edge-tracing pass identifiers must be unique."
        )

    for item in passes:
        if (
            item.source_image_sha256
            != reference.source_image_sha256
        ):
            raise ValueError(
                "Edge-tracing pass uses a different source image."
            )

        if (
            item.reference_matrix_sha256
            != reference.matrix_sha256
        ):
            raise ValueError(
                "Edge-tracing pass uses a different affine matrix."
            )

        if (
            item.reference_landmarks_sha256
            != reference.landmarks_sha256
        ):
            raise ValueError(
                "Edge-tracing pass uses different endpoint landmarks."
            )

    inverse = np.asarray(
        reference.inverse_matrix,
        dtype=float,
    )

    endpoint_points = np.asarray(
        reference.endpoint_normalized,
        dtype=float,
    )

    endpoint_results: list[
        EndpointPassTopology
    ] = []

    aggregate_residuals: dict[
        int,
        list[float],
    ] = {
        1: [],
        2: [],
        3: [],
    }

    endpoint_pass_wins = {
        1: 0,
        2: 0,
        3: 0,
    }

    for trace_pass in passes:
        for endpoint_index in range(7):
            endpoint_samples = tuple(
                sample
                for sample in trace_pass.samples
                if (
                    sample.endpoint_index
                    == endpoint_index
                )
            )

            if len(endpoint_samples) != 2:
                raise ValueError(
                    "Each endpoint requires exactly two ray samples."
                )

            normalized_samples = []

            for sample in endpoint_samples:
                cartesian = pixel_to_cartesian(
                    sample.pixel_x,
                    sample.pixel_y,
                    reference.image_height_pixels,
                )

                normalized = (
                    apply_registration_matrix(
                        inverse,
                        [cartesian],
                    )[0]
                )

                normalized_samples.append(
                    normalized
                )

            observed_vectors = (
                np.asarray(
                    normalized_samples,
                    dtype=float,
                )
                - endpoint_points[
                    endpoint_index
                ]
            )

            candidates = tuple(
                _fit_endpoint_candidate(
                    endpoint_index=endpoint_index,
                    observed_vectors=(
                        observed_vectors
                    ),
                    endpoint_points=(
                        endpoint_points
                    ),
                    step=step,
                )
                for step in (1, 2, 3)
            )

            ranked = sorted(
                candidates,
                key=lambda item: (
                    item.rms_degrees,
                    item.maximum_degrees,
                ),
            )

            winner = ranked[0]

            endpoint_pass_wins[
                winner.step
            ] += 1

            for candidate in candidates:
                aggregate_residuals[
                    candidate.step
                ].extend(
                    candidate.angular_residuals_degrees
                )

            endpoint_results.append(
                EndpointPassTopology(
                    pass_id=trace_pass.pass_id,
                    endpoint_index=(
                        endpoint_index
                    ),
                    endpoint_id=STAR_IDS[
                        endpoint_index
                    ],
                    candidates=candidates,
                    winning_step=(
                        winner.step
                    ),
                    winning_notation=(
                        winner.notation
                    ),
                )
            )

    endpoint_result_tuple = tuple(
        endpoint_results
    )

    candidate_summaries = tuple(
        TopologyCandidateSummary(
            step=step,
            notation=STEP_NOTATION[step],
            rms_degrees=_rms(
                aggregate_residuals[step]
            ),
            maximum_degrees=max(
                aggregate_residuals[step]
            ),
            endpoint_pass_wins=(
                endpoint_pass_wins[step]
            ),
            endpoint_pass_count=len(
                endpoint_result_tuple
            ),
        )
        for step in (1, 2, 3)
    )

    ranked_summaries = sorted(
        candidate_summaries,
        key=lambda item: (
            item.rms_degrees,
            item.maximum_degrees,
        ),
    )

    selected = ranked_summaries[0]
    second = ranked_summaries[1]

    return EdgeTopologyReport(
        passes=passes,
        endpoint_results=(
            endpoint_result_tuple
        ),
        candidate_summaries=(
            candidate_summaries
        ),
        selected_step=selected.step,
        selected_notation=(
            selected.notation
        ),
        selected_rms_degrees=(
            selected.rms_degrees
        ),
        selected_maximum_degrees=(
            selected.maximum_degrees
        ),
        second_best_rms_degrees=(
            second.rms_degrees
        ),
        rms_margin_degrees=(
            second.rms_degrees
            - selected.rms_degrees
        ),
        unanimous_endpoint_passes=(
            selected.endpoint_pass_wins
            == selected.endpoint_pass_count
        ),
    )


def write_edge_topology_details_csv(
    path: str | Path,
    report: EdgeTopologyReport,
) -> Path:
    """Write candidate residuals for every endpoint and pass."""

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
            fieldnames=(
                EDGE_TOPOLOGY_DETAIL_FIELDS
            ),
        )

        writer.writeheader()

        for result in report.endpoint_results:
            for candidate in result.candidates:
                writer.writerow(
                    {
                        "pass_id": result.pass_id,
                        "endpoint_index": (
                            result.endpoint_index
                        ),
                        "endpoint_id": (
                            result.endpoint_id
                        ),
                        "candidate_step": (
                            candidate.step
                        ),
                        "candidate_notation": (
                            candidate.notation
                        ),
                        "ray_0_target_id": (
                            candidate.assigned_target_ids[
                                0
                            ]
                        ),
                        "ray_1_target_id": (
                            candidate.assigned_target_ids[
                                1
                            ]
                        ),
                        "ray_0_angular_residual_degrees": format(
                            candidate.angular_residuals_degrees[
                                0
                            ],
                            ".12f",
                        ),
                        "ray_1_angular_residual_degrees": format(
                            candidate.angular_residuals_degrees[
                                1
                            ],
                            ".12f",
                        ),
                        "pair_rms_degrees": format(
                            candidate.rms_degrees,
                            ".12f",
                        ),
                        "pair_maximum_degrees": format(
                            candidate.maximum_degrees,
                            ".12f",
                        ),
                        "endpoint_pass_winner": (
                            "true"
                            if candidate.step
                            == result.winning_step
                            else "false"
                        ),
                    }
                )

    return output_path


def write_edge_topology_json(
    path: str | Path,
    report: EdgeTopologyReport,
) -> Path:
    """Write deterministic topology-audit summary metadata."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure14-near-endpoint-line-topology-audit"
        ),
        "method": (
            "At each endpoint, compare the unordered pair of "
            "two near-endpoint printed-stroke directions against "
            "the expected chord-direction pair for steps 1, 2, and 3."
        ),
        "independent_pass_ids": [
            item.pass_id
            for item in report.passes
        ],
        "endpoint_pass_count": len(
            report.endpoint_results
        ),
        "candidate_summaries": [
            {
                "step": item.step,
                "notation": item.notation,
                "rms_degrees": (
                    item.rms_degrees
                ),
                "maximum_degrees": (
                    item.maximum_degrees
                ),
                "endpoint_pass_wins": (
                    item.endpoint_pass_wins
                ),
                "endpoint_pass_count": (
                    item.endpoint_pass_count
                ),
            }
            for item in report.candidate_summaries
        ],
        "selected": {
            "step": report.selected_step,
            "notation": (
                report.selected_notation
            ),
            "rms_degrees": (
                report.selected_rms_degrees
            ),
            "maximum_degrees": (
                report.selected_maximum_degrees
            ),
            "second_best_rms_degrees": (
                report.second_best_rms_degrees
            ),
            "rms_margin_degrees": (
                report.rms_margin_degrees
            ),
            "unanimous_endpoint_passes": (
                report.unanimous_endpoint_passes
            ),
        },
        "interpretation_boundary": (
            "This is direct manual line-direction evidence near "
            "the endpoints. It avoids internal crossings but remains "
            "subject to printed-line thickness and manual sampling."
        ),
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


def write_edge_topology_markdown(
    path: str | Path,
    report: EdgeTopologyReport,
) -> Path:
    """Write a human-readable near-endpoint topology audit."""

    output_path = Path(path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ranked = sorted(
        report.candidate_summaries,
        key=lambda item: (
            item.rms_degrees,
            item.maximum_degrees,
        ),
    )

    lines = [
        "# Figure 14 near-endpoint line-topology audit",
        "",
        "## Method",
        "",
        "Two points were sampled on the two printed strokes immediately",
        "inside each of the seven source-calibrated endpoints. Sampling",
        "near the endpoints avoids ambiguity at the internal crossings.",
        "",
        "The two clicks at each endpoint were treated as an unordered pair.",
        "Their directions were compared with the two chord directions",
        "expected for connection steps 1, 2, and 3.",
        "",
        f"- Independent passes: {len(report.passes)}",
        f"- Endpoints per pass: 7",
        (
            f"- Endpoint/pass comparisons: "
            f"{len(report.endpoint_results)}"
        ),
        (
            f"- Total ray samples: "
            f"{2 * len(report.endpoint_results)}"
        ),
        "",
        "## Candidate ranking",
        "",
        "| Rank | Connection | Step | Angular RMS | Maximum residual | Endpoint/pass wins |",
        "|---:|---|---:|---:|---:|---:|",
    ]

    for rank, item in enumerate(
        ranked,
        start=1,
    ):
        lines.append(
            "| "
            f"{rank} | "
            f"{item.notation} | "
            f"{item.step} | "
            f"{item.rms_degrees:.9f}° | "
            f"{item.maximum_degrees:.9f}° | "
            f"{item.endpoint_pass_wins}/"
            f"{item.endpoint_pass_count} |"
        )

    lines.extend(
        [
            "",
            "## Selected topology",
            "",
            (
                f"- Selected connection: "
                f"**{report.selected_notation}**"
            ),
            (
                f"- Selected angular RMS: "
                f"{report.selected_rms_degrees:.9f}°"
            ),
            (
                f"- Selected maximum residual: "
                f"{report.selected_maximum_degrees:.9f}°"
            ),
            (
                f"- Second-best angular RMS: "
                f"{report.second_best_rms_degrees:.9f}°"
            ),
            (
                f"- RMS margin: "
                f"{report.rms_margin_degrees:.9f}°"
            ),
            (
                f"- Unanimous across endpoint/pass comparisons: "
                f"{'yes' if report.unanimous_endpoint_passes else 'no'}"
            ),
            "",
            "## Interpretation boundary",
            "",
            "This audit provides direct evidence from the printed line",
            "directions immediately inside the endpoints. It does not rely",
            "on the prior endpoint-row sequence or on resolving the internal",
            "line crossings.",
            "",
            "The result remains subject to printed-line thickness, source",
            "reproduction quality, affine-registration uncertainty, and",
            "manual sampling uncertainty.",
            "",
        ]
    )

    output_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return output_path
