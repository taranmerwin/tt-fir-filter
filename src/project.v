/*
 * Copyright (c) 2026 Taran Merwin
 * SPDX-License-Identifier: Apache-2.0
 *
 * 4-Tap Low-Pass FIR Filter
 * y[n] = (h0*x[n] + h1*x[n-1] + h2*x[n-2] + h3*x[n-3]) >> 3
 * h = [1, 3, 3, 1]  (symmetric -> linear phase), sum = 8
 */

`default_nettype none

module tt_um_fir4_taran (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

  localparam signed [7:0] H0 = 8'sd1;
  localparam signed [7:0] H1 = 8'sd3;
  localparam signed [7:0] H2 = 8'sd3;
  localparam signed [7:0] H3 = 8'sd1;

  reg signed [7:0] x0, x1, x2, x3;
  reg              out_valid;

  wire signed [10:0] mac;
  assign mac = (H0 * $signed(x0)) +
               (H1 * $signed(x1)) +
               (H2 * $signed(x2)) +
               (H3 * $signed(x3));

  wire signed [7:0] mac_norm;
  assign mac_norm = mac[10:3];   // arithmetic >>3 (floor divide by 8)

  wire sample_valid = uio_in[0];

  always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      x0 <= 8'sd0; x1 <= 8'sd0; x2 <= 8'sd0; x3 <= 8'sd0;
      out_valid <= 1'b0;
    end else if (sample_valid) begin
      x3 <= x2; x2 <= x1; x1 <= x0; x0 <= $signed(ui_in);
      out_valid <= 1'b1;
    end else begin
      out_valid <= 1'b0;
    end
  end

  assign uo_out  = mac_norm;
  assign uio_out = {6'b0, out_valid, 1'b0};
  assign uio_oe  = 8'b00000010;

  wire _unused = &{ena, uio_in[7:1], 1'b0};

endmodule
