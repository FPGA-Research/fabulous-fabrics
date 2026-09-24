# FABulous Fabrics

This repository contains a collection of fabrics using the [fabulous-tiles](https://github.com/mole99/fabulous-tiles) tile libraries.

The fabrics can be found under `fabrics/`. Current fabrics include:

- classic_fabric_10x10
- classic_fabric_32x32
- tiny_fabric_5x5

The prefix describes the tile library that is used, e.g. `classic` or `tiny`.

The fabrics can be implemented with LibreLane using the FABulous plugin for LibreLane: [librelane_plugin_fabulous](https://github.com/mole99/librelane_plugin_fabulous).
See below for more information about stitching the fabric. 

A Continuous Integration (CI) setup implements the fabrics for the gf180mcu, sky130, and ihp-sg13g2 PDKs.

## Python package

The repository is also the `fabulous-fabrics` Python package, which FABulous uses to create projects. `fabulous_fabrics.fabrics["fabulous"]` describes a fabric, and `fabrics["fabulous"].materialise(dest, Language.VERILOG)` copies it with its tile library into `dest`. A fabric directory registers itself when it holds a `fabric.yaml`:

```yaml
schema_version: 1
description: The FABulous demo fabric, formerly the packaged FABulous project template.
tile_library: fabulous
```

The project skeleton sits beside it in `common/` and one directory per HDL (`verilog/`, `vhdl/`). The flat fabrics listed above have no `fabric.yaml` and are not registered. Another package adds its own fabrics through the entry-point group `fabulous.fabrics`.

## Requirements

> [!NOTE]
> Make sure to clone the repository with submodules!
>
>```console
>git clone --recurse-submodules <url>.git
>```
> or initialize the submodules after cloning:
>
>```console
> git submodule update --init --recursive
>```

For information on installing Nix with the FOSSi Foundation cache, please refer to the LibreLane documentation: https://librelane.readthedocs.io/en/stable/installation/nix_installation/index.html

## Stitch the Fabrics

As a prerequisite make sure that the tiles for the tile library that you are using have been implemented in `ip/fabulous-tiles`.
If that is the case, you can proceed by enabling a Nix shell with LibreLane in this repository:

```
nix-shell
```

To implement all fabrics, run:

```
make all
```

To implement a single fabric, run:

```
make classic_fabric_10x10
```

After a fabrics has been implemented you can view it either in OpenROAD or KLayout by appending `-openroad` or `-klayout` to the fabric name.
For example, to view `classic_fabric_10x10` in OpenROAD, run: `make classic_fabric_10x10-openroad`.

By default the fabrics are implemented using the ihp-sg13g2 PDK.
The currently supported PDKs are: `gf180mcu`, `sky130`, `ihp-sg13g2`.

To change the PDK, set the `PDK` environment variable:

```
export PDK=gf180mcu
```

## Implement User Designs

Please see the README in `user_designs/` on how to implement a user design for the fabrics.

## Simulate the Fabric

After you have generated the bitstreams for the user designs you can simulate the fabric.
You will again need the Nix shell from the root of this repository.

Again, use `PDK`, `FABRIC` and `TILE_LIBRARY` accordingly.

There are two ways to simulate the fabric:

#### RTL "Emulation"

In this case, "emulation" means that we simulate the fabric, however, without uploading the bitstream.
The configuration bits of the fabric are already initialized with the user design bitstream.
This has the benefit that simulation is much faster: no need to upload the bitstream and the Verilog simulator can prune dead branches. However, the disadvantage is that only a single user design can be run per simulation.

To emulate a user design, simply set EMULATE to its name:

```
export EMULATE=counter
```

Then, run the simulation using cocotb:

```
cd tb; python3 fabric_tb.py
```

#### RTL Simulation

To start the RTL simulation, simply run cocotb:

```
cd tb; python3 fabric_tb.py
```

And it will run all available test cases for the selected fabric and tile library.
