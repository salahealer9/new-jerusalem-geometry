#!/usr/bin/env python3
"""Export frozen paper SVGs to publication PDF derivatives.

The source paper SVGs remain byte-identical.

For two figures, the SVG source uses ``vector-effect: non-scaling-stroke``
inside a uniformly scaled geometry group.  CairoSVG otherwise renders those
strokes with the group scale applied, producing visibly incorrect thick lines.

For those figures only, this exporter constructs a temporary renderer input in
memory.  Stroke widths and dash lengths belonging to the non-scaling geometry
are divided by the known uniform scale before CairoSVG rendering.  Geometry,
coordinates, labels, colours, fills, source SVGs, and scientific content are
unchanged.

Every PDF is rendered twice and byte identity is required.
"""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
import platform
import re
import shutil
import subprocess
import tempfile

import cairocffi
import cairosvg

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "paper" / "figures"
PDF_DIR = SVG_DIR / "pdf"

FIGURES = (
    "figure01_njg_michell_composite",
    "figure02_figure14_heptagram",
    "figure03_method1_28_point_scaffold",
    "figure04_method2_7_21_42",
    "figure05_exact_heptagon_synthesis",
    "figure06_plato_michell_whorls",
)

# These values are read directly from the frozen paper SVG group transforms.
#
# Figure 2:
#   scale(24.5787545788,-24.5787545788)
#
# Figure 3:
#   scale(42.1195652174,-42.1195652174)
#
# Only stroke/dash presentation properties are compensated.  Coordinates and
# shape dimensions are not changed.
NON_SCALING_STROKE_COMPAT = {
    "figure02_figure14_heptagram": {
        "scale": 24.5787545788,
        "classes": (
            "construction-circle",
            "earth-square",
            "earth-circle",
            "incidence-moon",
            "star-edge",
            "residual-vector",
            "candidate-vertex",
            "anchor-marker",
        ),
    },
    "figure03_method1_28_point_scaffold": {
        "scale": 42.1195652174,
        "classes": (
            "construction-circle",
            "earth-square",
            "earth-circle",
            "scaffold-ray",
            "incidence-moon",
            "scaffold-moon",
            "displacement",
            "incidence-centre-mark",
            "scaffold-marker",
        ),
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


_NUMBER = re.compile(
    r"(?<![\w.-])-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
)


def _divide_numeric_list(value: str, scale: float) -> str:
    """Divide every numeric token in a CSS stroke/dash value by scale."""
    return _NUMBER.sub(
        lambda m: f"{float(m.group(0)) / scale:.12g}",
        value,
    )


def _rewrite_class_rule(
    svg_text: str,
    class_name: str,
    scale: float,
) -> tuple[str, int]:
    """Scale stroke presentation properties in one simple class rule."""
    pattern = re.compile(
        rf"(\.{re.escape(class_name)}\s*\{{)(.*?)(\}})",
        re.DOTALL,
    )
    match = pattern.search(svg_text)
    if match is None:
        raise RuntimeError(f"CSS class rule not found: .{class_name}")

    body = match.group(2)
    changes = 0

    for prop in ("stroke-width", "stroke-dasharray", "stroke-dashoffset"):
        prop_pattern = re.compile(rf"({prop}\s*:\s*)([^;]+)(;)")

        def repl(m: re.Match[str]) -> str:
            nonlocal changes
            changes += 1
            return (
                m.group(1)
                + _divide_numeric_list(m.group(2), scale)
                + m.group(3)
            )

        body = prop_pattern.sub(repl, body)

    updated = (
        svg_text[: match.start()]
        + match.group(1)
        + body
        + match.group(3)
        + svg_text[match.end() :]
    )
    return updated, changes


def renderer_input(source: Path) -> tuple[bytes, str]:
    """Return exact SVG bytes or a renderer-only compatibility derivative."""
    original = source.read_bytes()
    cfg = NON_SCALING_STROKE_COMPAT.get(source.stem)

    if cfg is None:
        return original, "none"

    text = original.decode("utf-8")
    total_changes = 0

    for class_name in cfg["classes"]:
        text, changes = _rewrite_class_rule(
            text,
            class_name,
            cfg["scale"],
        )
        total_changes += changes

    vector_effect_count = text.count("vector-effect: non-scaling-stroke;")
    if vector_effect_count == 0:
        raise RuntimeError(
            f"{source.name}: expected non-scaling-stroke declarations"
        )

    # The widths/dashes have now been baked for the CairoSVG renderer input.
    text = text.replace("vector-effect: non-scaling-stroke;", "")

    if total_changes == 0:
        raise RuntimeError(
            f"{source.name}: compatibility transform changed no stroke values"
        )

    mode = (
        "renderer-only non-scaling-stroke bake; "
        f"uniform_scale={cfg['scale']:.12g}; "
        f"css_properties_rewritten={total_changes}; "
        f"vector_effect_declarations_removed={vector_effect_count}"
    )
    return text.encode("utf-8"), mode


def fc_match(pattern: str) -> str:
    exe = shutil.which("fc-match")
    if not exe:
        return "fc-match unavailable"

    result = subprocess.run(
        [exe, "-f", "%{family}|%{style}|%{file}\n", pattern],
        check=True,
        text=True,
        capture_output=True,
    )
    lines = result.stdout.strip().splitlines()
    return lines[0] if lines else "no match"


def render(svg_bytes: bytes, output: Path) -> None:
    cairosvg.svg2pdf(
        bytestring=svg_bytes,
        write_to=str(output),
    )


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="njg-paper-pdf-") as td:
        tmp = Path(td)

        for stem in FIGURES:
            src = SVG_DIR / f"{stem}.svg"
            out = PDF_DIR / f"{stem}.pdf"
            a = tmp / f"{stem}.a.pdf"
            b = tmp / f"{stem}.b.pdf"

            if not src.is_file():
                raise FileNotFoundError(src)

            source_before = sha256_file(src)
            input_bytes, compatibility = renderer_input(src)

            render(input_bytes, a)
            render(input_bytes, b)

            repeat_equal = a.read_bytes() == b.read_bytes()

            shutil.copyfile(a, out)

            source_after = sha256_file(src)
            if source_after != source_before:
                raise RuntimeError(
                    f"Source paper SVG changed during export: {src}"
                )

            rows.append(
                {
                    "paper_svg": str(src.relative_to(ROOT)),
                    "paper_svg_sha256": source_before,
                    "renderer_input_sha256": sha256_bytes(input_bytes),
                    "paper_pdf": str(out.relative_to(ROOT)),
                    "paper_pdf_sha256": sha256_file(out),
                    "renderer": "CairoSVG",
                    "renderer_version": cairosvg.__version__,
                    "cairo_version": cairocffi.cairo_version_string(),
                    "compatibility_transform": compatibility,
                    "repeat_byte_identical": str(repeat_equal).lower(),
                    "source_svg_modified": "false",
                    "scientific_content_changed": "false",
                }
            )

    manifest = PDF_DIR / "manifest.csv"
    with manifest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=(
                "paper_svg",
                "paper_svg_sha256",
                "renderer_input_sha256",
                "paper_pdf",
                "paper_pdf_sha256",
                "renderer",
                "renderer_version",
                "cairo_version",
                "compatibility_transform",
                "repeat_byte_identical",
                "source_svg_modified",
                "scientific_content_changed",
            ),
        )
        writer.writeheader()
        writer.writerows(rows)

    if not all(r["repeat_byte_identical"] == "true" for r in rows):
        raise SystemExit(
            "PDF export was not byte-identical across repeated renders."
        )

    environment = PDF_DIR / "ENVIRONMENT.txt"
    environment.write_text(
        "\n".join(
            (
                "New Jerusalem Geometry — paper PDF export environment",
                "",
                f"Python: {platform.python_version()}",
                f"Platform: {platform.platform()}",
                f"CairoSVG: {cairosvg.__version__}",
                f"Cairo: {cairocffi.cairo_version_string()}",
                "",
                "Font resolution:",
                f"sans-serif: {fc_match('sans-serif')}",
                f"system-ui: {fc_match('system-ui')}",
                f"Arial: {fc_match('Arial')}",
                f"Helvetica: {fc_match('Helvetica')}",
                "",
                "Renderer compatibility:",
                (
                    "Figure 2: renderer-only non-scaling-stroke bake "
                    "for uniform scale 24.5787545788."
                ),
                (
                    "Figure 3: renderer-only non-scaling-stroke bake "
                    "for uniform scale 42.1195652174."
                ),
                (
                    "The frozen paper SVGs are not modified. Only temporary "
                    "CairoSVG input bytes are adjusted so stroke/dash "
                    "appearance matches the SVG non-scaling-stroke intent."
                ),
                "",
                "All six repeated PDF renders were byte-identical.",
                "Source paper SVGs modified: false",
                "Scientific content changed: false",
                "",
            )
        ),
        encoding="utf-8",
    )

    print(f"wrote {len(rows)} PDF figures")
    print(manifest.relative_to(ROOT))
    print(environment.relative_to(ROOT))


if __name__ == "__main__":
    main()
