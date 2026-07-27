import csv
from collections import Counter
from pathlib import Path

import pytest

from new_jerusalem_geometry import (
    build_core_geometry,
)
from new_jerusalem_geometry.figure14_digitisation import (
    build_figure14_landmark_schema,
    read_landmark_schema_csv,
    write_digitisation_csv,
    write_landmark_schema_csv,
)


def _schema():
    return build_figure14_landmark_schema(
        build_core_geometry()
    )


def test_figure14_landmark_schema_counts() -> None:
    schema = _schema()

    assert len(schema) == 31

    counts = Counter(
        landmark.category
        for landmark in schema
    )

    assert counts == {
        "square_corner": 4,
        "square_circle_junction": 8,
        "moon_centre": 12,
        "star_endpoint": 7,
    }

    assert tuple(
        landmark.sequence_index
        for landmark in schema
    ) == tuple(range(31))


def test_registration_defaults_are_source_invariant() -> None:
    schema = _schema()

    registration = tuple(
        landmark
        for landmark in schema
        if landmark.registration_default
    )

    assert len(registration) == 12

    assert {
        landmark.category
        for landmark in registration
    } == {
        "square_corner",
        "square_circle_junction",
    }


def test_star_endpoints_have_no_assumed_model_coordinates() -> None:
    schema = _schema()

    endpoints = tuple(
        landmark
        for landmark in schema
        if landmark.category == "star_endpoint"
    )

    assert len(endpoints) == 7

    assert all(
        landmark.model_x is None
        and landmark.model_y is None
        and not landmark.registration_default
        for landmark in endpoints
    )


def test_landmark_schema_csv_round_trip(
    tmp_path: Path,
) -> None:
    schema = _schema()
    path = tmp_path / "schema.csv"

    returned = write_landmark_schema_csv(
        path,
        schema,
    )

    assert returned == path
    assert path.exists()

    recovered = read_landmark_schema_csv(
        path
    )

    assert recovered == schema


def test_write_complete_digitisation_csv(
    tmp_path: Path,
) -> None:
    schema = _schema()

    source_image = tmp_path / "source.png"
    source_image.write_bytes(
        b"fixed rendered source"
    )

    points = tuple(
        (
            100.0 + index,
            200.5 + index,
        )
        for index in range(len(schema))
    )

    output = tmp_path / "pass-01.csv"

    returned = write_digitisation_csv(
        output,
        schema=schema,
        points=points,
        pass_id="pass-01",
        source_image=source_image,
        image_width_pixels=1512,
        image_height_pixels=2327,
    )

    assert returned == output

    with output.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 31
    assert rows[0]["pass_id"] == "pass-01"
    assert rows[0]["image_width_pixels"] == "1512"
    assert rows[0]["image_height_pixels"] == "2327"
    assert rows[0]["landmark_id"] == (
        "square_corner_top_left"
    )

    assert rows[-1]["landmark_id"] == (
        "star_endpoint_06_upper_right"
    )

    assert rows[-1]["model_x"] == ""
    assert rows[-1]["model_y"] == ""

    with pytest.raises(
        ValueError,
        match="point count",
    ):
        write_digitisation_csv(
            tmp_path / "incomplete.csv",
            schema=schema,
            points=points[:-1],
            pass_id="pass-incomplete",
            source_image=source_image,
            image_width_pixels=1512,
            image_height_pixels=2327,
        )
