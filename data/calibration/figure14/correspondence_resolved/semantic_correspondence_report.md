# Figure 14 semantic correspondence resolution

## Data layers

The original digitisation files and the junction-corrected files
remain unchanged. This layer reassigns only coordinate pairs to
their resolved Moon-centre and spatial star-endpoint identities.

- Resolved passes: 3
- Numerical coordinate values changed: no
- Registration landmarks changed: no

## Moon-centre correspondence

- Best cyclic direction: `reversed`
- Best cyclic shift: 1
- Validation RMS after correspondence: 0.038035581 u
- Maximum validation residual: 0.058075363 u
- Second-best cyclic RMS: 3.672783232 u

| Target Moon identity | Coordinate source | Residual (u) |
|---|---|---:|
| `moon_centre_00` | `moon_centre_01` | 0.017104651 |
| `moon_centre_01` | `moon_centre_00` | 0.033736634 |
| `moon_centre_02` | `moon_centre_11` | 0.058075363 |
| `moon_centre_03` | `moon_centre_10` | 0.015276128 |
| `moon_centre_04` | `moon_centre_09` | 0.015521943 |
| `moon_centre_05` | `moon_centre_08` | 0.051478479 |
| `moon_centre_06` | `moon_centre_07` | 0.035851477 |
| `moon_centre_07` | `moon_centre_06` | 0.008898294 |
| `moon_centre_08` | `moon_centre_05` | 0.038509860 |
| `moon_centre_09` | `moon_centre_04` | 0.056031542 |
| `moon_centre_10` | `moon_centre_03` | 0.056209827 |
| `moon_centre_11` | `moon_centre_02` | 0.016913536 |

## Star endpoint circle

- Fitted centre: (-0.002237245, -0.010537990) u
- Centre displacement: 0.010772859 u
- Mean radius: 7.010804383 u
- Radial RMS: 0.009762565 u
- Radius range: 6.998732496–7.026455625 u

## Star spatial correspondence

| Spatial endpoint identity | Coordinate source |
|---|---|
| `star_endpoint_00_top` | `star_endpoint_00_top` |
| `star_endpoint_01_upper_left` | `star_endpoint_03_bottom_left` |
| `star_endpoint_02_lower_left` | `star_endpoint_06_upper_right` |
| `star_endpoint_03_bottom_left` | `star_endpoint_02_lower_left` |
| `star_endpoint_04_bottom_right` | `star_endpoint_05_lower_right` |
| `star_endpoint_05_lower_right` | `star_endpoint_01_upper_left` |
| `star_endpoint_06_upper_right` | `star_endpoint_04_bottom_right` |

## Recorded endpoint sequence

- Best regular-step consistency: {7/2} clockwise
- Angular RMS: 0.131987290°
- Maximum angular residual: 0.218134749°
- Second-best candidate RMS: 103.001649993°

### Interpretation boundary

The recorded row sequence is strongly consistent with a clockwise
`{7/2}` step pattern. This is preserved as sequence-consistency
evidence. It is not, by itself, treated as independent proof of
the printed line topology because the digitiser originally used
spatial endpoint descriptions rather than an explicit instruction
to trace the connected star line.
