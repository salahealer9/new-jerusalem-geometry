import csv
import json
from math import cos, pi, sin
from pathlib import Path

import numpy as np
import pytest

from new_jerusalem_geometry.figure14_edge_tracing import (
    analyze_edge_trace_passes,
    load_edge_trace_reference,
    write_edge_topology_details_csv,
    write_edge_topology_json,
    write_edge_topology_markdown,
    write_edge_trace_csv,
)
from new_jerusalem_geometry.figure14_registration import (
    apply_registration_matrix,
    cartesian_to_pixel,
)
from new_jerusalem_geometry.figure14_semantic_correspondence import (
    STAR_IDS,
)
from new_jerusalem_geometry.source_preparation import (
    sha256_file,
)


FORWARD = np.asarray(
    (
        (50.0, 0.8, 600.0),
        (-0.5, 49.0, 600.0),
        (0.0, 0.0, 1.0),
    ),
    dtype=float,
)


def _regular_endpoints() -> np.ndarray:
    return np.asarray(
        [
            (
                7.0
                * cos(
                    pi / 2.0
                    + index
                    * 2.0
                    * pi
                    / 7.0
                ),
                7.0
                * sin(
                    pi / 2.0
                    + index
                    * 2.0
                    * pi
                    / 7.0
                ),
            )
            for index in range(7)
        ],
        dtype=float,
    )


def _make_reference(
    tmp_path: Path,
) -> tuple[
    Path,
    Path,
    Path,
]:
    source_image = (
        tmp_path / "source.png"
    )

    source_image.write_bytes(
        b"fixed rendered source"
    )

    image_width = 1200
    image_height = 1200

    inverse = np.linalg.inv(
        FORWARD
    )

    matrix_path = (
        tmp_path / "matrix.json"
    )

    matrix_payload = {
        "selected_model": "affine",
        "source_image": {
            "filename": source_image.name,
            "sha256": sha256_file(
                source_image
            ),
            "width_pixels": image_width,
            "height_pixels": image_height,
        },
        "inverse_cartesian_pixel_to_model": (
            inverse.tolist()
        ),
    }

    matrix_path.write_text(
        json.dumps(
            matrix_payload,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    endpoint_points = (
        _regular_endpoints()
    )

    landmarks_path = (
        tmp_path / "landmarks.csv"
    )

    fieldnames = (
        "landmark_id",
        "category",
        "pixel_centroid_x",
        "pixel_centroid_y",
        "normalized_x",
        "normalized_y",
    )

    with landmarks_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for landmark_id, point in zip(
            STAR_IDS,
            endpoint_points,
            strict=True,
        ):
            cartesian = (
                apply_registration_matrix(
                    FORWARD,
                    [point],
                )[0]
            )

            pixel_x, pixel_y = (
                cartesian_to_pixel(
                    float(cartesian[0]),
                    float(cartesian[1]),
                    image_height,
                )
            )

            writer.writerow(
                {
                    "landmark_id": (
                        landmark_id
                    ),
                    "category": (
                        "star_endpoint"
                    ),
                    "pixel_centroid_x": (
                        format(
                            pixel_x,
                            ".12f",
                        )
                    ),
                    "pixel_centroid_y": (
                        format(
                            pixel_y,
                            ".12f",
                        )
                    ),
                    "normalized_x": (
                        format(
                            float(point[0]),
                            ".12f",
                        )
                    ),
                    "normalized_y": (
                        format(
                            float(point[1]),
                            ".12f",
                        )
                    ),
                }
            )

    return (
        source_image,
        matrix_path,
        landmarks_path,
    )


def _make_trace_passes(
    tmp_path: Path,
    *,
    step: int,
) -> tuple[
    object,
    tuple[Path, ...],
]:
    (
        source_image,
        matrix_path,
        landmarks_path,
    ) = _make_reference(
        tmp_path
    )

    reference = load_edge_trace_reference(
        matrix_path=matrix_path,
        landmarks_path=landmarks_path,
    )

    endpoints = np.asarray(
        reference.endpoint_normalized,
        dtype=float,
    )

    pass_paths = []

    for pass_number, fraction in enumerate(
        (0.12, 0.14, 0.16),
        start=1,
    ):
        samples = []

        for endpoint_index in range(7):
            endpoint = endpoints[
                endpoint_index
            ]

            target_indices = (
                (endpoint_index - step) % 7,
                (endpoint_index + step) % 7,
            )

            for ray_index, target_index in enumerate(
                target_indices
            ):
                target = endpoints[
                    target_index
                ]

                normalized_sample = (
                    endpoint
                    + fraction
                    * (target - endpoint)
                )

                cartesian = (
                    apply_registration_matrix(
                        FORWARD,
                        [normalized_sample],
                    )[0]
                )

                pixel_x, pixel_y = (
                    cartesian_to_pixel(
                        float(cartesian[0]),
                        float(cartesian[1]),
                        reference.image_height_pixels,
                    )
                )

                samples.append(
                    (
                        endpoint_index,
                        ray_index,
                        pixel_x,
                        pixel_y,
                    )
                )

        pass_path = (
            tmp_path
            / (
                "figure14_edge_trace_"
                f"pass-{pass_number:02d}.csv"
            )
        )

        write_edge_trace_csv(
            pass_path,
            reference=reference,
            source_image_path=(
                source_image
            ),
            pass_id=f"pass-{pass_number:02d}",
            samples=samples,
        )

        pass_paths.append(
            pass_path
        )

    return reference, tuple(
        pass_paths
    )


def test_step2_topology_is_recovered(
    tmp_path: Path,
) -> None:
    reference, pass_paths = (
        _make_trace_passes(
            tmp_path,
            step=2,
        )
    )

    report = analyze_edge_trace_passes(
        reference=reference,
        pass_paths=pass_paths,
    )

    assert report.selected_step == 2
    assert report.selected_notation == "{7/2}"
    assert report.unanimous_endpoint_passes
    assert report.selected_rms_degrees < 1.0e-5
    assert report.rms_margin_degrees > 10.0


def test_step3_topology_is_recovered(
    tmp_path: Path,
) -> None:
    reference, pass_paths = (
        _make_trace_passes(
            tmp_path,
            step=3,
        )
    )

    report = analyze_edge_trace_passes(
        reference=reference,
        pass_paths=pass_paths,
    )

    assert report.selected_step == 3
    assert report.selected_notation == "{7/3}"
    assert report.unanimous_endpoint_passes
    assert report.selected_rms_degrees < 1.0e-5


def test_trace_writer_rejects_incomplete_pass(
    tmp_path: Path,
) -> None:
    (
        source_image,
        matrix_path,
        landmarks_path,
    ) = _make_reference(
        tmp_path
    )

    reference = load_edge_trace_reference(
        matrix_path=matrix_path,
        landmarks_path=landmarks_path,
    )

    with pytest.raises(
        ValueError,
        match="fourteen",
    ):
        write_edge_trace_csv(
            tmp_path / "incomplete.csv",
            reference=reference,
            source_image_path=source_image,
            pass_id="pass-01",
            samples=[
                (
                    0,
                    0,
                    600.0,
                    600.0,
                )
            ],
        )


def test_topology_output_writers(
    tmp_path: Path,
) -> None:
    reference, pass_paths = (
        _make_trace_passes(
            tmp_path,
            step=2,
        )
    )

    report = analyze_edge_trace_passes(
        reference=reference,
        pass_paths=pass_paths,
    )

    details = (
        write_edge_topology_details_csv(
            tmp_path / "details.csv",
            report,
        )
    )

    summary = write_edge_topology_json(
        tmp_path / "summary.json",
        report,
    )

    markdown = (
        write_edge_topology_markdown(
            tmp_path / "report.md",
            report,
        )
    )

    assert details.exists()
    assert summary.exists()
    assert markdown.exists()

    payload = json.loads(
        summary.read_text(
            encoding="utf-8"
        )
    )

    assert (
        payload["selected"]["notation"]
        == "{7/2}"
    )

    assert (
        payload["selected"][
            "unanimous_endpoint_passes"
        ]
        is True
    )

    text = markdown.read_text(
        encoding="utf-8"
    )

    assert "near-endpoint" in text
    assert "internal crossings" in text
    assert "Selected topology" in text
