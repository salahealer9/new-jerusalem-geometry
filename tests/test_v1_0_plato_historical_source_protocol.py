from pathlib import Path
import csv
import new_jerusalem_geometry as njg

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/specification/v1.0_plato_historical_source_protocol.md"
MANIFEST = ROOT / "docs/sources/v1.0_plato_source_manifest.csv"


def test_protocol_and_manifest_exist():
    assert PROTOCOL.is_file()
    assert MANIFEST.is_file()


def test_protocol_is_preregistered_before_extraction():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "PREREGISTERED_BEFORE_SOURCE_EXTRACTION" in text
    assert "v1.0.0 — Plato and the Historical Cosmological Context" in text
    assert "8c5ec9e9c1b07864f6d0a35e3b278f69f8023e64" in text


def test_provenance_classes_are_frozen():
    text = PROTOCOL.read_text(encoding="utf-8")
    for value in (
        "DIRECT_PLATO_TEXT",
        "MICHELL_EXPLICIT",
        "PROJECT_RECONSTRUCTION",
        "SUPPORTING_HISTORICAL_CONTEXT",
        "ARCHIVAL_PENDING",
        "INTERPRETIVE_EXCLUDED",
    ):
        assert value in text


def test_target_driven_reconstruction_is_forbidden():
    text = PROTOCOL.read_text(encoding="utf-8")
    for phrase in (
        "permutation search",
        "free scale fitting",
        "least-squares fitting",
        "post-hoc sequence substitution",
        "importing the v0.9 exact-heptagon/trisection result",
    ):
        assert phrase in text


def test_plato_michell_project_layers_are_separated():
    text = PROTOCOL.read_text(encoding="utf-8")
    assert "No Michell-derived numerical widths may be imported into the Plato layer." in text
    assert "No project reconstruction may be promoted to a Michell statement" in text
    assert "A later numerical assignment cannot be back-projected into Plato." in text


def test_manifest_roles_and_statuses():
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_id = {row["source_id"]: row for row in rows}
    assert by_id["PLATO_REPUBLIC_MYTH_OF_ER"]["current_status"] == "pending_freeze"
    assert by_id["MICHELL_DIMENSIONS_OF_PARADISE"]["required_for_v1"] == "yes"
    assert by_id["SOMMERVILLE_1974_NOTE"]["allowed_claim_scope"] == "ARCHIVAL_PENDING"
    assert by_id["USER_INTERPRETIVE_FRAMEWORK"]["allowed_claim_scope"] == "INTERPRETIVE_EXCLUDED"


def test_package_version_remains_0_9_0_during_v10_development():
    assert njg.__version__ == "0.9.0"
