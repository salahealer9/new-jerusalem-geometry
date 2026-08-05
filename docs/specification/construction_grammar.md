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
SCAFFOLD_28
```

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
