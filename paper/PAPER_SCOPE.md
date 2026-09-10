# v1.0 manuscript scope

## Working title

**Reconstructing John Michell's New Jerusalem Geometry: A Reproducible Audit
of Euclidean Structure, Sevenfold Constructibility, and the Plato–Michell
Whorl Interpretation**

## Paper status

This manuscript is a publication layer over the frozen New Jerusalem Geometry
v1.0 scientific record.

It introduces no new geometric fitting, source interpretation, historical
claim, numerical search, or post-v1.0 hypothesis.

## Central contribution

The paper presents a reproducible audit of John Michell's New Jerusalem
geometry in which historical source claims, project reconstruction, exact
mathematics, approximate historical constructions, source-calibrated
comparisons, and downstream visualization remain explicitly separated.

The manuscript has four principal scientific claims.

### Claim A — deterministic geometry

A unit-only generative `NJG_MICHELL` composite reconstructs the principal
New Jerusalem geometry from explicit Euclidean rules.

Source calibration remains downstream and does not supply fitted geometric
parameters back into the frozen generative model.

### Claim B — source-calibrated historical geometry

Direct source-plate calibration resolves important ambiguities without
converting printed figures into exact mathematical objects.

In particular:

```text
Figure 12
preferred project reconstruction:
POLAR_PIVOT_TANGENT

Figure 14
source-supported topology:
{7/2}
```

The Figure 12 preferred wall remains a source-supported project
reconstruction, not a uniquely established construction algorithm stated by
Michell.

The Figure 14 source comparison is not statistically independent validation
of geometry that was previously informed by the same source family.

### Claim C — exact sevenfold constructibility boundary

For:

```text
y = 2*cos(2*pi/7)
```

the exact regular-sevenfold target satisfies the irreducible cubic:

```text
y^3 + y^2 - 2*y - 1 = 0
```

and is excluded from the frozen ordinary straightedge-and-compass quadratic
closure.

Within the frozen project operation-count model:

```text
0 cubic-capable operations: impossible
1 cubic-capable operation:  sufficient
```

The sufficient extension uses one registered `TRISECT_ANGLE` operation.

This exact construction is a project mathematical result and is not attributed
to Michell, Sommerville, Plato, or an ancient source.

### Claim D — Plato/Michell provenance boundary

The v1.0 historical audit separates:

```text
DIRECT_PLATO_TEXT
MICHELL_EXPLICIT
PROJECT_RECONSTRUCTION
```

Plato supplies the eight-whorl structure and ordinal rim-width ranking.

Michell supplies the later musical-number assignment, shaft rule, scale factor,
and dimensional correspondences.

The project reproduces Michell's arithmetic exactly with:

```text
free parameters          0
nearest-match choices    0
optimisations            0
permutation searches     0
scale fits               0
```

This exact reproduction validates the internal numerical chain of Michell's
printed construction. It does not establish that Plato supplied Michell's
numerical widths, intended Michell's assignment, or historically transmitted
the scheme from antiquity.

## Proposed manuscript structure

```text
1. Introduction
   1.1 Michell's New Jerusalem geometry
   1.2 Why a provenance-aware computational audit is needed
   1.3 Contributions and claim boundaries

2. Sources and methods
   2.1 Historical-source hierarchy
   2.2 Frozen source witnesses and provenance classes
   2.3 Normalized Euclidean model
   2.4 Source-plate calibration
   2.5 Deterministic generation and no-refit validation
   2.6 Exact constructibility analysis

3. Core New Jerusalem reconstruction
   3.1 Earth–Moon normalization
   3.2 Oblique Moon models
   3.3 Twelve-Moon structure and 28-point scaffold
   3.4 Figure 12 outer-wall reconstruction
   3.5 Integrated NJG_MICHELL composite

4. Source-calibrated sevenfold geometry
   4.1 Figure 14 topology
   4.2 Michell Method 1: 7 -> 14 -> 28
   4.3 Michell Method 2: 7 -> 21 -> 42
   4.4 Comparative approximation errors

5. Exact sevenfold boundary
   5.1 Algebraic degree-three obstruction
   5.2 Frozen native-incidence census
   5.3 One-trisection project extension
   5.4 Exact heptagon reconstruction
   5.5 Historical interpretation boundary

6. Historical metrology and Sommerville comparisons
   6.1 Retrospective versus predictive evidence
   6.2 Wall dimensional residuals
   6.3 Dodecagon radius classes
   6.4 Evidential dependence of derived quantities

7. Plato's eight whorls and Michell's numerical interpretation
   7.1 Literal Republic extraction
   7.2 Michell's numerical assignment
   7.3 Deterministic reconstruction
   7.4 Historical conclusion and non-transmission boundary

8. Discussion
   8.1 What is mathematically established
   8.2 What is source-supported but reconstructive
   8.3 What remains historically unresolved
   8.4 Reproducibility and limitations

9. Conclusion

Data and code availability
Acknowledgements
References
```

## Main figure set

### Figure 1 — integrated geometry

Canonical source:

```text
figures/generated/njg_michell_composite.svg
```

Paper role:

```text
complete unit-only generative reconstruction
```

### Figure 2 — Figure 14 source-calibrated comparison

Canonical source:

```text
figures/generated/michell_figure14_heptagram.svg
```

Paper role:

```text
source-supported {7/2} topology and calibrated endpoint comparison
```

### Figure 3 — Michell Method 1 scaffold

Canonical source:

```text
figures/generated/michell_28_point_scaffold.svg
```

Paper role:

```text
approximate 7 -> 14 -> 28 construction and Moon-position scaffold
```

### Figure 4 — Michell Method 2 propagation

Canonical source:

```text
figures/generated/v0.8_method2_7_21_42.svg
```

Paper role:

```text
distinct approximate 7 -> 21 -> 42 construction branch
```

### Figure 5 — exact sevenfold synthesis

Canonical source:

```text
figures/generated/v0.9_exact_heptagon_synthesis.svg
```

Paper role:

```text
exact target, Method-1 approximation, Figure-14 source endpoints,
and one-trisection synthesis
```

### Figure 6 — Plato/Michell whorl capstone

Canonical source:

```text
figures/generated/v1.0_plato_michell_whorl_capstone.svg
```

Paper role:

```text
ordinal Plato layer, Michell numerical layer, and deterministic project
reconstruction
```

## Main tables

The paper should use tables rather than extra figures for:

```text
Figure 12 competing wall metrics
frozen forward-validation metrics
historical wall residuals
Sommerville dodecagon dimensional audit
Method 1 / Method 2 / exact sevenfold comparison
Plato/Michell whorl assignment and cumulative radii
claim/provenance hierarchy
```

## Supplementary figure candidates

If a supplement is included:

```text
figures/generated/cardinal_core.svg
figures/generated/oblique_models_comparison.svg
figures/generated/sommerville_dodecagon_dimensional_audit.svg
figures/generated/sommerville_dodecagon_comparison.svg
```

The ignored local `figure12_wall_evidence_comparison.svg` is not used as a
canonical manuscript input unless a separate deterministic paper export is
explicitly registered later.

## Figure publication rule

Canonical SVGs under:

```text
figures/generated/
```

must remain byte-identical.

Paper figures under:

```text
paper/figures/
```

are publication derivatives only.

The permitted publication transformation is:

```text
transparent canvas -> white canvas
```

plus, for the Phase 10G capstone:

```text
existing near-white canvas -> white canvas
```

No coordinates, scientific annotations, colors, line geometry, data attributes,
or scientific content may be changed by the publication conversion.

One presentation-only exception is registered for Figure 5: the internal
development prefix `v0.9` is removed from the SVG title and visible figure
title in the paper derivative. The canonical source artifact remains
byte-identical.

Every paper derivative records the SHA-256 of both its canonical source and its
paper export in `paper/figures/manifest.csv`.

## Preregistered-manifest interpretation

`docs/sources/v1.0_plato_source_manifest.csv` is the Phase 10A preregistration
snapshot.

Its `pending_freeze` entries record the source state at preregistration and are
not rewritten retrospectively.

Current evidential status is instead established by the later source-freeze
artifacts, literal extraction outputs, and the v1.0 claim matrix.

## Bibliography boundary

The repository currently has no `.bib` database.

The manuscript bibliography must be built from frozen/source-verified
bibliographic information.

At minimum it will require verified entries for:

```text
Plato, Republic
John Michell, City of Revelation
John Michell, The Dimensions of Paradise
John Michell with Allan Brown, How the World Is Made
Perseus Digital Library source witnesses
relevant Ian Sommerville item if cited as an archival lead
the 2008 Wikimedia reconstruction if discussed
New Jerusalem Geometry v1.0 software/archive
```

The Sommerville 1974 item must remain labelled as an archival lead unless the
primary item is obtained and frozen.

## Explicit exclusions

The manuscript does not introduce:

```text
Atlantis comparison
new Platonic numerical claims
new fitting
new geometric models
new historical transmission claims
new archaeological claims
new physical or metaphysical claims
new significance tests
post-v1.0 exploratory research
```
