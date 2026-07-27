# Figure 14 selected affine calibration

## Selection

The affine registration is selected as the primary Figure 14
plate calibration.

- Training RMS: 1.919266 px
- Leave-one-out RMS: 2.545170 px
- Leave-one-out maximum: 4.245118 px
- Anisotropy ratio: 1.023099307

The projective model slightly reduced training residual but had
worse leave-one-landmark-out prediction. The similarity model
left materially larger systematic residuals.

## Scale and uncertainty

- Maximum directional scale: 72.294093 px/u
- Minimum directional scale: 70.661854 px/u
- Mean directional scale: 71.477974 px/u
- Overall repeated-click RMS: 0.895722 px
- Overall repeated-click RMS after the fixed affine inverse: 0.012484891 u
- Overall pass-specific registered variation: 0.012375768 u

## Landmark categories

| Category | N | Mean click RMS (px) | Mean click RMS (u) | Mean pass-registered RMS (u) |
|---|---:|---:|---:|---:|
| moon_centre | 12 | 1.100026 | 0.015324303 | 0.015952405 |
| square_circle_junction | 8 | 0.463779 | 0.006510191 | 0.005810956 |
| square_corner | 4 | 0.674908 | 0.009435838 | 0.007218688 |
| star_endpoint | 7 | 0.439571 | 0.006147782 | 0.006721317 |

## Largest residuals from predefined schema coordinates

| Rank | Landmark | Role | Residual (u) |
|---:|---|---|---:|
| 1 | `moon_centre_02` | validation | 0.058075363 |
| 2 | `moon_centre_10` | validation | 0.056209827 |
| 3 | `moon_centre_09` | validation | 0.056031542 |
| 4 | `moon_centre_05` | validation | 0.051478479 |
| 5 | `junction_right_upper` | registration | 0.044791761 |
| 6 | `moon_centre_08` | validation | 0.038509860 |
| 7 | `junction_left_upper` | registration | 0.038064296 |
| 8 | `square_corner_top_right` | registration | 0.036389765 |
| 9 | `moon_centre_06` | validation | 0.035851477 |
| 10 | `moon_centre_01` | validation | 0.033736634 |

## Interpretation boundary

The normalized star endpoints are source observations. They have
not yet been fitted to a regular heptagram, Michell scaffold,
or any Figure-14-specific candidate construction.

Moon-centre residuals are validation evidence and do not influence
the selected affine registration.
