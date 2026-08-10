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
    / "v0.9_one_trisection_heptagon_protocol.md"
)

EXPECTED_PROTOCOL_SHA256 = (
    "d125a37b1764c6dee558b36279dc45cfa10b2df6627d76ebecfba6b727fe629c"
)

EXPECTED_PHASE9B_COMMIT = (
    "76397adf7e2af00907e570d262a35836868a623c"
)

FROZEN_PHASE9B = {
    (
        ROOT
        / "docs"
        / "specification"
        / "v0.9_native_incidence_registry.md"
    ): (
        "e26b1725d44ce2454324b97d4b63d11e"
        "e8e371cfabef64c1f2da3bb7835cfc35"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "exact_sevenfold_boundary.py"
    ): (
        "81be21198b4ec7d1efea59b7512a7d4d"
        "8fa91fd00427ab54b8ce153c10abf7a9"
    ),
    (
        ROOT
        / "scripts"
        / "analyze_v0_9_exact_sevenfold_boundary.py"
    ): (
        "f4ea398dafcea4621cf7bd85b7a203b2"
        "03632241b9d25e138100885169c34877"
    ),
    (
        ROOT
        / "tests"
        / "test_v0_9_exact_sevenfold_boundary.py"
    ): (
        "26ccb6bc3c6e728d186c470fd740aa697"
        "8268f159e5cfa83b65ebb0f0ae4d37e"
    ),
    (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_9"
        / "exact_sevenfold_boundary.json"
    ): (
        "cc150e2c92efdebe130f86f2c03998336"
        "883abb985513e8e634977682c84442f"
    ),
    (
        ROOT
        / "docs"
        / "geometry"
        / "v0.9_exact_sevenfold_boundary_result.md"
    ): (
        "90e6067f21ef9d11f891ca786110f360"
        "3394ce1439c868c48588f54691f5dab5"
    ),
}


def _sha256(
    path: Path,
) -> str:
    return hashlib.sha256(
        path.read_bytes()
    ).hexdigest()


def _text() -> str:
    return PROTOCOL.read_text(
        encoding="utf-8"
    )


def test_protocol_hash_is_frozen() -> None:
    assert (
        _sha256(
            PROTOCOL
        )
        == EXPECTED_PROTOCOL_SHA256
    )


def test_phase9b_content_boundary_is_frozen() -> None:
    for path, digest in FROZEN_PHASE9B.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_phase9b_commit_is_recorded() -> None:
    assert (
        EXPECTED_PHASE9B_COMMIT
        in _text()
    )


def test_candidate_is_explicitly_post_phase9b() -> None:
    text = " ".join(
        _text().split()
    )

    required = (
        "not** a blind discovery phase",
        "identified after Phase 9B",
        "before any executable one-trisection construction",
        "no alternative angle",
    )

    for phrase in required:
        assert phrase in text


def test_exactly_one_extension_operation_is_registered() -> None:
    text = _text()

    required = (
        "TRISECT_ANGLE calls = exactly 1",
        "No second cubic-capable operation is allowed",
        "non_euclidean_operations = 1",
        "non_euclidean_operation_type = TRISECT_ANGLE",
    )

    for phrase in required:
        assert phrase in text


def test_native_metric_anchor_is_fixed() -> None:
    text = _text()

    required = (
        "R = 7",
        "D = 3",
        "u = R - 2*D",
        "= 1",
        "v = D*sqrt(3)",
        "= 3*sqrt(3)",
        "H = sqrt(u^2 + v^2)",
        "= 2*sqrt(7)",
        "Theta = atan(v/u)",
        "= atan(3*sqrt(3))",
        "cos(Theta) = 1/(2*sqrt(7))",
    )

    for phrase in required:
        assert phrase in text


def test_cubic_reconstruction_is_frozen() -> None:
    text = _text()

    required = (
        "z = (2*sqrt(7)/3)*cos(phi)",
        "y = z - 1/3",
        "z^3 - (7/3)*z - 7/27 = 0",
        "y^3 + y^2 - 2*y - 1 = 0",
    )

    for phrase in required:
        assert phrase in text


def test_root_selection_is_interval_based() -> None:
    text = _text()

    required = (
        "0 < phi < pi/6",
        "(sqrt(21)-1)/3",
        "(2*sqrt(7)-1)/3",
        "1 < y < 2",
        "f'(y) = 3*y^2 + 2*y - 2",
        "f'(y) > 0",
        "not a nearest-root numerical choice",
    )

    for phrase in required:
        assert phrase in text


def test_builder_target_injection_is_forbidden() -> None:
    text = _text()

    required = (
        "2*pi/7",
        "pi/7",
        "cos(2*pi/7)",
        "ObliqueModel.DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "separation/021-078",
        "The verifier may compare",
    )

    for phrase in required:
        assert phrase in text


def test_no_search_rule_is_explicit() -> None:
    text = _text()

    required = (
        "no angle search",
        "no native-anchor search",
        "no alternative depressed-cubic substitution",
        "no root-branch optimization",
        "no neusis parameter search",
        "no origami fold search",
        "no conic search",
        "no Method 1 / Method 2 averaging",
    )

    for phrase in required:
        assert phrase in text


def test_minimality_claim_is_narrowly_defined() -> None:
    text = _text()

    required = (
        "0 operations:",
        "excluded by frozen Phase 9B",
        "1 operation:",
        "minimum in **number of permitted cubic-capable operations",
        "not a claim that angle trisection is uniquely simplest",
    )

    for phrase in required:
        assert phrase in text


def test_historical_interpretation_boundary_is_explicit() -> None:
    text = " ".join(
        _text().split()
    )

    required = (
        "Michell knew this construction",
        "Sommerville knew this construction",
        "intentionally encoded",
        "ancient provenance",
        "physical or metaphysical significance",
        "sufficient to host a one-trisection exact-heptagon construction",
    )

    for phrase in required:
        assert phrase in text


def test_package_version_remains_0_8_0() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
