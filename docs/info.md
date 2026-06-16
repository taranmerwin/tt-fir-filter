<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a **4-tap low-pass FIR (Finite Impulse Response) filter**.

It computes the convolution sum:
y[n] = (h0·x[n] + h1·x[n-1] + h2·x[n-2] + h3·x[n-3]) >> 3

with fixed coefficients **h = [1, 3, 3, 1]** (sum = 8). The coefficients are **symmetric**, which guarantees a **linear phase response** — a key property of FIR filters where all frequency components are delayed by the same amount.

The design contains:
- A **delay line** (4-stage shift register) holding the current and previous 3 input samples
- A **multiply-accumulate (MAC)** unit computing the weighted sum
- A **normalization** stage (arithmetic right-shift by 3) that divides by 8 to keep the output within 8-bit range without a divider circuit

Inputs and outputs are treated as **8-bit signed** values. A new sample is loaded on each clock edge when the sample-valid strobe is high

## How to test

1. Apply a clock to `clk` and hold `rst_n` low for at least one cycle to reset the delay line.
2. Place an 8-bit signed sample on `ui_in[7:0]`.
3. Pulse `uio_in[0]` (sample valid strobe) high for one clock cycle to load the sample.
4. Read the filtered result on `uo_out[7:0]`. The `uio_out[1]` output valid flag goes high when a new output is ready.

**Impulse response test:** Feed a single sample of 127 followed by zeros. The output sequence will be `[15, 47, 47, 15, 0]` — the scaled, symmetric filter coefficients, confirming correct linear-phase FIR behavior.

**DC gain test:** Feed a constant value of 127. The steady-state output will be 127, confirming unity DC gain (the filter passes low frequencies unchanged).

## External hardware

No external hardware required. The design can be driven directly from the Tiny Tapeout demo board inputs and observed on the output LEDs, or tested via the cocotb testbench in the `test/` folder.
