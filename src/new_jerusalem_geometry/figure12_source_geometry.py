"""Source-derived normalized geometry for Michell's Figure 12.

This module applies the selected Figure 12 affine plate registration to the
raw source observations and derives geometry in normalized project units.

Evidence boundary
-----------------

This stage derives:

- twelve source-observed Moon circles;
- twelve source-observed outer-wall lines;
- twelve wall vertices derived from adjacent observed wall lines;
- source-derived wall side lengths, perimeter, and area.

It does NOT compare those observations with:

- NJG_INC;
- NJG_MICHELL_28;
- NJG_28;
- NJG_SVG;
- the radial-support wall hypothesis.

Primary geometry uses the centroid affine registration.

Measurement repeatability is estimated independently by applying each
pass-specific affine inverse to the observations from that pass before fitting
the corresponding circle or line.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from math import acos, atan2, degrees, hypot, sqrt
from pathlib import Path
from typing import Sequence

import numpy as np

from .figure12_digitisation import (
    Figure12DigitisedObservation,
    MOON_OBJECT_IDS,
    WALL_OBJECT_IDS,
    read_figure12_digitisation_pass_csv,
)
from .figure12_digitisation_qc import (
    fit_circle,
    fit_line,
)
from .figure12_registration import (
    analyze_figure12_registration,
)
from .figure14_registration import (
    RegistrationFit,
    RegistrationModel,
    apply_registration_matrix,
    pixel_to_cartesian,
)


MOON_PASS_FIELDS = (
    "pass_id",
    "moon_id",
    "centre_x_u",
    "centre_y_u",
    "radius_u",
    "radial_fit_rms_u",
)

MOON_FIELDS = (
    "moon_id",
    "centre_x_u",
    "centre_y_u",
    "radius_u",
    "radial_fit_rms_u",
    "centre_radius_from_origin_u",
    "centre_angle_degrees",
    "pass_centre_x_mean_u",
    "pass_centre_y_mean_u",
    "pass_centre_rms_u",
    "pass_centre_maximum_pairwise_u",
    "pass_radius_mean_u",
    "pass_radius_std_u",
    "pass_maximum_radial_fit_rms_u",
)

WALL_PASS_FIELDS = (
    "pass_id",
    "wall_id",
    "normal_x",
    "normal_y",
    "support_h_u",
    "normal_angle_degrees",
    "line_fit_rms_u",
)

WALL_FIELDS = (
    "wall_id",
    "normal_x",
    "normal_y",
    "support_h_u",
    "normal_angle_degrees",
    "line_fit_rms_u",
    "pass_angle_rms_degrees",
    "pass_maximum_pairwise_angle_degrees",
    "pass_support_mean_u",
    "pass_support_rms_u",
    "pass_maximum_pairwise_support_u",
    "pass_maximum_line_fit_rms_u",
)

VERTEX_FIELDS = (
    "vertex_index",
    "vertex_id",
    "wall_a",
    "wall_b",
    "x_u",
    "y_u",
    "radius_from_origin_u",
    "angle_degrees",
)

SIDE_FIELDS = (
    "wall_id",
    "length_u",
)


@dataclass(frozen=True, slots=True)
class MoonPassGeometry:
    pass_id: str
    moon_id: str
    centre_x_u: float
    centre_y_u: float
    radius_u: float
    radial_fit_rms_u: float


@dataclass(frozen=True, slots=True)
class MoonGeometry:
    moon_id: str
    centre_x_u: float
    centre_y_u: float
    radius_u: float
    radial_fit_rms_u: float
    centre_radius_from_origin_u: float
    centre_angle_degrees: float
    pass_centre_x_mean_u: float
    pass_centre_y_mean_u: float
    pass_centre_rms_u: float
    pass_centre_maximum_pairwise_u: float
    pass_radius_mean_u: float
    pass_radius_std_u: float
    pass_maximum_radial_fit_rms_u: float


@dataclass(frozen=True, slots=True)
class WallPassGeometry:
    pass_id: str
    wall_id: str
    normal_x: float
    normal_y: float
    support_h_u: float
    normal_angle_degrees: float
    line_fit_rms_u: float


@dataclass(frozen=True, slots=True)
class WallGeometry:
    wall_id: str
    normal_x: float
    normal_y: float
    support_h_u: float
    normal_angle_degrees: float
    line_fit_rms_u: float
    pass_angle_rms_degrees: float
    pass_maximum_pairwise_angle_degrees: float
    pass_support_mean_u: float
    pass_support_rms_u: float
    pass_maximum_pairwise_support_u: float
    pass_maximum_line_fit_rms_u: float


@dataclass(frozen=True, slots=True)
class WallVertex:
    vertex_index: int
    vertex_id: str
    wall_a: str
    wall_b: str
    x_u: float
    y_u: float
    radius_from_origin_u: float
    angle_degrees: float


@dataclass(frozen=True, slots=True)
class WallSide:
    wall_id: str
    length_u: float


@dataclass(frozen=True, slots=True)
class Figure12SourceGeometryReport:
    selected_fit: RegistrationFit
    forward_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    inverse_matrix: tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]
    pass_inverse_matrices: tuple[
        tuple[
            str,
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
            ],
        ],
        ...,
    ]
    source_image_sha256: str
    image_width_pixels: int
    image_height_pixels: int
    moon_pass_fits: tuple[MoonPassGeometry, ...]
    moons: tuple[MoonGeometry, ...]
    wall_pass_fits: tuple[WallPassGeometry, ...]
    walls: tuple[WallGeometry, ...]
    vertices: tuple[WallVertex, ...]
    sides: tuple[WallSide, ...]
    wall_perimeter_u: float
    wall_area_u2: float
    pixels_per_unit_maximum: float
    pixels_per_unit_minimum: float
    mean_pixels_per_unit: float


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


def _angle_degrees(
    x: float,
    y: float,
) -> float:
    return (
        degrees(
            atan2(y, x)
        )
        % 360.0
    )


def _rms(
    values: np.ndarray,
) -> float:
    if len(values) == 0:
        return 0.0

    return sqrt(
        float(
            np.mean(
                values * values
            )
        )
    )


def _maximum_pairwise_distance(
    points: np.ndarray,
) -> float:
    maximum = 0.0

    for index in range(len(points)):
        for other in range(
            index + 1,
            len(points),
        ):
            maximum = max(
                maximum,
                float(
                    np.linalg.norm(
                        points[index]
                        - points[other]
                    )
                ),
            )

    return maximum


def _angle_between_normals_degrees(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    dot = float(
        np.dot(
            first,
            second,
        )
    )

    dot = min(
        1.0,
        max(
            -1.0,
            dot,
        ),
    )

    return degrees(
        acos(dot)
    )


def _maximum_pairwise_scalar(
    values: np.ndarray,
) -> float:
    maximum = 0.0

    for index in range(len(values)):
        for other in range(
            index + 1,
            len(values),
        ):
            maximum = max(
                maximum,
                abs(
                    float(
                        values[index]
                        - values[other]
                    )
                ),
            )

    return maximum


def _load_passes(
    pass_paths: Sequence[str | Path],
) -> tuple[
    tuple[
        Figure12DigitisedObservation,
        ...,
    ],
    ...,
]:
    if len(pass_paths) != 3:
        raise ValueError(
            "Exactly three Figure 12 raw passes are required."
        )

    passes = tuple(
        read_figure12_digitisation_pass_csv(
            path,
            require_complete=True,
        )
        for path in pass_paths
    )

    if any(
        not observations
        for observations in passes
    ):
        raise ValueError(
            "Figure 12 raw pass is empty."
        )

    pass_ids = tuple(
        observations[0].pass_id
        for observations in passes
    )

    if len(set(pass_ids)) != 3:
        raise ValueError(
            "Figure 12 raw passes must have distinct pass IDs."
        )

    source_hashes = {
        observations[0].source_image_sha256
        for observations in passes
    }

    if len(source_hashes) != 1:
        raise ValueError(
            "Figure 12 raw passes use different source images."
        )

    dimensions = {
        (
            observations[0].image_width_pixels,
            observations[0].image_height_pixels,
        )
        for observations in passes
    }

    if len(dimensions) != 1:
        raise ValueError(
            "Figure 12 raw passes use different image dimensions."
        )

    identities = tuple(
        tuple(
            (
                item.definition.sequence_index,
                item.definition.observation_id,
                item.definition.category,
                item.definition.object_id,
                item.definition.sample_index,
            )
            for item in observations
        )
        for observations in passes
    )

    if any(
        identity != identities[0]
        for identity in identities[1:]
    ):
        raise ValueError(
            "Figure 12 observation ordering differs between passes."
        )

    return passes


def _transform_observations(
    observations: Sequence[
        Figure12DigitisedObservation
    ],
    inverse_matrix: np.ndarray,
) -> np.ndarray:
    if not observations:
        raise ValueError(
            "At least one source observation is required."
        )

    image_height = (
        observations[0].image_height_pixels
    )

    cartesian = np.asarray(
        [
            pixel_to_cartesian(
                item.pixel_x,
                item.pixel_y,
                image_height,
            )
            for item in observations
        ],
        dtype=float,
    )

    return apply_registration_matrix(
        inverse_matrix,
        cartesian,
    )


def _category_object_rows(
    observations: Sequence[
        Figure12DigitisedObservation
    ],
    *,
    category: str,
    object_id: str,
) -> tuple[
    Figure12DigitisedObservation,
    ...,
]:
    rows = tuple(
        item
        for item in observations
        if (
            item.definition.category
            == category
            and item.definition.object_id
            == object_id
        )
    )

    return rows


def _fit_outward_line(
    points: np.ndarray,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    """Fit n.x = h and orient n away from the diagram origin."""

    (
        normal_x,
        normal_y,
        offset,
        centroid_x,
        centroid_y,
        fit_rms,
    ) = fit_line(
        points
    )

    normal = np.asarray(
        (
            normal_x,
            normal_y,
        ),
        dtype=float,
    )

    centroid = np.asarray(
        (
            centroid_x,
            centroid_y,
        ),
        dtype=float,
    )

    if (
        float(
            np.dot(
                normal,
                centroid,
            )
        )
        < 0.0
    ):
        normal *= -1.0
        offset *= -1.0

    support_h = -float(
        offset
    )

    if support_h <= 0.0:
        raise ValueError(
            "Observed wall line does not place the origin "
            "on its interior side."
        )

    return (
        float(normal[0]),
        float(normal[1]),
        support_h,
        float(fit_rms),
    )


def _intersect_support_lines(
    first: WallGeometry,
    second: WallGeometry,
) -> tuple[float, float]:
    matrix = np.asarray(
        (
            (
                first.normal_x,
                first.normal_y,
            ),
            (
                second.normal_x,
                second.normal_y,
            ),
        ),
        dtype=float,
    )

    determinant = float(
        np.linalg.det(
            matrix
        )
    )

    if abs(determinant) < 1.0e-10:
        raise ValueError(
            "Adjacent observed wall lines are nearly parallel: "
            f"{first.wall_id}, {second.wall_id}"
        )

    rhs = np.asarray(
        (
            first.support_h_u,
            second.support_h_u,
        ),
        dtype=float,
    )

    point = np.linalg.solve(
        matrix,
        rhs,
    )

    return (
        float(point[0]),
        float(point[1]),
    )


def derive_figure12_source_geometry(
    pass_paths: Sequence[str | Path],
) -> Figure12SourceGeometryReport:
    """Derive normalized Figure 12 Moon and wall geometry."""

    passes = _load_passes(
        pass_paths
    )

    registration = (
        analyze_figure12_registration(
            pass_paths
        )
    )

    selected_fit = next(
        fit
        for fit in registration.fits
        if (
            fit.dataset_id == "centroid"
            and fit.model
            is RegistrationModel.AFFINE
        )
    )

    pass_affine_fits = {
        fit.dataset_id: fit
        for fit in registration.fits
        if (
            fit.dataset_id != "centroid"
            and fit.model
            is RegistrationModel.AFFINE
        )
    }

    expected_pass_ids = {
        observations[0].pass_id
        for observations in passes
    }

    if (
        set(pass_affine_fits)
        != expected_pass_ids
    ):
        raise AssertionError(
            "A pass-specific affine fit is missing."
        )

    forward_matrix = np.asarray(
        selected_fit.matrix,
        dtype=float,
    )

    inverse_matrix = np.linalg.inv(
        forward_matrix
    )

    pass_inverse_arrays = {
        pass_id: np.linalg.inv(
            np.asarray(
                fit.matrix,
                dtype=float,
            )
        )
        for pass_id, fit
        in pass_affine_fits.items()
    }

    linear = forward_matrix[
        :2,
        :2,
    ]

    singular_values = np.linalg.svd(
        linear,
        compute_uv=False,
    )

    singular_max = float(
        max(
            singular_values
        )
    )

    singular_min = float(
        min(
            singular_values
        )
    )

    if singular_min <= 0.0:
        raise ValueError(
            "Selected Figure 12 affine transformation is singular."
        )

    mean_pixels_per_unit = (
        0.5
        * (
            singular_max
            + singular_min
        )
    )

    reference = passes[0]

    # ==========================================================
    # Moon circles
    # ==========================================================

    moon_pass_fits: list[
        MoonPassGeometry
    ] = []

    for observations in passes:
        pass_id = (
            observations[0].pass_id
        )

        inverse = (
            pass_inverse_arrays[
                pass_id
            ]
        )

        for moon_id in MOON_OBJECT_IDS:
            rows = _category_object_rows(
                observations,
                category="moon_circumference",
                object_id=moon_id,
            )

            if len(rows) != 6:
                raise ValueError(
                    f"{moon_id} does not contain six "
                    f"samples in {pass_id}."
                )

            points = (
                _transform_observations(
                    rows,
                    inverse,
                )
            )

            (
                centre_x,
                centre_y,
                radius,
                radial_rms,
            ) = fit_circle(
                points
            )

            moon_pass_fits.append(
                MoonPassGeometry(
                    pass_id=pass_id,
                    moon_id=moon_id,
                    centre_x_u=centre_x,
                    centre_y_u=centre_y,
                    radius_u=radius,
                    radial_fit_rms_u=(
                        radial_rms
                    ),
                )
            )

    moons: list[
        MoonGeometry
    ] = []

    for moon_id in MOON_OBJECT_IDS:
        primary_rows: list[
            Figure12DigitisedObservation
        ] = []

        for observations in passes:
            primary_rows.extend(
                _category_object_rows(
                    observations,
                    category="moon_circumference",
                    object_id=moon_id,
                )
            )

        if len(primary_rows) != 18:
            raise ValueError(
                f"{moon_id} does not contain eighteen "
                "primary circumference observations."
            )

        primary_points = (
            _transform_observations(
                primary_rows,
                inverse_matrix,
            )
        )

        (
            centre_x,
            centre_y,
            radius,
            radial_rms,
        ) = fit_circle(
            primary_points
        )

        pass_fits = tuple(
            row
            for row in moon_pass_fits
            if row.moon_id == moon_id
        )

        if len(pass_fits) != 3:
            raise AssertionError(
                f"{moon_id} lacks three pass-specific fits."
            )

        pass_centres = np.asarray(
            [
                (
                    row.centre_x_u,
                    row.centre_y_u,
                )
                for row in pass_fits
            ],
            dtype=float,
        )

        pass_centre_mean = np.mean(
            pass_centres,
            axis=0,
        )

        centre_deviations = np.linalg.norm(
            pass_centres
            - pass_centre_mean,
            axis=1,
        )

        pass_radii = np.asarray(
            [
                row.radius_u
                for row in pass_fits
            ],
            dtype=float,
        )

        moons.append(
            MoonGeometry(
                moon_id=moon_id,
                centre_x_u=centre_x,
                centre_y_u=centre_y,
                radius_u=radius,
                radial_fit_rms_u=radial_rms,
                centre_radius_from_origin_u=hypot(
                    centre_x,
                    centre_y,
                ),
                centre_angle_degrees=_angle_degrees(
                    centre_x,
                    centre_y,
                ),
                pass_centre_x_mean_u=float(
                    pass_centre_mean[0]
                ),
                pass_centre_y_mean_u=float(
                    pass_centre_mean[1]
                ),
                pass_centre_rms_u=_rms(
                    centre_deviations
                ),
                pass_centre_maximum_pairwise_u=(
                    _maximum_pairwise_distance(
                        pass_centres
                    )
                ),
                pass_radius_mean_u=float(
                    np.mean(
                        pass_radii
                    )
                ),
                pass_radius_std_u=float(
                    np.std(
                        pass_radii
                    )
                ),
                pass_maximum_radial_fit_rms_u=max(
                    row.radial_fit_rms_u
                    for row in pass_fits
                ),
            )
        )

    # ==========================================================
    # Wall lines
    # ==========================================================

    wall_pass_fits: list[
        WallPassGeometry
    ] = []

    for observations in passes:
        pass_id = (
            observations[0].pass_id
        )

        inverse = (
            pass_inverse_arrays[
                pass_id
            ]
        )

        for wall_id in WALL_OBJECT_IDS:
            rows = _category_object_rows(
                observations,
                category="wall_line",
                object_id=wall_id,
            )

            if len(rows) != 3:
                raise ValueError(
                    f"{wall_id} does not contain three "
                    f"samples in {pass_id}."
                )

            points = (
                _transform_observations(
                    rows,
                    inverse,
                )
            )

            (
                normal_x,
                normal_y,
                support_h,
                fit_rms,
            ) = _fit_outward_line(
                points
            )

            wall_pass_fits.append(
                WallPassGeometry(
                    pass_id=pass_id,
                    wall_id=wall_id,
                    normal_x=normal_x,
                    normal_y=normal_y,
                    support_h_u=support_h,
                    normal_angle_degrees=(
                        _angle_degrees(
                            normal_x,
                            normal_y,
                        )
                    ),
                    line_fit_rms_u=fit_rms,
                )
            )

    walls: list[
        WallGeometry
    ] = []

    for wall_id in WALL_OBJECT_IDS:
        primary_rows: list[
            Figure12DigitisedObservation
        ] = []

        for observations in passes:
            primary_rows.extend(
                _category_object_rows(
                    observations,
                    category="wall_line",
                    object_id=wall_id,
                )
            )

        if len(primary_rows) != 9:
            raise ValueError(
                f"{wall_id} does not contain nine "
                "primary line observations."
            )

        primary_points = (
            _transform_observations(
                primary_rows,
                inverse_matrix,
            )
        )

        (
            normal_x,
            normal_y,
            support_h,
            fit_rms,
        ) = _fit_outward_line(
            primary_points
        )

        pass_fits = tuple(
            row
            for row in wall_pass_fits
            if row.wall_id == wall_id
        )

        if len(pass_fits) != 3:
            raise AssertionError(
                f"{wall_id} lacks three pass-specific fits."
            )

        pass_normals = np.asarray(
            [
                (
                    row.normal_x,
                    row.normal_y,
                )
                for row in pass_fits
            ],
            dtype=float,
        )

        mean_normal = np.mean(
            pass_normals,
            axis=0,
        )

        mean_normal_norm = float(
            np.linalg.norm(
                mean_normal
            )
        )

        if mean_normal_norm <= 0.0:
            raise ValueError(
                f"{wall_id} has unstable pass-normal orientation."
            )

        mean_normal /= (
            mean_normal_norm
        )

        angle_residuals = np.asarray(
            [
                _angle_between_normals_degrees(
                    normal,
                    mean_normal,
                )
                for normal in pass_normals
            ],
            dtype=float,
        )

        pairwise_angles = [
            _angle_between_normals_degrees(
                pass_normals[index],
                pass_normals[other],
            )
            for index in range(3)
            for other in range(
                index + 1,
                3,
            )
        ]

        pass_supports = np.asarray(
            [
                row.support_h_u
                for row in pass_fits
            ],
            dtype=float,
        )

        support_mean = float(
            np.mean(
                pass_supports
            )
        )

        support_residuals = (
            pass_supports
            - support_mean
        )

        walls.append(
            WallGeometry(
                wall_id=wall_id,
                normal_x=normal_x,
                normal_y=normal_y,
                support_h_u=support_h,
                normal_angle_degrees=(
                    _angle_degrees(
                        normal_x,
                        normal_y,
                    )
                ),
                line_fit_rms_u=fit_rms,
                pass_angle_rms_degrees=(
                    _rms(
                        angle_residuals
                    )
                ),
                pass_maximum_pairwise_angle_degrees=max(
                    pairwise_angles
                ),
                pass_support_mean_u=(
                    support_mean
                ),
                pass_support_rms_u=(
                    _rms(
                        support_residuals
                    )
                ),
                pass_maximum_pairwise_support_u=(
                    _maximum_pairwise_scalar(
                        pass_supports
                    )
                ),
                pass_maximum_line_fit_rms_u=max(
                    row.line_fit_rms_u
                    for row in pass_fits
                ),
            )
        )

    # ==========================================================
    # Derived wall vertices
    # ==========================================================

    vertices: list[
        WallVertex
    ] = []

    for index, first in enumerate(
        walls
    ):
        second = walls[
            (index + 1)
            % len(walls)
        ]

        x, y = (
            _intersect_support_lines(
                first,
                second,
            )
        )

        vertices.append(
            WallVertex(
                vertex_index=index,
                vertex_id=(
                    f"wall_vertex_{index:02d}"
                ),
                wall_a=first.wall_id,
                wall_b=second.wall_id,
                x_u=x,
                y_u=y,
                radius_from_origin_u=hypot(
                    x,
                    y,
                ),
                angle_degrees=_angle_degrees(
                    x,
                    y,
                ),
            )
        )

    vertex_points = np.asarray(
        [
            (
                vertex.x_u,
                vertex.y_u,
            )
            for vertex in vertices
        ],
        dtype=float,
    )

    sides: list[
        WallSide
    ] = []

    for index, wall in enumerate(
        walls
    ):
        previous_vertex = (
            vertex_points[
                (index - 1)
                % len(vertices)
            ]
        )

        current_vertex = (
            vertex_points[index]
        )

        sides.append(
            WallSide(
                wall_id=wall.wall_id,
                length_u=float(
                    np.linalg.norm(
                        current_vertex
                        - previous_vertex
                    )
                ),
            )
        )

    wall_perimeter = sum(
        side.length_u
        for side in sides
    )

    x = vertex_points[:, 0]
    y = vertex_points[:, 1]

    wall_area = abs(
        0.5
        * float(
            np.sum(
                x
                * np.roll(
                    y,
                    -1,
                )
                - y
                * np.roll(
                    x,
                    -1,
                )
            )
        )
    )

    return Figure12SourceGeometryReport(
        selected_fit=selected_fit,
        forward_matrix=_matrix_tuple(
            forward_matrix
        ),
        inverse_matrix=_matrix_tuple(
            inverse_matrix
        ),
        pass_inverse_matrices=tuple(
            (
                pass_id,
                _matrix_tuple(
                    pass_inverse_arrays[
                        pass_id
                    ]
                ),
            )
            for pass_id in sorted(
                pass_inverse_arrays
            )
        ),
        source_image_sha256=(
            reference[0].source_image_sha256
        ),
        image_width_pixels=(
            reference[0].image_width_pixels
        ),
        image_height_pixels=(
            reference[0].image_height_pixels
        ),
        moon_pass_fits=tuple(
            moon_pass_fits
        ),
        moons=tuple(
            moons
        ),
        wall_pass_fits=tuple(
            wall_pass_fits
        ),
        walls=tuple(
            walls
        ),
        vertices=tuple(
            vertices
        ),
        sides=tuple(
            sides
        ),
        wall_perimeter_u=float(
            wall_perimeter
        ),
        wall_area_u2=float(
            wall_area
        ),
        pixels_per_unit_maximum=(
            singular_max
        ),
        pixels_per_unit_minimum=(
            singular_min
        ),
        mean_pixels_per_unit=(
            mean_pixels_per_unit
        ),
    )


def _format_float(
    value: float,
) -> str:
    return format(
        value,
        ".12f",
    )


def _write_csv(
    path: Path,
    *,
    fieldnames: Sequence[str],
    rows: Sequence[object],
) -> Path:
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
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for row in rows:
            payload = asdict(row)

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
                    in payload.items()
                }
            )

    return path


def write_figure12_source_geometry(
    report: Figure12SourceGeometryReport,
    output_directory: str | Path,
) -> tuple[Path, ...]:
    """Write deterministic source-geometry outputs."""

    root = Path(
        output_directory
    )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    moon_pass_path = _write_csv(
        root
        / "figure12_moon_pass_fits.csv",
        fieldnames=MOON_PASS_FIELDS,
        rows=report.moon_pass_fits,
    )

    moon_path = _write_csv(
        root
        / "figure12_moon_geometry.csv",
        fieldnames=MOON_FIELDS,
        rows=report.moons,
    )

    wall_pass_path = _write_csv(
        root
        / "figure12_wall_pass_fits.csv",
        fieldnames=WALL_PASS_FIELDS,
        rows=report.wall_pass_fits,
    )

    wall_path = _write_csv(
        root
        / "figure12_wall_geometry.csv",
        fieldnames=WALL_FIELDS,
        rows=report.walls,
    )

    vertex_path = _write_csv(
        root
        / "figure12_wall_vertices.csv",
        fieldnames=VERTEX_FIELDS,
        rows=report.vertices,
    )

    side_path = _write_csv(
        root
        / "figure12_wall_side_lengths.csv",
        fieldnames=SIDE_FIELDS,
        rows=report.sides,
    )

    matrix_payload = {
        "schema_version": 1,
        "figure": 12,
        "selected_registration": {
            "dataset": "centroid",
            "model": "affine",
            "training_rms_pixels": (
                report.selected_fit.training_rms_pixels
            ),
            "loo_rms_pixels": (
                report.selected_fit.loo_rms_pixels
            ),
            "loo_maximum_pixels": (
                report.selected_fit.loo_maximum_pixels
            ),
            "anisotropy_ratio": (
                report.selected_fit.anisotropy_ratio
            ),
        },
        "coordinate_systems": {
            "source_pixel": (
                "Rendered image coordinates with positive y downward."
            ),
            "cartesian_pixel": (
                "Rendered pixel coordinates with positive y upward."
            ),
            "normalized": (
                "New Jerusalem project coordinates in units u "
                "with positive y upward."
            ),
        },
        "source_image": {
            "sha256": (
                report.source_image_sha256
            ),
            "width_pixels": (
                report.image_width_pixels
            ),
            "height_pixels": (
                report.image_height_pixels
            ),
        },
        "forward_model_to_cartesian_pixel": [
            list(row)
            for row in report.forward_matrix
        ],
        "inverse_cartesian_pixel_to_model": [
            list(row)
            for row in report.inverse_matrix
        ],
        "pass_inverse_cartesian_pixel_to_model": {
            pass_id: [
                list(row)
                for row in matrix
            ]
            for pass_id, matrix
            in report.pass_inverse_matrices
        },
        "linear_scale_diagnostics": {
            "pixels_per_unit_maximum": (
                report.pixels_per_unit_maximum
            ),
            "pixels_per_unit_minimum": (
                report.pixels_per_unit_minimum
            ),
            "mean_pixels_per_unit": (
                report.mean_pixels_per_unit
            ),
        },
    }

    matrix_path = (
        root
        / "figure12_affine_calibration.json"
    )

    matrix_path.write_text(
        json.dumps(
            matrix_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    summary_payload = {
        "schema_version": 1,
        "analysis_id": (
            "figure12-source-derived-normalized-geometry-v1"
        ),
        "evidence_class": (
            "source_plate_measurement"
        ),
        "selected_registration": (
            "centroid_affine"
        ),
        "moon_count": len(
            report.moons
        ),
        "wall_side_count": len(
            report.walls
        ),
        "wall_vertex_count": len(
            report.vertices
        ),
        "wall_perimeter_u": (
            report.wall_perimeter_u
        ),
        "wall_area_u2": (
            report.wall_area_u2
        ),
        "moon_radius_mean_u": float(
            np.mean(
                [
                    moon.radius_u
                    for moon in report.moons
                ]
            )
        ),
        "moon_radius_std_u": float(
            np.std(
                [
                    moon.radius_u
                    for moon in report.moons
                ]
            )
        ),
        "moon_centre_origin_radius_mean_u": float(
            np.mean(
                [
                    moon.centre_radius_from_origin_u
                    for moon in report.moons
                ]
            )
        ),
        "moon_centre_origin_radius_std_u": float(
            np.std(
                [
                    moon.centre_radius_from_origin_u
                    for moon in report.moons
                ]
            )
        ),
        "wall_support_mean_u": float(
            np.mean(
                [
                    wall.support_h_u
                    for wall in report.walls
                ]
            )
        ),
        "wall_support_std_u": float(
            np.std(
                [
                    wall.support_h_u
                    for wall in report.walls
                ]
            )
        ),
        "interpretation_boundary": (
            "No Moon-placement candidate or outer-wall "
            "construction hypothesis is tested in this stage."
        ),
    }

    summary_path = (
        root
        / "figure12_source_geometry_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summary_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = (
        root
        / "figure12_source_geometry_report.md"
    )

    maximum_moon_repeatability = max(
        report.moons,
        key=lambda item: (
            item.pass_centre_rms_u
        ),
    )

    maximum_wall_angle_repeatability = max(
        report.walls,
        key=lambda item: (
            item.pass_maximum_pairwise_angle_degrees
        ),
    )

    maximum_wall_support_repeatability = max(
        report.walls,
        key=lambda item: (
            item.pass_maximum_pairwise_support_u
        ),
    )

    lines = [
        "# Figure 12 source-derived normalized geometry",
        "",
        "## Evidence boundary",
        "",
        (
            "This analysis applies the selected centroid affine "
            "plate calibration to the raw Figure 12 source "
            "observations."
        ),
        "",
        (
            "Moon and wall geometry reported here is measured from "
            "the printed plate. No NJG Moon-placement candidate and "
            "no candidate wall construction is fitted or selected."
        ),
        "",
        "## Registration",
        "",
        "- Selected model: centroid affine",
        (
            f"- Training RMS: "
            f"{report.selected_fit.training_rms_pixels:.6f} px"
        ),
        (
            f"- Leave-one-out RMS: "
            f"{report.selected_fit.loo_rms_pixels:.6f} px"
        ),
        (
            f"- Leave-one-out maximum: "
            f"{report.selected_fit.loo_maximum_pixels:.6f} px"
        ),
        (
            f"- Anisotropy ratio: "
            f"{report.selected_fit.anisotropy_ratio:.9f}"
        ),
        (
            f"- Directional scale range: "
            f"{report.pixels_per_unit_minimum:.6f} to "
            f"{report.pixels_per_unit_maximum:.6f} px/u"
        ),
        (
            f"- Mean directional scale: "
            f"{report.mean_pixels_per_unit:.6f} px/u"
        ),
        "",
        "## Source-derived Moon geometry",
        "",
        (
            "| Moon | Centre x (u) | Centre y (u) | "
            "Origin radius (u) | Angle (deg) | Radius (u) | "
            "Circle RMS (u) | Pass centre RMS (u) |"
        ),
        (
            "|---|---:|---:|---:|---:|---:|---:|---:|"
        ),
    ]

    for moon in report.moons:
        lines.append(
            f"| `{moon.moon_id}` | "
            f"{moon.centre_x_u:.9f} | "
            f"{moon.centre_y_u:.9f} | "
            f"{moon.centre_radius_from_origin_u:.9f} | "
            f"{moon.centre_angle_degrees:.6f} | "
            f"{moon.radius_u:.9f} | "
            f"{moon.radial_fit_rms_u:.9f} | "
            f"{moon.pass_centre_rms_u:.9f} |"
        )

    lines.extend(
        [
            "",
            (
                "Worst pass-specific Moon-centre repeatability: "
                f"`{maximum_moon_repeatability.moon_id}`, "
                f"{maximum_moon_repeatability.pass_centre_rms_u:.9f} u."
            ),
            "",
            "## Source-derived wall lines",
            "",
            (
                "Each wall line is written in normalized support form "
                "`n_x x + n_y y = h`, with the unit normal oriented "
                "away from the diagram origin."
            ),
            "",
            (
                "| Wall | normal x | normal y | h (u) | "
                "normal angle (deg) | fit RMS (u) | "
                "pass angle RMS (deg) | pass support RMS (u) |"
            ),
            (
                "|---|---:|---:|---:|---:|---:|---:|---:|"
            ),
        ]
    )

    for wall in report.walls:
        lines.append(
            f"| `{wall.wall_id}` | "
            f"{wall.normal_x:.9f} | "
            f"{wall.normal_y:.9f} | "
            f"{wall.support_h_u:.9f} | "
            f"{wall.normal_angle_degrees:.6f} | "
            f"{wall.line_fit_rms_u:.9f} | "
            f"{wall.pass_angle_rms_degrees:.6f} | "
            f"{wall.pass_support_rms_u:.9f} |"
        )

    lines.extend(
        [
            "",
            (
                "Worst wall angular repeatability: "
                f"`{maximum_wall_angle_repeatability.wall_id}`, "
                f"{maximum_wall_angle_repeatability.pass_maximum_pairwise_angle_degrees:.6f} degrees."
            ),
            (
                "Worst wall support-position repeatability: "
                f"`{maximum_wall_support_repeatability.wall_id}`, "
                f"{maximum_wall_support_repeatability.pass_maximum_pairwise_support_u:.9f} u."
            ),
            "",
            "## Derived wall polygon",
            "",
            (
                f"- Vertices: {len(report.vertices)}"
            ),
            (
                f"- Perimeter: "
                f"{report.wall_perimeter_u:.9f} u"
            ),
            (
                f"- Area: "
                f"{report.wall_area_u2:.9f} u^2"
            ),
            "",
            (
                "| Wall side | Source-derived length (u) |"
            ),
            "|---|---:|",
        ]
    )

    for side in report.sides:
        lines.append(
            f"| `{side.wall_id}` | "
            f"{side.length_u:.9f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            (
                "These quantities are source-plate measurements. "
                "The next analysis stage may compare them with "
                "candidate Moon-placement systems and candidate "
                "outer-wall constructions."
            ),
            "",
        ]
    )

    report_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return (
        moon_pass_path,
        moon_path,
        wall_pass_path,
        wall_path,
        vertex_path,
        side_path,
        matrix_path,
        summary_path,
        report_path,
    )
