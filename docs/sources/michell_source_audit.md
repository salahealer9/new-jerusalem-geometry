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
