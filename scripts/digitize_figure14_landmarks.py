#!/usr/bin/env python3
"""Interactively digitise one independent Figure 14 landmark pass."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt

from new_jerusalem_geometry.figure14_digitisation import (
    LandmarkDefinition,
    read_landmark_schema_csv,
    write_digitisation_csv,
)


DEFAULT_SCHEMA = Path(
    "data/calibration/figure14/landmark_schema.csv"
)

DEFAULT_WORKING_DIRECTORY = Path(
    "data/working/figure14"
)


def safe_pass_id(value: str) -> str:
    """Validate an identifier suitable for metadata and filenames."""

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
            "Digitise one independent pass of the fixed "
            "Figure 14 landmark schema."
        )
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Path to the local rendered Figure 14 PNG.",
    )

    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
        help=f"Landmark schema. Default: {DEFAULT_SCHEMA}",
    )

    parser.add_argument(
        "--pass-id",
        type=safe_pass_id,
        required=True,
        help="Independent pass identifier, for example pass-01.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output CSV. By default it is written into "
            "data/working/figure14 using the pass ID."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of an existing pass CSV.",
    )

    return parser.parse_args()


class Figure14Digitiser:
    """Interactive state for one independent landmark pass."""

    def __init__(
        self,
        *,
        image_path: Path,
        schema: tuple[LandmarkDefinition, ...],
        pass_id: str,
        output_path: Path,
    ) -> None:
        self.image_path = image_path
        self.schema = schema
        self.pass_id = pass_id
        self.output_path = output_path

        self.image = mpimg.imread(
            image_path
        )

        if self.image.ndim < 2:
            raise ValueError(
                "Loaded image does not have two spatial dimensions."
            )

        self.image_height = int(
            self.image.shape[0]
        )

        self.image_width = int(
            self.image.shape[1]
        )

        self.points: list[
            tuple[float, float]
        ] = []

        self.artists: list[
            tuple[object, object]
        ] = []

        self.saved = False

        self.figure, self.axes = plt.subplots(
            figsize=(10, 12)
        )

        self.axes.imshow(
            self.image,
            origin="upper",
        )

        self.axes.set_xlim(
            0,
            self.image_width,
        )

        self.axes.set_ylim(
            self.image_height,
            0,
        )

        self.axes.set_xlabel(
            "Rendered pixel x"
        )

        self.axes.set_ylabel(
            "Rendered pixel y"
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
            "scroll_event",
            self.on_scroll,
        )

        self.figure.canvas.mpl_connect(
            "close_event",
            self.on_close,
        )

        self.update_title()

    def current_landmark(
        self,
    ) -> LandmarkDefinition | None:
        if len(self.points) >= len(self.schema):
            return None

        return self.schema[len(self.points)]

    def update_title(self) -> None:
        landmark = self.current_landmark()

        if landmark is None:
            status = (
                f"{self.pass_id}: complete — "
                f"{len(self.points)}/{len(self.schema)} points"
            )

            if self.saved:
                status += " — CSV saved"

            detail = (
                "Press U or Backspace to undo; "
                "Q to close."
            )
        else:
            status = (
                f"{self.pass_id}: "
                f"{landmark.sequence_index + 1}/"
                f"{len(self.schema)} — "
                f"{landmark.landmark_id}"
            )

            detail = landmark.description

        self.axes.set_title(
            status
            + "\n"
            + detail
            + "\n"
            + (
                "Left-click records a point. "
                "Use the toolbar or mouse wheel to zoom; "
                "U/Backspace undo; R resets view; "
                "S saves when complete; Q closes."
            ),
            fontsize=10,
        )

        self.figure.canvas.draw_idle()

    def toolbar_is_active(self) -> bool:
        manager = self.figure.canvas.manager
        toolbar = getattr(
            manager,
            "toolbar",
            None,
        )

        if toolbar is None:
            return False

        return bool(
            getattr(toolbar, "mode", "")
        )

    def draw_point(
        self,
        x: float,
        y: float,
        sequence_number: int,
    ) -> None:
        marker, = self.axes.plot(
            [x],
            [y],
            marker="o",
            markersize=5,
            linestyle="None",
            markerfacecolor="none",
            markeredgewidth=1.2,
        )

        label = self.axes.annotate(
            str(sequence_number),
            xy=(x, y),
            xytext=(6, -6),
            textcoords="offset points",
            fontsize=8,
            bbox={
                "boxstyle": "round,pad=0.15",
                "facecolor": "white",
                "alpha": 0.78,
                "linewidth": 0.5,
            },
        )

        self.artists.append(
            (marker, label)
        )

    def on_click(self, event: object) -> None:
        if getattr(event, "button", None) != 1:
            return

        if getattr(event, "inaxes", None) is not self.axes:
            return

        if self.toolbar_is_active():
            return

        landmark = self.current_landmark()

        if landmark is None:
            return

        x = getattr(event, "xdata", None)
        y = getattr(event, "ydata", None)

        if x is None or y is None:
            return

        point = (
            float(x),
            float(y),
        )

        self.points.append(point)

        self.draw_point(
            point[0],
            point[1],
            landmark.sequence_index + 1,
        )

        print(
            f"{landmark.sequence_index + 1:02d}/"
            f"{len(self.schema):02d} "
            f"{landmark.landmark_id}: "
            f"x={point[0]:.3f}, y={point[1]:.3f}"
        )

        if len(self.points) == len(self.schema):
            self.save()

        self.update_title()

    def undo(self) -> None:
        if not self.points:
            return

        removed_landmark = self.schema[
            len(self.points) - 1
        ]

        self.points.pop()

        marker, label = self.artists.pop()
        marker.remove()
        label.remove()

        if self.saved:
            self.output_path.unlink(
                missing_ok=True
            )
            self.saved = False

        print(
            "Undid "
            f"{removed_landmark.landmark_id}."
        )

        self.update_title()

    def reset_view(self) -> None:
        self.axes.set_xlim(
            0,
            self.image_width,
        )

        self.axes.set_ylim(
            self.image_height,
            0,
        )

        self.figure.canvas.draw_idle()

    def save(self) -> None:
        if len(self.points) != len(self.schema):
            print(
                "Pass is incomplete: "
                f"{len(self.points)}/{len(self.schema)} points."
            )
            return

        write_digitisation_csv(
            self.output_path,
            schema=self.schema,
            points=self.points,
            pass_id=self.pass_id,
            source_image=self.image_path,
            image_width_pixels=self.image_width,
            image_height_pixels=self.image_height,
        )

        self.saved = True

        print()
        print("Digitisation pass saved")
        print("=" * 25)
        print(f"Pass:          {self.pass_id}")
        print(f"Points:        {len(self.points)}")
        print(f"Source image:  {self.image_path}")
        print(f"Output CSV:    {self.output_path}")
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

        if key == "r":
            self.reset_view()
            return

        if key == "s":
            self.save()
            self.update_title()
            return

        if key == "q":
            plt.close(self.figure)

    def on_scroll(self, event: object) -> None:
        if getattr(event, "inaxes", None) is not self.axes:
            return

        x = getattr(event, "xdata", None)
        y = getattr(event, "ydata", None)

        if x is None or y is None:
            return

        current_xlim = self.axes.get_xlim()
        current_ylim = self.axes.get_ylim()

        current_width = abs(
            current_xlim[1]
            - current_xlim[0]
        )

        current_height = abs(
            current_ylim[1]
            - current_ylim[0]
        )

        button = getattr(event, "button", None)

        if button == "up":
            scale_factor = 1.0 / 1.25
        elif button == "down":
            scale_factor = 1.25
        else:
            return

        new_width = current_width * scale_factor
        new_height = current_height * scale_factor

        relative_x = (
            x - min(current_xlim)
        ) / current_width

        relative_y = (
            y - min(current_ylim)
        ) / current_height

        left = x - relative_x * new_width
        right = left + new_width

        top_numeric = y - relative_y * new_height
        bottom_numeric = top_numeric + new_height

        self.axes.set_xlim(
            left,
            right,
        )

        self.axes.set_ylim(
            bottom_numeric,
            top_numeric,
        )

        self.figure.canvas.draw_idle()

    def on_close(self, event: object) -> None:
        del event

        if len(self.points) != len(self.schema):
            print(
                "Digitiser closed without a complete pass; "
                "no final CSV was written."
            )


def main() -> int:
    args = parse_args()

    if not args.image.is_file():
        print(
            f"ERROR: image not found: {args.image}"
        )
        return 1

    if not args.schema.is_file():
        print(
            f"ERROR: schema not found: {args.schema}"
        )
        return 1

    output_path = args.output

    if output_path is None:
        output_path = (
            DEFAULT_WORKING_DIRECTORY
            / (
                "figure14_digitisation_"
                f"{args.pass_id}.csv"
            )
        )

    if output_path.exists() and not args.overwrite:
        print(
            "ERROR: output already exists: "
            f"{output_path}"
        )
        print(
            "Use a new pass ID or supply --overwrite."
        )
        return 1

    schema = read_landmark_schema_csv(
        args.schema
    )

    print("Figure 14 landmark digitiser")
    print("=" * 30)
    print(f"Pass:          {args.pass_id}")
    print(f"Source image:  {args.image}")
    print(f"Schema:        {args.schema}")
    print(f"Landmarks:     {len(schema)}")
    print(f"Output:        {output_path}")
    print()
    print(
        "Each pass must be completed independently. "
        "Do not inspect coordinates from an earlier pass."
    )
    print()

    digitiser = Figure14Digitiser(
        image_path=args.image,
        schema=schema,
        pass_id=args.pass_id,
        output_path=output_path,
    )

    plt.tight_layout()
    plt.show()

    if digitiser.saved:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
