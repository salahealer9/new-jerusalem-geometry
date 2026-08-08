from __future__ import annotations

import json
from pathlib import Path

from new_jerusalem_geometry.dodecagon_dimensional_audit import (
    JSON_OUTPUT_PATH,
    write_dodecagon_dimensional_audit_outputs,
)


write_dodecagon_dimensional_audit_outputs()

payload = json.loads(
    Path(
        JSON_OUTPUT_PATH
    ).read_text(
        encoding="utf-8"
    )
)

print(
    "Phase 7D stopping status:",
    payload[
        "stopping_status"
    ],
)

print(
    "Independent forward prediction:",
    payload[
        "evidential_policy"
    ][
        "independent_forward_prediction"
    ],
)

print(
    "Geometry fitted to Phase 7D targets:",
    payload[
        "evidential_policy"
    ][
        "geometry_fitted_to_phase7d_targets"
    ],
)

print(
    "Scale fitted to Phase 7D targets:",
    payload[
        "evidential_policy"
    ][
        "scale_fitted_to_phase7d_targets"
    ],
)

print()

print(
    "Frozen scale:",
    payload[
        "frozen_scale"
    ][
        "current_foot_per_normalized_unit"
    ],
    "current ft/u",
)

print()

for row in payload[
    "comparisons"
]:
    print(
        row[
            "comparison_id"
        ],
        row[
            "source_record_id"
        ],
        "prediction=",
        row[
            "prediction"
        ][
            "value"
        ],
        row[
            "prediction"
        ][
            "unit"
        ],
        "target=",
        row[
            "historical_target"
        ][
            "value"
        ],
        "signed=",
        row[
            "signed_residual"
        ],
        "percent=",
        row[
            "percent_residual"
        ],
    )
