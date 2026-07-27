from math import sqrt
from pathlib import Path

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.figure14_digitisation import (
    build_figure14_landmark_schema,
    write_digitisation_csv,
)
from new_jerusalem_geometry.figure14_digitisation_qc import (
    analyze_digitisation_passes,
    load_digitisation_pass,
    write_category_qc_csv,
    write_landmark_qc_csv,
    write_pass_qc_csv,
    write_qc_markdown,
)


def _write_passes(
    tmp_path: Path,
    *,
    anomalous: bool = False,
) -> tuple[Path, ...]:
    schema = build_figure14_landmark_schema(
        build_core_geometry()
    )

    source = tmp_path / "source.png"
    source.write_bytes(b"fixed source image")

    base = tuple(
        (
            300.0 + index * 10.0,
            500.0 + index * 12.0,
        )
        for index in range(len(schema))
    )

    offsets = (
        (0.0, 0.0),
        (1.0, 0.0),
        (-1.0, 0.0),
    )

    paths = []

    for pass_index, (dx, dy) in enumerate(
        offsets,
        start=1,
    ):
        points = list(
            (
                x + dx,
                y + dy,
            )
            for x, y in base
        )

        if anomalous and pass_index == 3:
            first_x, first_y = points[0]
            points[0] = (
                first_x + 10.0,
                first_y,
            )

        path = (
            tmp_path
            / f"figure14_digitisation_pass-{pass_index:02d}.csv"
        )

        write_digitisation_csv(
            path,
            schema=schema,
            points=points,
            pass_id=f"pass-{pass_index:02d}",
            source_image=source,
            image_width_pixels=1512,
            image_height_pixels=2327,
        )

        paths.append(path)

    return tuple(paths)


def test_load_digitisation_pass(
    tmp_path: Path,
) -> None:
    paths = _write_passes(tmp_path)

    result = load_digitisation_pass(
        paths[0]
    )

    assert result.pass_id == "pass-01"
    assert len(result.observations) == 31
    assert result.image_width_pixels == 1512
    assert result.image_height_pixels == 2327


def test_uniform_offsets_have_expected_uncertainty(
    tmp_path: Path,
) -> None:
    paths = _write_passes(tmp_path)

    report = analyze_digitisation_passes(
        paths
    )

    expected_rms = sqrt(2.0 / 3.0)

    assert len(report.landmarks) == 31
    assert len(report.pass_statistics) == 3
    assert len(report.category_statistics) == 4

    assert report.overall_rms_dispersion_pixels \
        == pytest.approx(
            expected_rms,
            abs=1.0e-12,
        )

    assert report.maximum_pairwise_separation_pixels \
        == pytest.approx(
            2.0,
            abs=1.0e-12,
        )

    assert report.review_flag_count == 0

    assert tuple(
        item.mean_dx_pixels
        for item in report.pass_statistics
    ) == pytest.approx(
        (0.0, 1.0, -1.0),
        abs=1.0e-12,
    )

    assert all(
        item.drift_corrected_rms_pixels
        == pytest.approx(
            0.0,
            abs=1.0e-12,
        )
        for item in report.pass_statistics
    )


def test_anomalous_landmark_is_flagged(
    tmp_path: Path,
) -> None:
    paths = _write_passes(
        tmp_path,
        anomalous=True,
    )

    report = analyze_digitisation_passes(
        paths
    )

    assert report.review_flag_count >= 1
    assert report.landmarks[0].review_flag
    assert (
        report.landmarks[0]
        .maximum_pairwise_separation_pixels
        > 5.0
    )


def test_qc_output_writers(
    tmp_path: Path,
) -> None:
    paths = _write_passes(tmp_path)

    report = analyze_digitisation_passes(
        paths
    )

    landmark_path = write_landmark_qc_csv(
        tmp_path / "landmarks.csv",
        report,
    )

    pass_path = write_pass_qc_csv(
        tmp_path / "passes.csv",
        report,
    )

    category_path = write_category_qc_csv(
        tmp_path / "categories.csv",
        report,
    )

    markdown_path = write_qc_markdown(
        tmp_path / "report.md",
        report,
    )

    assert landmark_path.exists()
    assert pass_path.exists()
    assert category_path.exists()
    assert markdown_path.exists()

    text = markdown_path.read_text(
        encoding="utf-8"
    )

    assert "Status: **PASS**" in text
    assert "Total measured points: 93" in text
    assert "Pass-level statistics" in text
