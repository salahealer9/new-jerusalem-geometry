# New Jerusalem Geometry

A reproducible Euclidean constraint specification and computational analysis of
John Michell's New Jerusalem Diagram.

## Project objective

This project formalises the New Jerusalem Diagram as a geometric constraint
system. Its goals are to:

- reconstruct the diagram from explicit Euclidean definitions;
- distinguish exact constructions from historical approximations;
- generate reproducible coordinates and vector graphics;
- verify incidences, tangencies, symmetries, ratios, and other invariants;
- compare alternative interpretations of the construction;
- provide a rigorous mathematical foundation for later historical, symbolic,
  harmonic, graph-theoretic, and information-theoretic analysis.

## Initial geometric models

The project will initially distinguish three related constructions:

- `NJG_INC`: exact square-circle incidence model;
- `NJG_28`: exact 28-fold angular-division model;
- `NJG_SVG`: reproduction of the 2008 Wikimedia SVG implementation.

These names are provisional until the primary sources have been fully audited.

## Repository status

Early formalisation stage. No scientific conclusions have yet been established.

## Author

Salah-Eddin Gherbi  
Independent Researcher, United Kingdom  
ORCID: 0009-0005-4017-1095

## Development

Create an isolated environment and install the package:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
````

Run the core verification:

```bash
python scripts/verify_core_geometry.py
```

Run the automated tests:

```bash
pytest
```

The initial executable model contains only the Earth circle, Earth square,
radius-7 construction circle, and four cardinal Moon circles. The eight
non-cardinal Moon circles will be introduced only after the competing geometric
definitions have been formally separated.

## Generate the verified core diagram

Generate the standalone SVG:

```bash
python scripts/generate_core_diagram.py
````

The default output is:

```text
figures/generated/cardinal_core.svg
```

The graphic is generated directly from the same coordinate objects used by the
verification and test suite. It introduces no manually positioned elements.

A different scale or output path may be selected without changing the
scale-free geometry:

```bash
python scripts/generate_core_diagram.py \
  --unit 720 \
  --output figures/generated/cardinal_core_u720.svg
```

## Compare the oblique Moon models

Generate the three-panel model comparison:

```bash
python scripts/generate_oblique_comparison.py
````

The default output is:

```text
figures/generated/oblique_models_comparison.svg
```

The figure compares:

* `NJG_INC`: exact square-circle incidence;
* `NJG_28`: exact 28-fold angular division;
* `NJG_SVG`: the 2008 Wikimedia reconstruction.

Each panel contains the same verified Earth-Moon core. Only the placement rule
for the eight oblique Moon circles changes. The residual bars use a common
scale across all three panels.

## Visualise the inferred Michell outer wall

Generate the source-comparison SVG:

```bash
python scripts/generate_michell_outer_wall.py
````

The default output is:

```text
figures/generated/michell_outer_wall.svg
```

The figure combines:

* the verified Earth-Moon cardinal core;
* the source-supported `NJG_INC` placement of twelve Moon circles;
* the eight square-construction-circle incidence points;
* twelve inferred outward radial support tangents;
* the resulting nonregular twelve-sided wall;
* the four-short/eight-long side classification;
* comparison with Michell's approximate wall dimensions.

The Moon-circle placement is supported directly by Michell's description.
The radial-support wall remains explicitly labelled as a project inference.
