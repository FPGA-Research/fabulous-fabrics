// SPDX-FileCopyrightText: © 2026 FABulous Contributors
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module ddr (
    input  wire       clk1,
    input  wire       rst,
    input  wire       ena,
    
    output wire my_ddr_out,
    input  wire my_ddr_in,
    
    output wire [5:0] a
);

    wire ddr_out_wire;

    (* BEL="X0Y5/A" *) IOBUF iobuf_0 (
      .PAD(my_ddr_out),
      .IN(ddr_out_wire),
      .EN(1'b1)
    );

    (* LOC="X0Y5/B" *) ODDR #(
      .INIT_Q0 (1'b0),
      .INIT_Q1 (1'b0)
    ) ODDR_i (
      .CLK  (clk1),
      .D0   (1'b0),
      .D1   (1'b1),
      .EN   (ena),
      .SR   (rst),
      .Q    (ddr_out_wire)
    );

    wire ddr_in_wire;

    (* BEL="X0Y6/A" *) IOBUF iobuf_1 (
      .PAD(my_ddr_in),
      .OUT(ddr_in_wire),
      .EN(1'b0)
    );

    (* LOC="X0Y6/C" *) IDDR #(
      .INIT_Q0 (1'b0),
      .INIT_Q1 (1'b0)
    ) IDDR_i (
      .CLK  (clk1),
      .EN   (ena),
      .SR   (rst),
      .D    (ddr_in_wire),
      .Q0   (a[0]),
      .Q1   (a[1])
    );


    /*reg [7:0] ctr1;

    // Reset before enable
    always @(posedge clk1_buf) begin
        if (rst) begin
            ctr1 <= '0;
        end else begin
            if (ena) begin
                ctr1 <= ctr1 + 1'b1;
            end
        end
    end*/

    // Enable before reset
    /*always @(posedge clk1_buf) begin
        if (ena) begin
            if (rst) begin
                ctr1 <= '0;
            end else begin
                ctr1 <= ctr1 + 1'b1;
            end
        end
    end*/

    //assign c = ctr1;

endmodule
