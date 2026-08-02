#!/usr/bin/env python3
"""Interactively digitise one Figure 12 source-plate pass."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton

from new_jerusalem_geometry.figure12_digitisation import (
    Figure12DigitisedObservation,
    read_figure12_digitisation_pass_csv,
    read_figure12_observation_schema_csv,
    write_figure12_digitisation_pass_csv,
)
from new_jerusalem_geometry.source_preparation import (
    sha256_file,
)


DEFAULT_SCHEMA = Path(
    "data/calibration/figure12/"
    "observation_schema.csv"
)

DEFAULT_OUTPUT_DIRECTORY = Path(
    "data/working/figure12/digitisation"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Digitise one independent Figure 12 "
            "source-observation pass."
        )
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="Local rendered Figure 12 PNG.",
    )

    parser.add_argument(
        "--pass-id",
        required=True,
        choices=(
            "pass-01",
            "pass-02",
            "pass-03",
        ),
    )

    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Resume a previously interrupted pass "
            "from its autosaved prefix."
        ),
    )

    return parser.parse_args()


def _instruction(
    *,
    sequence_index: int,
    total: int,
    category: str,
    object_id: str,
    sample_index: int,
    description: str,
) -> str:
    return (
        f"Figure 12 digitisation\n"
        f"{sequence_index + 1}/{total}  |  "
        f"{category}\n"
        f"{object_id}  |  sample {sample_index}\n"
        f"{description}\n\n"
        "LEFT CLICK = record point when toolbar mode is OFF\n"
        "Zoom/Pan toolbar clicks are ignored by the digitiser.\n"
        "Deactivate Zoom/Pan before recording the source point.\n"
        "Close window to abort; rerun with --resume."
    )


def _get_source_click(
    fig,
    ax,
) -> tuple[float, float] | None:
    """Wait for one deliberate source-image click.

    Zoom and pan operations performed while a Matplotlib toolbar
    navigation mode is active are ignored.

    Returns None if the figure is closed or the process is
    interrupted with Ctrl+C.
    """

    result: list[tuple[float, float]] = []
    closed = [False]

    def toolbar_is_active() -> bool:
        toolbar = getattr(
            fig.canvas,
            "toolbar",
            None,
        )

        if toolbar is None:
            return False

        mode = getattr(
            toolbar,
            "mode",
            None,
        )

        if mode is None:
            return False

        # Modern Matplotlib may expose toolbar.mode as an enum.
        # Its NONE member has value "", but the enum object itself
        # is truthy, so inspect .value when present.
        mode_value = getattr(
            mode,
            "value",
            mode,
        )

        return bool(mode_value)

    def on_click(event) -> None:
        if toolbar_is_active():
            return

        if event.button != MouseButton.LEFT:
            return

        if event.inaxes is not ax:
            return

        if (
            event.xdata is None
            or event.ydata is None
        ):
            return

        result.append(
            (
                float(event.xdata),
                float(event.ydata),
            )
        )

    def on_close(_event) -> None:
        closed[0] = True

    click_id = fig.canvas.mpl_connect(
        "button_press_event",
        on_click,
    )

    close_id = fig.canvas.mpl_connect(
        "close_event",
        on_close,
    )

    try:
        # Keep the normal Matplotlib GUI event loop responsive.
        # Unlike canvas.start_event_loop(), this works reliably
        # with the Linux desktop backends used by this project and
        # still allows KeyboardInterrupt to reach Python.
        while (
            not result
            and not closed[0]
            and plt.fignum_exists(fig.number)
        ):
            plt.pause(0.05)

    except KeyboardInterrupt:
        print()
        print(
            "Keyboard interrupt received."
        )
        return None

    finally:
        fig.canvas.mpl_disconnect(
            click_id
        )
        fig.canvas.mpl_disconnect(
            close_id
        )

    if closed[0] or not result:
        return None

    return result[0]


def main() -> int:
    args = parse_args()

    if not args.image.is_file():
        raise FileNotFoundError(
            args.image
        )

    schema = (
        read_figure12_observation_schema_csv(
            args.schema
        )
    )

    output_path = (
        args.output
        if args.output is not None
        else (
            DEFAULT_OUTPUT_DIRECTORY
            / (
                "figure12_observations_"
                f"{args.pass_id}.csv"
            )
        )
    )

    image = mpimg.imread(
        args.image
    )

    if image.ndim < 2:
        raise ValueError(
            "Source image has invalid dimensions."
        )

    image_height = int(
        image.shape[0]
    )
    image_width = int(
        image.shape[1]
    )

    source_hash = sha256_file(
        args.image
    )

    completed: list[
        Figure12DigitisedObservation
    ] = []

    if args.resume and output_path.exists():
        completed.extend(
            read_figure12_digitisation_pass_csv(
                output_path,
                require_complete=False,
            )
        )

        if completed:
            if completed[0].pass_id != args.pass_id:
                raise ValueError(
                    "Existing partial file has a different pass ID."
                )

            if (
                completed[0].source_image_sha256
                != source_hash
            ):
                raise ValueError(
                    "Existing partial file uses a different source image."
                )

            for existing, expected in zip(
                completed,
                schema,
                strict=False,
            ):
                if (
                    existing.definition.observation_id
                    != expected.observation_id
                ):
                    raise ValueError(
                        "Existing partial pass does not match "
                        "the current observation schema."
                    )

    elif output_path.exists():
        raise FileExistsError(
            f"{output_path} already exists. "
            "Use --resume or choose another output."
        )

    start_index = len(completed)

    if start_index == len(schema):
        print(
            "Pass is already complete."
        )
        return 0

    print(
        "Figure 12 source digitisation"
    )
    print(
        "=" * 29
    )
    print(
        f"Pass:         {args.pass_id}"
    )
    print(
        f"Source:       {args.image}"
    )
    print(
        f"SHA-256:      {source_hash}"
    )
    print(
        f"Image:        {image_width} × "
        f"{image_height} px"
    )
    print(
        f"Schema:       {args.schema}"
    )
    print(
        f"Output:       {output_path}"
    )
    print(
        f"Resume index: {start_index}"
    )
    print()

    fig, ax = plt.subplots(
        figsize=(10, 12)
    )

    ax.imshow(
        image,
        origin="upper",
    )

    ax.set_xlim(
        0,
        image_width,
    )
    ax.set_ylim(
        image_height,
        0,
    )

    ax.set_xlabel(
        "pixel x"
    )
    ax.set_ylabel(
        "pixel y"
    )

    # Explicitly create and display the GUI window before entering
    # the custom acquisition loop. plt.ginput() used to do this
    # implicitly; our toolbar-aware click handler must do it here.
    plt.show(
        block=False,
    )

    fig.canvas.draw()
    fig.canvas.flush_events()

    for index in range(
        start_index,
        len(schema),
    ):
        definition = schema[index]

        ax.set_title(
            _instruction(
                sequence_index=index,
                total=len(schema),
                category=definition.category,
                object_id=definition.object_id,
                sample_index=definition.sample_index,
                description=definition.description,
            ),
            fontsize=9,
        )

        fig.canvas.draw_idle()

        point = _get_source_click(
            fig,
            ax,
        )

        if point is None:
            plt.close(fig)

            print()
            print(
                "Digitisation interrupted."
            )
            print(
                f"Completed observations: {len(completed)}"
            )
            print(
                "Resume with the same command plus --resume."
            )
            return 1

        pixel_x, pixel_y = point

        completed.append(
            Figure12DigitisedObservation(
                pass_id=args.pass_id,
                definition=definition,
                pixel_x=float(pixel_x),
                pixel_y=float(pixel_y),
                source_image=str(
                    args.image
                ),
                source_image_sha256=source_hash,
                image_width_pixels=image_width,
                image_height_pixels=image_height,
            )
        )

        write_figure12_digitisation_pass_csv(
            output_path,
            completed,
            require_complete=False,
        )

        print(
            f"[{index + 1:03d}/{len(schema)}] "
            f"{definition.observation_id}: "
            f"({pixel_x:.3f}, {pixel_y:.3f})"
        )

    plt.close(fig)

    write_figure12_digitisation_pass_csv(
        output_path,
        completed,
        require_complete=True,
    )

    print()
    print(
        "Figure 12 digitisation pass complete"
    )
    print(
        "=" * 37
    )
    print(
        f"Pass:          {args.pass_id}"
    )
    print(
        f"Observations:  {len(completed)}"
    )
    print(
        f"Output:        {output_path}"
    )
    print(
        f"Source hash:   {source_hash}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
