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

This wall has not yet been implemented.

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
- `NJG_MICHELL`: proposed source-faithful composite model, not yet implemented.

The proposed `NJG_MICHELL` model will combine:

- exact normalized Earth–Moon dimensions;
- the pi = 22/7 perimeter convention;
- exact Moon-circle incidence at the square–construction-circle intersections;
- nonuniform Moon-centre spacing;
- a nonregular outer twelve-sided wall;
- approximate septenary, fourteenfold, and twenty-eightfold scaffolding.

## Open questions

1. What exact tangent construction defines every side of the outer wall?
2. Which internal lines in the published New Jerusalem plate are generative,
   and which are illustrative?
3. How are the seven stars located?
4. Which parts of the later twenty-eightfold construction correspond directly
   to the earlier New Jerusalem plate?
5. Does Michell specify a unique construction order for the complete diagram?

### 7. Candidate analytic construction of the outer wall

Figure 12 appears to assign one outward wall side to each Moon circle. The
cardinal Moon circles correspond to horizontal and vertical wall sides, while
the non-cardinal Moon circles correspond to oblique sides.

The present project therefore tests the following inferred construction:

1. draw the outward support tangent to each Moon circle perpendicular to the
   radius joining its centre to the common origin;
2. intersect consecutive support tangents;
3. use the twelve intersections as the wall vertices.

This construction is not explicitly stated by Michell and must remain labelled
as a project inference.

For the exact-incidence Moon placement, the inferred wall predicts:

- four shorter and eight longer wall sides;
- mean side length approximately 3289.16 feet;
- total area approximately 120.778 million square feet.

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

The line traversal shown in Figure 14 is consistent with the deep heptagram
{7/3}, whose traversal from the upper vertex is:

    0, 3, 6, 2, 5, 1, 4

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
