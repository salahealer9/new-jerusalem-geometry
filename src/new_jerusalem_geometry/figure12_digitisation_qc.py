"""Quality control for repeated Figure 12 source digitisation.

This module assesses repeatability of the raw source observations before
registration or comparison with any candidate geometric model.

The QC layers are:

- direct three-pass repeatability of registration landmarks;
- independent free-circle fits to each Moon circumference in each pass;
- independent orthogonal line fits to each outer-wall side in each pass.

No NJG Moon-placement model and no candidate outer-wall construction is used.
"""

from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from math import acos, degrees, sqrt
from pathlib import Path
from typing import Sequence

import numpy as np

from .figure12_digitisation import (
    Figure12DigitisedObservation,
    MOON_OBJECT_IDS,
    WALL_OBJECT_IDS,
    read_figure12_digitisation_pass_csv,
)


REGISTRATION_FIELDS = (
    "observation_id",
    "category",
    "centroid_x_pixels",
    "centroid_y_pixels",
    "rms_pixels",
    "maximum_pairwise_pixels",
)

MOON_FIT_FIELDS = (
    "pass_id",
    "moon_id",
    "centre_x_pixels",
    "centre_y_pixels",
    "radius_pixels",
    "radial_rms_pixels",
)

MOON_REPEATABILITY_FIELDS = (
    "moon_id",
    "centre_x_mean_pixels",
    "centre_y_mean_pixels",
    "centre_rms_pixels",
    "maximum_pairwise_centre_pixels",
    "radius_mean_pixels",
    "radius_std_pixels",
    "maximum_radial_fit_rms_pixels",
)

WALL_FIT_FIELDS = (
    "pass_id",
    "wall_id",
    "normal_x",
    "normal_y",
    "offset_pixels",
    "centroid_x_pixels",
    "centroid_y_pixels",
    "fit_rms_pixels",
)

WALL_REPEATABILITY_FIELDS = (
    "wall_id",
    "angular_rms_degrees",
    "maximum_pairwise_angle_degrees",
    "offset_rms_pixels",
    "maximum_pairwise_offset_pixels",
    "maximum_fit_rms_pixels",
)


@dataclass(frozen=True, slots=True)
class RegistrationRepeatability:
    observation_id: str
    category: str
    centroid_x_pixels: float
    centroid_y_pixels: float
    rms_pixels: float
    maximum_pairwise_pixels: float


@dataclass(frozen=True, slots=True)
class MoonCircleFit:
    pass_id: str
    moon_id: str
    centre_x_pixels: float
    centre_y_pixels: float
    radius_pixels: float
    radial_rms_pixels: float


@dataclass(frozen=True, slots=True)
class MoonRepeatability:
    moon_id: str
    centre_x_mean_pixels: float
    centre_y_mean_pixels: float
    centre_rms_pixels: float
    maximum_pairwise_centre_pixels: float
    radius_mean_pixels: float
    radius_std_pixels: float
    maximum_radial_fit_rms_pixels: float


@dataclass(frozen=True, slots=True)
class WallLineFit:
    pass_id: str
    wall_id: str
    normal_x: float
    normal_y: float
    offset_pixels: float
    centroid_x_pixels: float
    centroid_y_pixels: float
    fit_rms_pixels: float


@dataclass(frozen=True, slots=True)
class WallRepeatability:
    wall_id: str
    angular_rms_degrees: float
    maximum_pairwise_angle_degrees: float
    offset_rms_pixels: float
    maximum_pairwise_offset_pixels: float
    maximum_fit_rms_pixels: float


@dataclass(frozen=True, slots=True)
class Figure12DigitisationQC:
    source_image_sha256: str
    pass_sha256: tuple[tuple[str, str], ...]
    registration: tuple[RegistrationRepeatability, ...]
    moon_fits: tuple[MoonCircleFit, ...]
    moon_repeatability: tuple[MoonRepeatability, ...]
    wall_fits: tuple[WallLineFit, ...]
    wall_repeatability: tuple[WallRepeatability, ...]

    @property
    def maximum_registration_rms_pixels(self) -> float:
        return max(
            row.rms_pixels
            for row in self.registration
        )

    @property
    def maximum_registration_pairwise_pixels(self) -> float:
        return max(
            row.maximum_pairwise_pixels
            for row in self.registration
        )

    @property
    def maximum_moon_centre_rms_pixels(self) -> float:
        return max(
            row.centre_rms_pixels
            for row in self.moon_repeatability
        )

    @property
    def maximum_moon_centre_pairwise_pixels(self) -> float:
        return max(
            row.maximum_pairwise_centre_pixels
            for row in self.moon_repeatability
        )

    @property
    def maximum_moon_radial_fit_rms_pixels(self) -> float:
        return max(
            row.maximum_radial_fit_rms_pixels
            for row in self.moon_repeatability
        )

    @property
    def maximum_wall_angle_pairwise_degrees(self) -> float:
        return max(
            row.maximum_pairwise_angle_degrees
            for row in self.wall_repeatability
        )

    @property
    def maximum_wall_offset_pairwise_pixels(self) -> float:
        return max(
            row.maximum_pairwise_offset_pixels
            for row in self.wall_repeatability
        )

    @property
    def maximum_wall_fit_rms_pixels(self) -> float:
        return max(
            row.maximum_fit_rms_pixels
            for row in self.wall_repeatability
        )


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()

    with Path(path).open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()


def _rms(values: np.ndarray) -> float:
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
            distance = float(
                np.linalg.norm(
                    points[index]
                    - points[other]
                )
            )

            maximum = max(
                maximum,
                distance,
            )

    return maximum


def fit_circle(
    points: np.ndarray,
) -> tuple[float, float, float, float]:
    """Fit a free circle by linear least squares."""

    points = np.asarray(
        points,
        dtype=float,
    )

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError(
            "Circle-fit points must have shape (N, 2)."
        )

    if len(points) < 3:
        raise ValueError(
            "At least three points are required for a circle fit."
        )

    x = points[:, 0]
    y = points[:, 1]

    matrix = np.column_stack(
        (
            2.0 * x,
            2.0 * y,
            np.ones(len(points)),
        )
    )

    target = (
        x * x
        + y * y
    )

    solution, _, rank, _ = np.linalg.lstsq(
        matrix,
        target,
        rcond=None,
    )

    if rank < 3:
        raise ValueError(
            "Circle-fit points are degenerate."
        )

    centre_x = float(
        solution[0]
    )
    centre_y = float(
        solution[1]
    )

    radius_squared = (
        float(solution[2])
        + centre_x * centre_x
        + centre_y * centre_y
    )

    if radius_squared <= 0.0:
        raise ValueError(
            "Fitted circle has non-positive squared radius."
        )

    radius = sqrt(
        radius_squared
    )

    radii = np.sqrt(
        (x - centre_x) ** 2
        + (y - centre_y) ** 2
    )

    radial_rms = _rms(
        radii - radius
    )

    return (
        centre_x,
        centre_y,
        radius,
        radial_rms,
    )


def fit_line(
    points: np.ndarray,
) -> tuple[
    float,
    float,
    float,
    float,
    float,
    float,
]:
    """Fit an orthogonal 2D line using principal components.

    The returned line has normalized equation

        normal_x * x + normal_y * y + offset = 0.
    """

    points = np.asarray(
        points,
        dtype=float,
    )

    if points.ndim != 2 or points.shape[1] != 2:
        raise ValueError(
            "Line-fit points must have shape (N, 2)."
        )

    if len(points) < 2:
        raise ValueError(
            "At least two points are required for a line fit."
        )

    centroid = np.mean(
        points,
        axis=0,
    )

    centred = (
        points
        - centroid
    )

    _, singular_values, vh = np.linalg.svd(
        centred,
        full_matrices=False,
    )

    if (
        len(singular_values) == 0
        or singular_values[0] <= 0.0
    ):
        raise ValueError(
            "Line-fit points are degenerate."
        )

    normal = np.asarray(
        vh[-1],
        dtype=float,
    )

    normal /= np.linalg.norm(
        normal
    )

    # Deterministic sign convention.
    if (
        normal[0] < 0.0
        or (
            abs(normal[0]) < 1.0e-15
            and normal[1] < 0.0
        )
    ):
        normal = -normal

    offset = -float(
        np.dot(
            normal,
            centroid,
        )
    )

    residuals = (
        points @ normal
        + offset
    )

    fit_rms = _rms(
        residuals
    )

    return (
        float(normal[0]),
        float(normal[1]),
        offset,
        float(centroid[0]),
        float(centroid[1]),
        fit_rms,
    )


def _angle_between_unoriented_normals_degrees(
    first: np.ndarray,
    second: np.ndarray,
) -> float:
    dot = abs(
        float(
            np.dot(
                first,
                second,
            )
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


def _group_by_category_and_object(
    observations: Sequence[
        Figure12DigitisedObservation
    ],
    *,
    category: str,
) -> dict[
    str,
    tuple[Figure12DigitisedObservation, ...],
]:
    groups: dict[
        str,
        list[Figure12DigitisedObservation],
    ] = {}

    for item in observations:
        if item.definition.category != category:
            continue

        groups.setdefault(
            item.definition.object_id,
            [],
        ).append(item)

    return {
        object_id: tuple(rows)
        for object_id, rows in groups.items()
    }


def analyze_figure12_digitisation_qc(
    pass_paths: Sequence[str | Path],
) -> Figure12DigitisationQC:
    """Analyse three independent complete Figure 12 passes."""

    if len(pass_paths) != 3:
        raise ValueError(
            "Exactly three Figure 12 digitisation passes are required."
        )

    loaded: list[
        tuple[
            Path,
            tuple[Figure12DigitisedObservation, ...],
        ]
    ] = []

    for raw_path in pass_paths:
        path = Path(raw_path)

        observations = (
            read_figure12_digitisation_pass_csv(
                path,
                require_complete=True,
            )
        )

        loaded.append(
            (
                path,
                observations,
            )
        )

    pass_ids = tuple(
        observations[0].pass_id
        for _, observations in loaded
    )

    if len(set(pass_ids)) != 3:
        raise ValueError(
            "The three QC inputs must have distinct pass IDs."
        )

    source_hashes = {
        observations[0].source_image_sha256
        for _, observations in loaded
    }

    if len(source_hashes) != 1:
        raise ValueError(
            "QC passes do not use the same source image."
        )

    source_hash = next(
        iter(source_hashes)
    )

    pass_hashes = tuple(
        (
            observations[0].pass_id,
            sha256_file(path),
        )
        for path, observations in loaded
    )

    # --------------------------------------------------------------
    # Registration landmarks
    # --------------------------------------------------------------

    first_pass = loaded[0][1]

    registration_ids = tuple(
        item.definition.observation_id
        for item in first_pass
        if item.definition.registration_default
    )

    registration_rows: list[
        RegistrationRepeatability
    ] = []

    for observation_id in registration_ids:
        matches: list[
            Figure12DigitisedObservation
        ] = []

        for _, observations in loaded:
            found = [
                item
                for item in observations
                if (
                    item.definition.observation_id
                    == observation_id
                )
            ]

            if len(found) != 1:
                raise ValueError(
                    "Registration observation is missing or duplicated: "
                    f"{observation_id}"
                )

            matches.append(
                found[0]
            )

        points = np.asarray(
            [
                (
                    item.pixel_x,
                    item.pixel_y,
                )
                for item in matches
            ],
            dtype=float,
        )

        centroid = np.mean(
            points,
            axis=0,
        )

        distances = np.linalg.norm(
            points - centroid,
            axis=1,
        )

        registration_rows.append(
            RegistrationRepeatability(
                observation_id=observation_id,
                category=matches[0].definition.category,
                centroid_x_pixels=float(
                    centroid[0]
                ),
                centroid_y_pixels=float(
                    centroid[1]
                ),
                rms_pixels=_rms(
                    distances
                ),
                maximum_pairwise_pixels=(
                    _maximum_pairwise_distance(
                        points
                    )
                ),
            )
        )

    # --------------------------------------------------------------
    # Moon circle fits
    # --------------------------------------------------------------

    moon_fits: list[
        MoonCircleFit
    ] = []

    for _, observations in loaded:
        pass_id = observations[0].pass_id

        groups = (
            _group_by_category_and_object(
                observations,
                category="moon_circumference",
            )
        )

        if set(groups) != set(
            MOON_OBJECT_IDS
        ):
            raise ValueError(
                "Moon object set does not match the fixed schema."
            )

        for moon_id in MOON_OBJECT_IDS:
            rows = groups[
                moon_id
            ]

            if len(rows) != 6:
                raise ValueError(
                    f"{moon_id} does not contain six arc samples."
                )

            points = np.asarray(
                [
                    (
                        item.pixel_x,
                        item.pixel_y,
                    )
                    for item in rows
                ],
                dtype=float,
            )

            (
                centre_x,
                centre_y,
                radius,
                radial_rms,
            ) = fit_circle(
                points
            )

            moon_fits.append(
                MoonCircleFit(
                    pass_id=pass_id,
                    moon_id=moon_id,
                    centre_x_pixels=centre_x,
                    centre_y_pixels=centre_y,
                    radius_pixels=radius,
                    radial_rms_pixels=radial_rms,
                )
            )

    moon_repeatability: list[
        MoonRepeatability
    ] = []

    for moon_id in MOON_OBJECT_IDS:
        fits = [
            row
            for row in moon_fits
            if row.moon_id == moon_id
        ]

        if len(fits) != 3:
            raise ValueError(
                f"{moon_id} does not contain three pass fits."
            )

        centres = np.asarray(
            [
                (
                    row.centre_x_pixels,
                    row.centre_y_pixels,
                )
                for row in fits
            ],
            dtype=float,
        )

        mean_centre = np.mean(
            centres,
            axis=0,
        )

        centre_distances = np.linalg.norm(
            centres - mean_centre,
            axis=1,
        )

        radii = np.asarray(
            [
                row.radius_pixels
                for row in fits
            ],
            dtype=float,
        )

        moon_repeatability.append(
            MoonRepeatability(
                moon_id=moon_id,
                centre_x_mean_pixels=float(
                    mean_centre[0]
                ),
                centre_y_mean_pixels=float(
                    mean_centre[1]
                ),
                centre_rms_pixels=_rms(
                    centre_distances
                ),
                maximum_pairwise_centre_pixels=(
                    _maximum_pairwise_distance(
                        centres
                    )
                ),
                radius_mean_pixels=float(
                    np.mean(radii)
                ),
                radius_std_pixels=float(
                    np.std(radii)
                ),
                maximum_radial_fit_rms_pixels=max(
                    row.radial_rms_pixels
                    for row in fits
                ),
            )
        )

    # --------------------------------------------------------------
    # Wall-line fits
    # --------------------------------------------------------------

    wall_fits: list[
        WallLineFit
    ] = []

    for _, observations in loaded:
        pass_id = observations[0].pass_id

        groups = (
            _group_by_category_and_object(
                observations,
                category="wall_line",
            )
        )

        if set(groups) != set(
            WALL_OBJECT_IDS
        ):
            raise ValueError(
                "Wall object set does not match the fixed schema."
            )

        for wall_id in WALL_OBJECT_IDS:
            rows = groups[
                wall_id
            ]

            if len(rows) != 3:
                raise ValueError(
                    f"{wall_id} does not contain three line samples."
                )

            points = np.asarray(
                [
                    (
                        item.pixel_x,
                        item.pixel_y,
                    )
                    for item in rows
                ],
                dtype=float,
            )

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

            wall_fits.append(
                WallLineFit(
                    pass_id=pass_id,
                    wall_id=wall_id,
                    normal_x=normal_x,
                    normal_y=normal_y,
                    offset_pixels=offset,
                    centroid_x_pixels=centroid_x,
                    centroid_y_pixels=centroid_y,
                    fit_rms_pixels=fit_rms,
                )
            )

    wall_repeatability: list[
        WallRepeatability
    ] = []

    for wall_id in WALL_OBJECT_IDS:
        fits = [
            row
            for row in wall_fits
            if row.wall_id == wall_id
        ]

        if len(fits) != 3:
            raise ValueError(
                f"{wall_id} does not contain three pass fits."
            )

        normals = np.asarray(
            [
                (
                    row.normal_x,
                    row.normal_y,
                )
                for row in fits
            ],
            dtype=float,
        )

        offsets = np.asarray(
            [
                row.offset_pixels
                for row in fits
            ],
            dtype=float,
        )

        # Align line-normal signs before averaging.
        reference = normals[0].copy()

        for index in range(1, len(normals)):
            if (
                float(
                    np.dot(
                        reference,
                        normals[index],
                    )
                )
                < 0.0
            ):
                normals[index] *= -1.0
                offsets[index] *= -1.0

        mean_normal = np.mean(
            normals,
            axis=0,
        )

        mean_normal /= np.linalg.norm(
            mean_normal
        )

        angle_residuals = np.asarray(
            [
                _angle_between_unoriented_normals_degrees(
                    normal,
                    mean_normal,
                )
                for normal in normals
            ],
            dtype=float,
        )

        pairwise_angles: list[
            float
        ] = []

        for index in range(3):
            for other in range(
                index + 1,
                3,
            ):
                pairwise_angles.append(
                    _angle_between_unoriented_normals_degrees(
                        normals[index],
                        normals[other],
                    )
                )

        reference_point = np.mean(
            np.asarray(
                [
                    (
                        row.centroid_x_pixels,
                        row.centroid_y_pixels,
                    )
                    for row in fits
                ],
                dtype=float,
            ),
            axis=0,
        )

        signed_positions = np.asarray(
            [
                float(
                    np.dot(
                        normals[index],
                        reference_point,
                    )
                    + offsets[index]
                )
                for index in range(3)
            ],
            dtype=float,
        )

        position_mean = float(
            np.mean(
                signed_positions
            )
        )

        offset_residuals = (
            signed_positions
            - position_mean
        )

        pairwise_offsets = [
            abs(
                float(
                    signed_positions[index]
                    - signed_positions[other]
                )
            )
            for index in range(3)
            for other in range(
                index + 1,
                3,
            )
        ]

        wall_repeatability.append(
            WallRepeatability(
                wall_id=wall_id,
                angular_rms_degrees=_rms(
                    angle_residuals
                ),
                maximum_pairwise_angle_degrees=max(
                    pairwise_angles
                ),
                offset_rms_pixels=_rms(
                    offset_residuals
                ),
                maximum_pairwise_offset_pixels=max(
                    pairwise_offsets
                ),
                maximum_fit_rms_pixels=max(
                    row.fit_rms_pixels
                    for row in fits
                ),
            )
        )

    return Figure12DigitisationQC(
        source_image_sha256=source_hash,
        pass_sha256=pass_hashes,
        registration=tuple(
            registration_rows
        ),
        moon_fits=tuple(
            moon_fits
        ),
        moon_repeatability=tuple(
            moon_repeatability
        ),
        wall_fits=tuple(
            wall_fits
        ),
        wall_repeatability=tuple(
            wall_repeatability
        ),
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
            writer.writerow(
                asdict(row)
            )

    return path


def write_figure12_digitisation_qc(
    report: Figure12DigitisationQC,
    output_directory: str | Path,
) -> tuple[Path, ...]:
    """Write deterministic working QC outputs."""

    root = Path(
        output_directory
    )

    root.mkdir(
        parents=True,
        exist_ok=True,
    )

    registration_path = _write_csv(
        root
        / "registration_repeatability.csv",
        fieldnames=REGISTRATION_FIELDS,
        rows=report.registration,
    )

    moon_fit_path = _write_csv(
        root
        / "moon_circle_fits.csv",
        fieldnames=MOON_FIT_FIELDS,
        rows=report.moon_fits,
    )

    moon_repeatability_path = _write_csv(
        root
        / "moon_repeatability.csv",
        fieldnames=MOON_REPEATABILITY_FIELDS,
        rows=report.moon_repeatability,
    )

    wall_fit_path = _write_csv(
        root
        / "wall_line_fits.csv",
        fieldnames=WALL_FIT_FIELDS,
        rows=report.wall_fits,
    )

    wall_repeatability_path = _write_csv(
        root
        / "wall_repeatability.csv",
        fieldnames=WALL_REPEATABILITY_FIELDS,
        rows=report.wall_repeatability,
    )

    summary = {
        "source_image_sha256": (
            report.source_image_sha256
        ),
        "raw_pass_sha256": dict(
            report.pass_sha256
        ),
        "counts": {
            "registration_landmarks": len(
                report.registration
            ),
            "moon_circle_fits": len(
                report.moon_fits
            ),
            "moon_objects": len(
                report.moon_repeatability
            ),
            "wall_line_fits": len(
                report.wall_fits
            ),
            "wall_objects": len(
                report.wall_repeatability
            ),
        },
        "maxima": {
            "registration_rms_pixels": (
                report.maximum_registration_rms_pixels
            ),
            "registration_pairwise_pixels": (
                report.maximum_registration_pairwise_pixels
            ),
            "moon_centre_rms_pixels": (
                report.maximum_moon_centre_rms_pixels
            ),
            "moon_centre_pairwise_pixels": (
                report.maximum_moon_centre_pairwise_pixels
            ),
            "moon_radial_fit_rms_pixels": (
                report.maximum_moon_radial_fit_rms_pixels
            ),
            "wall_pairwise_angle_degrees": (
                report.maximum_wall_angle_pairwise_degrees
            ),
            "wall_pairwise_offset_pixels": (
                report.maximum_wall_offset_pairwise_pixels
            ),
            "wall_fit_rms_pixels": (
                report.maximum_wall_fit_rms_pixels
            ),
        },
    }

    summary_path = (
        root
        / "figure12_digitisation_qc_summary.json"
    )

    summary_path.write_text(
        json.dumps(
            summary,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    report_path = (
        root
        / "figure12_digitisation_qc_report.md"
    )

    registration_worst = max(
        report.registration,
        key=lambda row: row.rms_pixels,
    )

    moon_centre_worst = max(
        report.moon_repeatability,
        key=lambda row: row.centre_rms_pixels,
    )

    moon_fit_worst = max(
        report.moon_repeatability,
        key=lambda row: row.maximum_radial_fit_rms_pixels,
    )

    wall_angle_worst = max(
        report.wall_repeatability,
        key=lambda row: row.maximum_pairwise_angle_degrees,
    )

    wall_offset_worst = max(
        report.wall_repeatability,
        key=lambda row: row.maximum_pairwise_offset_pixels,
    )

    lines = [
        "# Figure 12 digitisation QC",
        "",
        "## Scope",
        "",
        (
            "This report evaluates repeatability of the three raw "
            "source-digitisation passes before registration or comparison "
            "with any candidate Moon-placement or outer-wall model."
        ),
        "",
        "## Raw evidence",
        "",
        f"- Source image SHA-256: `{report.source_image_sha256}`",
    ]

    for pass_id, digest in report.pass_sha256:
        lines.append(
            f"- {pass_id}: `{digest}`"
        )

    lines.extend(
        [
            "",
            "## Registration repeatability",
            "",
            (
                f"- Maximum landmark RMS: "
                f"{report.maximum_registration_rms_pixels:.6f} px"
            ),
            (
                f"- Maximum landmark pairwise separation: "
                f"{report.maximum_registration_pairwise_pixels:.6f} px"
            ),
            (
                f"- Worst RMS landmark: "
                f"`{registration_worst.observation_id}` "
                f"({registration_worst.rms_pixels:.6f} px)"
            ),
            "",
            "## Moon-circle repeatability",
            "",
            (
                f"- Maximum fitted-centre RMS: "
                f"{report.maximum_moon_centre_rms_pixels:.6f} px"
            ),
            (
                f"- Maximum fitted-centre pairwise separation: "
                f"{report.maximum_moon_centre_pairwise_pixels:.6f} px"
            ),
            (
                f"- Maximum within-pass circle radial RMS: "
                f"{report.maximum_moon_radial_fit_rms_pixels:.6f} px"
            ),
            (
                f"- Worst centre-repeatability Moon: "
                f"`{moon_centre_worst.moon_id}` "
                f"({moon_centre_worst.centre_rms_pixels:.6f} px)"
            ),
            (
                f"- Worst circle-fit Moon: "
                f"`{moon_fit_worst.moon_id}` "
                f"({moon_fit_worst.maximum_radial_fit_rms_pixels:.6f} px)"
            ),
            "",
            "## Wall-line repeatability",
            "",
            (
                f"- Maximum pairwise line-angle difference: "
                f"{report.maximum_wall_angle_pairwise_degrees:.6f} degrees"
            ),
            (
                f"- Maximum pairwise line-position difference: "
                f"{report.maximum_wall_offset_pairwise_pixels:.6f} px"
            ),
            (
                f"- Maximum within-pass line-fit RMS: "
                f"{report.maximum_wall_fit_rms_pixels:.6f} px"
            ),
            (
                f"- Worst angular-repeatability side: "
                f"`{wall_angle_worst.wall_id}` "
                f"({wall_angle_worst.maximum_pairwise_angle_degrees:.6f} degrees)"
            ),
            (
                f"- Worst positional-repeatability side: "
                f"`{wall_offset_worst.wall_id}` "
                f"({wall_offset_worst.maximum_pairwise_offset_pixels:.6f} px)"
            ),
            "",
            "## Interpretation boundary",
            "",
            (
                "These statistics describe source-digitisation repeatability "
                "only. They do not select an NJG Moon model and do not validate "
                "the radial-support wall hypothesis."
            ),
            "",
        ]
    )

    report_path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    return (
        registration_path,
        moon_fit_path,
        moon_repeatability_path,
        wall_fit_path,
        wall_repeatability_path,
        summary_path,
        report_path,
    )
