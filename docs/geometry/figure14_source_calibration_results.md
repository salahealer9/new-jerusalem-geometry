# Figure 14 source-plate calibration results

## Status

This document records the completed source calibration of John Michell's
Figure 14 seven-pointed star.

The result supersedes the provisional `{7/3}` project reconstruction recorded
at the `v0.1.0` architectural checkpoint. The calibrated printed topology is
consistent with `{7/2}`.

## Evidence boundary

The source plate is treated as measured historical evidence, not as an exact
Euclidean construction.

The audit separates:

1. source rendering and provenance;
2. repeated manual landmark digitisation;
3. affine registration;
4. endpoint regularity and radius analysis;
5. independent printed-line topology testing;
6. canonical computational reconstruction.

No endpoint coordinates were used to choose between `{7/2}` and `{7/3}`.
Those two heptagrams share the same regular seven-vertex set. Their edge
topology was tested independently from the printed near-endpoint strokes.

## Source preparation

The source page was rendered locally from *City of Revelation* at 300 DPI.

- source PDF SHA-256:
  `ce161c0703c3080948fb437bebab7b283ff28621492440357f9b13c80ab3fdbd`;
- rendered PNG dimensions: 1512 by 2327 pixels;
- rendered PNG SHA-256:
  `d2ba830db44db6b0a6db8a6d41be780e2f9ef6391d6d832355d0531c282563fa`.

The source PDF and rendered page remain private local inputs.

## Landmark digitisation

The fixed schema contains 31 landmarks:

- 4 square corners;
- 8 square/construction-circle junctions;
- 12 Moon-circle centres;
- 7 visually observed star endpoints.

Three independent passes produced 93 landmark observations.

Digitisation quality-control values were:

- overall click RMS: 0.895722 pixels;
- median landmark RMS: 0.547206 pixels;
- maximum pairwise separation: 5.516718 pixels.

The raw landmark passes were preserved. A documented cyclic relabelling was
applied only to the eight junction identities, followed by a documented
semantic correspondence resolution for the Moon centres and star endpoints.

## Affine registration

Similarity, affine, and projective models were compared using training and
leave-one-out residuals.

The affine model was selected:

- training RMS: 1.919266 pixels;
- leave-one-out RMS: 2.545170 pixels;
- maximum leave-one-out residual: 4.245118 pixels;
- anisotropy ratio: 1.023099307;
- mean scale: 71.477973517 pixels per normalized unit;
- leave-one-out equivalent: 0.035607747 normalized units.

The projective model reduced training residual only slightly while increasing
leave-one-out error. The similarity model underfit the plate.

## Endpoint geometry

A free regular seven-vertex fit to the calibrated source endpoints gives:

- centre: `(0.003540084, -0.011232015)` normalized units;
- centre displacement: 0.011776687 normalized units;
- radius: 7.010785783 normalized units;
- phase: 90.172294927 degrees;
- RMS residual: 0.017951284 normalized units;
- maximum residual: 0.025103754 normalized units;
- angular RMS: 0.118418906 degrees.

With the centre fixed at the origin and radius fixed at 7, the best-phase fit
has:

- phase: 90.172294927 degrees;
- RMS residual: 0.024026486 normalized units;
- maximum residual: 0.039153283 normalized units.

The fully canonical origin-centred, radius-7, top-vertex construction has:

- RMS residual: 0.031953847 normalized units;
- maximum residual: 0.059258803 normalized units.

The free-fit RMS is approximately 0.504140 of the affine leave-one-out
registration scale. The endpoint geometry therefore supports a near-regular
radius-7 vertex system but does not by itself identify the edge traversal.

## Independent edge-topology audit

At each calibrated endpoint, two points were sampled on the two printed
strokes immediately inside the endpoint. Sampling near the endpoints avoids
ambiguity at the internal line crossings.

The audit used:

- 3 independent tracing passes;
- 7 endpoints per pass;
- 2 ray samples per endpoint;
- 42 total ray samples;
- 21 endpoint/pass topology comparisons.

Candidate results:

| Rank | Connection | Step | Angular RMS | Maximum residual | Wins |
|---:|---|---:|---:|---:|---:|
| 1 | `{7/2}` | 2 | 1.248033670 degrees | 2.765953418 degrees | 21/21 |
| 2 | `{7/3}` | 3 | 24.993300526 degrees | 27.188061375 degrees | 0/21 |
| 3 | perimeter | 1 | 26.476050606 degrees | 28.615104636 degrees | 0/21 |

The RMS margin between `{7/2}` and the second-ranked candidate is
23.745266856 degrees.

The result is unanimous across all endpoint/pass comparisons.

## Promoted evidence

The three raw edge-tracing passes were promoted byte-for-byte:

- pass 01:
  `d9cba92ab9cbb335df48b4b4a0a322d58b51c526d5b620274cf332f4c3401a06`;
- pass 02:
  `feec511b6c5527a60b36bdb436d7df1df62212af7b68b4aa2717432e3be7f0ec`;
- pass 03:
  `a82223673efd3d43073ab2e9f8c963f0f5da10721c281cb8f69ae5a7b69eccca`.

Derived evidence hashes:

- details CSV:
  `75831974d760dab5714ccef6f2973b467fe9186cc76964067747b4201291a8cd`;
- Markdown report:
  `180e123fd9bceeffba86b146d72fb4a6e4ef9a8ad7c2d6dce002465ad0d727bd`;
- summary JSON:
  `ed2cedcef9138e283a6a42b1238b9d1744b4fc0a42ab53757fd104fa9a94a1d1`;
- promotion manifest:
  `e9a63b6af932975ae5b9e8ec3bac43b01556c161aa6b4e21d60a87b51ee5c661`.

The relevant tracked tree is:

```text
data/calibration/figure14/
├── raw/
├── corrected/
├── correspondence_resolved/
├── derived/
└── edge_topology/
    ├── raw/
    ├── derived/
    └── edge_topology_manifest.json
````

## Canonical result

The calibrated Figure 14 source supports the following reconstruction:

> Michell's Figure 14 depicts a near-regular `{7/2}` heptagram inscribed
> approximately in the radius-7 construction circle.

The canonical traversal from the upper vertex is:

```text
0, 2, 4, 6, 1, 3, 5
```

The earlier `{7/3}` reconstruction is retained only in historical checkpoint
documentation and as a rejected comparison candidate in the topology audit.

## Limitations

The result remains subject to:

* source reproduction quality;
* printed-line thickness;
* manual landmark and ray sampling;
* affine-registration uncertainty;
* the distinction between Michell's approximate printed construction and an
  exact regular Euclidean heptagram.

Within those limits, the separation between `{7/2}` and `{7/3}` is large,
unanimous across the repeated tracing passes, and much greater than the
near-endpoint sampling residuals.
