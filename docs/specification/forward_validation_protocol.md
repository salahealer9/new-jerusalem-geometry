# NJG_MICHELL frozen forward-validation protocol

## Status

This protocol defines the v0.4 forward validation of the integrated
`NJG_MICHELL` construction.

The predictor is frozen at Git commit:

`43096326d5c1862fc7e33f9d90eb1df861c3b642`

Commit subject:

`Promote NJG_MICHELL forward composite reconstruction`

The validation is descriptive frozen forward validation with no refitting.

It is not described as a statistically independent hold-out experiment,
because the Figure 12 and Figure 14 source plates informed earlier stages of
model development and hypothesis selection.

The purpose of this phase is narrower and auditable:

1. freeze the integrated predictor;
2. prohibit source-calibration quantities from entering the predictor;
3. evaluate that fixed predictor against the promoted source-derived geometry;
4. report residuals without fitting new geometric degrees of freedom.

## Generative boundary

`build_michell_composite(unit=1.0)` is the frozen predictor.

The caller supplies only the scale unit.

The predictor must not receive:

- Figure 12 digitised landmarks;
- Figure 12 affine-registration parameters;
- Figure 12 source-derived wall measurements;
- Figure 14 digitised landmarks;
- Figure 14 affine-registration parameters;
- Figure 14 registered endpoint coordinates;
- Figure 14 fitted phase, centre, or radius;
- plate-derived fitting parameters of any kind.

The validation layer may read both the frozen prediction and the promoted
calibration data. Information flow must remain one-way:

```text
NJG_MICHELL prediction ──┐
                         ├──> validation report
source calibration ──────┘
````

Calibration data must never flow back into `NJG_MICHELL`.

## No-refitting rule

No parameter may be optimized during validation.

In particular, validation must not fit or adjust:

* translation;
* rotation;
* phase;
* isotropic scale;
* anisotropic scale;
* affine transformation;
* projective transformation;
* Moon-centre positions;
* wall-line orientations;
* wall-line supports;
* heptagram vertex positions;
* vertex permutations or cyclic reassignments.

Any correspondence used in validation must already have been fixed upstream
and promoted before this protocol.

## Figure 12 validation

### Prediction

Use the `NJG_MICHELL` polar-pivot wall generated at `unit=1.0`.

### Source target

Use the promoted normalized Figure 12 source geometry under:

`data/calibration/figure12/source_geometry/`

The primary comparison must use the already registered normalized wall
geometry rather than raw pixel coordinates.

### Primary line metrics

For the twelve corresponding wall lines report:

1. RMS normal-angle residual in degrees;
2. maximum normal-angle residual in degrees;
3. RMS support residual in normalized units;
4. maximum support residual in normalized units.

Correspondence must follow the existing fixed semantic wall ordering. No new
wall permutation may be selected from the validation residuals.

### Secondary polygon metrics

Where the promoted source representation provides the necessary fixed
correspondence, also report:

1. wall-vertex RMS point residual;
2. wall-vertex maximum point residual;
3. side-length RMS residual;
4. perimeter residual;
5. relative perimeter residual;
6. area residual;
7. relative area residual.

The line metrics are primary because they compare the actual geometric wall
constraints directly. Perimeter and area are secondary global diagnostics.

### Structural diagnostics

Report separately:

* 12 predicted wall sides;
* 4 polar sides;
* 8 oblique pivoted sides.

No Figure 12 metric is used to modify the polar-pivot construction.

## Figure 14 validation

### Prediction

Use only:

`NJG_MICHELL.scaffold_heptagram_candidate`

This is the seven-vertex candidate selected from the independently generated
28-point scaffold.

Do not use `build_figure14_aligned_heptagram()` as the predictor.

### Source target

Use the promoted affine-registered Figure 14 star endpoint centroids under:

`data/calibration/figure14/derived/`

Use only the semantic endpoint correspondence already fixed upstream.

No new cyclic shift, reflection, permutation, phase fit, radius fit, centre
fit, or registration fit may be performed.

### Primary positional metrics

For the seven fixed corresponding vertices report:

1. RMS Euclidean point residual in normalized units;
2. maximum Euclidean point residual;
3. RMS angular residual in degrees;
4. maximum angular residual in degrees;
5. RMS radial residual relative to radius 7;
6. maximum radial residual relative to radius 7.

### Evidence subsets

Also report Euclidean point residuals separately for:

* the five source-text-supported endpoint identities;
* the two plate-inferred endpoint identities.

The seven-point aggregate must not erase this evidential distinction.

### Registration-scale diagnostic

Report:

`vertex RMS / affine-registration LOO equivalent`

using the already promoted Figure 14 registration uncertainty scale.

This ratio is a descriptive diagnostic only. It is not a p-value and no
pass/fail threshold is assigned to it.

### Canonical comparator

As a fixed benchmark, also evaluate the canonical regular radius-7 heptagram
with top vertex at 90 degrees.

The comparator receives exactly the same no-refitting treatment.

This comparison asks whether the approximate 28-point scaffold candidate
predicts the printed vertex locations better or worse than the simpler
canonical regular heptagram.

### Topology boundary

The `{7/2}` edge topology is not counted as a new forward positional
prediction in this validation.

That topology was selected earlier using the independent Figure 14 printed-line
edge-tracing audit.

The positional validation concerns the scaffold-derived vertex set.

## Interpretation

No post-hoc pass/fail threshold will be introduced.

The report will present:

* fixed-predictor residuals;
* source-registration and repeatability scales where already available;
* the canonical Figure 14 comparator;
* evidence-class-separated metrics;
* limitations arising from source reproduction, manual digitisation,
  registration, and prior model-development exposure.

Any subsequent modification of `NJG_MICHELL` motivated by these validation
residuals must occur in a later model version and must not be retroactively
reported as part of this frozen v0.4 validation.
