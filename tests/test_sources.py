import shutil
from collections.abc import Callable
from pathlib import Path, PurePosixPath

import pytest
from fabulous_tiles import Language, TileLibrary
from pydantic import ValidationError

from fabulous_fabrics import FabricSource, fabrics, load_fabrics

METADATA = "description: A test fabric.\ntile_library: lib\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


@pytest.fixture
def libraries(tmp_path: Path) -> dict[str, TileLibrary]:
    return {"lib": TileLibrary(name="lib", root=tmp_path / "lib", tiles={})}


@pytest.fixture
def fabric_root(tmp_path: Path) -> Path:
    """A fabric `demo` with a common file, a Verilog override and a VHDL-only file."""
    root = tmp_path / "fabrics"
    _write(root / "demo/fabric.yaml", METADATA)
    _write(root / "demo/common/fabric.csv", "common\n")
    _write(root / "demo/common/Fabric/shared.txt", "common\n")
    _write(root / "demo/verilog/Fabric/shared.txt", "verilog\n")
    _write(root / "demo/vhdl/Fabric/only.vhdl", "vhdl\n")
    _write(root / "flat/flat.csv", "not registered\n")
    return root


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (
            Language.VERILOG,
            {"fabric.csv": "common", "Fabric/shared.txt": "verilog"},
        ),
        (
            Language.VHDL,
            {
                "fabric.csv": "common",
                "Fabric/shared.txt": "common",
                "Fabric/only.vhdl": "vhdl",
            },
        ),
    ],
)
def test_files_layer_language_over_common(
    fabric_root: Path,
    libraries: dict[str, TileLibrary],
    language: Language,
    expected: dict[str, str],
) -> None:
    files = load_fabrics(fabric_root, libraries)["demo"].files(language)
    assert {
        str(rel): src.parent.relative_to(fabric_root / "demo").parts[0]
        for rel, src in files.items()
    } == expected
    assert all(isinstance(rel, PurePosixPath) for rel in files)


def test_only_directories_with_metadata_register(
    fabric_root: Path, libraries: dict[str, TileLibrary]
) -> None:
    found = load_fabrics(fabric_root, libraries)
    assert list(found) == ["demo"]
    assert found["demo"].description == "A test fabric."
    assert found["demo"].tile_library is libraries["lib"]
    assert found["demo"].languages == {Language.VERILOG, Language.VHDL}


@pytest.mark.parametrize(
    ("edit", "error", "match"),
    [
        (
            lambda r: _write(r / "fabric.yaml", "description: x\ntile_library: gone\n"),
            ValueError,
            "gone",
        ),
        (
            lambda r: _write(r / "fabric.yaml", METADATA + "extra: 1\n"),
            ValidationError,
            "extra",
        ),
        (
            lambda r: _write(r / "fabric.yaml", "description: x\n"),
            ValidationError,
            "tile_library",
        ),
        (lambda r: shutil.rmtree(r / "common"), FileNotFoundError, "common"),
    ],
)
def test_fabric_errors(
    fabric_root: Path,
    libraries: dict[str, TileLibrary],
    edit: Callable[[Path], object],
    error: type[Exception],
    match: str,
) -> None:
    edit(fabric_root / "demo")
    with pytest.raises(error, match=match):
        FabricSource.from_dir(fabric_root / "demo", libraries)


def test_files_rejects_missing_language(
    fabric_root: Path, libraries: dict[str, TileLibrary]
) -> None:
    shutil.rmtree(fabric_root / "demo/vhdl")
    with pytest.raises(ValueError, match="not vhdl"):
        load_fabrics(fabric_root, libraries)["demo"].files(Language.VHDL)


@pytest.mark.parametrize("language", list(Language))
def test_packaged_fabulous_fabric(language: Language) -> None:
    fabric = fabrics["fabulous"]
    assert fabric.tile_library.name == "fabulous"
    assert PurePosixPath("fabric.csv") in fabric.files(language)
