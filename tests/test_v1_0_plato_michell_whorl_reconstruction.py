from __future__ import annotations

from pathlib import Path
import hashlib
import importlib.util
import json


ROOT = Path(__file__).resolve().parents[1]

SCRIPT = (
    ROOT
    / "scripts"
    / "reconstruct_v1_0_plato_michell_whorls.py"
)

JSON_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_whorl_reconstruction.json"
)

MARKDOWN_PATH = (
    ROOT
    / "docs"
    / "geometry"
    / "v1.0_plato_michell_whorl_reconstruction.md"
)

PLATO_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_myth_of_er_literal.json"
)

MICHELL_PATH = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "michell_2008_ch4_literal.json"
)


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _payload() -> dict:
    return json.loads(
        JSON_PATH.read_text(
            encoding="utf-8"
        )
    )


def _load_script_module():
    spec = importlib.util.spec_from_file_location(
        "phase10e_reconstruction",
        SCRIPT,
    )

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(
        spec
    )

    spec.loader.exec_module(
        module
    )

    return module


def test_phase10e_frozen_input_hashes() -> None:
    assert (
        _sha256(
            PLATO_PATH
        )
        == (
            "42edbe735c6d91bc180198702f411889e"
            "05ea503989c24b0d44a134362a63f3c"
        )
    )

    assert (
        _sha256(
            MICHELL_PATH
        )
        == (
            "ef6e17b7d9de47157025a2bf3aa9812d"
            "79859a5cc3b7bbe44185a67bacc99807"
        )
    )


def test_phase10e_status_and_provenance() -> None:
    payload = _payload()

    assert (
        payload[
            "status"
        ]
        == (
            "MICHELL_PLATO_NUMERICAL_"
            "RECONSTRUCTION_COMPLETE"
        )
    )

    assert (
        payload[
            "provenance_class"
        ]
        == "PROJECT_RECONSTRUCTION"
    )


def test_phase10e_plato_and_michell_ordinal_orders_match() -> None:
    inputs = _payload()[
        "source_inputs"
    ]

    assert (
        inputs[
            "plato_width_order_broadest_to_narrowest"
        ]
        == [
            1,
            6,
            4,
            8,
            7,
            5,
            3,
            2,
        ]
    )

    assert (
        inputs[
            "plato_width_order_broadest_to_narrowest"
        ]
        == inputs[
            "michell_width_order_broadest_to_narrowest"
        ]
    )


def test_phase10e_rank_assignment_is_deterministic() -> None:
    reconstructed = _payload()[
        "reconstructed"
    ]

    assert (
        reconstructed[
            "descending_numbers_assigned_by_width_rank"
        ]
        == [
            36,
            27,
            24,
            18,
            12,
            9,
            8,
            6,
        ]
    )

    assert (
        reconstructed[
            "width_by_whorl"
        ]
        == {
            "1": 36,
            "2": 6,
            "3": 8,
            "4": 24,
            "5": 9,
            "6": 27,
            "7": 12,
            "8": 18,
        }
    )


def test_phase10e_center_out_widths() -> None:
    reconstructed = _payload()[
        "reconstructed"
    ]

    assert (
        reconstructed[
            "center_out_whorls"
        ]
        == [
            8,
            7,
            6,
            5,
            4,
            3,
            2,
            1,
        ]
    )

    assert (
        reconstructed[
            "center_out_ring_widths"
        ]
        == [
            18,
            12,
            27,
            9,
            24,
            8,
            6,
            36,
        ]
    )


def test_phase10e_exact_cumulative_radii() -> None:
    reconstructed = _payload()[
        "reconstructed"
    ]

    assert (
        reconstructed[
            "shaft_radius"
        ]
        == 4
    )

    assert (
        reconstructed[
            "cumulative_radii_including_shaft"
        ]
        == [
            4,
            22,
            34,
            61,
            70,
            94,
            102,
            108,
            144,
        ]
    )

    assert (
        reconstructed[
            "full_radius"
        ]
        == 144
    )


def test_phase10e_scaled_integer_construction() -> None:
    reconstructed = _payload()[
        "reconstructed"
    ]

    assert (
        reconstructed[
            "scale_factor"
        ]
        == 180
    )

    assert (
        reconstructed[
            "scaled_shaft_radius"
        ]
        == 720
    )

    assert (
        reconstructed[
            "scaled_ring_widths"
        ]
        == [
            3240,
            2160,
            4860,
            1620,
            4320,
            1440,
            1080,
            6480,
        ]
    )

    assert (
        reconstructed[
            "scaled_cumulative_radii_including_shaft"
        ]
        == [
            720,
            3960,
            6120,
            10980,
            12600,
            16920,
            18360,
            19440,
            25920,
        ]
    )

    assert (
        reconstructed[
            "scaled_total_whorl_width"
        ]
        == 25200
    )

    assert (
        reconstructed[
            "scaled_outer_radius"
        ]
        == 25920
    )


def test_phase10e_interval_ratios_are_exact() -> None:
    assert (
        _payload()[
            "reconstructed"
        ][
            "successive_interval_ratios"
        ]
        == [
            "4/3",
            "9/8",
            "4/3",
            "3/2",
            "4/3",
            "9/8",
            "4/3",
        ]
    )


def test_phase10e_all_michell_printed_values_reproduced() -> None:
    checks = _payload()[
        "exact_validation_against_michell_printed_values"
    ]

    assert checks
    assert all(
        checks.values()
    )


def test_phase10e_printed_correspondence_values_reproduced() -> None:
    checks = _payload()[
        "printed_correspondence_value_checks"
    ]

    assert (
        checks
        == {
            "central_spindle_radius_720": True,
            "first_cumulative_radius_3960": True,
            "second_cumulative_radius_6120": True,
            "second_ring_width_2160": True,
        }
    )


def test_phase10e_has_zero_fit_degrees_of_freedom() -> None:
    algorithm = _payload()[
        "deterministic_algorithm"
    ]

    assert (
        algorithm[
            "free_parameters"
        ]
        == 0
    )

    assert (
        algorithm[
            "permutation_searches"
        ]
        == 0
    )

    assert (
        algorithm[
            "scale_fits"
        ]
        == 0
    )

    assert (
        algorithm[
            "optimizations"
        ]
        == 0
    )

    assert (
        algorithm[
            "nearest_match_choices"
        ]
        == 0
    )


def test_phase10e_historical_boundary() -> None:
    boundary = _payload()[
        "historical_boundary"
    ]

    assert (
        boundary[
            "plato_supplies_numeric_widths"
        ]
        is False
    )

    assert (
        boundary[
            "michell_supplies_numeric_interpretation"
        ]
        is True
    )

    assert (
        boundary[
            "project_arithmetic_reproduces_michell"
        ]
        is True
    )

    assert (
        boundary[
            "historical_transmission_established"
        ]
        is False
    )

    assert (
        boundary[
            "plato_intention_established"
        ]
        is False
    )


def test_phase10e_regeneration_is_deterministic() -> None:
    module = _load_script_module()

    before_json = JSON_PATH.read_bytes()
    before_markdown = MARKDOWN_PATH.read_bytes()

    module.write_outputs()

    assert (
        JSON_PATH.read_bytes()
        == before_json
    )

    assert (
        MARKDOWN_PATH.read_bytes()
        == before_markdown
    )


def test_phase10e_markdown_boundary() -> None:
    text = MARKDOWN_PATH.read_text(
        encoding="utf-8"
    )

    required = (
        "1 > 6 > 4 > 8 > 7 > 5 > 3 > 2",
        "18, 12, 27, 9, 24, 8, 6, 36",
        "4, 22, 34, 61, 70, 94, 102, 108, 144",
        "free parameters: 0",
        "does **not** show that Plato supplied",
    )

    for phrase in required:
        assert phrase in text

