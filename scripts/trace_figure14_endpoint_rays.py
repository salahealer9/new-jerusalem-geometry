#!/usr/bin/env python3
"""Interactively trace the two printed strokes near each Figure 14 endpoint."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from new_jerusalem_geometry.figure14_edge_tracing import (
    EdgeTraceReference,
    load_edge_trace_reference,
    write_edge_trace_csv,
)


DEFAULT_MATRIX = Path(
    "data/calibration/figure14/derived/"
    "affine_registration_matrix.json"
)

DEFAULT_LANDMARKS = Path(
    "data/calibration/figure14/derived/"
    "registered_landmark_centroids.csv"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure14/edge_tracing"
)


def safe_pass_id(value: str) -> str:
    if not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9_.-]*",
        value,
    ):
        raise argparse.ArgumentTypeError(
            "Pass ID must begin with an alphanumeric "
            "character and contain only letters, numbers, "
            "underscores, dots, or hyphens."
        )

    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Click the two printed star strokes immediately "
            "inside each source-calibrated Figure 14 endpoint."
        )
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Local rendered Figure 14 PNG.",
    )

    parser.add_argument(
        "--pass-id",
        type=safe_pass_id,
        required=True,
        help="Independent pass identifier, such as pass-01.",
    )

    parser.add_argument(
        "--matrix",
        type=Path,
        default=DEFAULT_MATRIX,
        help=f"Affine matrix JSON. Default: {DEFAULT_MATRIX}",
    )

    parser.add_argument(
        "--landmarks",
        type=Path,
        default=DEFAULT_LANDMARKS,
        help=(
            "Registered landmarks CSV. "
            f"Default: {DEFAULT_LANDMARKS}"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output CSV. By default it is written under "
            "data/working/figure14/edge_tracing."
        ),
    )

    parser.add_argument(
        "--minimum-radius",
        type=float,
        default=35.0,
        help=(
            "Minimum accepted distance from endpoint in pixels. "
            "Default: 35."
        ),
    )

    parser.add_argument(
        "--maximum-radius",
        type=float,
        default=130.0,
        help=(
            "Maximum accepted distance from endpoint in pixels. "
            "Default: 130."
        ),
    )

    parser.add_argument(
        "--zoom-half-width",
        type=float,
        default=175.0,
        help=(
            "Half-width of each endpoint view in pixels. "
            "Default: 175."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of an existing trace CSV.",
    )

    return parser.parse_args()


class EndpointRayTracer:
    """Interactive state for one fourteen-click tracing pass."""

    def __init__(
        self,
        *,
        image_path: Path,
        reference: EdgeTraceReference,
        pass_id: str,
        output_path: Path,
        minimum_radius: float,
        maximum_radius: float,
        zoom_half_width: float,
    ) -> None:
        self.image_path = image_path
        self.reference = reference
        self.pass_id = pass_id
        self.output_path = output_path
        self.minimum_radius = (
            minimum_radius
        )
        self.maximum_radius = (
            maximum_radius
        )
        self.zoom_half_width = (
            zoom_half_width
        )

        self.image = mpimg.imread(
            image_path
        )

        self.samples: list[
            tuple[int, int, float, float]
        ] = []

        self.saved = False

        self.figure, self.axes = plt.subplots(
            figsize=(9, 9)
        )

        self.figure.canvas.mpl_connect(
            "button_press_event",
            self.on_click,
        )

        self.figure.canvas.mpl_connect(
            "key_press_event",
            self.on_key,
        )

        self.figure.canvas.mpl_connect(
            "close_event",
            self.on_close,
        )

        self.redraw()

    @property
    def endpoint_index(self) -> int:
        return min(
            len(self.samples) // 2,
            6,
        )

    @property
    def ray_index(self) -> int:
        return (
            len(self.samples) % 2
        )

    def redraw(self) -> None:
        self.axes.clear()

        self.axes.imshow(
            self.image,
            origin="upper",
        )

        endpoint_index = (
            self.endpoint_index
        )

        endpoint_id = (
            self.reference.endpoint_ids[
                endpoint_index
            ]
        )

        endpoint_x, endpoint_y = (
            self.reference.endpoint_pixels[
                endpoint_index
            ]
        )

        self.axes.plot(
            [endpoint_x],
            [endpoint_y],
            marker="o",
            markersize=7,
            markerfacecolor="none",
            linestyle="None",
        )

        for radius in (
            self.minimum_radius,
            self.maximum_radius,
        ):
            self.axes.add_patch(
                Circle(
                    (endpoint_x, endpoint_y),
                    radius=radius,
                    fill=False,
                    linestyle="--",
                    linewidth=0.8,
                )
            )

        for (
            sample_endpoint,
            sample_ray,
            sample_x,
            sample_y,
        ) in self.samples:
            if (
                sample_endpoint
                != endpoint_index
            ):
                continue

            self.axes.plot(
                [endpoint_x, sample_x],
                [endpoint_y, sample_y],
                marker="o",
                markersize=4,
                linewidth=0.8,
            )

            self.axes.annotate(
                f"ray {sample_ray + 1}",
                xy=(sample_x, sample_y),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=8,
            )

        half = self.zoom_half_width

        self.axes.set_xlim(
            endpoint_x - half,
            endpoint_x + half,
        )

        self.axes.set_ylim(
            endpoint_y + half,
            endpoint_y - half,
        )

        completed = len(
            self.samples
        )

        if completed >= 14:
            title = (
                f"{self.pass_id}: complete — "
                "14/14 rays"
            )
        else:
            title = (
                f"{self.pass_id}: endpoint "
                f"{endpoint_index + 1}/7 — "
                f"{endpoint_id}\n"
                f"Click printed stroke "
                f"{self.ray_index + 1}/2"
            )

        self.axes.set_title(
            title
            + "\n"
            + (
                "Click one point on each distinct printed stroke "
                "between the dashed circles, in either order.\n"
                "U/Backspace: undo · S: save when complete · Q: close"
            ),
            fontsize=10,
        )

        self.axes.set_xlabel(
            "Rendered pixel x"
        )

        self.axes.set_ylabel(
            "Rendered pixel y"
        )

        self.figure.canvas.draw_idle()

    def on_click(self, event: object) -> None:
        if len(self.samples) >= 14:
            return

        if getattr(event, "button", None) != 1:
            return

        if getattr(event, "inaxes", None) is not self.axes:
            return

        x = getattr(event, "xdata", None)
        y = getattr(event, "ydata", None)

        if x is None or y is None:
            return

        endpoint_index = (
            self.endpoint_index
        )

        endpoint_x, endpoint_y = (
            self.reference.endpoint_pixels[
                endpoint_index
            ]
        )

        distance = (
            (
                float(x) - endpoint_x
            ) ** 2
            + (
                float(y) - endpoint_y
            ) ** 2
        ) ** 0.5

        if not (
            self.minimum_radius
            <= distance
            <= self.maximum_radius
        ):
            print(
                "Rejected click: distance "
                f"{distance:.3f} px is outside "
                f"{self.minimum_radius:.1f}–"
                f"{self.maximum_radius:.1f} px."
            )
            return

        ray_index = self.ray_index

        self.samples.append(
            (
                endpoint_index,
                ray_index,
                float(x),
                float(y),
            )
        )

        print(
            f"{len(self.samples):02d}/14  "
            f"{self.reference.endpoint_ids[endpoint_index]}  "
            f"ray-{ray_index + 1}  "
            f"x={float(x):.3f}, "
            f"y={float(y):.3f}, "
            f"r={distance:.3f} px"
        )

        if len(self.samples) == 14:
            self.save()

        self.redraw()

    def undo(self) -> None:
        if not self.samples:
            return

        removed = self.samples.pop()

        if self.saved:
            self.output_path.unlink(
                missing_ok=True
            )
            self.saved = False

        print(
            "Undid "
            f"{self.reference.endpoint_ids[removed[0]]} "
            f"ray-{removed[1] + 1}."
        )

        self.redraw()

    def save(self) -> None:
        if len(self.samples) != 14:
            print(
                "Trace pass is incomplete: "
                f"{len(self.samples)}/14 samples."
            )
            return

        write_edge_trace_csv(
            self.output_path,
            reference=self.reference,
            source_image_path=(
                self.image_path
            ),
            pass_id=self.pass_id,
            samples=self.samples,
        )

        self.saved = True

        print()
        print("Endpoint-ray trace saved")
        print("=" * 24)
        print(f"Pass:       {self.pass_id}")
        print(f"Samples:    {len(self.samples)}")
        print(f"Output CSV: {self.output_path}")
        print()

    def on_key(self, event: object) -> None:
        key = getattr(event, "key", None)

        if key in {
            "u",
            "backspace",
            "delete",
        }:
            self.undo()
            return

        if key == "s":
            self.save()
            return

        if key == "q":
            plt.close(
                self.figure
            )

    def on_close(self, event: object) -> None:
        del event

        if not self.saved:
            print(
                "Tracer closed without a complete saved pass."
            )


def main() -> int:
    args = parse_args()

    if (
        args.minimum_radius <= 0.0
        or args.maximum_radius
        <= args.minimum_radius
    ):
        print(
            "ERROR: radius limits must satisfy "
            "0 < minimum < maximum."
        )
        return 1

    if not args.image.is_file():
        print(
            f"ERROR: image not found: {args.image}"
        )
        return 1

    reference = load_edge_trace_reference(
        matrix_path=args.matrix,
        landmarks_path=args.landmarks,
    )

    output_path = args.output

    if output_path is None:
        output_path = (
            DEFAULT_OUTPUT_DIRECTORY
            / (
                "figure14_edge_trace_"
                f"{args.pass_id}.csv"
            )
        )

    if (
        output_path.exists()
        and not args.overwrite
    ):
        print(
            f"ERROR: output already exists: {output_path}"
        )
        print(
            "Use another pass ID or supply --overwrite."
        )
        return 1

    print("Figure 14 endpoint-ray tracer")
    print("=" * 29)
    print(f"Pass:         {args.pass_id}")
    print(f"Source image: {args.image}")
    print(f"Output:       {output_path}")
    print()
    print(
        "At each endpoint, click one point on each of the "
        "two distinct printed star strokes. The click order "
        "does not matter."
    )
    print(
        "Keep each click near the endpoint and between the "
        "two dashed guide circles."
    )
    print()

    tracer = EndpointRayTracer(
        image_path=args.image,
        reference=reference,
        pass_id=args.pass_id,
        output_path=output_path,
        minimum_radius=(
            args.minimum_radius
        ),
        maximum_radius=(
            args.maximum_radius
        ),
        zoom_half_width=(
            args.zoom_half_width
        ),
    )

    plt.tight_layout()
    plt.show()

    return 0 if tracer.saved else 1


if __name__ == "__main__":
    raise SystemExit(main())
