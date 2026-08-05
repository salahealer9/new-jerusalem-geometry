#!/usr/bin/env python3

from new_jerusalem_geometry.forward_validation import (
    analyze_forward_validation,
    write_forward_validation,
)


OUTPUT_DIR = (
    "data/validation/"
    "njg_michell_v0_4"
)


def main() -> None:
    report = (
        analyze_forward_validation()
    )

    figure12 = (
        report.figure12
    )

    scaffold = (
        report
        .figure14
        .scaffold_candidate
    )

    canonical = (
        report
        .figure14
        .canonical_regular
    )

    print(
        "NJG_MICHELL frozen forward validation"
    )
    print(
        "====================================="
    )

    print()
    print("Predictor")
    print("---------")
    print(
        "Frozen commit:              "
        + report.frozen_predictor_commit
    )
    print(
        "Mode:                       "
        + report.validation_mode
    )
    print(
        "Validation input hashes:    "
        f"{len(report.input_sha256)} verified"
    )

    print()
    print("Figure 12")
    print("---------")
    print(
        f"Wall-angle RMS:             "
        f"{figure12.angle_rms_degrees:.9f}°"
    )
    print(
        f"Wall-angle maximum:         "
        f"{figure12.angle_maximum_degrees:.9f}°"
    )
    print(
        f"Wall-support RMS:           "
        f"{figure12.support_rms_u:.9f} u"
    )
    print(
        f"Wall-support maximum:       "
        f"{figure12.support_maximum_u:.9f} u"
    )
    print(
        f"Wall-vertex RMS:            "
        f"{figure12.vertex_rms_u:.9f} u"
    )
    print(
        f"Wall-vertex maximum:        "
        f"{figure12.vertex_maximum_u:.9f} u"
    )
    print(
        f"Side-length RMS:            "
        f"{figure12.side_length_rms_u:.9f} u"
    )
    print(
        f"Predicted perimeter:        "
        f"{figure12.predicted_perimeter_u:.9f} u"
    )
    print(
        f"Source perimeter:           "
        f"{figure12.source_perimeter_u:.9f} u"
    )
    print(
        f"Perimeter difference:       "
        f"{100.0 * figure12.perimeter_relative_residual:+.6f}%"
    )
    print(
        f"Predicted area:             "
        f"{figure12.predicted_area_u2:.9f} u^2"
    )
    print(
        f"Source area:                "
        f"{figure12.source_area_u2:.9f} u^2"
    )
    print(
        f"Area difference:            "
        f"{100.0 * figure12.area_relative_residual:+.6f}%"
    )

    print()
    print("Figure 14")
    print("---------")
    print(
        f"Scaffold point RMS:         "
        f"{scaffold.point_rms_u:.9f} u"
    )
    print(
        f"Canonical point RMS:        "
        f"{canonical.point_rms_u:.9f} u"
    )
    print(
        f"Scaffold point maximum:     "
        f"{scaffold.point_maximum_u:.9f} u"
    )
    print(
        f"Canonical point maximum:    "
        f"{canonical.point_maximum_u:.9f} u"
    )
    print(
        f"Scaffold angular RMS:       "
        f"{scaffold.angular_rms_degrees:.9f}°"
    )
    print(
        f"Canonical angular RMS:      "
        f"{canonical.angular_rms_degrees:.9f}°"
    )
    print(
        f"Scaffold RMS / reg. LOO:    "
        f"{scaffold.point_rms_fraction_of_registration_loo:.9f}"
    )
    print(
        f"Canonical RMS / reg. LOO:   "
        f"{canonical.point_rms_fraction_of_registration_loo:.9f}"
    )

    print()
    print("Evidence subsets")
    print("----------------")
    print(
        f"Scaffold source-5 RMS:      "
        f"{scaffold.source_supported_point_rms_u:.9f} u"
    )
    print(
        f"Canonical source-5 RMS:     "
        f"{canonical.source_supported_point_rms_u:.9f} u"
    )
    print(
        f"Scaffold inferred-2 RMS:    "
        f"{scaffold.inferred_point_rms_u:.9f} u"
    )
    print(
        f"Canonical inferred-2 RMS:   "
        f"{canonical.inferred_point_rms_u:.9f} u"
    )

    print()
    print("Fixed comparator")
    print("----------------")
    print(
        f"Scaffold - canonical RMS:   "
        f"{report.figure14.scaffold_minus_canonical_point_rms_u:+.9f} u"
    )
    print(
        f"Scaffold - canonical max:   "
        f"{report.figure14.scaffold_minus_canonical_point_maximum_u:+.9f} u"
    )

    paths = (
        write_forward_validation(
            report,
            OUTPUT_DIR,
        )
    )

    print()
    print("Outputs")
    print("-------")

    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
