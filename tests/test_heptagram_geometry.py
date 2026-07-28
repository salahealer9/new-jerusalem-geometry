from math import pi
from statistics import mean, pstdev

import pytest

from new_jerusalem_geometry import (
    AnchorEvidence,
    Figure14AnchorRole,
    HeptagramFamily,
    build_core_geometry,
    build_figure14_aligned_heptagram,
    build_figure14_anchor_set,
    build_regular_heptagram,
    build_scaffold_heptagram,
    verify_figure14_heptagrams,
)


def _report():
    diagram = build_core_geometry()
    anchors = build_figure14_anchor_set(diagram)
    regular = build_regular_heptagram(diagram)
    scaffold = build_scaffold_heptagram(diagram)
    aligned = build_figure14_aligned_heptagram(
        diagram
    )

    report = verify_figure14_heptagrams(
        diagram,
        anchors,
        regular,
        scaffold,
        aligned,
    )

    return (
        diagram,
        anchors,
        regular,
        scaffold,
        aligned,
        report,
    )


def test_figure14_anchor_roles_and_evidence() -> None:
    _, anchors, _, _, _, _ = _report()

    assert len(anchors) == 7

    roles = [anchor.role for anchor in anchors]
    evidence = [anchor.evidence for anchor in anchors]

    assert roles.count(
        Figure14AnchorRole.MOON_CENTRE
    ) == 3

    assert roles.count(
        Figure14AnchorRole.SQUARE_CIRCLE_JUNCTION
    ) == 2

    assert roles.count(
        Figure14AnchorRole.INTER_MOON_GAP
    ) == 2

    assert evidence.count(
        AnchorEvidence.SOURCE_TEXT_AND_PLATE
    ) == 5

    assert evidence.count(
        AnchorEvidence.PLATE_INFERENCE
    ) == 2


def test_figure14_anchor_angles() -> None:
    _, anchors, _, _, _, _ = _report()

    angles = tuple(
        anchor.angle_degrees
        for anchor in anchors
    )

    assert angles == pytest.approx(
        (
            90.0,
            141.78678929826182,
            192.95596552292805,
            244.08806895414388,
            295.9119310458561,
            347.04403447707195,
            38.21321070173819,
        ),
        abs=1.0e-12,
    )


def test_all_figure14_anchors_lie_on_zodiac_circle() -> None:
    diagram, anchors, _, _, _, _ = _report()

    assert tuple(
        anchor.radius
        for anchor in anchors
    ) == pytest.approx(
        (diagram.construction_circle.radius,) * 7,
        abs=1.0e-12,
    )


def test_figure14_anchor_system_is_reflection_symmetric() -> None:
    _, anchors, _, _, _, _ = _report()

    for left_index, right_index in (
        (1, 6),
        (2, 5),
        (3, 4),
    ):
        left = anchors[left_index].point
        right = anchors[right_index].point

        assert left.x == pytest.approx(
            -right.x,
            abs=1.0e-12,
        )

        assert left.y == pytest.approx(
            right.y,
            abs=1.0e-12,
        )


def test_figure14_uses_source_supported_step2_traversal() -> None:
    _, _, regular, _, _, _ = _report()

    assert regular.family is HeptagramFamily.STEP_2

    assert regular.traversal_indices() == (
        0,
        2,
        4,
        6,
        1,
        3,
        5,
    )

    assert regular.edge_index_pairs() == (
        (0, 2),
        (2, 4),
        (4, 6),
        (6, 1),
        (1, 3),
        (3, 5),
        (5, 0),
    )


def test_regular_heptagram_has_equal_edges() -> None:
    _, _, regular, _, _, _ = _report()

    lengths = regular.edge_lengths()

    assert max(lengths) - min(lengths) < 1.0e-12


def test_scaffold_heptagram_selected_angles() -> None:
    _, _, _, scaffold, _, _ = _report()

    angles = []

    for point in scaffold.vertices:
        angle = (
            __import__("math").atan2(
                point.y,
                point.x,
            )
            * 180.0
            / pi
        )

        if angle < 0.0:
            angle += 360.0

        angles.append(angle)

    assert tuple(angles) == pytest.approx(
        (
            90.0,
            141.47070143243994,
            192.9414028648799,
            244.41210429731987,
            295.58789570268016,
            347.0585971351201,
            38.52929856756003,
        ),
        abs=1.0e-12,
    )


def test_figure14_verification_passes() -> None:
    _, _, _, _, _, report = _report()

    assert report.passed
    assert report.moon_centre_count == 3
    assert report.junction_count == 2
    assert report.gap_count == 2

    assert sum(
        report.anchor_step_angles_radians
    ) == pytest.approx(
        2.0 * pi,
        abs=1.0e-12,
    )


def test_candidate_fit_metrics() -> None:
    _, _, _, _, _, report = _report()

    assert report.regular_fit.maximum_point_residual \
        == pytest.approx(
            0.04376449758023334,
            abs=1.0e-12,
        )

    assert report.regular_fit.rms_point_residual \
        == pytest.approx(
            0.02748596302093325,
            abs=1.0e-12,
        )

    assert report.scaffold_fit.maximum_point_residual \
        == pytest.approx(
            0.03958833265983687,
            abs=1.0e-12,
        )

    assert report.scaffold_fit.rms_point_residual \
        == pytest.approx(
            0.029576548096559897,
            abs=1.0e-12,
        )

    assert report.aligned_fit.maximum_point_residual \
        == pytest.approx(
            0.0,
            abs=1.0e-12,
        )


def test_aligned_star_has_small_nonregularity() -> None:
    _, _, regular, scaffold, aligned, _ = _report()

    def coefficient_of_variation(
        lengths: tuple[float, ...],
    ) -> float:
        return pstdev(lengths) / mean(lengths)

    assert coefficient_of_variation(
        regular.edge_lengths()
    ) < 1.0e-12

    assert coefficient_of_variation(
        scaffold.edge_lengths()
    ) == pytest.approx(
        0.0009278022133903409,
        abs=1.0e-15,
    )

    assert coefficient_of_variation(
        aligned.edge_lengths()
    ) == pytest.approx(
        0.002845183908818653,
        abs=1.0e-15,
    )
