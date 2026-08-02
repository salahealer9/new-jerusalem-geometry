from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from new_jerusalem_geometry.figure12_digitisation import (
    MOON_OBJECT_IDS,
    WALL_OBJECT_IDS,
    Figure12DigitisedObservation,
    build_figure12_observation_schema,
    read_figure12_digitisation_pass_csv,
    read_figure12_observation_schema_csv,
    write_figure12_digitisation_pass_csv,
    write_figure12_observation_schema_csv,
)


def test_schema_has_fixed_observation_counts() -> None:
    schema = build_figure12_observation_schema()

    counts = Counter(
        item.category
        for item in schema
    )

    assert len(schema) == 120

    assert counts == {
        "square_corner": 4,
        "square_circle_junction": 8,
        "moon_circumference": 72,
        "wall_line": 36,
    }


def test_only_registration_observations_have_model_coordinates() -> None:
    schema = build_figure12_observation_schema()

    registration = tuple(
        item
        for item in schema
        if item.registration_default
    )

    assert len(registration) == 12

    for item in schema:
        if item.registration_default:
            assert item.model_x is not None
            assert item.model_y is not None
        else:
            assert item.model_x is None
            assert item.model_y is None


def test_registration_landmarks_have_expected_coordinates() -> None:
    schema = build_figure12_observation_schema()

    by_id = {
        item.observation_id: item
        for item in schema
    }

    q = (75.0 / 4.0) ** 0.5

    assert by_id[
        "square_corner_top_left"
    ].model_x == pytest.approx(-5.5)

    assert by_id[
        "square_corner_top_left"
    ].model_y == pytest.approx(+5.5)

    assert by_id[
        "square_corner_bottom_right"
    ].model_x == pytest.approx(+5.5)

    assert by_id[
        "square_corner_bottom_right"
    ].model_y == pytest.approx(-5.5)

    assert by_id[
        "junction_top_left"
    ].model_x == pytest.approx(-q)

    assert by_id[
        "junction_top_left"
    ].model_y == pytest.approx(+5.5)

    assert by_id[
        "junction_right_lower"
    ].model_x == pytest.approx(+5.5)

    assert by_id[
        "junction_right_lower"
    ].model_y == pytest.approx(-q)


def test_each_moon_has_six_source_samples() -> None:
    schema = build_figure12_observation_schema()

    for moon_id in MOON_OBJECT_IDS:
        rows = [
            item
            for item in schema
            if item.object_id == moon_id
        ]

        assert len(rows) == 6

        assert [
            item.sample_index
            for item in rows
        ] == [1, 2, 3, 4, 5, 6]


def test_each_wall_side_has_three_source_samples() -> None:
    schema = build_figure12_observation_schema()

    for wall_id in WALL_OBJECT_IDS:
        rows = [
            item
            for item in schema
            if item.object_id == wall_id
        ]

        assert len(rows) == 3

        assert [
            item.sample_index
            for item in rows
        ] == [1, 2, 3]


def test_schema_roundtrip(
    tmp_path: Path,
) -> None:
    schema = build_figure12_observation_schema()

    path = tmp_path / "schema.csv"

    write_figure12_observation_schema_csv(
        path,
        schema,
    )

    loaded = (
        read_figure12_observation_schema_csv(
            path
        )
    )

    assert loaded == schema


def test_complete_pass_roundtrip(
    tmp_path: Path,
) -> None:
    schema = build_figure12_observation_schema()

    observations = tuple(
        Figure12DigitisedObservation(
            pass_id="pass-01",
            definition=item,
            pixel_x=100.0 + item.sequence_index,
            pixel_y=200.0 + item.sequence_index,
            source_image="source.png",
            source_image_sha256="a" * 64,
            image_width_pixels=1512,
            image_height_pixels=2327,
        )
        for item in schema
    )

    path = tmp_path / "pass.csv"

    write_figure12_digitisation_pass_csv(
        path,
        observations,
    )

    loaded = (
        read_figure12_digitisation_pass_csv(
            path
        )
    )

    assert loaded == observations


def test_partial_pass_must_be_contiguous_prefix(
    tmp_path: Path,
) -> None:
    schema = build_figure12_observation_schema()

    observations = (
        Figure12DigitisedObservation(
            pass_id="pass-01",
            definition=schema[1],
            pixel_x=100.0,
            pixel_y=200.0,
            source_image="source.png",
            source_image_sha256="a" * 64,
            image_width_pixels=1512,
            image_height_pixels=2327,
        ),
    )

    with pytest.raises(
        ValueError,
        match="contiguous prefix",
    ):
        write_figure12_digitisation_pass_csv(
            tmp_path / "bad.csv",
            observations,
            require_complete=False,
        )
