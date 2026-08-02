# Figure 12 source-plate calibration protocol

## Purpose

This phase measures John Michell's printed Figure 12 directly in order to test
two related but logically separate parts of the New Jerusalem reconstruction:

1. the placement of the twelve Moon circles;
2. the geometry of the enclosing twelve-sided wall.

The source plate is treated as measured historical evidence, not as an exact
Euclidean drawing.

The existing analytic constructions are candidate models. They must not be
used to force the source measurements into a preferred result.

## Primary source

Primary source:

- John Michell, *City of Revelation*;
- Figure 12;
- printed page 63;
- PDF page 65 in the frozen project source copy.

Relevant textual context occurs across the surrounding discussion of the
twelve Moon circles and enclosing wall.

The private source PDF and rendered source image are not committed.

## Questions

### Moon placement

The source calibration will test whether the printed Moon centres are most
consistent with:

- `NJG_INC`: exact square/construction-circle incidence placement;
- `NJG_MICHELL_28`: Michell's approximate twenty-eight-point scaffold;
- `NJG_28`: exact regular twenty-eightfold idealisation;
- `NJG_SVG`: the independent Wikimedia reconstruction.

No candidate model is selected from appearance alone.

### Outer wall

The existing radial-support wall is a project inference.

Its rule is:

1. associate one outward support line with each Moon circle;
2. orient that line perpendicular to the radius through the Moon centre;
3. place it tangent to the Moon circle;
4. intersect consecutive support lines to obtain twelve wall vertices.

The source calibration will test this construction rather than assume it.

Michell's textual statement that the enclosing figure is not quite a regular
dodecagon and that four pairs of sides are drawn inward to touch Moon circles
is treated separately from the project's stronger radial-support hypothesis.

## Source preparation

The Figure 12 source page is rendered deterministically from the frozen
private PDF.

Default preparation parameters:

- PDF page: 65;
- resolution: 300 DPI;
- output directory: `data/working/figure12/`.

The rendering manifest records:

- source PDF identity;
- source PDF SHA-256;
- page number;
- rendering resolution;
- rendered image dimensions;
- rendered image SHA-256.

The source PDF, rendered PNG, and local preparation manifest remain outside
the tracked repository.

## Calibration coordinate system

The normalized project coordinate system is retained:

- origin at the common Earth/construction-circle centre;
- Earth square side: 11 units;
- Earth radius: 5.5 units;
- construction-circle radius: 7 units;
- Moon radius: 1.5 units.

Pixel coordinates use the source-image convention with y increasing
downwards.

Registered normalized coordinates use the geometric convention with y
increasing upwards.

## Registration landmarks

Registration is performed independently of Moon placement and wall geometry.

The default registration landmarks are:

- four Earth-square corners;
- eight Earth-square/construction-circle intersections.

These twelve landmarks have model coordinates determined by the common core
geometry.

Moon centres, wall lines, wall vertices, and tangency observations must not be
used to fit the registration transformation.

## Structural Moon observations

The printed plate does not explicitly mark the Moon-circle centres. Centre
coordinates will therefore not be estimated by clicking apparent centres
directly.

For each of the twelve Moon circles, six well-separated points will be sampled
from clearly visible circumference arcs. Samples should avoid line crossings,
tangencies, heavy overprinting, and wall vertices wherever possible.

The complete Moon sampling design is therefore:

- 12 Moon circles;
- 6 circumference samples per circle;
- 3 independent passes;
- 216 raw Moon-circumference observations.

No candidate Moon-placement coordinates are assigned during digitisation.

After registration, the six circumference samples for each Moon and pass are
fitted to a free circle in normalized coordinates. The fitted centre is the
source-derived Moon-centre observation. The fitted radius is retained as an
independent diagnostic rather than fixed to the theoretical radius of 1.5
units.

The three independently fitted centres for each Moon provide a direct estimate
of centre-location repeatability.

## Wall-line observations

The wall is tested primarily as a set of printed lines rather than from
manually inferred vertices.

For every one of the twelve visible wall sides:

- sample three well-separated points on the printed stroke;
- avoid the wall vertices where line thickness or intersections make the
  direction ambiguous;
- repeat the full sampling procedure in three independent passes.

This produces:

- 12 wall sides;
- 3 samples per side;
- 3 independent passes;
- 108 wall-line point observations.

Each wall side is fitted independently from its source samples.

Wall vertices are then derived from intersections of adjacent fitted lines.

## Registration-model comparison

The same model-selection framework used for Figure 14 will be applied:

- similarity transformation;
- affine transformation;
- projective transformation.

Models are compared using:

- training residual;
- leave-one-out residual;
- maximum leave-one-out residual;
- anisotropy;
- perspective distortion where applicable;
- geometric plausibility.

A more flexible transformation is not selected merely because it lowers the
training residual.

## Moon-model comparison

After registration and source-circle fitting, the twelve source-derived Moon
centres are compared against each candidate construction.

The three independent passes are retained separately when estimating
measurement repeatability before pass-mean centres are formed.

Reported diagnostics will include:

- pointwise centre displacement;
- RMS centre displacement;
- maximum centre displacement;
- angular displacement;
- radial displacement;
- cardinal versus oblique subsets.

The eight oblique centres are the principal discriminating observations,
because the four cardinal centres are common to the candidate models.

## Wall-model comparison

For every observed wall side the source-derived fitted line will be compared
with candidate wall lines using:

- normal-angle residual;
- signed perpendicular offset residual;
- distance from the corresponding Moon centre;
- Moon-circle tangency residual;
- derived adjacent-vertex displacement.

Global diagnostics will include:

- RMS line-angle residual;
- RMS offset residual;
- maximum line residual;
- side-length classes;
- perimeter;
- polygon area;
- symmetry diagnostics.

## Evidence hierarchy

Results will be labelled explicitly as one of:

- `source_statement`;
- `source_plate_measurement`;
- `project_derivation`;
- `project_inference`;
- `external_reconstruction`.

A good numerical fit does not convert a project inference into an explicit
historical statement.

## Decision rule

The source plate determines the result.

Possible outcomes include:

- support for `NJG_INC`;
- support for Michell's approximate 28-point placement;
- inability to distinguish the closely spaced candidates at plate precision;
- support for the radial-support wall;
- rejection or modification of the radial-support wall;
- evidence for a different wall construction.

No preferred outcome is required for the calibration to succeed.

## Reproducibility boundary

Raw digitisation and wall-line trace passes are preserved unchanged.

Any semantic relabelling, coordinate promotion, registration, model fitting,
or derived measurement is stored as a separate deterministic layer.

Repeated analysis must reproduce identical derived files and hashes from the
same promoted raw observations.
