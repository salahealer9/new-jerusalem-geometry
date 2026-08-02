# New Jerusalem Geometry

A reproducible Euclidean constraint specification and computational analysis of
John Michell's New Jerusalem Diagram.

## Project objective

This project formalises the New Jerusalem Diagram as a geometric constraint
system. Its goals are to:

- reconstruct the diagram from explicit Euclidean definitions;
- distinguish exact constructions from historical approximations;
- generate reproducible coordinates and vector graphics;
- verify incidences, tangencies, symmetries, ratios, and other invariants;
- compare alternative interpretations of the construction;
- provide a rigorous mathematical foundation for later historical, symbolic,
  harmonic, graph-theoretic, and information-theoretic analysis.

## Geometric model distinctions

The project keeps visually similar but mathematically distinct constructions
separate.

For the twelve Moon circles:

- `NJG_INC`: source-supported exact square-circle incidence model;
- `NJG_28`: exact regular 28-fold angular idealisation;
- `NJG_SVG`: reproduction of the independent 2008 Wikimedia SVG;
- `NJG_MICHELL_28`: Michell's approximate 28-point scaffold construction.

For the Figure 12 outer wall:

- `RADIAL_SUPPORT`: historical project inference;
- `REGULAR_DIRECTION_TANGENT`: fixed regular-direction tangent comparison;
- `POLAR_PIVOT_TANGENT`: current preferred source-supported reconstruction.

The preferred wall model is selected from combined source-plate and historical
dimensional evidence; it is not claimed to be an explicitly stated construction
algorithm in Michell's text.

## Repository status

Early formalisation stage. No scientific conclusions have yet been established.

## Author

Salah-Eddin Gherbi  
Independent Researcher, United Kingdom  
ORCID: 0009-0005-4017-1095

## Development

Create an isolated environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
````

Run the core verification:

```bash
python scripts/verify_core_geometry.py
```

Run the automated tests:

```bash
pytest
```

The executable model now includes the normalized Earth-Moon core, competing
oblique Moon-circle placements, Michell's approximate 28-point scaffold,
source-calibrated Figure 12 Moon and wall geometry, the preferred polar-pivot
outer-wall reconstruction, and the source-calibrated Figure 14 heptagram.

Competing constructions remain explicitly separated rather than being merged
into a single model without evidential justification.

## Generate the verified core diagram

Generate the standalone SVG:

```bash
python scripts/generate_core_diagram.py
````

The default output is:

```text
figures/generated/cardinal_core.svg
```

The graphic is generated directly from the same coordinate objects used by the
verification and test suite. It introduces no manually positioned elements.

A different scale or output path may be selected without changing the
scale-free geometry:

```bash
python scripts/generate_core_diagram.py \
  --unit 720 \
  --output figures/generated/cardinal_core_u720.svg
```

## Compare the oblique Moon models

Generate the three-panel model comparison:

```bash
python scripts/generate_oblique_comparison.py
````

The default output is:

```text
figures/generated/oblique_models_comparison.svg
```

The figure compares:

* `NJG_INC`: exact square-circle incidence;
* `NJG_28`: exact 28-fold angular division;
* `NJG_SVG`: the 2008 Wikimedia reconstruction.

Each panel contains the same verified Earth-Moon core. Only the placement rule
for the eight oblique Moon circles changes. The residual bars use a common
scale across all three panels.

## Figure 12 outer-wall evidence comparison

Generate the three-model source comparison:

```bash
python scripts/generate_figure12_wall_evidence.py
```

The default SVG output is:

```text
figures/generated/figure12_wall_evidence_comparison.svg
```

The comparison holds the exact `NJG_INC` Moon geometry fixed and tests three
outer-wall rules against the affine-calibrated Figure 12 wall:

| Wall model                  |    Angle RMS | Support RMS |
| --------------------------- | -----------: | ----------: |
| `POLAR_PIVOT_TANGENT`       | 1.019836 deg |  0.038999 u |
| `REGULAR_DIRECTION_TANGENT` | 1.458882 deg |  0.036819 u |
| `RADIAL_SUPPORT`            | 4.755396 deg |  0.032822 u |

The angular ranking is reproduced across all three independent Figure 12
digitisation passes.

`POLAR_PIVOT_TANGENT` is the current preferred combined reconstruction because
it gives the best wall-direction agreement and independently reproduces
Michell's later Sommerville dimensions:

* four polar sides: approximately 3279.698 ft versus 3280 ft;
* eight oblique sides: approximately 3271.121 ft versus 3270 ft;
* area: approximately 120,002,600 ft^2 versus 120,000,000 ft^2;
* old-English-foot perimeter: approximately 36,013.8 ft versus 36,000 ft.

The support-distance metric by itself instead favours `RADIAL_SUPPORT`. This
counter-evidence is retained explicitly; the polar-pivot construction is
therefore described as a source-supported project reconstruction rather than
as a uniquely established historical construction.

### Historical radial-support artifact

The earlier figure remains preserved at:

```text
figures/generated/michell_outer_wall.svg
```

and can still be regenerated with:

```bash
python scripts/generate_michell_outer_wall.py
```

It records the project's earlier radial-support inference and is retained for
reproducibility. It is no longer the preferred Figure 12 wall reconstruction.

## Analyse Michell's approximate 28-point scaffold

Run:

```bash
python scripts/analyze_septenary_scaffold.py
````

This reconstructs the approximate sevenfold step described in Figure 194,
repeats it through four quadrants to obtain twenty-eight points, classifies the
points into Michell's stated 12 + 8 + 8 roles, and compares the resulting Moon
centres with the exact-incidence `NJG_INC` model.

## Visualise Michell's approximate 28-point scaffold

Generate the comparison SVG:

```bash
python scripts/generate_michell_28_point_scaffold.py
````

The default output is:

```text
figures/generated/michell_28_point_scaffold.svg
```

The figure shows:

* the twenty-eight approximate scaffold points;
* Michell's 12 + 8 + 8 role classification;
* twelve Moon circles positioned by the scaffold;
* the source-supported `NJG_INC` Moon circles;
* the displacement between the two centre systems;
* the eight square-circle incidence points;
* a magnified oblique-centre displacement inset;
* the exact circumference accounting under the pi = 22/7 convention.

The SVG background is transparent. The inset magnification may be changed with:

```bash
python scripts/generate_michell_28_point_scaffold.py \
  --displacement-magnification 60
```

## Analyse Michell's Figure 14 heptagram

Run:

```bash
python scripts/analyze_figure14_heptagram.py
````

The analysis reconstructs the seven endpoint roles visible in Figure 14,
compares exact-regular, Michell-28-point, and Figure-14-aligned vertex systems,
and uses the source-supported heptagram `{7/2}` traversal.

Five endpoints are supported by Michell's text and printed plate. The two
inter-Moon-gap endpoints remain explicitly labelled as plate-based project
inferences.

Three independent near-endpoint line-tracing passes sampled 42 printed-stroke
directions. The `{7/2}` candidate won all 21 endpoint/pass comparisons, with an
angular RMS residual of 1.248033670 degrees, compared with 24.993300526 degrees
for `{7/3}`.

The full calibration result is documented in
[`docs/geometry/figure14_source_calibration_results.md`](docs/geometry/figure14_source_calibration_results.md).

## Visualise Michell's Figure 14 heptagram candidates

Generate the three-panel comparison SVG:

```bash
python scripts/generate_michell_figure14_heptagram.py
````

The default output is:

```text
figures/generated/michell_figure14_heptagram.svg
```

The figure compares:

* an exact regular `{7/2}` heptagram;
* a `{7/2}` heptagram selected from Michell's approximate 28-point scaffold;
* a Figure-14-aligned `{7/2}` heptagram.

Black circular markers identify the five text-and-plate anchors. Open orange
diamonds identify the two inter-Moon-gap anchors inferred from the printed
plate. Dashed orange segments show candidate-to-anchor residuals.

The SVG is a transparent-background computational reconstruction and is not
a facsimile of Michell's printed plate.
