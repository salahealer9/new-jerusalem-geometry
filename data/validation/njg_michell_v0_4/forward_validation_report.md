# NJG_MICHELL frozen forward validation

## Status

- Validation mode: `frozen_forward_no_refitting`
- Frozen predictor commit: `43096326d5c1862fc7e33f9d90eb1df861c3b642`
- Caller-supplied geometric scale: `unit = 1.0`
- Post-freeze geometric refitting: none
- Post-hoc pass/fail threshold: none

## Figure 12

### Primary wall-line residuals

- Angular RMS: 1.019835793°
- Angular maximum: 2.062522195°
- Support RMS: 0.038999406 u
- Support maximum: 0.072467862 u

### Polygon diagnostics

- Vertex RMS: 0.100021612 u
- Vertex maximum: 0.162698870 u
- Side-length RMS: 0.142495117 u
- Side-length maximum: 0.307307130 u
- Predicted perimeter: 54.566330097 u
- Source perimeter: 54.773997038 u
- Perimeter residual: -0.207666941 u (-0.379134%)
- Predicted area: 231.486496089 u²
- Source area: 233.140234440 u²
- Area residual: -1.653738350 u² (-0.709332%)

## Figure 14

| Metric | Scaffold candidate | Canonical regular |
|---|---:|---:|
| Point RMS (u) | 0.031023606 | 0.031953847 |
| Point maximum (u) | 0.049325681 | 0.059258803 |
| Angular RMS (deg) | 0.215205853 | 0.224058789 |
| Angular maximum (deg) | 0.385791171 | 0.470051178 |
| Radial RMS (u) | 0.016436996 | 0.016436996 |
| RMS / registration LOO | 0.871259992 | 0.897384694 |

### Evidence-separated endpoint residuals

- Source-supported endpoints, scaffold RMS: 0.023288890 u
- Source-supported endpoints, canonical RMS: 0.023451831 u
- Plate-inferred endpoints, scaffold RMS: 0.044863052 u
- Plate-inferred endpoints, canonical RMS: 0.046890280 u

### Fixed-comparator difference

- Scaffold minus canonical point RMS: -0.000930242 u
- Scaffold minus canonical point maximum: -0.009933122 u

## Interpretation boundary

These are descriptive frozen-predictor residuals. No parameter was fitted during validation.
Figure 12 and Figure 14 were involved in earlier model-development stages, so this analysis is not represented as a statistically independent hold-out experiment.
The Figure 14 `{7/2}` topology was established earlier by an independent printed-line tracing audit and is not counted here as a new positional prediction.
