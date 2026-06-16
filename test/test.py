# SPDX-FileCopyrightText: 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge

async def send_sample(dut, value):
    dut.ui_in.value  = value & 0xFF
    dut.uio_in.value = 0x01
    await RisingEdge(dut.clk)
    dut.uio_in.value = 0x00
    await RisingEdge(dut.clk)

def signed8(v):
    v = int(v) & 0xFF
    return v - 256 if v >= 128 else v

@cocotb.test()
async def test_fir_filter(dut):
    dut._log.info("Start FIR filter test")

    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 4)
    dut.rst_n.value  = 1
    await ClockCycles(dut.clk, 2)

    dut._log.info("Test 1: impulse response")
    expected = [15, 47, 47, 15, 0]
    inputs   = [127, 0, 0, 0, 0]
    for i, (inp, exp) in enumerate(zip(inputs, expected)):
        await send_sample(dut, inp)
        got = signed8(dut.uo_out.value)
        assert got == exp, f"Impulse tap {i}: expected {exp}, got {got}"
        dut._log.info(f"  tap {i}: got {got} == {exp} OK")

    dut._log.info("Test 2: DC gain")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    for _ in range(4):
        await send_sample(dut, 127)
    got = signed8(dut.uo_out.value)
    assert got == 127, f"DC gain: expected 127, got {got}"
    dut._log.info(f"  DC output: {got} OK")

    dut._log.info("Test 3: negative sample")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)
    await send_sample(dut, 0x80)
    got = signed8(dut.uo_out.value)
    assert got == -16, f"Negative: expected -16, got {got}"
    dut._log.info(f"  -128 -> {got} OK")

    dut._log.info("Test 4: out_valid flag")
    dut.rst_n.value  = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value  = 1
    dut.ui_in.value  = 10
    dut.uio_in.value = 0x01
    await RisingEdge(dut.clk)
    dut.uio_in.value = 0x00
    await RisingEdge(dut.clk)
    valid = (int(dut.uio_out.value) >> 1) & 1
    assert valid == 1, f"out_valid should be 1, got {valid}"
    dut._log.info("  out_valid high OK")
    await RisingEdge(dut.clk)
    valid = (int(dut.uio_out.value) >> 1) & 1
    assert valid == 0, f"out_valid should be 0 when idle, got {valid}"
    dut._log.info("  out_valid low when idle OK")

    dut._log.info("ALL TESTS PASSED")
