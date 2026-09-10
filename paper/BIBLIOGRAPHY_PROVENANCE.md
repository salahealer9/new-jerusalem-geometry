# Manuscript bibliography provenance

## Status

This note records the bibliographic decisions used by `paper/references.bib`.

It is a publication-layer record only. It does not alter the frozen source
manifests, source audits, scientific results, or historical claim hierarchy.

## Plato — Republic

### English

Underlying print edition:

```text
Plato, Republic
translated by Paul Shorey
Plato in Twelve Volumes, Vols. 5–6
Harvard University Press / William Heinemann Ltd.
1935
```

Perseus catalogue identifier for the underlying Shorey translation:

```text
urn:cts:greekLit:tlg0059.tlg030.perseus-eng1
```

Exact project-frozen XML witness:

```text
data/sources/v1_0/plato/tlg0059.tlg030.perseus-eng2.xml
```

Frozen project SHA-256:

```text
36826064d30be3b40d20b820f4904ed170d375e41dd3f450cbe4eb733054766d
```

### Greek

Underlying print edition:

```text
Platonis Opera, Tomus IV, Tetralogia VIII
edited by John Burnet
Clarendon Press, Oxford
1902
```

Perseus catalogue identifier for the underlying Burnet edition:

```text
urn:cts:greekLit:tlg0059.tlg030.perseus-grc1
```

Exact project-frozen XML witness:

```text
data/sources/v1_0/plato/tlg0059.tlg030.perseus-grc2.xml
```

Frozen project SHA-256:

```text
da2bfcf943497bb147fc49ae4b47bf0919e1db790bcf7de830dc259e76379d4f
```

Both XML files were frozen from Perseus upstream commit:

```text
790c84289edbdbe289dd7b752bfea29f0af4299d
```

The normalized section hashes in the literal-extraction report are passage
hashes. They are not the upstream commit identifier and not the complete XML
file hashes.

## John Michell — City of Revelation

The actual local project witness identifies itself on its copyright page as:

```text
CITY OF REVELATION
John Michell
On the proportion and symbolic numbers of the cosmic temple

ABACUS edition published 1973
by Sphere Books Ltd
30/32 Gray's Inn Road, London WC1X 8JL

First published in Great Britain by Garnstone Press Ltd 1972
Copyright © John Michell 1972

ISBN 0 349 12320 9
```

The manuscript therefore cites the edition actually used by the source-plate
work:

```text
Michell, John.
City of Revelation: On the Proportion and Symbolic Numbers of the Cosmic Temple.
Abacus / Sphere Books Ltd, London, 1973.
ISBN 0-349-12320-9.
```

Private local project source:

```text
data/source_private/city_of_revelation.pdf
```

Frozen source-PDF SHA-256 recorded by the Figure 14 calibration:

```text
ce161c0703c3080948fb437bebab7b283ff28621492440357f9b13c80ab3fdbd
```

The private PDF is not redistributed through Git.

## John Michell — The Dimensions of Paradise

The v1.0 historical audit uses the purchased 2008 digital edition.

Bibliographic decision:

```text
John Michell
The Dimensions of Paradise:
Sacred Geometry, Ancient Science, and the Heavenly Order on Earth
Inner Traditions
2008
3rd Edition, New Edition
eBook ISBN 9781594777738
```

The purchased source screenshots remain outside Git.

Frozen provenance:

```text
bundle_manifest_sha256
ed60002c9afd98db27e615198c1429dea6f70d6b2cc7d02377d032f779d9746c

bundle_sha256
f662aa6221a4ceb232025569fc501ca6613ebbdc6b44394d6631eec7e5a7137d
```

The individual screenshot hashes remain in the frozen source-extraction record.

## John Michell with Allan Brown — How the World Is Made

Bibliographic decision for the project source edition:

```text
John Michell with Allan Brown
How the World Is Made:
The Story of Creation According to Sacred Geometry
Thames & Hudson
London
2009
ISBN 9780500515105
```

The v0.8 source audit records Figure 194 as the source for the two approximate
sevenfold methods.

Important provenance distinction:

```text
48a7892bb7be5ebd1b0cfdc2e66f0de7a4f380b6926d7a1799c6693e7dd441b4
```

is the frozen Phase-8A **source-audit hash**, not a hash of the copyrighted book
file itself. The bibliography does not mislabel it as a book-file hash.

## Wikimedia external reconstruction

The external SVG comparator is:

```text
New Jerusalem (Michell) Sacred Geometry.svg
creator: User:AnonMoos
Wikimedia Commons
file-history timestamp: 27 August 2008
licence: creator dedication to the public domain
```

The project treats this only as the external reconstruction variant:

```text
NJG_SVG
```

It is not a primary Michell source.

## Ian Sommerville 1974

Status:

```text
ARCHIVAL_PENDING
```

No primary bibliographic title, journal, volume, pages, or other details are
invented.

When the manuscript discusses numerical quantities attributed to Sommerville,
it cites Michell's later report in *How the World Is Made* and states that the
underlying 1974 primary item has not been independently frozen.

## New Jerusalem Geometry software

Current package state at the v1.0.0 software-release boundary:

```text
1.0.0
```

The scientific content remains frozen.  The final software/archive reference
is deliberately omitted from `references.bib` until the public GitHub/Zenodo
archival release and DOI exist.

## Post-freeze Sommerville archival search

A targeted reproduction request to Thompson Library Special Collections,
The Ohio State University, covered the William S. Burroughs Papers
(`SPEC.RARE.0087`), box 30, folders 253--254.

The supplied research-use-only files were:

- `SPEC-RARE-CMS-0087-b30-f253.pdf` — 12 PDF pages —
  SHA-256 `56450ebbae8706125898df2816f57969c4d31d8f4727449b834655946dacdf61`
- `SPEC-RARE-CMS-0087-b30-f254.pdf` — 38 PDF pages —
  SHA-256 `2df9a4d351ce3cc1c5ecce087b92e28f0da1f60cf00fd65c78f72164401497a0`

The supplied folders contain no direct witness to the reported 1974
Sommerville geometric work and no project-relevant dodecagon derivation.
The primary item therefore remains `ARCHIVAL_PENDING`.

The archive originally quoted 58 scans/pages, whereas the two supplied PDFs
contain 50 PDF pages.  Clarification was requested on 2026-09-02 and remained
unconfirmed at this checkpoint.  This is recorded as a scan-count/PDF-page
discrepancy, not as proof that eight pages are missing.

The scans themselves are not redistributed.
