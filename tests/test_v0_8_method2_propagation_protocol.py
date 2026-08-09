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
    / "v0.8_method2_propagation_protocol.md"
)

PHASE8C_MODULE = (
    ROOT
    / "src"
    / "new_jerusalem_geometry"
    / "sevenfold_dual_method.py"
)

PHASE8C_JSON = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v0_8"
    / "dual_method_comparison.json"
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


def test_protocol_binds_phase8c_commit() -> None:
    assert (
        "05e8a89"
        in _text()
    )


def test_protocol_binds_phase8c_hashes() -> None:
    text = _text()

    required = (
        "33c5fee3a1d198abc1eb73c1ff114829b1dc5a66f0e355605ed25793b33f5c70",
        "b13e532ec45e8c1c7ba0872c53d81c453696814741f45a4fac46c73924a1a056",
        "0f7ad7a71a256a879590d493c546a1e11d1292bd1fe4505854257136f72a4107",
        "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f",
        "43a30345489d2fb0e7e77c60fbd2b3f17a67560f891243576f557437778b6cc4",
    )

    for digest in required:
        assert digest in text


def test_frozen_phase8c_files_still_match_protocol() -> None:
    assert (
        _sha256(
            PHASE8C_MODULE
        )
        == "33c5fee3a1d198abc1eb73c1ff114829b1dc5a66f0e355605ed25793b33f5c70"
    )

    assert (
        _sha256(
            PHASE8C_JSON
        )
        == "e5de2cf65eaeac7884d11a3617479a52a3aeefa28e45bd89cd3fe4e6172e396f"
    )


def test_method2_step_is_frozen_as_acos_five_eighths() -> None:
    text = _text()

    assert (
        "alpha_2 = acos(5/8)"
        in text
    )

    assert (
        "reuse the frozen Phase 8C implementation"
        in text
    )


def test_local_seven_completion_is_preregistered() -> None:
    text = _text()

    required = (
        "k in {-3, -2, -1, 0, 1, 2, 3}",
        "theta(gamma, k)",
        "normalize(gamma + k*alpha_2)",
        "project operationalization",
    )

    for phrase in required:
        assert phrase in text


def test_twenty_one_carriers_are_frozen() -> None:
    text = _text()

    assert (
        "gamma_0 + j*(2*pi/3)"
        in text
    )

    assert (
        "j in {0, 1, 2}"
        in text
    )

    assert (
        "No proximity-based deduplication is allowed."
        in text
    )


def test_forty_two_carriers_are_frozen() -> None:
    text = _text()

    assert (
        "gamma_0 + n*(pi/3)"
        in text
    )

    assert (
        "n in {0, 1, 2, 3, 4, 5}"
        in text
    )

    assert (
        "even n:"
        in text
    )

    assert (
        "odd n:"
        in text
    )


def test_global_phase_is_fixed_not_fitted() -> None:
    text = _text()

    assert (
        "gamma_0 = pi/2"
        in text
    )

    assert (
        "not a fitted parameter"
        in text
    )


def test_identity_tolerance_is_frozen_and_non_evidential() -> None:
    text = _text()

    assert (
        "identity_tolerance_radians = 1e-12"
        in text
    )

    assert (
        "not a goodness-of-fit threshold"
        in text
    )


def test_all_five_structural_identities_are_registered() -> None:
    text = _text()

    required = (
        "S1 — semantic cardinality",
        "S2 — original-triangle rotational identity",
        "S3 — reciprocal-triangle relationship",
        "S4 — 42-point decomposition",
        "S5 — hexagonal rotational identity",
    )

    for phrase in required:
        assert phrase in text


def test_cyclic_gap_algorithm_is_frozen() -> None:
    text = _text()

    required = (
        "normalize every angle to `[0, 2*pi)`",
        "sort all angles in ascending numeric order",
        "include the wraparound gap",
        "regular_gap_N = 2*pi/N",
        "signed_gap_residual_i",
        "absolute_gap_residual_i",
    )

    for phrase in required:
        assert phrase in text


def test_nonuniformity_metrics_are_frozen() -> None:
    text = _text()

    required = (
        "minimum_gap",
        "maximum_gap",
        "mean_gap",
        "gap_range",
        "rms_gap_residual",
        "maximum_absolute_gap_residual",
        "normalized_rms_gap_residual",
    )

    for phrase in required:
        assert phrase in text


def test_21_vs_42_comparison_is_outcome_neutral() -> None:
    text = _text()

    required = (
        "rms_ratio_42_over_21",
        "max_abs_ratio_42_over_21",
        "No direction of improvement is preregistered.",
    )

    for phrase in required:
        assert phrase in text


def test_zero_fit_degrees_of_freedom_are_registered() -> None:
    text = _text()

    required = (
        "new continuous fitted parameters: 0",
        "new scale parameters:             0",
        "target-based candidate choices:   0",
        "plate-registration parameters:    0",
        "optimized phase parameters:       0",
        "deduplication thresholds fitted:  0",
    )

    for phrase in required:
        assert phrase in text


def test_method1_28_and_figure14_are_deferred() -> None:
    text = _text()

    assert (
        "comparison of Method 2 42-point geometry with Method 1 28-point geometry"
        in text
    )

    assert (
        "Figure 14 downstream testing"
        in text
    )


def test_protocol_contains_no_precomputed_propagation_results() -> None:
    text = _text()

    forbidden = (
        "16.589062",
        "17.364374",
        "7.906875",
        "8.682187",
        "0.350250",
        "0.271302",
        "0.553794",
        "0.664553",
    )

    for literal in forbidden:
        assert literal not in text


def test_stopping_rule_is_outcome_independent() -> None:
    text = _text()

    assert (
        "METHOD2_7_21_42_PROPAGATION_COMPLETE"
        in text
    )

    assert (
        "whether either set is numerically regular"
        in text
    )

    assert (
        "whether 42 is more regular than 21"
        in text
    )


def test_package_version_remains_0_7_0() -> None:
    assert (
        njg.__version__
        == "0.7.0"
    )
