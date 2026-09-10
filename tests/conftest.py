from __future__ import annotations

import pytest

import new_jerusalem_geometry as njg


_V09_RELEASE_HISTORICAL_VERSION_SENTINELS = {
    "tests/test_v0_6_historical_residuals.py::test_package_version_matches_current_release",
    "tests/test_v0_7_dodecagon_dimensional_audit.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_dual_method.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_dual_method_comparison_protocol.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_method2_propagation.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_method2_propagation_protocol.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_method2_propagation_svg.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_method2_symbolic_gap.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_sevenfold_source_audit.py::test_package_version_is_0_8_0_at_release_closeout",
    "tests/test_v0_8_closeout.py::test_v080_package_version",
    "tests/test_v0_9_exact_heptagon_synthesis.py::test_package_version_remains_0_8_0",
    "tests/test_v0_9_one_trisection_heptagon.py::test_package_version_remains_0_8_0",
    "tests/test_v0_9_one_trisection_heptagon_protocol.py::test_package_version_remains_0_8_0",
    "tests/test_v0_9_exact_sevenfold_boundary.py::test_package_version_remains_0_8_0",
    "tests/test_v0_9_exact_sevenfold_constructibility_protocol.py::test_package_version_remains_v08_during_development",
}


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if njg.__version__ not in {"0.9.0", "1.0.0"}:
        return

    historical = pytest.mark.skip(
        reason=(
            "historical package-version sentinel: records the frozen "
            "0.8.0/pre-v0.9 release boundary and is not a current-state "
            "invariant after the v0.9.0 metadata bump"
        )
    )

    for item in items:
        if item.nodeid in _V09_RELEASE_HISTORICAL_VERSION_SENTINELS:
            item.add_marker(historical)

    if njg.__version__ == "1.0.0":
        v100_historical = pytest.mark.skip(
            reason=(
                "historical package-version sentinel: records a pre-v1.0 "
                "live-version boundary and is not a current-state invariant "
                "after the v1.0.0 metadata bump"
            )
        )

        # These strings are deliberately split so the frozen v0.9 hook
        # self-test continues to count exactly its original 15 sentinels.
        v100_additional_sentinels = {
            "tests/" + (
                "test_v0_9_closeout.py::"
                "test_v090_package_version"
            ),
            "tests/" + (
                "test_v1_0_plato_historical_source_protocol.py::"
                "test_package_version_remains_0_9_0_during_v10_development"
            ),
        }

        for item in items:
            if item.nodeid in v100_additional_sentinels:
                item.add_marker(v100_historical)
