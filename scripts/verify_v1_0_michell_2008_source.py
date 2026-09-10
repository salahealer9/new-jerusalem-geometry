from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import io
import json
import zipfile


ROOT = Path(__file__).resolve().parents[1]

FREEZE = (
    ROOT
    / "data"
    / "provenance"
    / "njg_michell_v1_0"
    / "michell_dimensions_paradise_2008_source_freeze.json"
)


def sha256(
    data: bytes,
) -> str:
    return hashlib.sha256(
        data
    ).hexdigest()


def verify(
    source: Path,
) -> None:
    record = json.loads(
        FREEZE.read_text(
            encoding="utf-8"
        )
    )

    bundle_bytes = source.read_bytes()

    expected_bundle = record[
        "source_storage"
    ][
        "bundle_sha256"
    ]

    assert (
        sha256(
            bundle_bytes
        )
        == expected_bundle
    )


    with zipfile.ZipFile(
        io.BytesIO(
            bundle_bytes
        )
    ) as outer:
        manifest_bytes = outer.read(
            "bundle_manifest.json"
        )

        assert (
            sha256(
                manifest_bytes
            )
            == record[
                "source_storage"
            ][
                "bundle_manifest_sha256"
            ]
        )

        manifest = json.loads(
            manifest_bytes
        )

        chapter_name = (
            "chapter4/"
            "the_dimensions_of_paradise_v2008_"
            "chapter_4_plato.zip"
        )

        chapter_bytes = outer.read(
            chapter_name
        )

        assert (
            sha256(
                chapter_bytes
            )
            == record[
                "chapter_archive"
            ][
                "sha256"
            ]
        )

        assert (
            manifest[
                "bibliographic_identity"
            ]
            == record[
                "bibliographic_identity"
            ]
        )

        assert (
            manifest[
                "chapter_scope"
            ]
            == record[
                "chapter_scope"
            ]
        )

        for item in record[
            "frontmatter"
        ]:
            member = (
                "frontmatter/"
                + item[
                    "filename"
                ]
            )

            assert (
                sha256(
                    outer.read(
                        member
                    )
                )
                == item[
                    "sha256"
                ]
            )


    print(
        "MICHELL_2008_SOURCE_WITNESS_VERIFIED"
    )

    print(
        "bundle_sha256",
        expected_bundle,
    )

    print(
        "chapter_screenshots",
        record[
            "chapter_scope"
        ][
            "chapter_screenshot_count"
        ],
    )

    print(
        "frontmatter_screenshots",
        record[
            "chapter_scope"
        ][
            "frontmatter_screenshot_count"
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "source",
        type=Path,
    )

    args = parser.parse_args()

    verify(
        args.source
    )


if __name__ == "__main__":
    main()
