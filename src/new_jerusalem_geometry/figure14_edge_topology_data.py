"""Promote Figure 14 endpoint-ray traces into tracked calibration evidence.

The three original tracing-pass CSVs are preserved byte-for-byte. The
topology analysis is then regenerated from those promoted copies.

The resulting manifest records:

- source-image identity;
- affine matrix and registered-landmark hashes;
- raw trace hashes;
- candidate rankings;
- selected topology;
- hashes of all derived outputs.

No timestamp is written, keeping the promoted evidence deterministic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .figure14_edge_tracing import (
    EdgeTopologyReport,
    analyze_edge_trace_passes,
    load_edge_trace_pass,
    load_edge_trace_reference,
    write_edge_topology_details_csv,
    write_edge_topology_json,
    write_edge_topology_markdown,
)
from .source_preparation import sha256_file


TRACE_GLOB = (
    "figure14_edge_trace_pass-*.csv"
)


@dataclass(frozen=True, slots=True)
class EdgeTraceFileRecord:
    """One promoted endpoint-ray tracing pass."""

    pass_id: str
    input_path: Path
    output_path: Path
    input_sha256: str
    output_sha256: str


@dataclass(frozen=True, slots=True)
class EdgeTopologyPromotionResult:
    """Completed promotion of the Figure 14 topology evidence."""

    output_root: Path
    raw_directory: Path
    derived_directory: Path
    manifest_path: Path
    details_path: Path
    summary_path: Path
    report_path: Path
    topology_report: EdgeTopologyReport
    files: tuple[EdgeTraceFileRecord, ...]


def _check_outputs(
    paths: Sequence[Path],
    *,
    overwrite: bool,
) -> None:
    existing = tuple(
        path
        for path in paths
        if path.exists()
    )

    if existing and not overwrite:
        formatted = "\n".join(
            f"  {path}"
            for path in existing
        )

        raise FileExistsError(
            "Edge-topology calibration outputs already exist:\n"
            f"{formatted}\n"
            "Use overwrite=True only after reviewing them."
        )


def promote_figure14_edge_topology_evidence(
    *,
    input_directory: str | Path,
    output_root: str | Path,
    matrix_path: str | Path,
    landmarks_path: str | Path,
    expected_pass_count: int = 3,
    expected_selected_step: int = 2,
    require_unanimous: bool = True,
    overwrite: bool = False,
) -> EdgeTopologyPromotionResult:
    """Preserve raw traces and regenerate the topology analysis."""

    input_path = Path(
        input_directory
    )

    root_path = Path(
        output_root
    )

    raw_directory = (
        root_path / "raw"
    )

    derived_directory = (
        root_path / "derived"
    )

    manifest_path = (
        root_path
        / "edge_topology_manifest.json"
    )

    details_path = (
        derived_directory
        / "edge_topology_details.csv"
    )

    summary_path = (
        derived_directory
        / "edge_topology_summary.json"
    )

    report_path = (
        derived_directory
        / "edge_topology_report.md"
    )

    input_pass_paths = sorted(
        input_path.glob(
            TRACE_GLOB
        )
    )

    if (
        len(input_pass_paths)
        != expected_pass_count
    ):
        raise ValueError(
            f"Expected {expected_pass_count} endpoint-ray "
            f"trace passes in {input_path}; "
            f"found {len(input_pass_paths)}."
        )

    loaded_input_passes = tuple(
        load_edge_trace_pass(path)
        for path in input_pass_paths
    )

    pass_ids = tuple(
        trace_pass.pass_id
        for trace_pass in loaded_input_passes
    )

    if len(set(pass_ids)) != len(pass_ids):
        raise ValueError(
            "Endpoint-ray trace pass identifiers must be unique."
        )

    planned_outputs = [
        manifest_path,
        details_path,
        summary_path,
        report_path,
    ]

    planned_outputs.extend(
        raw_directory / path.name
        for path in input_pass_paths
    )

    _check_outputs(
        planned_outputs,
        overwrite=overwrite,
    )

    raw_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    derived_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_records: list[
        EdgeTraceFileRecord
    ] = []

    promoted_paths: list[
        Path
    ] = []

    for source_path, trace_pass in zip(
        input_pass_paths,
        loaded_input_passes,
        strict=True,
    ):
        destination_path = (
            raw_directory
            / source_path.name
        )

        source_bytes = (
            source_path.read_bytes()
        )

        destination_path.write_bytes(
            source_bytes
        )

        input_digest = sha256_file(
            source_path
        )

        output_digest = sha256_file(
            destination_path
        )

        if output_digest != input_digest:
            raise AssertionError(
                "Promoted edge-trace file does not "
                "match its source bytes."
            )

        promoted_pass = (
            load_edge_trace_pass(
                destination_path
            )
        )

        if (
            promoted_pass.pass_id
            != trace_pass.pass_id
        ):
            raise AssertionError(
                "Trace pass identifier changed "
                "during promotion."
            )

        file_records.append(
            EdgeTraceFileRecord(
                pass_id=trace_pass.pass_id,
                input_path=source_path,
                output_path=destination_path,
                input_sha256=input_digest,
                output_sha256=output_digest,
            )
        )

        promoted_paths.append(
            destination_path
        )

    reference = load_edge_trace_reference(
        matrix_path=matrix_path,
        landmarks_path=landmarks_path,
    )

    topology_report = (
        analyze_edge_trace_passes(
            reference=reference,
            pass_paths=promoted_paths,
        )
    )

    if (
        topology_report.selected_step
        != expected_selected_step
    ):
        raise ValueError(
            "Promoted topology analysis selected "
            f"step {topology_report.selected_step}; "
            f"expected step {expected_selected_step}."
        )

    if (
        require_unanimous
        and not topology_report.unanimous_endpoint_passes
    ):
        raise ValueError(
            "Promoted topology result is not unanimous "
            "across endpoint/pass comparisons."
        )

    write_edge_topology_details_csv(
        details_path,
        topology_report,
    )

    write_edge_topology_json(
        summary_path,
        topology_report,
    )

    write_edge_topology_markdown(
        report_path,
        topology_report,
    )

    selected_summary = next(
        item
        for item in topology_report.candidate_summaries
        if (
            item.step
            == topology_report.selected_step
        )
    )

    ranked_summaries = sorted(
        topology_report.candidate_summaries,
        key=lambda item: (
            item.rms_degrees,
            item.maximum_degrees,
        ),
    )

    manifest = {
        "schema_version": 1,
        "evidence_id": (
            "figure14-near-endpoint-edge-topology-v1"
        ),
        "method": (
            "Two manually sampled printed-stroke directions "
            "immediately inside each of seven calibrated endpoints, "
            "compared against unordered direction pairs for "
            "connection steps 1, 2, and 3."
        ),
        "raw_files_modified": False,
        "coordinate_values_modified": False,
        "independent_pass_count": len(
            file_records
        ),
        "endpoint_count_per_pass": 7,
        "ray_count_per_endpoint": 2,
        "total_ray_samples": (
            2
            * len(
                topology_report.endpoint_results
            )
        ),
        "source_image": {
            "filename": (
                reference.source_image
            ),
            "sha256": (
                reference.source_image_sha256
            ),
            "width_pixels": (
                reference.image_width_pixels
            ),
            "height_pixels": (
                reference.image_height_pixels
            ),
        },
        "calibration_references": {
            "affine_matrix": {
                "filename": Path(
                    matrix_path
                ).name,
                "sha256": (
                    reference.matrix_sha256
                ),
            },
            "registered_landmarks": {
                "filename": Path(
                    landmarks_path
                ).name,
                "sha256": (
                    reference.landmarks_sha256
                ),
            },
        },
        "raw_trace_passes": [
            {
                "pass_id": record.pass_id,
                "filename": (
                    record.output_path.name
                ),
                "sha256": (
                    record.output_sha256
                ),
                "preserved_byte_for_byte": True,
            }
            for record in file_records
        ],
        "candidate_ranking": [
            {
                "rank": rank,
                "step": item.step,
                "notation": item.notation,
                "angular_rms_degrees": (
                    item.rms_degrees
                ),
                "maximum_residual_degrees": (
                    item.maximum_degrees
                ),
                "endpoint_pass_wins": (
                    item.endpoint_pass_wins
                ),
                "endpoint_pass_count": (
                    item.endpoint_pass_count
                ),
            }
            for rank, item in enumerate(
                ranked_summaries,
                start=1,
            )
        ],
        "selected_topology": {
            "step": (
                topology_report.selected_step
            ),
            "notation": (
                topology_report.selected_notation
            ),
            "angular_rms_degrees": (
                topology_report.selected_rms_degrees
            ),
            "maximum_residual_degrees": (
                topology_report.selected_maximum_degrees
            ),
            "second_best_rms_degrees": (
                topology_report.second_best_rms_degrees
            ),
            "rms_margin_degrees": (
                topology_report.rms_margin_degrees
            ),
            "endpoint_pass_wins": (
                selected_summary.endpoint_pass_wins
            ),
            "endpoint_pass_count": (
                selected_summary.endpoint_pass_count
            ),
            "unanimous_endpoint_passes": (
                topology_report.unanimous_endpoint_passes
            ),
        },
        "derived_outputs": {
            "details": {
                "filename": (
                    details_path.name
                ),
                "sha256": sha256_file(
                    details_path
                ),
            },
            "summary": {
                "filename": (
                    summary_path.name
                ),
                "sha256": sha256_file(
                    summary_path
                ),
            },
            "report": {
                "filename": (
                    report_path.name
                ),
                "sha256": sha256_file(
                    report_path
                ),
            },
        },
        "interpretation_boundary": (
            "The selected topology is supported by direct "
            "near-endpoint printed-line direction evidence. "
            "The result remains subject to source reproduction, "
            "printed-line thickness, affine registration, and "
            "manual sampling uncertainty."
        ),
    }

    manifest_path.write_text(
        json.dumps(
            manifest,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    return EdgeTopologyPromotionResult(
        output_root=root_path,
        raw_directory=raw_directory,
        derived_directory=(
            derived_directory
        ),
        manifest_path=manifest_path,
        details_path=details_path,
        summary_path=summary_path,
        report_path=report_path,
        topology_report=topology_report,
        files=tuple(file_records),
    )
