# Figure 14 source-derived star endpoint geometry

## Evidence boundary

This analysis uses the seven correspondence-resolved endpoint
centroids obtained from the selected affine plate registration.
No heptagram edge topology is assumed.

## Regular seven-vertex fits

| Model | Free parameters | Centre (u) | Radius (u) | Phase | RMS residual (u) | Maximum residual (u) | Angular RMS |
|---|---|---|---:|---:|---:|---:|---:|
| Free regular fit | centre, radius, phase | (+0.003540084, -0.011232015) | 7.010785783 | 90.172294927° | 0.017951284 | 0.025103754 | 0.118418906° |
| Origin, radius 7 | phase only | (0, 0) | 7.000000000 | 90.172294927° | 0.024026486 | 0.039153283 | 0.143297920° |
| Canonical origin, radius 7 | none | (0, 0) | 7.000000000 | 90.000000000° | 0.031953847 | 0.059258803 | 0.224058789° |

## Registration scale

- Mean affine scale: 71.477974 px/u
- Registration leave-one-out RMS: 2.545170 px
- Registration leave-one-out equivalent: 0.035607747 u
- Free-fit RMS / registration LOO scale: 0.504140
- Radius-7 fit RMS / registration LOO scale: 0.674754
- Canonical fit RMS / registration LOO scale: 0.897385

These ratios are scale comparisons, not statistical z-scores.

## Chord statistics

| Connection step | Geometric role | Observed mean (u) | Observed SD (u) | Exact radius-7 value (u) |
|---:|---|---:|---:|---:|
| 1 | Seven-vertex perimeter | 6.083745959 | 0.021123688 | 6.074372348 |
| 2 | Possible `{7/2}` edge | 10.962528721 | 0.019509975 | 10.945640755 |
| 3 | Possible `{7/3}` edge | 13.670038350 | 0.017338950 | 13.648990771 |

## Topology boundary

The seven endpoint coordinates determine a vertex set but do not distinguish a regular {7/2} from a regular {7/3}, because both topologies use the same seven vertices. Edge adjacency must be established from the printed line connections or an independent line-tracing audit.

The endpoint geometry may establish regularity, centre, radius,
and angular phase. It cannot by itself establish whether the
printed edges connect every second or every third vertex.
