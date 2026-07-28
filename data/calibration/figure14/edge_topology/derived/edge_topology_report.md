# Figure 14 near-endpoint line-topology audit

## Method

Two points were sampled on the two printed strokes immediately
inside each of the seven source-calibrated endpoints. Sampling
near the endpoints avoids ambiguity at the internal crossings.

The two clicks at each endpoint were treated as an unordered pair.
Their directions were compared with the two chord directions
expected for connection steps 1, 2, and 3.

- Independent passes: 3
- Endpoints per pass: 7
- Endpoint/pass comparisons: 21
- Total ray samples: 42

## Candidate ranking

| Rank | Connection | Step | Angular RMS | Maximum residual | Endpoint/pass wins |
|---:|---|---:|---:|---:|---:|
| 1 | {7/2} | 2 | 1.248033670° | 2.765953418° | 21/21 |
| 2 | {7/3} | 3 | 24.993300526° | 27.188061375° | 0/21 |
| 3 | perimeter | 1 | 26.476050606° | 28.615104636° | 0/21 |

## Selected topology

- Selected connection: **{7/2}**
- Selected angular RMS: 1.248033670°
- Selected maximum residual: 2.765953418°
- Second-best angular RMS: 24.993300526°
- RMS margin: 23.745266856°
- Unanimous across endpoint/pass comparisons: yes

## Interpretation boundary

This audit provides direct evidence from the printed line
directions immediately inside the endpoints. It does not rely
on the prior endpoint-row sequence or on resolving the internal
line crossings.

The result remains subject to printed-line thickness, source
reproduction quality, affine-registration uncertainty, and
manual sampling uncertainty.
