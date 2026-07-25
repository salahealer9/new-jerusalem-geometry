# New Jerusalem Geometry Model Variants

## NJG_INC

Exact geometric-incidence model.

The eight non-cardinal Moon circles are constrained to pass exactly through the
intersections of the Earth square and the radius-7 construction circle.

## NJG_28

Exact angular-division model.

Moon-circle centres are selected from an exact division of the construction
circle into 28 equal angular parts.

## NJG_SVG

Exact reproduction of the constants and construction choices encoded in the
2008 Wikimedia SVG.

## Research question

The project will determine which constraints are primary in Michell's published
construction and whether the three models are equivalent, approximately
equivalent, or mathematically distinct.

## Analytic definitions

Let

- `R = 7u` be the construction-circle radius;
- `r = 3u/2` be the Moon radius;
- `h = 11u/2` be the Earth-square half-side.

The first-quadrant square-circle intersection angle is

    theta = arccos(h / R) = arccos(11 / 14).

### NJG_INC

The centre-to-intersection chord must equal the Moon radius:

    2R sin(delta / 2) = r.

Therefore

    delta = 2 arcsin(r / 2R)

and

    beta_INC = theta - 2 arcsin(r / 2R).

### NJG_28

Two steps of an exact 28-fold angular division give

    beta_28 = 2(2pi / 28) = pi / 7.

### NJG_SVG

The Wikimedia implementation uses

    beta_SVG = theta - arcsin(r / R).

The three definitions are close but not identical.
