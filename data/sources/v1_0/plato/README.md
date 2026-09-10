# Frozen Plato source witnesses

This directory contains the exact Plato *Republic* witnesses frozen for the
v1.0 historical-source audit.

## Files

```text
tlg0059.tlg030.perseus-eng2.xml
tlg0059.tlg030.perseus-grc2.xml
source_freeze.json
```

The English and Greek XML files were frozen from the Perseus Digital Library
`PerseusDL/canonical-greekLit` repository at:

```text
790c84289edbdbe289dd7b752bfea29f0af4299d
```

Their project-recorded SHA-256 values are:

```text
36826064d30be3b40d20b820f4904ed170d375e41dd3f450cbe4eb733054766d
  tlg0059.tlg030.perseus-eng2.xml

da2bfcf943497bb147fc49ae4b47bf0919e1db790bcf7de830dc259e76379d4f
  tlg0059.tlg030.perseus-grc2.xml
```

## Licensing

These two XML witnesses are third-party Perseus material.

The upstream `canonical-greekLit` repository at the frozen commit is licensed
under the **Creative Commons Attribution-ShareAlike 4.0 International License
(CC BY-SA 4.0)** unless otherwise indicated.

```text
https://creativecommons.org/licenses/by-sa/4.0/
https://github.com/PerseusDL/canonical-greekLit
```

The repository's top-level MIT license applies to the New Jerusalem Geometry
software and original project material; it does not relicense these third-party
Perseus source witnesses.

See:

```text
THIRD_PARTY_NOTICES.md
```

## Research role

The XML witnesses are source inputs only.

They were frozen before literal extraction and do not themselves encode the
project's numerical reconstruction or historical conclusion.

The exact source-freeze provenance is recorded in:

```text
source_freeze.json
```
