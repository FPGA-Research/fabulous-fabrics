"""Fabrics discovered from the directory layout.

A package registers a directory of fabrics under the entry-point group
`fabulous.fabrics`; this package registers its own `fabrics/` the same way. Inside
a registered directory, a fabric is any `<name>/` holding a `fabric.yaml`, which
names the tile library the fabric is built from. The fabric's project skeleton sits
beside it in `common/` and one directory per HDL (`verilog/`, `vhdl/`). Adding such
a directory registers it; the registry scans on first access and caches the result
for the life of the process.

`fabric.yaml` carries a `schema_version`, checked before anything else, so a fabric
written for a newer schema fails with a request to upgrade rather than with an
unknown-field error.
"""

import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from importlib import resources
from pathlib import Path, PurePosixPath

import yaml
from fabulous_tiles import (
    Language,
    Registry,
    TileLibrary,
    load_entry_points,
    tile_libraries,
)
from pydantic import BaseModel, ConfigDict


def _package_root() -> Path:
    root = resources.files(__package__)
    if not isinstance(root, Path):
        raise RuntimeError(
            f"fabulous_fabrics is installed as {root!r}, not a directory. Install it "
            "from a wheel or a source checkout, not a zip archive."
        )
    return root


PACKAGE_ROOT = _package_root()
FABRICS_ROOT = PACKAGE_ROOT / "fabrics"
FABRICS_GROUP = "fabulous.fabrics"
METADATA_FILE = "fabric.yaml"
SCHEMA_VERSION = 1
# Every fabric CSV addresses its tiles as `./Tile/<name>/`.
TILE_DIR = "Tile"


class FabricMetadata(BaseModel):
    """The contents of a fabric's `fabric.yaml`."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: int
    description: str
    tile_library: str


@dataclass(frozen=True, slots=True)
class FabricSource:
    """A fabric: its metadata, tile library and project skeleton per HDL."""

    name: str
    root: Path
    description: str
    tile_library: TileLibrary
    languages: frozenset[Language]

    @classmethod
    def from_dir(
        cls, root: Path, libraries: Mapping[str, TileLibrary]
    ) -> "FabricSource":
        """Read the fabric in `root`, named after the directory.

        Raises
        ------
        FileNotFoundError
            If `root` has no `fabric.yaml` or no `common/` directory.
        ValueError
            If `fabric.yaml` lacks `schema_version`, has one this package cannot
            read, or names a tile library missing from `libraries`.
        pydantic.ValidationError
            If `fabric.yaml` does not match `FabricMetadata`.
        """
        root = root.resolve()
        metadata_path = root / METADATA_FILE
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Fabric {root.name} has no {metadata_path}.")
        raw = yaml.safe_load(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or "schema_version" not in raw:
            raise ValueError(
                f"{metadata_path} has no schema_version. Add "
                f"`schema_version: {SCHEMA_VERSION}`."
            )
        if raw["schema_version"] != SCHEMA_VERSION:
            raise ValueError(
                f"{metadata_path} has schema_version {raw['schema_version']!r}, but "
                f"this fabulous-fabrics reads schema_version {SCHEMA_VERSION}. "
                "Upgrade fabulous-fabrics."
            )
        metadata = FabricMetadata.model_validate(raw)
        if not (root / "common").is_dir():
            raise FileNotFoundError(f"Fabric {root.name} has no {root / 'common'}.")
        if metadata.tile_library not in libraries:
            raise ValueError(
                f"Fabric {root.name} names tile library {metadata.tile_library}, which "
                f"does not exist. Available: {sorted(libraries)}."
            )
        return cls(
            name=root.name,
            root=root,
            description=metadata.description,
            tile_library=libraries[metadata.tile_library],
            languages=frozenset(
                language for language in Language if (root / language).is_dir()
            ),
        )

    def files(self, language: Language) -> dict[PurePosixPath, Path]:
        """Map each project-relative path of the skeleton to its source file.

        `common/` is read first and the `language` directory second, so a language
        file replaces a common file at the same path.

        Raises
        ------
        ValueError
            If the fabric has no skeleton for `language`.
        """
        if language not in self.languages:
            raise ValueError(
                f"Fabric {self.name} ships {sorted(self.languages)}, not {language}."
            )
        found: dict[PurePosixPath, Path] = {}
        for layer in (self.root / "common", self.root / language):
            for src in sorted(layer.rglob("*")):
                if src.is_file():
                    found[PurePosixPath(src.relative_to(layer).as_posix())] = src
        return found

    def materialise(self, dest: Path, language: Language) -> None:
        """Copy the fabric for `language` into `dest` as a self-contained project.

        The skeleton from `files(language)` lands in `dest` and the tile library in
        `dest/Tile`. The copies are writable even when the installed package is not.

        Raises
        ------
        ValueError
            If the fabric or a tile of its library has nothing for `language`.
        FileExistsError
            If two tile library files with different bytes would land at the same
            path.
        """
        for rel, src in self.files(language).items():
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
        self.tile_library.materialise(dest / TILE_DIR, language)


def load_fabrics(
    root: Path, libraries: Mapping[str, TileLibrary]
) -> dict[str, FabricSource]:
    """Read every fabric directory under `root` that holds a `fabric.yaml`."""
    return {
        d.name: FabricSource.from_dir(d, libraries)
        for d in sorted(root.iterdir())
        if (d / METADATA_FILE).is_file()
    }


fabrics: Registry[FabricSource] = Registry(
    "fabric",
    lambda: load_entry_points(
        FABRICS_GROUP, "fabric", lambda root: load_fabrics(root, tile_libraries)
    ),
)
