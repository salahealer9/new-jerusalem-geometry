"""Frozen forward validation of the NJG_MICHELL composite.

This module compares the fixed NJG_MICHELL predictor against promoted
source-derived Figure 12 and Figure 14 geometry.

No geometric parameter is fitted here.

The predictor is frozen at:

    43096326d5c1862fc7e33f9d90eb1df861c3b642

Calibration data flow only into this validation layer and never back into
the generative composite.
"""

from __future__ import annotations

from dataclasses import (
    asdict,
    dataclass,
)
import csv
import hashlib
import json
from math import (
    atan2,
    degrees,
    hypot,
    sqrt,
)
from pathlib import Path
from typing import Sequence

from .heptagram_geometry import (
    HeptagramGeometry,
    build_regular_heptagram,
)
from .michell_composite import (
    MichellComposite,
    build_michell_composite,
)
from .polar_pivot_wall import (
    POLAR_PIVOT_WALL_IDS,
)
from .wall_geometry import (
    WallLine,
)


FROZEN_PREDICTOR_COMMIT = (
    "43096326d5c1862fc7e33f9d90eb1df861c3b642"
)


FROZEN_PREDICTOR_PATHS = (
    "src/new_jerusalem_geometry/primitives.py",
    "src/new_jerusalem_geometry/core_geometry.py",
    "src/new_jerusalem_geometry/model_variants.py",
    "src/new_jerusalem_geometry/oblique_geometry.py",
    "src/new_jerusalem_geometry/wall_geometry.py",
    "src/new_jerusalem_geometry/polar_pivot_wall.py",
    "src/new_jerusalem_geometry/moon_geometry.py",
    "src/new_jerusalem_geometry/septenary_geometry.py",
    "src/new_jerusalem_geometry/heptagram_geometry.py",
    "src/new_jerusalem_geometry/michell_composite.py",
)


VALIDATION_INPUT_PATHS = {
    "figure12_wall_geometry": Path(
        "data/calibration/figure12/source_geometry/"
        "figure12_wall_geometry.csv"
    ),
    "figure12_wall_vertices": Path(
        "data/calibration/figure12/source_geometry/"
        "figure12_wall_vertices.csv"
    ),
    "figure12_wall_side_lengths": Path(
        "data/calibration/figure12/source_geometry/"
        "figure12_wall_side_lengths.csv"
    ),
    "figure12_source_summary": Path(
        "data/calibration/figure12/source_geometry/"
        "figure12_source_geometry_summary.json"
    ),
    "figure14_registered_landmarks": Path(
        "data/calibration/figure14/derived/"
        "registered_landmark_centroids.csv"
    ),
    "figure14_endpoint_geometry_csv": Path(
        "data/calibration/figure14/derived/"
        "star_endpoint_geometry.csv"
    ),
    "figure14_endpoint_geometry_json": Path(
        "data/calibration/figure14/derived/"
        "star_endpoint_geometry.json"
    ),
    "figure14_semantic_correspondence": Path(
        "data/calibration/figure14/"
        "correspondence_resolved/"
        "semantic_correspondence_manifest.json"
    ),
}


EXPECTED_VALIDATION_INPUT_SHA256 = {
    "figure12_wall_geometry": (
        "c763cf325c4470ea29b966c814604b03"
        "d30d2db68b90f32289bb9e5f5079cf6b"
    ),
    "figure12_wall_vertices": (
        "8c2a30b79dcf58e7352abe5ac680b4b3"
        "32e7469055dc6f754547a52fb2c356ec"
    ),
    "figure12_wall_side_lengths": (
        "30c3caed82da4bd1db235db0000e0d50b"
        "f17df3a3de11efdcc1444c9b0158896"
    ),
    "figure12_source_summary": (
        "0c0cb10f996478b5b9efc90d0324a5ff"
        "30ea52fc3347f24f5c143add65554602"
    ),
    "figure14_registered_landmarks": (
        "9549c5d416e903781a3ff227e84c27846"
        "5f9d729259d1a5985c316773814ebd0"
    ),
    "figure14_endpoint_geometry_csv": (
        "ca9a9dde2dc43f44d64f9dbe78fdfd6a"
        "9e773be22ddc37bdb0a79381fa9b2e65"
    ),
    "figure14_endpoint_geometry_json": (
        "3b4eaffb33b5984441a88039d6e5a972"
        "343b6b6ef43dbe980bfa7dc28bde98a0"
    ),
    "figure14_semantic_correspondence": (
        "0c605726b7b55c96033a275a7ae337384"
        "0b02374c07cd55f9ce970d2cae75ffc"
    ),
}


FIGURE14_ENDPOINT_ORDER = (
    "star_endpoint_00_top",
    "star_endpoint_01_upper_left",
    "star_endpoint_02_lower_left",
    "star_endpoint_03_bottom_left",
    "star_endpoint_04_bottom_right",
    "star_endpoint_05_lower_right",
    "star_endpoint_06_upper_right",
)


FIGURE14_SOURCE_SUPPORTED_ENDPOINTS = frozenset(
    {
        "star_endpoint_00_top",
        "star_endpoint_01_upper_left",
        "star_endpoint_03_bottom_left",
        "star_endpoint_04_bottom_right",
        "star_endpoint_06_upper_right",
    }
)


FIGURE14_INFERRED_ENDPOINTS = frozenset(
    {
        "star_endpoint_02_lower_left",
        "star_endpoint_05_lower_right",
    }
)


FIGURE12_POLAR_WALL_IDS = frozenset(
    {
        "wall_east",
        "wall_north",
        "wall_west",
        "wall_south",
    }
)


@dataclass(frozen=True, slots=True)
class Figure12LineResidual:
    wall_id: str
    predicted_angle_degrees: float
    source_angle_degrees: float
    angle_residual_degrees: float
    predicted_support_u: float
    source_support_u: float
    support_residual_u: float
    source_line_fit_rms_u: float
    source_pass_angle_rms_degrees: float
    source_pass_support_rms_u: float


@dataclass(frozen=True, slots=True)
class Figure12VertexResidual:
    vertex_id: str
    wall_a: str
    wall_b: str
    predicted_x_u: float
    predicted_y_u: float
    source_x_u: float
    source_y_u: float
    point_residual_u: float


@dataclass(frozen=True, slots=True)
class Figure12SideResidual:
    wall_id: str
    predicted_length_u: float
    source_length_u: float
    length_residual_u: float


@dataclass(frozen=True, slots=True)
class Figure12ForwardValidation:
    line_residuals: tuple[Figure12LineResidual, ...]
    vertex_residuals: tuple[Figure12VertexResidual, ...]
    side_residuals: tuple[Figure12SideResidual, ...]

    angle_rms_degrees: float
    angle_maximum_degrees: float
    support_rms_u: float
    support_maximum_u: float

    vertex_rms_u: float
    vertex_maximum_u: float
    side_length_rms_u: float
    side_length_maximum_u: float

    predicted_perimeter_u: float
    source_perimeter_u: float
    perimeter_residual_u: float
    perimeter_relative_residual: float

    predicted_area_u2: float
    source_area_u2: float
    area_residual_u2: float
    area_relative_residual: float

    wall_side_count: int
    polar_side_count: int
    oblique_side_count: int


@dataclass(frozen=True, slots=True)
class Figure14VertexResidual:
    sequence_index: int
    landmark_id: str
    evidence_class: str

    predicted_x_u: float
    predicted_y_u: float
    source_x_u: float
    source_y_u: float

    point_residual_u: float
    angular_residual_degrees: float
    radial_residual_u: float


@dataclass(frozen=True, slots=True)
class Figure14CandidateValidation:
    candidate_name: str
    vertex_residuals: tuple[
        Figure14VertexResidual,
        ...,
    ]

    point_rms_u: float
    point_maximum_u: float
    angular_rms_degrees: float
    angular_maximum_degrees: float
    radial_rms_u: float
    radial_maximum_u: float

    source_supported_point_rms_u: float
    source_supported_point_maximum_u: float
    inferred_point_rms_u: float
    inferred_point_maximum_u: float

    registration_loo_equivalent_u: float
    point_rms_fraction_of_registration_loo: float


@dataclass(frozen=True, slots=True)
class Figure14ForwardValidation:
    scaffold_candidate: Figure14CandidateValidation
    canonical_regular: Figure14CandidateValidation

    scaffold_minus_canonical_point_rms_u: float
    scaffold_minus_canonical_point_maximum_u: float

    endpoint_count: int
    source_supported_endpoint_count: int
    inferred_endpoint_count: int


@dataclass(frozen=True, slots=True)
class MichellForwardValidationReport:
    analysis_id: str
    schema_version: int
    frozen_predictor_commit: str
    validation_mode: str

    input_sha256: tuple[
        tuple[str, str],
        ...,
    ]

    figure12: Figure12ForwardValidation
    figure14: Figure14ForwardValidation


def _sha256_file(
    path: Path,
) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(
                1024 * 1024
            ),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def verify_validation_input_hashes(
    repo_root: str | Path = ".",
) -> tuple[tuple[str, str], ...]:
    """Verify every preregistered validation input byte-for-byte."""

    root = Path(repo_root)

    actual: list[
        tuple[str, str]
    ] = []

    for key, relative_path in (
        VALIDATION_INPUT_PATHS.items()
    ):
        path = (
            root
            / relative_path
        )

        if not path.is_file():
            raise FileNotFoundError(
                f"Missing validation input: {path}"
            )

        digest = _sha256_file(
            path
        )

        expected = (
            EXPECTED_VALIDATION_INPUT_SHA256[
                key
            ]
        )

        if digest != expected:
            raise ValueError(
                "Validation input hash mismatch "
                f"for {key}: "
                f"expected {expected}, "
                f"received {digest}."
            )

        actual.append(
            (
                key,
                digest,
            )
        )

    return tuple(actual)


def _read_csv(
    path: Path,
) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        return list(
            csv.DictReader(handle)
        )


def _rms(
    values: Sequence[float],
) -> float:
    if not values:
        raise ValueError(
            "RMS requires at least one value."
        )

    return sqrt(
        sum(
            value * value
            for value in values
        )
        / len(values)
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


def _angular_delta_degrees(
    first: float,
    second: float,
) -> float:
    return abs(
        (
            first
            - second
            + 180.0
        )
        % 360.0
        - 180.0
    )


def _intersect_wall_lines(
    first: WallLine,
    second: WallLine,
) -> tuple[float, float]:
    determinant = (
        first.normal.x
        * second.normal.y
        - first.normal.y
        * second.normal.x
    )

    if abs(
        determinant
    ) <= 1.0e-15:
        raise ValueError(
            "Validation wall lines are parallel."
        )

    x = (
        first.offset
        * second.normal.y
        - first.normal.y
        * second.offset
    ) / determinant

    y = (
        first.normal.x
        * second.offset
        - first.offset
        * second.normal.x
    ) / determinant

    return (
        x,
        y,
    )


def _figure12_validation(
    composite: MichellComposite,
    repo_root: Path,
) -> Figure12ForwardValidation:
    wall = (
        composite.wall_reconstruction
    )

    predicted_lines = {
        line.name: line
        for line in wall.lines
    }

    expected_wall_ids = set(
        POLAR_PIVOT_WALL_IDS
    )

    if (
        set(predicted_lines)
        != expected_wall_ids
    ):
        raise ValueError(
            "Predicted wall IDs do not match "
            "the fixed polar-pivot semantic IDs."
        )

    source_line_rows = _read_csv(
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure12_wall_geometry"
        ]
    )

    source_lines = {
        row["wall_id"]: row
        for row in source_line_rows
    }

    if (
        set(source_lines)
        != expected_wall_ids
    ):
        raise ValueError(
            "Figure 12 source wall IDs do not "
            "match the fixed prediction IDs."
        )

    line_residuals: list[
        Figure12LineResidual
    ] = []

    for wall_id in (
        POLAR_PIVOT_WALL_IDS
    ):
        predicted = (
            predicted_lines[
                wall_id
            ]
        )

        source = (
            source_lines[
                wall_id
            ]
        )

        predicted_angle = (
            _point_angle_degrees(
                predicted.normal.x,
                predicted.normal.y,
            )
        )

        source_angle = float(
            source[
                "normal_angle_degrees"
            ]
        )

        predicted_support = (
            predicted.offset
        )

        source_support = float(
            source[
                "support_h_u"
            ]
        )

        line_residuals.append(
            Figure12LineResidual(
                wall_id=wall_id,
                predicted_angle_degrees=(
                    predicted_angle
                ),
                source_angle_degrees=(
                    source_angle
                ),
                angle_residual_degrees=(
                    _angular_delta_degrees(
                        predicted_angle,
                        source_angle,
                    )
                ),
                predicted_support_u=(
                    predicted_support
                ),
                source_support_u=(
                    source_support
                ),
                support_residual_u=(
                    predicted_support
                    - source_support
                ),
                source_line_fit_rms_u=float(
                    source[
                        "line_fit_rms_u"
                    ]
                ),
                source_pass_angle_rms_degrees=float(
                    source[
                        "pass_angle_rms_degrees"
                    ]
                ),
                source_pass_support_rms_u=float(
                    source[
                        "pass_support_rms_u"
                    ]
                ),
            )
        )

    source_vertex_rows = _read_csv(
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure12_wall_vertices"
        ]
    )

    if len(
        source_vertex_rows
    ) != 12:
        raise ValueError(
            "Expected twelve Figure 12 "
            "source wall vertices."
        )

    vertex_residuals: list[
        Figure12VertexResidual
    ] = []

    for row in source_vertex_rows:
        wall_a = row["wall_a"]
        wall_b = row["wall_b"]

        if (
            wall_a
            not in predicted_lines
            or wall_b
            not in predicted_lines
        ):
            raise ValueError(
                "Source wall vertex references "
                "an unknown semantic wall ID."
            )

        predicted_x, predicted_y = (
            _intersect_wall_lines(
                predicted_lines[
                    wall_a
                ],
                predicted_lines[
                    wall_b
                ],
            )
        )

        source_x = float(
            row["x_u"]
        )

        source_y = float(
            row["y_u"]
        )

        point_residual = hypot(
            predicted_x
            - source_x,
            predicted_y
            - source_y,
        )

        vertex_residuals.append(
            Figure12VertexResidual(
                vertex_id=(
                    row[
                        "vertex_id"
                    ]
                ),
                wall_a=wall_a,
                wall_b=wall_b,
                predicted_x_u=(
                    predicted_x
                ),
                predicted_y_u=(
                    predicted_y
                ),
                source_x_u=source_x,
                source_y_u=source_y,
                point_residual_u=(
                    point_residual
                ),
            )
        )

    predicted_side_lengths = {
        line.name: length
        for line, length in zip(
            wall.lines,
            wall.side_lengths,
            strict=True,
        )
    }

    source_side_rows = _read_csv(
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure12_wall_side_lengths"
        ]
    )

    source_side_lengths = {
        row["wall_id"]: float(
            row["length_u"]
        )
        for row in source_side_rows
    }

    if (
        set(source_side_lengths)
        != expected_wall_ids
    ):
        raise ValueError(
            "Figure 12 source side-length IDs "
            "do not match the fixed prediction IDs."
        )

    side_residuals = tuple(
        Figure12SideResidual(
            wall_id=wall_id,
            predicted_length_u=(
                predicted_side_lengths[
                    wall_id
                ]
            ),
            source_length_u=(
                source_side_lengths[
                    wall_id
                ]
            ),
            length_residual_u=(
                predicted_side_lengths[
                    wall_id
                ]
                - source_side_lengths[
                    wall_id
                ]
            ),
        )
        for wall_id in (
            POLAR_PIVOT_WALL_IDS
        )
    )

    summary_path = (
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure12_source_summary"
        ]
    )

    source_summary = json.loads(
        summary_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        source_summary[
            "selected_registration"
        ]
        != "centroid_affine"
    ):
        raise ValueError(
            "Figure 12 validation requires "
            "the promoted centroid-affine "
            "source geometry."
        )

    source_perimeter = float(
        source_summary[
            "wall_perimeter_u"
        ]
    )

    source_area = float(
        source_summary[
            "wall_area_u2"
        ]
    )

    predicted_perimeter = (
        wall.perimeter
    )

    predicted_area = (
        wall.area
    )

    perimeter_residual = (
        predicted_perimeter
        - source_perimeter
    )

    area_residual = (
        predicted_area
        - source_area
    )

    line_angles = tuple(
        row.angle_residual_degrees
        for row in line_residuals
    )

    line_supports = tuple(
        row.support_residual_u
        for row in line_residuals
    )

    vertex_points = tuple(
        row.point_residual_u
        for row in vertex_residuals
    )

    side_lengths = tuple(
        row.length_residual_u
        for row in side_residuals
    )

    return Figure12ForwardValidation(
        line_residuals=tuple(
            line_residuals
        ),
        vertex_residuals=tuple(
            vertex_residuals
        ),
        side_residuals=side_residuals,

        angle_rms_degrees=_rms(
            line_angles
        ),
        angle_maximum_degrees=max(
            line_angles
        ),
        support_rms_u=_rms(
            line_supports
        ),
        support_maximum_u=max(
            abs(value)
            for value in line_supports
        ),

        vertex_rms_u=_rms(
            vertex_points
        ),
        vertex_maximum_u=max(
            vertex_points
        ),
        side_length_rms_u=_rms(
            side_lengths
        ),
        side_length_maximum_u=max(
            abs(value)
            for value in side_lengths
        ),

        predicted_perimeter_u=(
            predicted_perimeter
        ),
        source_perimeter_u=(
            source_perimeter
        ),
        perimeter_residual_u=(
            perimeter_residual
        ),
        perimeter_relative_residual=(
            perimeter_residual
            / source_perimeter
        ),

        predicted_area_u2=(
            predicted_area
        ),
        source_area_u2=(
            source_area
        ),
        area_residual_u2=(
            area_residual
        ),
        area_relative_residual=(
            area_residual
            / source_area
        ),

        wall_side_count=len(
            wall.lines
        ),
        polar_side_count=sum(
            line.name
            in FIGURE12_POLAR_WALL_IDS
            for line in wall.lines
        ),
        oblique_side_count=sum(
            line.name
            not in FIGURE12_POLAR_WALL_IDS
            for line in wall.lines
        ),
    )


def _figure14_source_rows(
    repo_root: Path,
) -> tuple[
    dict[str, str],
    ...,
]:
    rows = _read_csv(
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure14_registered_landmarks"
        ]
    )

    star_rows = [
        row
        for row in rows
        if (
            row["category"]
            == "star_endpoint"
        )
    ]

    star_rows.sort(
        key=lambda row: int(
            row[
                "sequence_index"
            ]
        )
    )

    observed_order = tuple(
        row["landmark_id"]
        for row in star_rows
    )

    if (
        observed_order
        != FIGURE14_ENDPOINT_ORDER
    ):
        raise ValueError(
            "Promoted Figure 14 endpoints "
            "do not match the preregistered "
            "semantic order."
        )

    return tuple(
        star_rows
    )


def _figure14_candidate_validation(
    candidate: HeptagramGeometry,
    source_rows: tuple[
        dict[str, str],
        ...,
    ],
    registration_loo_u: float,
) -> Figure14CandidateValidation:
    if len(
        candidate.vertices
    ) != 7:
        raise ValueError(
            "Figure 14 validation candidate "
            "must have seven vertices."
        )

    if len(
        source_rows
    ) != 7:
        raise ValueError(
            "Figure 14 validation target "
            "must have seven source endpoints."
        )

    residuals: list[
        Figure14VertexResidual
    ] = []

    for index, (
        vertex,
        row,
    ) in enumerate(
        zip(
            candidate.vertices,
            source_rows,
            strict=True,
        )
    ):
        landmark_id = (
            row[
                "landmark_id"
            ]
        )

        if (
            landmark_id
            in FIGURE14_SOURCE_SUPPORTED_ENDPOINTS
        ):
            evidence_class = (
                "source_text_and_plate"
            )

        elif (
            landmark_id
            in FIGURE14_INFERRED_ENDPOINTS
        ):
            evidence_class = (
                "plate_inference"
            )

        else:
            raise ValueError(
                "Figure 14 endpoint has no "
                "fixed evidence classification: "
                f"{landmark_id}"
            )

        source_x = float(
            row[
                "normalized_x"
            ]
        )

        source_y = float(
            row[
                "normalized_y"
            ]
        )

        point_residual = hypot(
            vertex.x
            - source_x,
            vertex.y
            - source_y,
        )

        predicted_angle = (
            _point_angle_degrees(
                vertex.x,
                vertex.y,
            )
        )

        source_angle = (
            _point_angle_degrees(
                source_x,
                source_y,
            )
        )

        predicted_radius = hypot(
            vertex.x,
            vertex.y,
        )

        source_radius = hypot(
            source_x,
            source_y,
        )

        residuals.append(
            Figure14VertexResidual(
                sequence_index=index,
                landmark_id=(
                    landmark_id
                ),
                evidence_class=(
                    evidence_class
                ),

                predicted_x_u=(
                    vertex.x
                ),
                predicted_y_u=(
                    vertex.y
                ),
                source_x_u=(
                    source_x
                ),
                source_y_u=(
                    source_y
                ),

                point_residual_u=(
                    point_residual
                ),
                angular_residual_degrees=(
                    _angular_delta_degrees(
                        predicted_angle,
                        source_angle,
                    )
                ),
                radial_residual_u=(
                    source_radius
                    - predicted_radius
                ),
            )
        )

    point_values = tuple(
        row.point_residual_u
        for row in residuals
    )

    angle_values = tuple(
        row.angular_residual_degrees
        for row in residuals
    )

    radial_values = tuple(
        row.radial_residual_u
        for row in residuals
    )

    source_supported = tuple(
        row.point_residual_u
        for row in residuals
        if (
            row.evidence_class
            == "source_text_and_plate"
        )
    )

    inferred = tuple(
        row.point_residual_u
        for row in residuals
        if (
            row.evidence_class
            == "plate_inference"
        )
    )

    point_rms = _rms(
        point_values
    )

    return Figure14CandidateValidation(
        candidate_name=(
            candidate.name
        ),
        vertex_residuals=tuple(
            residuals
        ),

        point_rms_u=point_rms,
        point_maximum_u=max(
            point_values
        ),
        angular_rms_degrees=_rms(
            angle_values
        ),
        angular_maximum_degrees=max(
            angle_values
        ),
        radial_rms_u=_rms(
            radial_values
        ),
        radial_maximum_u=max(
            abs(value)
            for value in radial_values
        ),

        source_supported_point_rms_u=(
            _rms(
                source_supported
            )
        ),
        source_supported_point_maximum_u=(
            max(
                source_supported
            )
        ),
        inferred_point_rms_u=(
            _rms(
                inferred
            )
        ),
        inferred_point_maximum_u=(
            max(
                inferred
            )
        ),

        registration_loo_equivalent_u=(
            registration_loo_u
        ),
        point_rms_fraction_of_registration_loo=(
            point_rms
            / registration_loo_u
        ),
    )


def _figure14_validation(
    composite: MichellComposite,
    repo_root: Path,
) -> Figure14ForwardValidation:
    source_rows = (
        _figure14_source_rows(
            repo_root
        )
    )

    endpoint_json_path = (
        repo_root
        / VALIDATION_INPUT_PATHS[
            "figure14_endpoint_geometry_json"
        ]
    )

    endpoint_payload = json.loads(
        endpoint_json_path.read_text(
            encoding="utf-8"
        )
    )

    if (
        endpoint_payload[
            "endpoint_count"
        ]
        != 7
    ):
        raise ValueError(
            "Promoted Figure 14 endpoint "
            "geometry must contain seven endpoints."
        )

    if tuple(
        endpoint_payload[
            "endpoint_order"
        ]
    ) != FIGURE14_ENDPOINT_ORDER:
        raise ValueError(
            "Figure 14 endpoint JSON order "
            "does not match the fixed semantic order."
        )

    registration_loo_u = float(
        endpoint_payload[
            "registration_scale"
        ][
            "loo_rms_equivalent_normalized"
        ]
    )

    if (
        registration_loo_u
        <= 0.0
    ):
        raise ValueError(
            "Figure 14 registration LOO "
            "scale must be positive."
        )

    scaffold_candidate = (
        composite
        .scaffold_heptagram_candidate
    )

    canonical_regular = (
        build_regular_heptagram(
            composite.core,
            family=(
                scaffold_candidate.family
            ),
        )
    )

    scaffold_validation = (
        _figure14_candidate_validation(
            scaffold_candidate,
            source_rows,
            registration_loo_u,
        )
    )

    canonical_validation = (
        _figure14_candidate_validation(
            canonical_regular,
            source_rows,
            registration_loo_u,
        )
    )

    return Figure14ForwardValidation(
        scaffold_candidate=(
            scaffold_validation
        ),
        canonical_regular=(
            canonical_validation
        ),

        scaffold_minus_canonical_point_rms_u=(
            scaffold_validation.point_rms_u
            - canonical_validation.point_rms_u
        ),
        scaffold_minus_canonical_point_maximum_u=(
            scaffold_validation.point_maximum_u
            - canonical_validation.point_maximum_u
        ),

        endpoint_count=len(
            source_rows
        ),
        source_supported_endpoint_count=sum(
            row[
                "landmark_id"
            ]
            in FIGURE14_SOURCE_SUPPORTED_ENDPOINTS
            for row in source_rows
        ),
        inferred_endpoint_count=sum(
            row[
                "landmark_id"
            ]
            in FIGURE14_INFERRED_ENDPOINTS
            for row in source_rows
        ),
    )


def analyze_forward_validation(
    repo_root: str | Path = ".",
) -> MichellForwardValidationReport:
    """Run the preregistered zero-refit forward validation."""

    root = Path(
        repo_root
    )

    input_hashes = (
        verify_validation_input_hashes(
            root
        )
    )

    composite = (
        build_michell_composite(
            unit=1.0
        )
    )

    figure12 = (
        _figure12_validation(
            composite,
            root,
        )
    )

    figure14 = (
        _figure14_validation(
            composite,
            root,
        )
    )

    return MichellForwardValidationReport(
        analysis_id=(
            "njg-michell-v0.4-"
            "frozen-forward-validation"
        ),
        schema_version=1,
        frozen_predictor_commit=(
            FROZEN_PREDICTOR_COMMIT
        ),
        validation_mode=(
            "frozen_forward_no_refitting"
        ),
        input_sha256=(
            input_hashes
        ),
        figure12=figure12,
        figure14=figure14,
    )


def _write_dataclass_csv(
    path: Path,
    rows: Sequence[object],
) -> None:
    if not rows:
        raise ValueError(
            "Cannot write an empty validation CSV."
        )

    records = [
        asdict(row)
        for row in rows
    ]

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(
                records[0]
            ),
            lineterminator="\n",
        )

        writer.writeheader()
        writer.writerows(
            records
        )


def write_forward_validation(
    report: MichellForwardValidationReport,
    output_dir: str | Path,
) -> tuple[Path, ...]:
    """Write deterministic machine-readable and Markdown outputs."""

    output = Path(
        output_dir
    )

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary_path = (
        output
        / "forward_validation_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            asdict(report),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    figure12_line_path = (
        output
        / "figure12_wall_line_residuals.csv"
    )

    _write_dataclass_csv(
        figure12_line_path,
        report.figure12.line_residuals,
    )

    figure12_vertex_path = (
        output
        / "figure12_wall_vertex_residuals.csv"
    )

    _write_dataclass_csv(
        figure12_vertex_path,
        report.figure12.vertex_residuals,
    )

    figure12_side_path = (
        output
        / "figure12_wall_side_residuals.csv"
    )

    _write_dataclass_csv(
        figure12_side_path,
        report.figure12.side_residuals,
    )

    figure14_scaffold_path = (
        output
        / "figure14_scaffold_vertex_residuals.csv"
    )

    _write_dataclass_csv(
        figure14_scaffold_path,
        (
            report
            .figure14
            .scaffold_candidate
            .vertex_residuals
        ),
    )

    figure14_canonical_path = (
        output
        / "figure14_canonical_vertex_residuals.csv"
    )

    _write_dataclass_csv(
        figure14_canonical_path,
        (
            report
            .figure14
            .canonical_regular
            .vertex_residuals
        ),
    )

    markdown_path = (
        output
        / "forward_validation_report.md"
    )

    figure12 = (
        report.figure12
    )

    scaffold = (
        report
        .figure14
        .scaffold_candidate
    )

    canonical = (
        report
        .figure14
        .canonical_regular
    )

    markdown = [
        "# NJG_MICHELL frozen forward validation",
        "",
        "## Status",
        "",
        (
            "- Validation mode: "
            "`frozen_forward_no_refitting`"
        ),
        (
            "- Frozen predictor commit: "
            f"`{report.frozen_predictor_commit}`"
        ),
        "- Caller-supplied geometric scale: `unit = 1.0`",
        "- Post-freeze geometric refitting: none",
        "- Post-hoc pass/fail threshold: none",
        "",
        "## Figure 12",
        "",
        "### Primary wall-line residuals",
        "",
        (
            f"- Angular RMS: "
            f"{figure12.angle_rms_degrees:.9f}°"
        ),
        (
            f"- Angular maximum: "
            f"{figure12.angle_maximum_degrees:.9f}°"
        ),
        (
            f"- Support RMS: "
            f"{figure12.support_rms_u:.9f} u"
        ),
        (
            f"- Support maximum: "
            f"{figure12.support_maximum_u:.9f} u"
        ),
        "",
        "### Polygon diagnostics",
        "",
        (
            f"- Vertex RMS: "
            f"{figure12.vertex_rms_u:.9f} u"
        ),
        (
            f"- Vertex maximum: "
            f"{figure12.vertex_maximum_u:.9f} u"
        ),
        (
            f"- Side-length RMS: "
            f"{figure12.side_length_rms_u:.9f} u"
        ),
        (
            f"- Side-length maximum: "
            f"{figure12.side_length_maximum_u:.9f} u"
        ),
        (
            f"- Predicted perimeter: "
            f"{figure12.predicted_perimeter_u:.9f} u"
        ),
        (
            f"- Source perimeter: "
            f"{figure12.source_perimeter_u:.9f} u"
        ),
        (
            f"- Perimeter residual: "
            f"{figure12.perimeter_residual_u:+.9f} u "
            f"({100.0 * figure12.perimeter_relative_residual:+.6f}%)"
        ),
        (
            f"- Predicted area: "
            f"{figure12.predicted_area_u2:.9f} u²"
        ),
        (
            f"- Source area: "
            f"{figure12.source_area_u2:.9f} u²"
        ),
        (
            f"- Area residual: "
            f"{figure12.area_residual_u2:+.9f} u² "
            f"({100.0 * figure12.area_relative_residual:+.6f}%)"
        ),
        "",
        "## Figure 14",
        "",
        "| Metric | Scaffold candidate | Canonical regular |",
        "|---|---:|---:|",
        (
            "| Point RMS (u) | "
            f"{scaffold.point_rms_u:.9f} | "
            f"{canonical.point_rms_u:.9f} |"
        ),
        (
            "| Point maximum (u) | "
            f"{scaffold.point_maximum_u:.9f} | "
            f"{canonical.point_maximum_u:.9f} |"
        ),
        (
            "| Angular RMS (deg) | "
            f"{scaffold.angular_rms_degrees:.9f} | "
            f"{canonical.angular_rms_degrees:.9f} |"
        ),
        (
            "| Angular maximum (deg) | "
            f"{scaffold.angular_maximum_degrees:.9f} | "
            f"{canonical.angular_maximum_degrees:.9f} |"
        ),
        (
            "| Radial RMS (u) | "
            f"{scaffold.radial_rms_u:.9f} | "
            f"{canonical.radial_rms_u:.9f} |"
        ),
        (
            "| RMS / registration LOO | "
            f"{scaffold.point_rms_fraction_of_registration_loo:.9f} | "
            f"{canonical.point_rms_fraction_of_registration_loo:.9f} |"
        ),
        "",
        "### Evidence-separated endpoint residuals",
        "",
        (
            "- Source-supported endpoints, scaffold RMS: "
            f"{scaffold.source_supported_point_rms_u:.9f} u"
        ),
        (
            "- Source-supported endpoints, canonical RMS: "
            f"{canonical.source_supported_point_rms_u:.9f} u"
        ),
        (
            "- Plate-inferred endpoints, scaffold RMS: "
            f"{scaffold.inferred_point_rms_u:.9f} u"
        ),
        (
            "- Plate-inferred endpoints, canonical RMS: "
            f"{canonical.inferred_point_rms_u:.9f} u"
        ),
        "",
        "### Fixed-comparator difference",
        "",
        (
            "- Scaffold minus canonical point RMS: "
            f"{report.figure14.scaffold_minus_canonical_point_rms_u:+.9f} u"
        ),
        (
            "- Scaffold minus canonical point maximum: "
            f"{report.figure14.scaffold_minus_canonical_point_maximum_u:+.9f} u"
        ),
        "",
        "## Interpretation boundary",
        "",
        (
            "These are descriptive frozen-predictor residuals. "
            "No parameter was fitted during validation."
        ),
        (
            "Figure 12 and Figure 14 were involved in earlier model-development "
            "stages, so this analysis is not represented as a statistically "
            "independent hold-out experiment."
        ),
        (
            "The Figure 14 `{7/2}` topology was established earlier by an "
            "independent printed-line tracing audit and is not counted here "
            "as a new positional prediction."
        ),
        "",
    ]

    markdown_path.write_text(
        "\n".join(
            markdown
        ),
        encoding="utf-8",
    )

    return (
        summary_path,
        figure12_line_path,
        figure12_vertex_path,
        figure12_side_path,
        figure14_scaffold_path,
        figure14_canonical_path,
        markdown_path,
    )
