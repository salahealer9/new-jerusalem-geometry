# Figure 12 outer-wall reconstruction result

## Status

The preferred current reconstruction of Michell's Figure 12 outer wall is the
**polar-pivot tangent construction**.

This is a source-supported project reconstruction. It is not claimed to be a
construction rule stated uniquely or explicitly by John Michell.

## Candidate constructions

Three wall rules were tested.

### RADIAL_SUPPORT

Each wall normal points through the corresponding Moon centre and the wall side
is the outward support tangent to that Moon.

This was the project's earlier wall inference.

### REGULAR_DIRECTION_TANGENT

The twelve wall normals retain regular-dodecagon directions at 30-degree
intervals. Each wall side is translated until tangent to its corresponding
Moon.

### POLAR_PIVOT_TANGENT

The four polar wall sides remain fixed.

Each of the eight oblique sides begins as a side of the regular dodecagon and
is pivoted inward about its endpoint on the neighbouring polar side until it
is tangent to its corresponding Moon circle.

The Moon placement used for the exact reconstruction is NJG_INC.

## Figure 12 plate comparison

Using the fixed centroid affine registration:

| Model | Angle RMS | Support RMS |
|---|---:|---:|
| POLAR_PIVOT_TANGENT | 1.019835793 deg | 0.038999406 u |
| REGULAR_DIRECTION_TANGENT | 1.458881984 deg | 0.036819219 u |
| RADIAL_SUPPORT | 4.755395950 deg | 0.032822024 u |

The polar-pivot construction therefore gives the best wall-direction agreement.

The support-distance residual instead favours RADIAL_SUPPORT. This distinction
is retained explicitly and the plate is not treated as an exact geometric
drawing.

## Independent-pass stability

The angular ranking is identical in all three independently digitised and
registered passes:

    POLAR_PIVOT_TANGENT
      < REGULAR_DIRECTION_TANGENT
      << RADIAL_SUPPORT

The support-distance ranking is also stable across all three passes:

    RADIAL_SUPPORT
      < REGULAR_DIRECTION_TANGENT
      < POLAR_PIVOT_TANGENT

## Exact polar-pivot geometry

For NJG_INC:

- polar-side length:
  4.555136271329 u = 3279.698115 ft;
- oblique-side length:
  4.543223126508 u = 3271.120651 ft;
- perimeter:
  54.566330097384 u;
- area:
  231.486496089401 u^2
  = 120,002,599.573 ft^2;
- perimeter in the old-English-foot conversion:
  approximately 36,013.778 ft.

## Historical numerical comparison

Michell's later discussion reports approximately:

- four longer sides of 3280 ft;
- eight shorter sides of 3270 ft;
- area close to 120,000,000 square feet;
- perimeter virtually 36,000 old English feet.

The polar-pivot reconstruction differs by approximately:

- polar side: -0.009204%;
- oblique side: +0.034271%;
- area: +0.002166%;
- old-English perimeter: +0.038272%.

All four are within approximately the 1:2500 tolerance discussed in connection
with Sommerville's analysis.

## Interpretation

The combined evidence favours the polar-pivot tangent construction as the
current source-supported reconstruction because:

1. it gives the lowest Figure 12 wall-direction residual;
2. that angular preference is reproduced in all three independent
   digitisation passes;
3. it naturally produces four longer polar sides and eight shorter oblique
   sides;
4. its dimensions closely reproduce the later Michell/Sommerville numerical
   values.

The source plate's support distances do not uniquely select this construction,
so the result remains a project reconstruction rather than an asserted
historical construction rule.

The earlier radial-support model is preserved for reproducibility but is no
longer the preferred Figure 12 wall reconstruction.
