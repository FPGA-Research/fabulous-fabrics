"""Fabrics registered through entry points.

A package registers a directory of fabrics under the entry-point group
`fabulous.fabrics`; this package registers its own `fabrics/` the same way. Inside
a registered directory, a fabric is any `<name>/` holding a `fabric.yaml`, so adding
such a directory registers it. The registry scans on first access and caches the
result for the life of the process.
"""

from collections.abc import Mapping
from importlib import resources
from pathlib import Path

from fabulous_tiles import Registry, TileLibrary, load_entry_points, tile_libraries

from fabulous_fabrics.model import METADATA_FILE, FabricSource

FABRICS_GROUP = "fabulous.fabrics"

PACKAGE_ROOT = resources.files(__package__)
if not isinstance(PACKAGE_ROOT, Path):
    raise RuntimeError(
        f"fabulous_fabrics is installed as {PACKAGE_ROOT!r}, not a directory. "
        "Install it from a wheel or a source checkout, not a zip archive."
    )
FABRICS_ROOT = PACKAGE_ROOT / "fabrics"


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
