# Figure 14 source-plate calibration protocol

## Purpose

This phase tests candidate geometric reconstructions against the printed
Figure 14 plate in John Michell's *City of Revelation*.

The plate is treated as measured historical evidence rather than as an exact
Euclidean construction.

## Evidential boundary

Michell states that the seven-pointed star has extremities corresponding to
points in the New Jerusalem diagram, including:

- the centres of three circles;
- two junctions of the circle and square.

The text does not uniquely identify all seven endpoints.

The current identification of two inter-Moon-gap endpoints is therefore a
project inference to be tested against the digitised plate.

## Source handling

The copyrighted source PDF and rendered page images remain local and are not
committed to the repository.

Committed records may include:

- source checksum;
- bibliographic identification;
- PDF page number;
- rendering resolution;
- rendering software and version;
- pixel dimensions;
- manually digitised landmark coordinates;
- registration and fitting results;
- derived overlays that do not reproduce the source plate itself.

## Coordinate systems

Three coordinate systems are distinguished.

### 1. PDF page coordinates

Coordinates native to the source document.

### 2. Rendered pixel coordinates

Image coordinates with:

- origin at the upper-left;
- x increasing rightward;
- y increasing downward.

### 3. Normalised diagram coordinates

Project geometry with:

- origin at the centre of the Earth circle;
- x increasing rightward;
- y increasing upward;
- Earth-square side equal to 11 units;
- construction-circle radius equal to 7 units.

No comparison may mix coordinate systems without an explicit transformation.

## Landmark classes

The calibration dataset will contain the following classes.

### Registration landmarks

- four Earth-square corners;
- visible square-circle junctions;
- selected cardinal points of the construction circle where reliably visible.

### Structural landmarks

- twelve Moon-circle centres;
- seven apparent heptagram extremities.

### Optional diagnostic landmarks

- visible Moon-circle tangencies;
- selected heptagram line intersections;
- outer-wall vertices where sufficiently distinct.

## Digitisation procedure

Landmarks will be digitised in at least three independent passes.

Each pass must:

- begin from the unchanged rendered page;
- record every point independently;
- preserve the original click coordinates;
- avoid copying coordinates from an earlier pass;
- use the same landmark names and ordering.

The repeated passes provide an empirical estimate of manual digitisation
uncertainty.

## Registration models

At least three plate-to-model transformations will be compared.

### Similarity transformation

Allows:

- translation;
- rotation;
- uniform scale.

This is the least flexible model.

### Affine transformation

Additionally allows:

- unequal horizontal and vertical scale;
- shear.

This can represent ordinary scan anisotropy.

### Projective transformation

Allows a planar homography and can represent mild perspective distortion.

The projective model must not be preferred merely because it has more
parameters. Model selection will consider:

- residuals on fitted landmarks;
- residuals on withheld landmarks;
- parameter count;
- geometric plausibility;
- stability under repeated digitisation.

## Candidate star systems

The calibrated plate endpoints will be compared against:

- exact regular `{7/2}`;
- exact regular `{7/3}`;
- Michell approximate 28-point `{7/2}`;
- Michell approximate 28-point `{7/3}`;
- the current Figure-14-aligned reconstruction;
- unconstrained seven-point plate measurements.

Both heptagram families remain candidates until the plate line topology and
endpoint fits have been tested numerically.

## Error reporting

Results will report:

- per-landmark pixel residuals;
- residuals in normalised units;
- angular residuals on the construction circle;
- RMS residual;
- maximum residual;
- repeated-digitisation uncertainty;
- model-selection diagnostics;
- sensitivity to landmark inclusion and exclusion.

A candidate will not be declared uniquely supported when competing models
remain indistinguishable within digitisation or registration uncertainty.

## Planned outputs

Committed outputs will eventually include:

- source provenance manifest without the source file;
- landmark-template CSV;
- three or more completed digitisation CSVs;
- registered landmark CSV;
- transformation-model comparison CSV;
- candidate-fit comparison CSV;
- calibration report;
- source-calibration diagnostic SVGs.

## Release boundary

The completed and verified source-calibration phase will form the basis of the
`v0.2.0` checkpoint.
