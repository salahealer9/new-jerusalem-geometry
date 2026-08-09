# New Jerusalem Construction Grammar

## Status

This document defines the dependency architecture for the developing
`NJG_MICHELL` composite reconstruction.

It does not assert that computational dependency is equivalent to historical
construction order.

The machine-readable node and edge catalogues are:

- `docs/specification/construction_nodes.csv`
- `docs/specification/construction_dependencies.csv`

## Principle

Every reconstructed object must distinguish:

1. what geometric objects it depends on;
2. what operation relates those objects;
3. what evidential status supports that dependency.

A dependency present in the software does not by itself establish that John
Michell used the same dependency historically.

## Relation types

`parameterizes`
: A dimensional system supplies the numerical parameters of another object.

`intersects`
: Two geometric objects determine intersection points.

`extends`
: A larger construction contains or extends an already constructed subset.

`groups_as`
: An existing set of geometric objects is partitioned according to a
source-described grouping structure.

`constrains`
: One object supplies an incidence or metric condition on another.

`constructs_from`
: A construction is generated from another geometric object or scaffold.

`tangent_constraint`
: Tangency to one geometry constrains another.

`construction_domain`
: An object provides the circle, square, or other domain on which a
construction is performed.

`repeats_fourfold`
: One source-described local construction is repeated through four quadrants.

`locates_on`
: Points are constrained to lie on a specified geometric locus.

`role_correspondence`
: Two source-described structures share role or count assignments.

`selects_moon_centres`
: A subset of Moon centres is selected as downstream construction points.

`selects_junctions`
: A subset of intersection points is selected as downstream construction
points.

`defines_gap_bisectors`
: Gap points are inferred from adjacent Moon-centre geometry.

`combines`
: Two independently classified subsets form a composite vertex set.

`selects`
: A project implementation chooses a subset of an upstream construction.

`connects`
: A topology specifies edges between an existing set of vertices.

`candidate_correspondence`
: A proposed relationship is retained as a hypothesis rather than accepted as
historical fact.

`validated_by`
: A frozen generative object is evaluated by a downstream validation result.
The validation may consume promoted source-derived evidence but must not feed
parameters back into the construction.

## Evidence statuses

Where possible the dependency catalogue reuses the evidence vocabulary of
`docs/sources/geometric_claim_matrix.csv`.

`stated_exact`
: The underlying dependency is directly supported by an exact source
statement.

`stated_approximate`
: The source describes the dependency as approximate.

`conventional_exact`
: Exact only within a stated historical numerical convention.

`project_derivation`
: The dependency follows mathematically from source-defined geometry.

`project_inference`
: The dependency is a reconstruction proposed by this project.

`project_result`
: The dependency or topology has been selected by a project-level empirical
test.

`project_idealisation`
: An exact idealised construction introduced for comparison.

`external_reconstruction`
: The dependency belongs to an external reconstruction rather than Michell's
source.

`implementation_only`
: The dependency currently exists in code but has not been established as a
historical dependency.

`hypothesis_to_test`
: The dependency is a deliberately unresolved relationship to be tested in a
later phase.

## Present dependency architecture

The source-supported core is:

```text
CORE_DIMENSIONS
    ├── EARTH_CIRCLE
    ├── EARTH_SQUARE
    ├── CONSTRUCTION_CIRCLE
    └── CARDINAL_MOONS

EARTH_SQUARE
    ┐
    ├── SQUARE_CIRCLE_INTERSECTIONS
CONSTRUCTION_CIRCLE
    ┘

CARDINAL_MOONS
    ┐
    ├── NJG_INC_MOONS
SQUARE_CIRCLE_INTERSECTIONS
    ┘
````

The current preferred Figure 12 wall reconstruction is:

```text
CORE_DIMENSIONS
    ↓
REGULAR_DODECAGON_BASELINE
    ┐
    ├── POLAR_PIVOT_WALL
NJG_INC_MOONS
    ┘
```

The pivot operation remains a project reconstruction.

Michell's approximate septenary layer is:

```text
CONSTRUCTION_CIRCLE
    ↓
SEPTENARY_METHOD_1
    ↓
RECIPROCAL_TRIANGLE_14
    ↓
SCAFFOLD_28
```

The intermediate fourteenfold layer is source-stated rather than inferred.
The first Method-1 triangle gives an approximate sevenfold division. Its
reciprocal triangle on the opposite side of the square extends the construction
to fourteen distinct marks. Corresponding triangles on the remaining two
square sides complete the twenty-eight-point construction.

The analytic implementation formulates the 7-, 14-, and 28-point stages
independently. The four-triangle union reproduces the existing role-labelled
28-point scaffold to floating-point precision, with a maximum angular mismatch
of approximately `2.220e-16` radians.

The presently calibrated Figure 14 anchor system is:

```text
NJG_INC_MOONS ────────────────┐
                              ├── FIG14_TEXT_ANCHORS ──┐
SQUARE_CIRCLE_INTERSECTIONS ──┘                        │
                                                       ├── FIG14_ALIGNED_VERTICES
NJG_INC_MOONS ── FIG14_GAP_ANCHORS ───────────────────┘
                                                       ↓
                                            FIG14_HEPTAGRAM_7_2
```

The later-scaffold relationship is intentionally unresolved:

```text
SCAFFOLD_28
    ↓
FIG14_SCAFFOLD_VERTICES
    ?
    ↓
FIG14_HEPTAGRAM_7_2
```

The final arrow is currently classified `hypothesis_to_test`.

## Interpretation boundary

This grammar encodes dependency and provenance, not symbolic meaning.

It does not treat:

* historical numerical coincidence;
* sacred-geometric interpretation;
* gematria;
* symbolic correspondence;

as evidence for a geometric dependency.

The purpose of the grammar is to make the developing `NJG_MICHELL` composite
auditable enough that every final object can be traced back to its exact,
approximate, inferred, or tested inputs.

## Forward composite integration

`NJG_MICHELL_COMPOSITE` is the executable forward integration of the audited
construction grammar.

Its caller-supplied geometric input is limited to the scale unit. The core
dimensions, exact-incidence Moon system, four-by-three Moon grouping,
polar-pivot wall reconstruction, approximate septenary construction, reciprocal
fourteenfold extension, and four-triangle twenty-eight-point scaffold are then
generated deterministically.

The forward branch is therefore:

CORE_DIMENSIONS
→ NJG_INC_MOONS
→ MOON_GROUPS_4X3
→ POLAR_PIVOT_WALL

together with:

CONSTRUCTION_CIRCLE
→ SEPTENARY_METHOD_1
→ RECIPROCAL_TRIANGLE_14
→ SCAFFOLD_28

The seven scaffold points used for the Figure 14 heptagram remain a project
candidate. Their correspondence with the earlier printed Figure 14 is not
promoted to a historical dependency.

Figure 12 and Figure 14 plate calibration, digitisation, registration, and
measured source landmarks are excluded from the generative composite. They are
reserved for downstream frozen forward validation with no refitting.

## Frozen forward validation

The completed v0.4 validation is represented downstream of the generative
grammar:

```text
NJG_MICHELL_COMPOSITE
        |
        | validated_by
        v
FROZEN_FORWARD_VALIDATION
````

`FROZEN_FORWARD_VALIDATION` is a project result, not a construction input.

The predictor was frozen before the validation metrics were calculated. The
validation protocol prohibits fitting translation, rotation, phase, scale,
wall geometry, Moon geometry, or heptagram vertices to the source plates.

Figure 12 and Figure 14 had already informed earlier model-development stages,
so this is not represented as a statistically independent hold-out experiment.

The Figure 14 scaffold-to-printed-heptagram correspondence remains a project
candidate. The frozen validation does not promote that relationship to a
historical construction dependency.

## v0.8 Figure 194 dual-method branch

Version `v0.8.0` extends the source construction grammar to preserve both
approximate sevenfold methods described in Figure 194.

The existing Method 1 branch remains:

```text
CONSTRUCTION_CIRCLE
        |
        v
SEPTENARY_METHOD_1
        |
        v
RECIPROCAL_TRIANGLE_14
        |
        v
SCAFFOLD_28
```

The newly formalized Method 2 branch is:

```text
CONSTRUCTION_CIRCLE
        |
        v
SEPTENARY_METHOD_2
        |
        v
METHOD2_21
        |
        v
METHOD2_42
```

`SEPTENARY_METHOD_2` records the source-described equilateral-triangle and
midpoint-arc construction. The local analytic identity

```text
alpha_2 = acos(5/8)
```

is a project derivation from that geometry.

The source explicitly extends Method 2 to 21 divisions using corresponding
arcs from the other two vertices and then to 42 divisions after addition of
the reciprocal triangle.

The deterministic `k = -3,...,+3` completion used by the executable
propagation audit is a project operationalization of the source description
"seven virtually equal parts". It must not be reclassified as a further
formula stated by Michell.

The existing `NJG_MICHELL_COMPOSITE` continues to use Method 1 and its
28-point scaffold. The Method 2 branch is deliberately not inserted into that
composite at v0.8.

The Phase 8F symbolic gap identities are downstream analytical results, not
construction dependencies. They are therefore not represented as source
construction nodes.

No grammar edge combines, averages, ranks, or optimizes the Method 1 and
Method 2 branches.
