# Figure 12 digitisation QC

## Scope

This report evaluates repeatability of the three raw source-digitisation passes before registration or comparison with any candidate Moon-placement or outer-wall model.

## Raw evidence

- Source image SHA-256: `4f9ab63b94ac4c1a2ce2fe5217c2cb0542a6df77e30eb1f272f5c6f2c3d650d6`
- pass-01: `54c325b1729be92dd278004faee1d73b6524c8e022799368a974d8e456db07d2`
- pass-02: `218892c33d991cd9c010bbefca6c17ee632a55fa5eee645d2eb81f2c945edae8`
- pass-03: `d28f48f47a962742fe9bb1ad62b2322816bb5895a07270e04b6661cd42a04551`

## Registration repeatability

- Maximum landmark RMS: 1.630485 px
- Maximum landmark pairwise separation: 3.641145 px
- Worst RMS landmark: `square_corner_bottom_right` (1.630485 px)

## Moon-circle repeatability

- Maximum fitted-centre RMS: 0.661769 px
- Maximum fitted-centre pairwise separation: 1.533439 px
- Maximum within-pass circle radial RMS: 1.280223 px
- Worst centre-repeatability Moon: `moon_north_east` (0.661769 px)
- Worst circle-fit Moon: `moon_west` (1.280223 px)

## Wall-line repeatability

- Maximum pairwise line-angle difference: 0.701724 degrees
- Maximum pairwise line-position difference: 2.482369 px
- Maximum within-pass line-fit RMS: 1.139257 px
- Worst angular-repeatability side: `wall_west` (0.701724 degrees)
- Worst positional-repeatability side: `wall_west` (2.482369 px)

## Interpretation boundary

These statistics describe source-digitisation repeatability only. They do not select an NJG Moon model and do not validate the radial-support wall hypothesis.
