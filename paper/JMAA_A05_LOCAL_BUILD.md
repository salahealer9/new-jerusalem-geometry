# JMAA A05 — publication-only local build

The A05 manuscript includes two **estate-licensed** original illustrations by John Michell. Written rights clearance is specific to their use in the *Journal of Mathematics and the Arts*, including its print and electronic editions. This is **not** permission to redistribute the illustrations independently on GitHub. Therefore the two figure PDFs and the illustrated `manuscript.pdf` are **never committed** to this public repository.

The source file `paper/manuscript.tex` deliberately refers to the local paths:

- `paper/figures/licensed_historical/Michell1973_Figure12_ORIGINAL_CROP.pdf`
- `paper/figures/licensed_historical/Michell1973_Figure14_ORIGINAL_CROP.pdf`

The same `paper/.gitignore` excludes this directory and the rendered manuscript. Obtain the two local PDFs **from the author's already-preserved private A05 source package**, check SHA-256, and then build:

```bash
bash paper/build_a05_local.sh
```

The build fails closed if either licensed file is absent or differs from the authorised source. It also fails on missing LaTeX dependencies, unexpected page count, unresolved references, overfull boxes, or wrong figure/table label counts.

Expected result: 20-page A4 paper, ten numbered figures and five tables. This checks structure but **not visual parity across TeX engines and fonts**. Compare every page of the resulting `paper/manuscript.pdf` with the author's separately preserved approved A05 PDF before committing. The release is a new *publication-source* milestone, not a revision of the frozen scientific v1.0.0 release.

**Never run `git add -A` or `git add .`**. Stage and review exact allowlisted publication files only. Store the estate's correspondence outside this public repository; do not paste private addresses or email threads into commits.
