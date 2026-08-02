# Figure 12 plate-registration comparison

## Evidence boundary

Only the four Earth-square corners and eight square/construction-circle junctions are used for registration.

Moon-circumference observations and outer-wall observations do not influence any fitted transformation.

## Centroid model comparison

| Rank | Model | Training RMS (px) | LOO RMS (px) | LOO max (px) | Anisotropy | Perspective |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `affine` | 1.342228 | 1.790924 | 2.541469 | 1.013122338 | 0 |
| 2 | `projective` | 1.292473 | 1.956598 | 3.334061 | 1.013950089 | 0.000187973178064 |
| 3 | `similarity` | 3.659795 | 4.386620 | 5.751442 | 1.000000000 | 0 |

## Independent-pass fits

| Dataset | Model | Training RMS (px) | LOO RMS (px) | LOO max (px) |
|---|---|---:|---:|---:|
| `pass-01` | `similarity` | 3.720796 | 4.463466 | 5.860725 |
| `pass-01` | `affine` | 1.427672 | 1.886571 | 3.439698 |
| `pass-01` | `projective` | 1.305806 | 1.945009 | 3.151911 |
| `pass-02` | `similarity` | 3.626213 | 4.339067 | 5.500790 |
| `pass-02` | `affine` | 1.447859 | 1.944321 | 2.974535 |
| `pass-02` | `projective` | 1.421997 | 2.169921 | 3.546234 |
| `pass-03` | `similarity` | 3.865202 | 4.637519 | 6.421379 |
| `pass-03` | `affine` | 1.683826 | 2.251123 | 3.366914 |
| `pass-03` | `projective` | 1.628455 | 2.474501 | 3.840204 |

## Selection boundary

No registration family is selected merely because it has the smallest training error.

Selection must consider leave-one-landmark-out prediction, maximum prediction error, affine anisotropy, projective perspective magnitude, independent-pass stability, and geometric plausibility.

No Moon-placement or wall hypothesis is evaluated at this stage.
