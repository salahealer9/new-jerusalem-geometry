# Michell Source Audit

## Scope

This audit uses only:

1. John Michell, *City of Revelation*.
2. John Michell with Allan Brown, *How the World Is Made*.

The purpose is to distinguish:

- exact geometric definitions;
- stated approximations;
- symbolic interpretations;
- later computational reconstructions.

## Current findings

### 1. Earth–Moon squared-circle core

Michell defines the Earth and Moon through the dimensions:

- Earth radius: 3960 miles;
- Moon radius: 1080 miles;
- combined radius: 5040 miles.

The construction circle passes through the Moon centres, while the Moon circles
touch the Earth circle.

After division by 720, the normalized dimensions are:

- Earth diameter: 11;
- Moon diameter: 3;
- construction-circle radius: 7;
- Earth-square side: 11.

The square perimeter is 44. The construction-circle circumference is also taken
as 44 under the convention pi = 22/7.

### 2. Cardinal Moon circles

The four cardinal Moon circles are centred on the construction circle and are
externally tangent to the Earth circle.

They are also tangent to the corresponding side-lines of the Earth square.

This layer is exact within the normalized Euclidean model.

### 3. Twelve Moon-circle placement

In *City of Revelation*, Michell states that the twelve Moon circles are
arranged in four groups of three.

For each group, the circumference of each of the two outer circles touches the
point where the circle through their centres meets the Earth square.

The twelve Moon circles are therefore not evenly spaced.

This wording supports the exact-incidence placement currently implemented as
`NJG_INC`.

### 4. Outer twelve-sided wall

Michell explicitly states that the enclosing twelve-sided figure is not quite a
regular dodecagon because the Moon circles are not evenly spaced.

The four pairs of sides opposite the corners of the Earth square are drawn
slightly inward so that they touch the corresponding Moon circles.

The Figure 12 source-calibration programme now provides direct plate
measurements of all twelve wall side-lines. Three wall constructions have been
kept mathematically distinct:

- `RADIAL_SUPPORT`: the project's original inference in which each wall normal
  follows the radius through its Moon centre;
- `REGULAR_DIRECTION_TANGENT`: regular-dodecagon normal directions retained
  while each line is translated to Moon tangency;
- `POLAR_PIVOT_TANGENT`: the four polar sides remain fixed while the eight
  oblique sides pivot inward about their polar-side endpoints until tangent to
  the corresponding Moon circles.

Against the affine-calibrated Figure 12 plate, the primary wall-normal RMS
residuals are approximately:

    POLAR_PIVOT_TANGENT        1.019835793 degrees
    REGULAR_DIRECTION_TANGENT  1.458881984 degrees
    RADIAL_SUPPORT              4.755395950 degrees

The same angular ordering occurs independently in all three digitisation
passes.

Support-distance residuals give a different ordering for the complete exact
NJG_INC constructions:

    RADIAL_SUPPORT              0.032822024 u
    REGULAR_DIRECTION_TANGENT  0.036819219 u
    POLAR_PIVOT_TANGENT        0.038999406 u

The plate therefore does not uniquely identify a construction rule from every
metric.

A second source constraint comes from Michell's later Figure 30 discussion of
Ian Sommerville's analysis. Michell reports that the dodecagon is regular at
its four polar sides, that the other eight sides are slightly shorter, and
quotes approximate dimensions of 3280 feet for the four longer sides and
3270 feet for the eight shorter sides. He also gives an area close to
120,000,000 square feet and a perimeter virtually equal to 36,000 old English
feet, with a stated working tolerance of 1:2500.

The exact NJG_INC polar-pivot reconstruction gives:

- four polar sides of 3279.698115 feet;
- eight oblique sides of 3271.120651 feet;
- area 120,002,599.573 square feet;
- old-English-foot perimeter approximately 36,013.778 feet.

Those discrepancies are all approximately 0.04 percent or smaller.

The polar-pivot construction is therefore the project's present preferred
source-supported reconstruction of the Figure 12 wall. It remains a project
reconstruction rather than a claim that Michell explicitly states the complete
analytic construction.

### 5. Sevenfold, fourteenfold, and twenty-eightfold geometry

In *How the World Is Made*, Michell states that a perfect sevenfold division
cannot be constructed by the method shown.

He describes the construction as a close approximation and states that its
accuracy is better than one part in one thousand.

The fourteenfold and twenty-eightfold divisions are derived from this
approximate septenary construction.

The twenty-eightfold structure should therefore not be represented as an exact
regular angular division in a source-faithful Michell model.

### 6. Current model interpretation

The present computational models should be understood as follows:

- `NJG_INC`: source-supported Moon-circle incidence model;
- `NJG_28`: exact regular idealisation of a twenty-eightfold angular division;
- `NJG_SVG`: exact reproduction of the independent 2008 Wikimedia
  reconstruction;
- `RADIAL_SUPPORT`: retained historical project inference for the outer wall;
- `REGULAR_DIRECTION_TANGENT`: intermediate Figure 12 wall reconstruction;
- `POLAR_PIVOT_TANGENT`: present preferred source-supported Figure 12 wall
  reconstruction;
- `NJG_MICHELL`: proposed source-faithful composite model whose individual
  geometric layers are being resolved separately.

The developing `NJG_MICHELL` composite will combine:

- exact normalized Earth–Moon dimensions;
- the pi = 22/7 perimeter convention;
- exact Moon-circle incidence at the square–construction-circle intersections;
- nonuniform Moon-centre spacing;
- the source-calibrated nonregular outer wall;
- approximate septenary, fourteenfold, and twenty-eightfold scaffolding.

The outer-wall layer is therefore now implemented and source-tested even
though the full composite model remains incomplete.

## Open questions

1. Does a primary source specify the exact construction sequence of the outer
   wall, or is the polar-pivot tangent geometry recoverable only as the best
   source-supported reconstruction?
2. Which internal lines in the published New Jerusalem plate are generative,
   and which are illustrative?
3. How are the seven stars located?
4. Which parts of the later twenty-eightfold construction correspond directly
   to the earlier New Jerusalem plate?
5. Does Michell specify a unique construction order for the complete diagram?

### 7. Figure 12 wall-reconstruction audit

The project's first analytic wall construction assigned one outward radial
support tangent to each Moon circle. In that model each wall normal is parallel
to the radius through its Moon centre and consecutive support lines define the
wall vertices.

That construction remains implemented as `RADIAL_SUPPORT` for historical
reproducibility, but Figure 12 source calibration shows that it is not the
preferred reconstruction of the printed wall.

A regular-direction tangent model was therefore tested next. It retains
regular-dodecagon normal directions at thirty-degree intervals and translates
each side to Moon tangency. This substantially improves the plate-direction
fit over radial support.

The source wording and Michell's later Figure 30 discussion motivate a third
construction. Begin with the regular dodecagon of apothem 8.5 normalized units.
Retain the four polar sides. For each of the eight oblique sides, hold fixed
the endpoint shared with its neighbouring polar side and pivot the side inward
until it becomes tangent to the corresponding NJG_INC Moon circle. Intersections
of consecutive lines define the twelve wall vertices.

This `POLAR_PIVOT_TANGENT` construction gives the best Figure 12 wall-direction
fit and reproduces the later Michell/Sommerville four-long/eight-short numerical
structure within approximately the stated 1:2500 working tolerance.

The evidence boundary remains explicit:

- Figure 12 directly supports a nonregular wall and inward adjustment of the
  eight corner-facing sides;
- Figure 30 directly supports four regular polar sides and eight slightly
  shorter sides;
- source-calibrated plate measurements favor the polar-pivot rule for wall
  direction;
- the exact pivot operation itself remains a project reconstruction because
  no currently audited primary-source passage states that construction
  algorithm explicitly.

These differ from Michell's approximate values of 3264 feet and 120 million
square feet by less than one percent.

### 8. Michell's approximate twenty-eight-point scaffold

In Figure 194 of How the World Is Made Michell gives an approximate
construction of sevenfold division. A circle is enclosed in a square and an
equilateral triangle is erected on one side. The relevant triangle-circle
intersections determine an approximate heptagonal step. Repetition on all four
sides produces a twenty-eight-point division.

The present project derives the central step angle analytically as

    alpha = acos((1 - sqrt(3) + sqrt(6 sqrt(3))) / 4)

which gives approximately 51.470701432440 degrees. The exact regular
heptagonal step is approximately 51.428571428571 degrees. Interpreting
Michell's accuracy statement as relative central-angle error gives approximately
0.081919 percent which is better than one part in one thousand.

Within each quadrant the seven unique points have the source-described role
pattern:

    Moon centre
    inter-Moon gap
    Moon centre
    square-circle-intersection positioner
    square-circle-intersection positioner
    Moon centre
    inter-Moon gap

Four repetitions therefore give exactly twelve Moon-centre points eight
inter-Moon-gap points and eight intersection-positioner points.

The scaffold predicts a first oblique Moon-centre angle of approximately
25.587895702680 degrees. This differs from the exact-incidence angle by
approximately 0.324035343176 degrees and gives a maximum Moon-centre
displacement of approximately 0.039588332660 normalized units.

The approximate twenty-eight-point scaffold and the exact-incidence model are
therefore close but mathematically distinct constructions.

### 9. Circumference gap arithmetic

Figure 28 divides the conventional circumference 31680 into:

- twelve Moon diameters totalling 25920;
- four large gaps of 1200 totalling 4800;
- eight small gaps of 120 totalling 960.

After division by 720 this becomes:

    44 = 12 x 3 + 4 x (5/3) + 8 x (1/6)

This arithmetic is exact within Michell's pi = 22/7 convention.

### 10. Figure 14 seven-pointed star

City of Revelation states that a seven-pointed star is placed within the
zodiac circle of the New Jerusalem diagram. Michell identifies among its
extremities the centres of three circles and two junctions of the construction
circle and Earth square.

The printed plate identifies the five source-described extremities as:

- the upper cardinal Moon centre;
- the upper-left square-circle junction;
- the lower-left Moon centre of the bottom group;
- the lower-right Moon centre of the bottom group;
- the upper-right square-circle junction.

The remaining two extremities are not named in the accompanying text. The
present project identifies them provisionally as points on the zodiac circle in
the small gaps between the lower oblique Moon circles and the adjacent cardinal
Moon circles. This is a plate-based project inference, supported by their
positions and by Michell's later 28-point scaffold.

The project's initial reconstruction provisionally classified the printed
line traversal as `{7/3}`. That classification was subsequently tested against
the source plate rather than retained as an interpretive assumption.

Three independent near-endpoint tracing passes sampled both printed strokes at
each of the seven calibrated endpoints. The direct line-direction audit selects
the `{7/2}` heptagram, whose traversal from the upper vertex is:

    0, 2, 4, 6, 1, 3, 5

The `{7/2}` candidate has an angular RMS residual of 1.248033670 degrees and
wins all 21 endpoint/pass comparisons. The `{7/3}` candidate has an angular RMS
residual of 24.993300526 degrees and wins none. The earlier `{7/3}` project
inference is therefore superseded by the calibrated source result.

Three vertex systems are compared:

- an exact regular heptagram;
- the corresponding seven points of Michell's approximate 28-point scaffold;
- a Figure-14-aligned heptagram using the stated and inferred anchors.

Relative to the Figure-14-aligned anchors:

- the exact regular candidate has maximum residual about
  0.043764497580 normalized units and RMS residual about
  0.027485963021 normalized units;
- the Michell scaffold candidate has maximum residual about
  0.039588332660 normalized units and RMS residual about
  0.029576548097 normalized units.

The regular candidate therefore has the lower RMS residual while the Michell
scaffold candidate has the lower maximum residual. Neither approximate
candidate strictly dominates the other.
