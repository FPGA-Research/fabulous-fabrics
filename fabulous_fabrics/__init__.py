"""FABulous fabrics, registered from the directory layout.

`fabrics["fabulous"]` is a `FabricSource`. See `fabulous_fabrics.registry` for the
layout rules that register it and the entry-point group another package uses to add
its own.
"""

from fabulous_fabrics.model import SCHEMA_VERSION, FabricMetadata, FabricSource
from fabulous_fabrics.registry import (
    FABRICS_GROUP,
    FABRICS_ROOT,
    fabrics,
    load_fabrics,
)

__all__ = [
    "FABRICS_GROUP",
    "FABRICS_ROOT",
    "SCHEMA_VERSION",
    "FabricMetadata",
    "FabricSource",
    "fabrics",
    "load_fabrics",
]
