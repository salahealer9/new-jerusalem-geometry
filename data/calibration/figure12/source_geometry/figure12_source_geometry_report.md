# Figure 12 source-derived normalized geometry

## Evidence boundary

This analysis applies the selected centroid affine plate calibration to the raw Figure 12 source observations.

Moon and wall geometry reported here is measured from the printed plate. No NJG Moon-placement candidate and no candidate wall construction is fitted or selected.

## Registration

- Selected model: centroid affine
- Training RMS: 1.342228 px
- Leave-one-out RMS: 1.790924 px
- Leave-one-out maximum: 2.541469 px
- Anisotropy ratio: 1.013122338
- Directional scale range: 71.392702 to 72.329541 px/u
- Mean directional scale: 71.861122 px/u

## Source-derived Moon geometry

| Moon | Centre x (u) | Centre y (u) | Origin radius (u) | Angle (deg) | Radius (u) | Circle RMS (u) | Pass centre RMS (u) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `moon_north_west` | -3.030858749 | 6.311129234 | 7.001175398 | 115.652196 | 1.510699833 | 0.006871727 | 0.009190861 |
| `moon_north` | 0.013650007 | 7.008869480 | 7.008882772 | 89.888415 | 1.531421995 | 0.008466347 | 0.010236811 |
| `moon_north_east` | 3.052062429 | 6.314972483 | 7.013840784 | 64.205255 | 1.520349158 | 0.007320720 | 0.010512533 |
| `moon_east_north` | 6.323644842 | 3.047419769 | 7.019633276 | 25.729824 | 1.513431494 | 0.009872828 | 0.007935591 |
| `moon_east` | 7.028652878 | -0.011498885 | 7.028662284 | 359.906264 | 1.542953366 | 0.011642644 | 0.010773083 |
| `moon_east_south` | 6.304307756 | -3.082560182 | 7.017583171 | 333.943173 | 1.509734531 | 0.012694071 | 0.018104117 |
| `moon_south_east` | 3.075152174 | -6.316414626 | 7.025215628 | 295.959177 | 1.514862854 | 0.006619575 | 0.012451070 |
| `moon_south` | -0.002572633 | -7.024682339 | 7.024682810 | 269.979017 | 1.538168461 | 0.005333334 | 0.012495974 |
| `moon_south_west` | -3.047394181 | -6.340759638 | 7.035044000 | 244.330876 | 1.514506295 | 0.008050905 | 0.007739953 |
| `moon_west_south` | -6.306437514 | -3.050703142 | 7.005565201 | 205.815111 | 1.512437061 | 0.008517556 | 0.010017039 |
| `moon_west` | -7.005011864 | 0.004211419 | 7.005013130 | 179.965554 | 1.528467340 | 0.010611447 | 0.006334341 |
| `moon_west_north` | -6.281968668 | 3.094651463 | 7.002856419 | 153.774015 | 1.505784012 | 0.008973420 | 0.006944190 |

Worst pass-specific Moon-centre repeatability: `moon_east_south`, 0.018104117 u.

## Source-derived wall lines

Each wall line is written in normalized support form `n_x x + n_y y = h`, with the unit normal oriented away from the diagram origin.

| Wall | normal x | normal y | h (u) | normal angle (deg) | fit RMS (u) | pass angle RMS (deg) | pass support RMS (u) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `wall_north_west` | -0.539268635 | 0.842133802 | 8.472543874 | 122.633865 | 0.006139458 | 0.127815 | 0.005766994 |
| `wall_north` | 0.005139167 | 0.999986794 | 8.496731931 | 89.705546 | 0.005630292 | 0.048951 | 0.003504780 |
| `wall_north_east` | 0.522735642 | 0.852494838 | 8.508045853 | 58.484068 | 0.009448968 | 0.205523 | 0.009169510 |
| `wall_east_north` | 0.854655927 | 0.519194805 | 8.493286891 | 31.278256 | 0.008191923 | 0.195657 | 0.006132191 |
| `wall_east` | 0.999993281 | -0.003665705 | 8.558789749 | 359.789970 | 0.011412603 | 0.110571 | 0.007422598 |
| `wall_east_south` | 0.852544173 | -0.522655176 | 8.533674456 | 328.489475 | 0.007554523 | 0.203990 | 0.012819690 |
| `wall_south_east` | 0.522588224 | -0.852585215 | 8.541941891 | 301.506025 | 0.006742040 | 0.060553 | 0.013854372 |
| `wall_south` | -0.001961317 | -0.999998077 | 8.572467862 | 269.887625 | 0.008274981 | 0.113947 | 0.006546020 |
| `wall_south_west` | -0.530171467 | -0.847890450 | 8.502020244 | 237.982959 | 0.010808974 | 0.158683 | 0.003179398 |
| `wall_west_south` | -0.856280757 | -0.516510664 | 8.481762031 | 211.098483 | 0.013687930 | 0.114530 | 0.007255525 |
| `wall_west` | -0.999990316 | -0.004400788 | 8.500374513 | 180.252147 | 0.019769251 | 0.318315 | 0.011907452 |
| `wall_west_north` | -0.846622550 | 0.532193816 | 8.489260341 | 147.846198 | 0.009700836 | 0.199089 | 0.004082709 |

Worst wall angular repeatability: `wall_west`, 0.745336 degrees.
Worst wall support-position repeatability: `wall_east_south`, 0.029824869 u.

## Derived wall polygon

- Vertices: 12
- Perimeter: 54.773997038 u
- Area: 233.140234440 u^2

| Wall side | Source-derived length (u) |
|---|---:|
| `wall_north_west` | 4.482453203 |
| `wall_north` | 4.862443401 |
| `wall_north_east` | 4.381868927 |
| `wall_east_north` | 4.607304223 |
| `wall_east` | 4.636884753 |
| `wall_east_south` | 4.504728082 |
| `wall_south_east` | 4.508047441 |
| `wall_south` | 4.686127626 |
| `wall_south_west` | 4.550848964 |
| `wall_west_south` | 4.448306371 |
| `wall_west` | 4.758118383 |
| `wall_west_north` | 4.346865665 |

## Interpretation boundary

These quantities are source-plate measurements. The next analysis stage may compare them with candidate Moon-placement systems and candidate outer-wall constructions.
