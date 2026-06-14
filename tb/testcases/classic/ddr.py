# SPDX-FileCopyrightText: © 2026 FABulous Contributors
# SPDX-License-Identifier: Apache-2.0

import os
from pathlib import Path
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge, FallingEdge
from cocotb.types import LogicArray, Logic

from ..common import zero_bitstream, upload_bitstream, PCF, fabric, tile_library

testname = Path(__file__).stem
proj_path = Path(__file__).resolve().parent

@cocotb.test()
async def test_ddr(dut):
    """Load bitstream for ddr"""

    pcf = PCF(dut, proj_path / f"../../../fabrics/{fabric}/constraints.pcf")

    pcf.signals["my_ddr_out"] = {
      0: {
        'IN': dut.Tile_X0Y5_A_IN_top,
        'OUT': dut.Tile_X0Y5_A_OUT_top,
        'EN': dut.Tile_X0Y5_A_EN_top,
      }
    }

    pcf.signals["my_ddr_in"] = {
      0: {
        'IN': dut.Tile_X0Y6_A_IN_top,
        'OUT': dut.Tile_X0Y6_A_OUT_top,
        'EN': dut.Tile_X0Y6_A_EN_top,
      }
    }
    
    pcf.write_gtkw(f"{testname}.gtkw", ["clk1", "rst", "ena", "a", "my_ddr_out", "my_ddr_in"])

    # Reset
    pcf.set("clk1", Logic(0), index=0)
    pcf.set("clk2", Logic(0), index=0)
    pcf.set("rst", Logic(1), index=0)
    pcf.set("ena", Logic(1), index=0)
    await Timer(10, unit="ns")

    # Zero all config bits
    await zero_bitstream(dut)
    await Timer(10, unit="ns")

    # Upload the bitstream
    await upload_bitstream(dut, proj_path / f'../../../user_designs/designs/{tile_library}/{testname}/{testname}.bit')
    await Timer(10, unit="ns")

    # Start a clock on clk1
    clock = pcf.get_raw("clk1", "OUT")
    cocotb.start_soon(Clock(clock, 10, 'ns').start())

    await ClockCycles(clock, 10)
    
    pcf.set("rst", Logic(0), index=0)
    pcf.set("ena", Logic(0), index=0)
    
    cocotb.start_soon(Clock(pcf.get_raw("my_ddr_in", "OUT"), 10, 'ns').start())

    await ClockCycles(clock, 10)

    pcf.set("ena", Logic(1), index=0)

    await ClockCycles(clock, 10)
    
    # my_ddr_out inverts the clock
    await RisingEdge(clock)
    assert pcf.get("my_ddr_out").to_unsigned() == 1
    await FallingEdge(clock)
    assert pcf.get("my_ddr_out").to_unsigned() == 0
    
    # Sampling the clock via IDDR gives us 2'b01 pattern
    assert pcf.get("a").to_unsigned() == 0x01
