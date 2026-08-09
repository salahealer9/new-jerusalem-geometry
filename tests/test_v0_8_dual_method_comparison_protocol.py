from __future__ import annotations

import hashlib
from pathlib import Path

import new_jerusalem_geometry as njg


ROOT = Path(
    __file__
).resolve().parents[
    1
]

PROTOCOL = (
    ROOT
    / "docs"
    / "specification"
    / "v0.8_dual_method_numerical_comparison_protocol.md"
)

METHOD1 = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "septenary_geometry.py"
)


def _text() -> str:
    return PROTOCOL.read_text(
        encoding="utf-8"
    )


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def test_protocol_exists() -> None:
    assert PROTOCOL.is_file()


def test_protocol_binds_phase8a_commit() -> None:
    assert (
        "d30a384"
        in _text()
    )


def test_protocol_binds_phase8a_hashes() -> None:
    text = _text()

    required = (
        "c3ac054a93c73e42ebf915fe8d43768e90008495c8dc3f369894c5969ef8ed10",
        "48a7892bb7be5ebd1b0cfdc2e66f0de7a4f380b6926d7a1799c6693e7dd441b4",
        "247caef1ac52ef3ec275e5ce161300ff46dd5cdffc11cef77145a32b7c54fc28",
    )

    for digest in required:
        assert digest in text


def test_protocol_binds_current_method1_source_hash() -> None:
    digest = _sha256(
        METHOD1
    )

    assert digest in _text()


def test_exact_reference_and_method2_identity_are_registered() -> None:
    text = _text()

    assert (
        "alpha_exact = 2*pi/7"
        in text
    )

    assert (
        "alpha_2 = acos(5/8)"
        in text
    )


def test_primary_residual_formulas_are_registered() -> None:
    text = _text()

    required = (
        "signed_residual_i",
        "absolute_residual_i",
        "relative_residual_i",
        "percent_residual_i",
        "absolute_percent_residual_i",
        "seven_step_closure_i",
    )

    for phrase in required:
        assert phrase in text


def test_all_five_relationship_tests_are_registered() -> None:
    text = _text()

    required = (
        "R1 — bracketing",
        "R2 — opposite signed errors",
        "R3 — absolute-accuracy ordering",
        "R4 — absolute-error ratio",
        "R5 — arithmetic midpoint",
    )

    for phrase in required:
        assert phrase in text


def test_midpoint_is_explicitly_exploratory() -> None:
    text = _text()

    assert (
        "This is explicitly exploratory/descriptive."
        in text
    )

    prohibited_interpretations = (
        "a third Michell construction",
        "an intended averaging scheme",
        "a tuned correction",
        "evidence of deliberate compensation",
    )

    for phrase in prohibited_interpretations:
        assert phrase in text


def test_zero_fit_degrees_of_freedom_are_registered() -> None:
    text = _text()

    required = (
        "new continuous fitted parameters: 0",
        "new scale parameters:             0",
        "target-based candidate choices:   0",
        "plate-registration parameters:    0",
        "optimized combination weights:    0",
    )

    for phrase in required:
        assert phrase in text


def test_21_and_42_propagation_are_deferred() -> None:
    text = _text()

    assert (
        "Method 2: 7 -> 21 propagation"
        in text
    )

    assert (
        "Method 2: 21 -> 42 reciprocal-triangle propagation"
        in text
    )


def test_protocol_contains_no_precomputed_decimal_outcomes() -> None:
    text = _text()

    forbidden = (
        "51.470701",
        "51.317812",
        "51.428571",
        "0.042130",
        "0.110758",
        "0.294910",
        "0.775312",
    )

    for literal in forbidden:
        assert literal not in text


def test_protocol_does_not_modify_package_version() -> None:
    assert (
        njg.__version__
        == "0.7.0"
    )


def test_stopping_rule_is_outcome_independent() -> None:
    text = _text()

    assert (
        "DUAL_METHOD_LOCAL_COMPARISON_COMPLETE"
        in text
    )

    assert (
        "does not depend on whether either method is closer"
        in text
    )


def test_protocol_defers_figure14_and_plate_calibration() -> None:
    text = _text()

    assert (
        "use Figure 14 or any plate calibration"
        in text
    )

    assert (
        "Figure 14 downstream comparison"
        in text
    )
