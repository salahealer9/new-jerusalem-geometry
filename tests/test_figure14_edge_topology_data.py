import csv
import json
from math import cos, pi, sin
from pathlib import Path

import numpy as np
import pytest

from new_jerusalem_geometry.figure14_edge_topology_data import (
    promote_figure14_edge_topology_evidence,
)
from new_jerusalem_geometry.figure14_edge_tracing import (
    load_edge_trace_reference,
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
        (52.0, 0.7, 620.0),
        (-0.4, 51.0, 610.0),
        (0.0, 0.0, 1.0),
    ),
    dtype=float,
)


def _make_input_evidence(
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

    image_width = 1300
    image_height = 1300

    inverse = np.linalg.inv(
        FORWARD
    )

    matrix_path = (
        tmp_path / "affine_registration_matrix.json"
    )

    matrix_path.write_text(
        json.dumps(
            {
                "selected_model": "affine",
                "source_image": {
                    "filename": (
                        source_image.name
                    ),
                    "sha256": sha256_file(
                        source_image
                    ),
                    "width_pixels": (
                        image_width
                    ),
                    "height_pixels": (
                        image_height
                    ),
                },
                "inverse_cartesian_pixel_to_model": (
                    inverse.tolist()
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    endpoints = np.asarray(
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

    landmarks_path = (
        tmp_path
        / "registered_landmark_centroids.csv"
    )

    with landmarks_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as handle:
        fieldnames = (
            "landmark_id",
            "category",
            "pixel_centroid_x",
            "pixel_centroid_y",
            "normalized_x",
            "normalized_y",
        )

        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for landmark_id, point in zip(
            STAR_IDS,
            endpoints,
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
                    "pixel_centroid_x": format(
                        pixel_x,
                        ".12f",
                    ),
                    "pixel_centroid_y": format(
                        pixel_y,
                        ".12f",
                    ),
                    "normalized_x": format(
                        float(point[0]),
                        ".12f",
                    ),
                    "normalized_y": format(
                        float(point[1]),
                        ".12f",
                    ),
                }
            )

    reference = load_edge_trace_reference(
        matrix_path=matrix_path,
        landmarks_path=landmarks_path,
    )

    input_directory = (
        tmp_path / "working"
    )

    input_directory.mkdir()

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
                (endpoint_index - 2) % 7,
                (endpoint_index + 2) % 7,
            )

            for ray_index, target_index in enumerate(
                target_indices
            ):
                target = endpoints[
                    target_index
                ]

                sample = (
                    endpoint
                    + fraction
                    * (target - endpoint)
                )

                cartesian = (
                    apply_registration_matrix(
                        FORWARD,
                        [sample],
                    )[0]
                )

                pixel_x, pixel_y = (
                    cartesian_to_pixel(
                        float(cartesian[0]),
                        float(cartesian[1]),
                        image_height,
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

        write_edge_trace_csv(
            input_directory
            / (
                "figure14_edge_trace_"
                f"pass-{pass_number:02d}.csv"
            ),
            reference=reference,
            source_image_path=source_image,
            pass_id=f"pass-{pass_number:02d}",
            samples=samples,
        )

    return (
        input_directory,
        matrix_path,
        landmarks_path,
    )


def test_promotion_preserves_raw_traces_and_result(
    tmp_path: Path,
) -> None:
    (
        input_directory,
        matrix_path,
        landmarks_path,
    ) = _make_input_evidence(
        tmp_path
    )

    result = (
        promote_figure14_edge_topology_evidence(
            input_directory=(
                input_directory
            ),
            output_root=(
                tmp_path / "calibration"
            ),
            matrix_path=matrix_path,
            landmarks_path=landmarks_path,
        )
    )

    assert len(result.files) == 3

    assert (
        result.topology_report.selected_step
        == 2
    )

    assert (
        result.topology_report.selected_notation
        == "{7/2}"
    )

    assert (
        result.topology_report.unanimous_endpoint_passes
    )

    for record in result.files:
        assert (
            record.input_path.read_bytes()
            == record.output_path.read_bytes()
        )

        assert (
            record.input_sha256
            == record.output_sha256
        )


def test_manifest_records_provenance_and_ranking(
    tmp_path: Path,
) -> None:
    (
        input_directory,
        matrix_path,
        landmarks_path,
    ) = _make_input_evidence(
        tmp_path
    )

    result = (
        promote_figure14_edge_topology_evidence(
            input_directory=input_directory,
            output_root=(
                tmp_path / "calibration"
            ),
            matrix_path=matrix_path,
            landmarks_path=landmarks_path,
        )
    )

    payload = json.loads(
        result.manifest_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload[
        "raw_files_modified"
    ] is False

    assert payload[
        "total_ray_samples"
    ] == 42

    assert payload[
        "selected_topology"
    ]["notation"] == "{7/2}"

    assert payload[
        "selected_topology"
    ]["unanimous_endpoint_passes"] is True

    assert len(
        payload["raw_trace_passes"]
    ) == 3

    assert (
        payload["candidate_ranking"][0][
            "notation"
        ]
        == "{7/2}"
    )


def test_promotion_refuses_silent_overwrite(
    tmp_path: Path,
) -> None:
    (
        input_directory,
        matrix_path,
        landmarks_path,
    ) = _make_input_evidence(
        tmp_path
    )

    output_root = (
        tmp_path / "calibration"
    )

    promote_figure14_edge_topology_evidence(
        input_directory=input_directory,
        output_root=output_root,
        matrix_path=matrix_path,
        landmarks_path=landmarks_path,
    )

    with pytest.raises(
        FileExistsError,
        match="already exist",
    ):
        promote_figure14_edge_topology_evidence(
            input_directory=(
                input_directory
            ),
            output_root=output_root,
            matrix_path=matrix_path,
            landmarks_path=landmarks_path,
        )


def test_overwrite_regeneration_is_deterministic(
    tmp_path: Path,
) -> None:
    (
        input_directory,
        matrix_path,
        landmarks_path,
    ) = _make_input_evidence(
        tmp_path
    )

    output_root = (
        tmp_path / "calibration"
    )

    first = (
        promote_figure14_edge_topology_evidence(
            input_directory=input_directory,
            output_root=output_root,
            matrix_path=matrix_path,
            landmarks_path=landmarks_path,
        )
    )

    first_hashes = {
        path.name: sha256_file(path)
        for path in (
            first.details_path,
            first.summary_path,
            first.report_path,
            first.manifest_path,
        )
    }

    second = (
        promote_figure14_edge_topology_evidence(
            input_directory=input_directory,
            output_root=output_root,
            matrix_path=matrix_path,
            landmarks_path=landmarks_path,
            overwrite=True,
        )
    )

    second_hashes = {
        path.name: sha256_file(path)
        for path in (
            second.details_path,
            second.summary_path,
            second.report_path,
            second.manifest_path,
        )
    }

    assert second_hashes == first_hashes
