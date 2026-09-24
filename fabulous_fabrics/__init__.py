"""FABulous fabrics, registered from the directory layout.

`fabrics["fabulous"]` is a `FabricSource`. See `fabulous_fabrics.sources` for the
layout rules that register it.
"""

from fabulous_fabrics.sources import (
    FABRICS_ROOT,
    FabricMetadata,
    FabricSource,
    fabrics,
    load_fabrics,
)

__all__ = ["FABRICS_ROOT", "FabricMetadata", "FabricSource", "fabrics", "load_fabrics"]
