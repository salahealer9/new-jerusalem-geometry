from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from new_jerusalem_geometry.plato_michell_whorl_svg import (
    SVG_NS,
    plato_michell_whorl_capstone_to_svg,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT = (
    ROOT
    / "data"
    / "analysis"
    / "njg_michell_v1_0"
    / "plato_michell_whorl_reconstruction.json"
)
OUTPUT = (
    ROOT
    / "figures"
    / "generated"
    / "v1.0_plato_michell_whorl_capstone.svg"
)


def _data() -> dict:
    return json.loads(INPUT.read_text(encoding="utf-8"))


def _root(svg: str | None = None) -> ET.Element:
    if svg is None:
        svg = plato_michell_whorl_capstone_to_svg(_data())
    return ET.fromstring(svg)


def _by_id(root: ET.Element, element_id: str) -> ET.Element:
    for element in root.iter():
        if element.get("id") == element_id:
            return element
    raise AssertionError(f"SVG element not found: {element_id}")


def test_renderer_is_deterministic() -> None:
    data = _data()
    first = plato_michell_whorl_capstone_to_svg(data)
    second = plato_michell_whorl_capstone_to_svg(data)
    assert first == second


def test_svg_root_records_phase_10e_provenance() -> None:
    data = _data()
    root = _root()

    assert root.tag == f"{{{SVG_NS}}}svg"
    assert root.get("data-upstream-audit-phase") == data["audit_phase"]
    assert root.get("data-provenance-class") == data["provenance_class"]
    assert root.get("data-free-parameters") == "0"


def test_svg_has_accessible_title_and_description() -> None:
    root = _root()
    title = root.find(f"{{{SVG_NS}}}title")
    desc = root.find(f"{{{SVG_NS}}}desc")

    assert title is not None
    assert desc is not None
    assert title.text == "The Spindle of Necessity — Plato's Eight Whorls"

    description = desc.text or ""
    assert (
        "Deterministic reconstruction from Plato's ordinal ranking and "
        "Michell's musical-number interpretation"
    ) in description
    assert "Phase 10G" not in description
    assert "Phase 10E" not in description


def test_shaft_semantics_follow_frozen_input() -> None:
    data = _data()
    reconstructed = data["reconstructed"]
    root = _root()
    shaft = _by_id(root, "shaft")

    assert shaft.get("data-radius") == str(reconstructed["shaft_radius"])
    assert shaft.get("data-scaled-radius") == str(
        reconstructed["scaled_cumulative_radii_including_shaft"][0]
    )


def test_all_eight_whorls_follow_frozen_input() -> None:
    data = _data()
    reconstructed = data["reconstructed"]

    whorls = reconstructed["center_out_whorls"]
    widths = reconstructed["center_out_ring_widths"]
    radii = reconstructed["cumulative_radii_including_shaft"]
    scaled = reconstructed["scaled_cumulative_radii_including_shaft"]

    root = _root()

    for index, (whorl, width) in enumerate(zip(whorls, widths, strict=True)):
        element = _by_id(root, f"whorl-{whorl}")

        assert element.get("data-whorl") == str(whorl)
        assert element.get("data-width") == str(width)
        assert element.get("data-inner-radius") == str(radii[index])
        assert element.get("data-outer-radius") == str(radii[index + 1])
        assert element.get("data-scaled-outer-radius") == str(scaled[index + 1])


def test_all_cumulative_boundaries_follow_frozen_input() -> None:
    data = _data()
    reconstructed = data["reconstructed"]
    radii = reconstructed["cumulative_radii_including_shaft"]
    scaled = reconstructed["scaled_cumulative_radii_including_shaft"]

    root = _root()

    for index in range(1, len(radii)):
        element = _by_id(root, f"boundary-{index}")
        assert element.get("data-cumulative-index") == str(index)
        assert element.get("data-radius") == str(radii[index])
        assert element.get("data-scaled-radius") == str(scaled[index])


def test_key_correspondences_are_the_first_second_and_outer_boundaries() -> None:
    data = _data()
    reconstructed = data["reconstructed"]
    radii = reconstructed["cumulative_radii_including_shaft"]
    scaled = reconstructed["scaled_cumulative_radii_including_shaft"]

    root = _root()

    first = _by_id(root, "first-cumulative-correspondence")
    second = _by_id(root, "second-cumulative-correspondence")
    outer = _by_id(root, "outer-boundary-correspondence")

    assert first.get("data-radius") == str(radii[1])
    assert first.get("data-scaled-radius") == str(scaled[1])

    assert second.get("data-radius") == str(radii[2])
    assert second.get("data-scaled-radius") == str(scaled[2])

    assert outer.get("data-radius") == str(radii[-1])
    assert outer.get("data-scaled-radius") == str(scaled[-1])


def test_historical_boundary_note_is_rendered_from_frozen_input() -> None:
    data = _data()
    note = data["historical_boundary"]["note"]
    svg = plato_michell_whorl_capstone_to_svg(data)

    # The SVG wraps the note across deterministic text elements, so test
    # distinctive source-derived phrases rather than one contiguous string.
    assert "Exact arithmetic reproduction validates" in svg
    assert "does not establish that Plato intended" in svg
    assert note.startswith("Exact arithmetic reproduction validates")


def test_renderer_rejects_nonzero_search_or_fit_fields() -> None:
    data = _data()
    data["deterministic_algorithm"]["free_parameters"] = 1

    try:
        plato_michell_whorl_capstone_to_svg(data)
    except ValueError as exc:
        assert "free_parameters=0" in str(exc)
    else:
        raise AssertionError("renderer accepted a nonzero free-parameter count")


def test_renderer_rejects_inconsistent_cumulative_geometry() -> None:
    data = _data()
    data["reconstructed"]["cumulative_radii_including_shaft"][2] += 1

    try:
        plato_michell_whorl_capstone_to_svg(data)
    except ValueError as exc:
        assert "cumulative radii are inconsistent" in str(exc)
    else:
        raise AssertionError("renderer accepted inconsistent cumulative geometry")


def test_renderer_preserves_ordinal_only_plato_boundary() -> None:
    data = _data()
    data["historical_boundary"]["plato_supplies_numeric_widths"] = True

    try:
        plato_michell_whorl_capstone_to_svg(data)
    except ValueError as exc:
        assert "ordinal-only Plato data" in str(exc)
    else:
        raise AssertionError("renderer accepted a changed historical boundary")


def test_committed_svg_equals_current_renderer_output() -> None:
    data = _data()
    expected = plato_michell_whorl_capstone_to_svg(data) + "\n"
    assert OUTPUT.read_text(encoding="utf-8") == expected
