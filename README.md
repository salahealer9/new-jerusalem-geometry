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

Version `v0.8.0` is the Figure 194 dual-method construction checkpoint.

The repository now preserves both approximate sevenfold construction branches
described by Michell:

```text
Method 1: 7 -> 14 -> 28
Method 2: 7 -> 21 -> 42
```

Method 1 remains the branch used by the existing `NJG_MICHELL` forward
composite. Method 2 is audited separately and is not silently inserted into
that composite.

The v0.8 audit reconstructs the Method 2 local identity
`alpha_2 = acos(5/8)`, preregisters and executes the 21/42-point propagation,
derives the resulting two-class gap structure, and provides a deterministic
transparent SVG.

The symbolic gap derivation is explicitly post-result explanatory work, not a
preregistered prediction or a claim of historical intention.


## v0.8 Figure 194 dual-method audit

The complete synthesis is:

```text
docs/geometry/v0.8_figure194_dual_method_synthesis.md
```

The two local approximate steps are:

```text
exact 360/7:  51.42857142857143 deg
Method 1:     51.47070143243995 deg
Method 2:     51.31781254651057 deg
```

so the exact regular step lies between the two approximations. Method 1 is the
more accurate local construction.

Method 2 propagates through the source-described `7 -> 21 -> 42` branch. Its
entire nonuniformity is explained by:

```text
delta = 2*pi/7 - alpha_2

RMS_21   = sqrt(10)*delta
MAX_21   = 5*delta
RANGE_21 = 7*delta

RMS_42   = sqrt(6)*delta
MAX_42   = 6*delta
RANGE_42 = 7*delta
```

The exact cross-relations are:

```text
RMS_42 / RMS_21 = sqrt(3/5)
MAX_42 / MAX_21 = 6/5
RANGE_42 / RANGE_21 = 1
```

The reciprocal stage lowers raw RMS but raises worst-case error and normalized
RMS, so it is not assigned an unqualified "more regular" or "less regular"
label.

Generate the v0.8 analyses and visualization with:

```bash
python scripts/analyze_v0_8_dual_method.py
python scripts/analyze_v0_8_method2_propagation.py
python scripts/analyze_v0_8_method2_symbolic_gap.py
python scripts/generate_v0_8_method2_propagation_svg.py
```

Canonical visualization:

```text
figures/generated/v0.8_method2_7_21_42.svg
```

The SVG is visualization-only and does not feed back into model selection,
calibration, or fitting.

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
```

Run the core verification:

```bash
python scripts/verify_core_geometry.py
```

Run the automated tests:

```bash
pytest
```

The executable model now includes the normalized Earth-Moon core, competing
oblique Moon-circle placements, Michell's approximate septenary construction,
the reciprocal fourteenfold extension, the four-triangle 28-point scaffold,
source-calibrated Figure 12 Moon and wall geometry, the preferred polar-pivot
outer-wall reconstruction, the source-calibrated Figure 14 heptagram, and the
integrated unit-only `NJG_MICHELL` forward composite.

Competing constructions remain explicitly separated rather than being merged
without evidential justification. The frozen validation layer is downstream of
the composite and supplies no fitted parameters back into the generative model.

## NJG_MICHELL integrated forward reconstruction

The v0.5 `NJG_MICHELL` composite can be analysed with:

```bash
python scripts/analyze_michell_composite.py
```

`NJG_MICHELL` accepts only the scale unit as a caller-supplied geometric
quantity. It deterministically combines:

* the normalized Earth-Moon core;
* the exact-incidence `NJG_INC` Moon system;
* Michell's four groups of three Moon circles;
* the preferred polar-pivot wall reconstruction;
* the approximate Method-1 sevenfold construction;
* the reciprocal fourteenfold construction;
* the four-triangle 28-point scaffold;
* a scaffold-derived `{7/2}` Figure 14 candidate.

The independently formulated four-triangle construction and the role-labelled
28-point scaffold coincide to floating-point precision, with a maximum angular
mismatch of approximately `2.220e-16` radians.

Plate calibration, digitisation, registration, and measured source landmarks
are excluded from this generative composite.

## v0.5 generative outputs and phase audit

Generate the complete canonical `NJG_MICHELL` SVG:

```bash
python scripts/generate_michell_composite.py
```

Generate the machine-readable geometry export:

```bash
python scripts/generate_michell_geometry.py
```

Generate the provenance manifest:

```bash
python scripts/generate_michell_provenance.py
```

Run the completed sevenfold phase-selection audit:

```bash
python scripts/audit_sevenfold_phase_selection_stage_b.py
```

The canonical geometry and provenance exports each contain 132 objects with
the same ordered `(object_id, geometry_type)` identity. The SVG contains 59
provenance-linked rendered objects.

The Phase 5E generative-invariance audit passes at the registered scales
`0.25`, `0.73`, `1.00`, `2.75`, and `8.00`.

For the sevenfold phase question, Stage A remains
`GRAMMAR_UNDERDETERMINED`: phases 0, 1, 2, and 3 all survive the grammar-only
audit. Stage B then compares those frozen candidates to the promoted Figure
14 endpoints with 14 discrete cyclic/orientation correspondences per phase
and no continuous refitting. The descriptive source-consistency ranking is
`[3, 0, 2, 1]`, with phase 3 preferred.

That Stage B result is not an independent prediction and does not change the
grammar-only conclusion.

## Frozen forward validation (v0.4 validation layer)

The preregistered no-refitting validation can be reproduced with:

```bash
python scripts/analyze_forward_validation.py
```

The predictor was frozen at commit
`43096326d5c1862fc7e33f9d90eb1df861c3b642` before the validation metrics were
calculated.

For Figure 12, the frozen polar-pivot wall gives:

* wall-normal angular RMS: approximately `1.019836` degrees;
* wall-support RMS: approximately `0.038999 u`;
* wall-vertex RMS: approximately `0.100022 u`;
* perimeter difference from the affine-calibrated source wall: `-0.379134%`;
* area difference: `-0.709332%`.

The global dimensions are therefore close while measurable local
line, vertex, and side-length discrepancies remain.

For Figure 14, the fixed scaffold-derived candidate gives:

| Metric        | Scaffold candidate | Canonical regular |
| ------------- | -----------------: | ----------------: |
| Point RMS     |    `0.031023606 u` |   `0.031953847 u` |
| Point maximum |    `0.049325681 u` |   `0.059258803 u` |
| Angular RMS   |  `0.215205853 deg` | `0.224058789 deg` |

The scaffold candidate modestly improves on the fixed canonical regular
comparator without refitting. The difference remains within the source
registration uncertainty and does not establish that Michell historically
derived Figure 14 from the 28-point scaffold.

This is described as **frozen forward validation with no refitting**, not as a
statistically independent hold-out experiment, because the source plates had
already informed earlier model-development stages.

The complete report is:

```text
data/validation/njg_michell_v0_4/forward_validation_report.md
```

## Generate the verified core diagram

Generate the standalone SVG:

```bash
python scripts/generate_core_diagram.py
```

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
```

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
```

This reconstructs the approximate sevenfold step described in Figure 194,
repeats it through four quadrants to obtain twenty-eight points, classifies the
points into Michell's stated 12 + 8 + 8 roles, and compares the resulting Moon
centres with the exact-incidence `NJG_INC` model.

## Visualise Michell's approximate 28-point scaffold

Generate the comparison SVG:

```bash
python scripts/generate_michell_28_point_scaffold.py
```

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
```

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
```

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

## v0.6.0 — Historical metrology and prediction-status audit

v0.6.0 keeps the v0.5 `NJG_MICHELL` geometry frozen and audits the historical
dimensional/metrological layer around it.

```text
24 registered metrology records accounted for
6 development-used targets
0 frozen-unused targets
0 independent forward predictions
7 numerical comparison rows:
    6 retrospective
    1 descriptive
```

The later Sommerville wall dimensions are reproduced very closely by the frozen
polar-pivot wall:

```text
polar side                  -0.00920%
oblique side                +0.03427%
wall area                   +0.002166%
old-English-foot perimeter  +0.03827%
```

These are reported as retrospective agreements, not blind predictions, because
the historical dimensions were available during model development.

The earlier Figure 12 mean-side/perimeter layer differs by about +0.305754%.
No aggregate score, ranking, post-hoc tolerance, or inferred historical
uncertainty is introduced.

See `docs/checkpoints/v0.6.0.md` and
`docs/geometry/v0.6_historical_residual_sensitivity_report.md`.

## v0.7.0 — Sommerville dodecagon vertex-radius audit

v0.7.0 resolves the Figure 30 radius problem without adding a new polygon or
refitting the frozen v0.5 geometry.

The source prose says `decagon`, but source inspection shows that the marked
6336/6300 radii refer to vertices of the irregular outer dodecagon. v0.7
preserves the literal wording in provenance while treating the operational
geometric referent as `dodecagon_vertex_radii`.

The frozen polar-pivot wall already contains exactly two semantically defined
radius classes:

```text
8 polar-adjacent vertices   r = 8.79984753348571 u
4 oblique-pair vertices     r = 8.75294593972281 u
```

The eight polar-adjacent vertices lie on the parameter-free regular-dodecagon
baseline; the four oblique-pair vertices are displaced inward by
`0.0469015937628932 u`.

Under the already-frozen `720 current ft/u` scale:

```text
long radius   6335.8902241097 ft   vs 6336 ft   (-0.001732574%)
short radius  6302.1210766004 ft   vs 6300 ft   (+0.033667883%)
class ratio   1.0053583780919       vs 176/175   (-0.035388542%)
```

These are retrospective no-refit source-consistency results, not independent
forward predictions. `31680/5` is equivalent to the 6336-ft row, and `176/175`
is derived from the same long/short historical pair, so the four registered
rows are not four independent numerical matches.

See `docs/checkpoints/v0.7.0.md` and
`docs/geometry/v0.7_dodecagon_dimensional_audit_report.md`.

