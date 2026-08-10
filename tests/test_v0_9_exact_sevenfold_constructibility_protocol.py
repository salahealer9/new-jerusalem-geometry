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
    / "v0.9_exact_sevenfold_constructibility_protocol.md"
)

FROZEN = {
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "septenary_geometry.py"
    ): (
        "419d38ac8b5a4d0201e6e0cb4ed05a8d"
        "776386286119885463fa95fae374fa6c"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "sevenfold_dual_method.py"
    ): (
        "33c5fee3a1d198abc1eb73c1ff114829b"
        "1dc5a66f0e355605ed25793b33f5c70"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "method2_propagation.py"
    ): (
        "8b28ee957a7ee210ee35dfe80f66bd642"
        "07e5c146da23623d859d6cc7d491a9d"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "method2_symbolic_gap.py"
    ): (
        "2f81fce15e6863a877e28c0ad0ffb1a9"
        "5a35c6186cfb5b42313d58077b1bdb2c"
    ),
    (
        ROOT
        / "src"
        / "new_jerusalem_geometry"
        / "method2_propagation_svg.py"
    ): (
        "3c6f7cc6b28688bba398c5b56db9007a"
        "e853a452f77825c9ec14f5d5662e202b"
    ),
    (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_8"
        / "dual_method_comparison.json"
    ): (
        "e5de2cf65eaeac7884d11a3617479a52"
        "a3aeefa28e45bd89cd3fe4e6172e396f"
    ),
    (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_8"
        / "method2_propagation.json"
    ): (
        "5af0b893ef9f18f5bb6c04e013f12298"
        "d816f426a2a248eccbd9230ab5ad4a43"
    ),
    (
        ROOT
        / "data"
        / "analysis"
        / "njg_michell_v0_8"
        / "method2_symbolic_gap_audit.json"
    ): (
        "db314c890636a2a435d4065a42c49c08"
        "bba8df00c7e29a2cca156b00eef47078"
    ),
    (
        ROOT
        / "docs"
        / "geometry"
        / "v0.8_figure194_dual_method_synthesis.md"
    ): (
        "956defbb3b47dce18f69bc30ca2804ead"
        "1d4da5c25c2e0dacc6f5e7013209dba"
    ),
    (
        ROOT
        / "docs"
        / "checkpoints"
        / "v0.8.0.md"
    ): (
        "9ddef73480641e7eae1ec0d3db4ff092"
        "5ce34bf5eff3c88564ddc16d7a9a4a5d"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_nodes.csv"
    ): (
        "5c13a735882ebb27c4e1b942bea605cf7"
        "6d76f996c486ca049325d7246735bc7"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_dependencies.csv"
    ): (
        "cdb8f7fc881851e2c52ba84fec5f2f80"
        "c51e45193c47eef4f11f6e42512657a5"
    ),
    (
        ROOT
        / "docs"
        / "specification"
        / "construction_grammar.md"
    ): (
        "3f2d7a4cb879565509be05dbc71f6cc8"
        "b5d8d57c54a7f7324393c9f71fe25110"
    ),
    (
        ROOT
        / "figures"
        / "generated"
        / "v0.8_method2_7_21_42.svg"
    ): (
        "11477e6db0ac662dd82d5cb23c73147c"
        "039683148720cecb56f39fc8cd8ee9a1"
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
        == "ac50f47c4a57000a831958b4e47381533768ed8cebe1d40d309e5c66e3aa2d22"
    )


def test_frozen_v08_surfaces_are_unchanged() -> None:
    for path, digest in FROZEN.items():
        assert (
            _sha256(
                path
            )
            == digest
        )


def test_protocol_has_three_separate_questions() -> None:
    text = _text()

    required = (
        "## Question A — Euclidean closure",
        "## Question B — native-incidence census",
        "## Question C — minimal cubic-capable extension",
    )

    for phrase in required:
        assert phrase in text


def test_target_polynomials_are_registered_before_execution() -> None:
    text = _text()

    required = (
        "f(y) = y^3 + y^2 - 2*y - 1",
        "g(c) = 8*c^3 + 4*c^2 - 4*c - 1",
        "[Q(y_7) : Q] = 3",
        "rational-root theorem",
    )

    for phrase in required:
        assert phrase in text


def test_primary_native_seed_tier_is_fixed() -> None:
    text = _text()

    required = (
        "CORE_DIMENSIONS",
        "EARTH_CIRCLE",
        "EARTH_SQUARE",
        "CONSTRUCTION_CIRCLE",
        "CARDINAL_MOONS",
        "SQUARE_CIRCLE_INTERSECTIONS",
        "NJG_INC_MOONS",
        "SEPTENARY_METHOD_1",
        "RECIPROCAL_TRIANGLE_14",
        "SCAFFOLD_28",
        "SEPTENARY_METHOD_2",
        "METHOD2_21",
        "METHOD2_42",
    )

    for phrase in required:
        assert phrase in text


def test_target_injected_reference_geometry_is_explicitly_excluded() -> None:
    text = _text()

    required = (
        "ObliqueModel.DIVISION_28",
        "NJG_28",
        "build_regular_heptagram",
        "free regular seven-vertex fits",
        "exact_heptagon_step_radians",
        "exact_heptagonal_step_radians",
        "any direct 2*pi/7 reference",
    )

    for phrase in required:
        assert phrase in text


def test_native_census_uses_symbolic_not_numeric_acceptance() -> None:
    text = _text()

    required = (
        "No numerical tolerance can establish",
        "symbolic algebra proves",
        "Near matches are not discoveries",
        "no tolerance",
        "no best-of-N selection",
    )

    for phrase in required:
        assert phrase in text


def test_question_c_is_deferred() -> None:
    text = _text()

    required = (
        "Question C is not executed",
        "No candidate neusis",
        "marked-ruler",
        "origami",
        "conic",
        "separately preregistered",
    )

    for phrase in required:
        assert phrase in text


def test_zero_fit_boundary_is_explicit() -> None:
    text = _text()

    required = (
        "continuous_fitted_parameters = 0",
        "scale_fitted_parameters = 0",
        "phase_optimized_parameters = 0",
        "target_based_candidate_choices = 0",
        "numerical_acceptance_tolerances = 0",
        "post_hoc_seed_additions = 0",
        "non_euclidean_operations = 0",
    )

    for phrase in required:
        assert phrase in text


def test_protocol_preserves_interpretation_boundary() -> None:
    text = _text()

    required = (
        "would not establish that Michell or Sommerville attempted every",
        "historical knowledge",
        "physical significance",
        "metaphysical significance",
    )

    for phrase in required:
        assert phrase in text


def test_package_version_remains_v08_during_development() -> None:
    assert (
        njg.__version__
        == "0.8.0"
    )
